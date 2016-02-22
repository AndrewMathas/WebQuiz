import time, os, re, string, urlparse, httplib, cgi

startjsmath = '''
<script src="/jsMath/jsMath.js" type="text/javascript"></script>
<script type="text/javascript">
    jsMath.Setup.Script("plugins/tex2math.js");
      if (!jsMath.Font) {jsMath.Font = {}}
      jsMath.Font.Message = function (message) {if (jsMath.Element("Warning")) return;
    var div = jsMath.Setup.DIV("Warning",{height:"0px"});
    div.innerHTML =
      '<center><table><tr><td>'
      + '<div id="jsMath_noFont"><div style="border:1px solid #666666; background-color:#FFFFFF; font-size:80%; padding:2px; position:absolute; top:0px; left:0px; z-index:102;">jsMath: using image fonts'
      + '<div style="text-align:left"><span style="float:left; margin: 4px 0px 4px 0px">'
      + '<span onclick="jsMath.Controls.Panel()" title=" Open the jsMath Control Panel " class="link" style="font-size:100%">Controls<\/span>'
      + '<\/span><span style="margin: 4px 0px 4px 0px; float:right">'
      + '<span onclick="jsMath.Font.HideMessage()" title=" Remove this font warning message " class="link" style="font-size:100%">Hide This<\/span>'
      + '<\/span><\/div><\/div><\/div>'
      + '<\/td><\/tr><\/table><\/center>'};
</script>'''
endjsmath = '''
<script type="text/javascript">
jsMath.ConvertTeX();
jsMath.ProcessBeforeShowing(document);
</script>'''
# http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS_HTML
usemathjax = '''
<script src="/u/SMS/MathJax/MathJax.js?config=TeX-AMS-MML_HTMLorMML"  type="text/javascript"></script>'''
def processtemplate(things,pageinserts,page,pagename):
    proxy_server = 'siv'
    main_local_server = 'http://siv'
    local_servers = ['www.maths.usyd.edu.au','www.maths.usyd.edu.au','siv','rome','bari']
    localtime = time.localtime(time.time())
    nextyeartime = time.localtime(time.time()+31536000)
    htpath = "/users/misc/httpd/htdocs"
    ustring = 'u'
    things['thisPage'] = page + '/' + pagename
    things['monthname'] = time.strftime('%B',localtime)
    things['monthnumber'] = `int(time.strftime('%m',localtime))`
    things['dayofweek'] = time.strftime('%A',localtime)
    things['dayofmonth'] =  `int(time.strftime('%d',localtime))`
    things['year'] = time.strftime('%Y',localtime)
    things['nextyear'] = time.strftime('%Y',nextyeartime)
    things['AMPM'] = time.strftime('%p',localtime)
    things['ampm'] = string.lower(things['AMPM'])
    things['hour12'] = `int(time.strftime('%I',localtime))`
    things['hour24'] = `int(time.strftime('%H',localtime))`
    things['minute'] = `int(time.strftime('%M',localtime))`
    if not things.has_key('UNITS_OF_STUDY,doctype'):
        things['UNITS_OF_STUDY,doctype'] = 'html'
    if not things.has_key('UNIT_OF_STUDY,doctype'):
        things['UNIT_OF_STUDY,doctype'] = things['UNITS_OF_STUDY,doctype']
    if not things.has_key('UNIT_OF_STUDY,template_file'):
        if things['UNIT_OF_STUDY,doctype'] in ['xhtml','mathml']:
            things['UNIT_OF_STUDY,template_file'] = 'u/SMS/web2010/xmltemplate.txt'
        else:
            things['UNIT_OF_STUDY,template_file'] = 'u/SMS/web2010/template.txt'
    begin_block = '[@@'
    end_block = '@@]'
    bb_len = len(begin_block)
    eb_len = len(end_block)
    begin_quote = '[^^'
    end_quote = '^^]'
    rebq = re.escape(begin_quote)
    reeq = re.escape(end_quote)
    command = re.compile('(?s)(?P<name>[A-Za-z0-9]*)\\='+rebq+'(?P<value>.*?)'+reeq)

    def varrep(a):
        error = []
        if string.count(a,'~') == 0:
            return error,a
        alist = string.split(a,'|')
        newalist = []
        for i in alist:
            if i[:1] != '~':
                newalist.append(i)
            elif i[:2] == '~~':
                newalist.append(i[1:])
            elif things.has_key(i[1:]):
                newalist.append(things[i[1:]])
            else:
                error.append(i[1:]+' not defined')
                newalist.append(i)
        return error, string.join(newalist,'|')

    pjoin = os.path.join

    def parse_block(block):
        dict = {}
        while 1:
            c_match = command.search(block)
            if not c_match: return dict
            dict[c_match.group('name')] = c_match.group('value')
            block = block[c_match.end():]

    def strip(s):
        s = re.sub('(?i)<(/?html)>','',s)
        s = re.sub('(?is)<(/?body.*?)>','',s)
        s = re.sub('(?is)<head>(.*?)</head>','',s)
        s = re.sub('(?is)<!doctype.*?>','',s)
        s = string.replace(s,'rooms.html','/w/tt/rooms.html')
        s = string.strip(s)
        return s

#  Remove nonalphanumeric characters from a string

    def rnan(s):
        s = re.sub(r'\W+', '', s)
        return s
    
    template_filename = pjoin(htpath,things['UNIT_OF_STUDY,template_file'])
    template_file = open(template_filename)
    t = template_file.read()
    template_file.close()
    files = [template_filename]
    errors = []
    URLproblems = []
    start = max(string.find(t,begin_block),0)
    b_end = string.find(t,end_block)
    while b_end != -1:
        rep = ''
        b_start = string.rfind(t,begin_block,start,b_end)
        if b_start == -1:
            block_commands = {'error':"Grouping error: no '[@@' to match a '@@]', "}
        else:
            block_commands = parse_block(t[b_start+bb_len:b_end])

        # convert all of the '~...' for 'if' 'is' 'ifexists'
        # to 'things[...]'

        for i in block_commands.keys():
            if i in ['if','is','ifexists']:
                err, block_commands[i] = varrep(block_commands[i])
                errors = errors + err

        if block_commands.has_key('if') and block_commands.has_key('is'):
            tempdict = {}
            ifval = block_commands['if']
            isval = block_commands['is']
            del block_commands['if']
            del block_commands['is']
            if ifval in string.split(isval,'|'):
                for at in block_commands.keys():
                    if at[:4] != 'else':
                        tempdict[at] = block_commands[at]
            else:
                for at in block_commands.keys():
                    if at[:4] == 'else':
                        tempdict[at[4:]] = block_commands[at]
            block_commands = tempdict


        if block_commands.has_key('ifexists'):
            tempdict = {}
            ifexists = block_commands['ifexists']
            del block_commands['ifexists']
            if things.has_key(ifexists):
                for at in block_commands.keys():
                    if at[:4] != 'else':
                        tempdict[at] = block_commands[at]
            else:
                for at in block_commands.keys():
                    if at[:4] == 'else':
                        tempdict[at[4:]] = block_commands[at]
            block_commands = tempdict

        if block_commands.has_key('ifURLexists'):
            tempdict = {}
            test_URL = block_commands['ifURLexists']
            test_URL_old = block_commands['ifURLexists']
            del block_commands['ifURLexists']
            urlok = 0
            if test_URL != 'nonexistent':
	        if test_URL[:5] == 'http:':
                    split_URL = urlparse.urlparse(test_URL)
                    lastpart_URL = split_URL[2]+split_URL[3]+split_URL[4]+split_URL[5]
                    if split_URL[1] in local_servers:
                        if os.access(pjoin(htpath,lastpart_URL[1:]),os.R_OK) == 1:
                            urlok = 1
                        else:
                            test_URL = urlparse.urljoin(main_local_server,lastpart_URL)
                else:
                    if test_URL[:1] != '/':
                        test_URL = '/'+pjoin(ustring,page,test_URL)
                    if os.access(pjoin(htpath,test_URL[1:]),os.R_OK) == 1:
                        urlok = 1
                    else:
                        test_URL = urlparse.urljoin(main_local_server,test_URL[1:])
                if urlok == 0:
                    conn = httplib.HTTPConnection(proxy_server)
                    conn.request("GET", test_URL)
                    resp = conn.getresponse()
                    while (resp.status < 400) and (resp.status > 299):
                        conn = httplib.HTTPConnection(proxy_server)
                        conn.request("GET", resp.getheader("Location"))
                        resp = conn.getresponse()
                    if resp.status < 300:
                        urlok = 1
            if urlok == 0:
                for at in block_commands.keys():
                    if at[:4] == 'else':
                        tempdict[at[4:]] = block_commands[at]
            else:
                for at in block_commands.keys():
                    if at[:4] != 'else':
                        tempdict[at] = block_commands[at]
            block_commands = tempdict

        # convert all of the '~...' for remaining commands
        # to 'things[...]'

        for i in block_commands.keys():
            err, block_commands[i] = varrep(block_commands[i])
            errors = errors + err


        # Note: text and insert used to be synonyms

        if block_commands.has_key('unset'):
            del things[block_commands['unset']]
            del block_commands['unset']

        if block_commands.has_key('insert'):
            rep = block_commands['insert']
            del block_commands['insert']

        if block_commands.has_key('insert1'):
            rep += block_commands['insert1']
            del block_commands['insert1']

        if block_commands.has_key('insert2'):
            rep += block_commands['insert2']
            del block_commands['insert2']

        if block_commands.has_key('insert3'):
            rep += block_commands['insert3']
            del block_commands['insert3']

        if block_commands.has_key('text'):
            rep += block_commands['text']
            del block_commands['text']
            if block_commands.has_key('replace'):
                if block_commands.has_key('with'):
                    rep = rep.replace(block_commands['replace'],block_commands['with'])
                    del block_commands['with']
                del block_commands['replace']
            if block_commands.has_key('SliceStart'):
                if block_commands.has_key('SliceEnd'):
                    rep = rep[int(block_commands['SliceStart']):int(block_commands['SliceEnd'])]
                    del block_commands['SliceEnd']
                else:
                    rep = rep[int(block_commands['SliceStart']):]
                del block_commands['SliceStart']
            elif block_commands.has_key('SliceEnd'):
                rep = rep[:int(block_commands['SliceEnd'])]
                del block_commands['SliceEnd']

 #       if block_commands.has_key('eval'):
 #           rep = eval(block_commands['eval'])
 #           del block_commands['eval']


        if block_commands.has_key('pageinsert'):
            if pageinserts.has_key(block_commands['pageinsert']):
	        if pageinserts[block_commands['pageinsert']] != 'nonexistent':
                    block_commands['URLplus'] = pageinserts[block_commands['pageinsert']]
		things['URL,' + block_commands['pageinsert']] = pageinserts[block_commands['pageinsert']]
            del block_commands['pageinsert']

        if block_commands.has_key('URL'):
            block_commands['URLplus'] = block_commands['URL']
            del block_commands['URL']

        if block_commands.has_key('URLplus'):
            test_URL = block_commands['URLplus']
            del block_commands['URLplus']
            if block_commands.has_key('pass'):
                passlist = []
                for var in string.split(block_commands['pass'],'|'):
                    if things.has_key(var):
                        if var[:9] == 'formname,':
                            varname = var[9:]
                        else:
                            varname = var
                        passlist.append(urllib.quote_plus(varname)+'='+urllib.quote_plus(things[var]))
                ins_URL = ins_URL+'?'+string.join(passlist,'&')
                del block_commands['pass']
            if test_URL in files:
                errors.append('file '+test_URL+' referenced twice')
            elif test_URL != '':
                files.append(test_URL)
                repfound = 0
                if test_URL[:6] == 'file:/':
                    test_URL = test_URL[6:]
                    if os.access(test_URL,os.R_OK) == 1:
                        insert_file = open(test_URL)
                        rep = strip(insert_file.read())
                        insert_file.close()
                        repfound = 1
                elif test_URL[:5] == 'http:':
                    split_URL = urlparse.urlsplit(test_URL)
                    lastpart_URL = split_URL[2]
                    if split_URL[1] in local_servers:
                        if os.access(pjoin(htpath,lastpart_URL[1:]),os.R_OK) == 1:
                            insert_file = open(pjoin(htpath,lastpart_URL[1:]))
                            rep = strip(insert_file.read())
                            insert_file.close()
                            repfound = 1
                        else:
                            test_URL = urlparse.urlunsplit([split_URL[0],"siv",split_URL[2],split_URL[3],split_URL[4]])
                else:
                    if test_URL[:1] != '/':
                        test_URL = '/'+pjoin(ustring,page,test_URL)
                    if os.access(pjoin(htpath,test_URL[1:]),os.R_OK) == 1:
                        insert_file = open(pjoin(htpath,test_URL[1:]))
                        rep = strip(insert_file.read())
                        insert_file.close()
                        repfound = 1
                    else:
                        test_URL = urlparse.urljoin(main_local_server,test_URL[1:])
                if repfound == 0:
                    conn = httplib.HTTPConnection(proxy_server)
                    conn.request("GET", test_URL)
                    resp = conn.getresponse()
                    while (resp.status < 400) and (resp.status > 299):
                        conn = httplib.HTTPConnection(proxy_server)
                        conn.request("GET", resp.getheader("Location"))
                        resp = conn.getresponse()
                    if resp.status > 399:
                        conn.close()
                        rep=''
                        URLproblems.append(test_URL)
                    else:
                        rep = strip(resp.read())
                        conn.close()


        if block_commands.has_key('preview'):
            rep = '#########preview#########'
            del block_commands['preview']
            if block_commands.has_key('action'):
                preview_action = block_commands['action']
                del block_commands['action']
            if block_commands.has_key('name'):
                preview_name = block_commands['name']
                del block_commands['name']
            if block_commands.has_key('value'):
                preview_value = block_commands['value']
                del block_commands['value']
            if block_commands.has_key('method'):
                preview_method = block_commands['method']
                del block_commands['method']
            if (block_commands.has_key('hiddenname') and block_commands.has_key('hiddenvalue')):
                preview_hiddenname = block_commands['hiddenname']
                del block_commands['hiddenname']
                preview_hiddenvalue = block_commands['hiddenvalue']
                del block_commands['hiddenvalue']

        if block_commands.has_key('basehref'):
            rep = '#########basehref#########'
            del block_commands['basehref']

        if block_commands.has_key('webinsert') and block_commands.has_key('source'):
            pageinserts[block_commands['webinsert']] = block_commands['source']
            del block_commands['webinsert']
            del block_commands['source']


        if block_commands.has_key('set') and block_commands.has_key('to'):
            things[block_commands['set']] = block_commands['to']
            del block_commands['set']
            del block_commands['to']


        if block_commands.has_key('comment'):
            del block_commands['comment']


        if block_commands.keys() not in [['error'],[]]:
            block_commands['error'] =  `block_commands.keys()`+" doesn't make sense"


        if block_commands.has_key('error'):
            rep = ''
            if block_commands['error'] == 'buttons':
                errors.append('Must preview without buttons before updating')
            elif block_commands['error'][:24] == 'Unknown files accessible':
                errors.append(block_commands['error'])
            else:
                errors.append(block_commands['error']+' near the following text: <br><table><tr><td><div style="color:#6666ff"><pre>'+cgi.escape(t[max(b_start-100,0):max(b_start,0)]+'...'+t[b_end+3:b_end+100])+'</pre></div></td></tr></table>')
            start = start+eb_len

        if b_start == -1:
            t = str(rep)+t[b_end+eb_len:]
        else:
            t = t[:b_start]+str(rep)+t[b_end+eb_len:]
        start = max(string.find(t,begin_block,start),0)
        b_end = string.find(t,end_block,start)
    if string.find(t,begin_block) != -1:
        errors.append("""Grouping error: a '[@@' without a matching '@@]' near the following text: <br><table><tr><td><div style="color:#6666ff"><pre>..."""+cgi.escape(t[max(start,0):max(start+100,0)])+'</pre></div></td></tr></table>')
    t = string.replace(t,'Check your marks|','Check your marks')
    if things.has_key('nopreview'):
        t = string.strip(t)
        t = re.sub('(\s?)+\\n','\\n',t)
        t = re.sub('(\s?)+\\n((\s?)+\\n)+','\\n',t)
        t = string.replace(t,str('#########preview#########'),'')
        t = string.replace(t,str('#########basehref#########'),'')
    if not things.has_key('UNIT_OF_STUDY,noMathJax'):
        if string.find(t,'\\(') != -1 or string.find(t,'\\[') != -1:
            t = string.replace(t,'</head>',usemathjax+'</head>')
    return t,errors,URLproblems
