#!/usr/bin/python
"""  MathQuiz.py | 2001-03-21     | Don Taylor
                   2004 Version 3 | Andrew Mathas

     Convert an XML quiz description file to an HTML file
     using CSS and JavaScript.

     See quiz.dtd for the DTD and xmlquiz.py for the
     Python object structure reflecting the DTD.

     27 Jan 03
     Swapped the position of the progress strip with
     the main text.  Added support for <meta> and <link>
     tags coming from the tex4ht conversion.
"""
import sys, os, xmlquiz
VERSION   = 'MathQuiz 3.0'
alphabeta = " abcdefghijklmnopqrstuvwxyz"

TIMED = 0
if TIMED:
  import time
 
def main():

  dispatch = {
    'html'    : html,
    'xml'     : xml,
    'tex'     : tex,
    'text'    : text,
    }

  def fail(lst):
    print 'Usage: %s <xml-file> <target>' % sys.argv[0]
    print 'where <target> is one of:',
    for k in lst.keys(): print k,
    sys.exit(1)

  if len(sys.argv) < 2:
    fail(dispatch)

  try:
    f = open(sys.argv[1])
  except IOError,e:
    print >> sys.stderr, e
    sys.exit(1)

  if len(sys.argv) > 2:
    target = sys.argv[2]
  else:
    target = 'html'

  if TIMED: start = time.clock()
  quiz = xmlquiz.DocumentTree(f)
  if TIMED: print >> sys.stderr, 'Parse time:',time.clock()-start
  f.close()
  try:
    fn = dispatch[target]
  except KeyError:
    fail(dispatch)
  if TIMED: start = time.clock()
  fn(quiz)
  if TIMED: print >> sys.stderr,'Processing time:', time.clock()-start

# -----------------------------------------------------
# End of main()
# -----------------------------------------------------
def text(doc):
  print doc


# -----------------------------------------------------
#  Visitor classes 
# -----------------------------------------------------
# A visitor class must define the following interface
#
#  forQuiz
#  forQuestion
#  forChoice
#  forAnswer
#  forItem
#
#  xmlquiz.nodeVisitor is an adaptor class with default
#  methods that do nothing except pass on the visitor
#  to their children
#
# -----------------------------------------------------
#  xmlWriter() is a visitor defined in xmlquiz.py
# -----------------------------------------------------
def xml(doc):
  doc.accept(xmlquiz.xmlWriter())
# -----------------------------------------------------
#  TeX visitor
# -----------------------------------------------------
def tex(doc):
  doc.accept(TeXWriter())

class TeXWriter(xmlquiz.nodeVisitor):
  """ This visitor class traverses the document tree
      and writes out the data in the form expected
      by the genquiz.sty style file.
  """

# A lot of this needs improvement.  For example, the
# number of choices per question is hard-wired to 4.
  def forQuiz(self,node):
    print '\\input genquiz.sty'
    print '\\def\\quizid{xxxxx}'
    print '\\def\\infoline{%s}' % node.title
    print '\\RecordAnswers'
    print '\\quiztop{%d}{4}' % len(node.questionList)
    print '\\signaturebox'
    print '\\vskip\\quizskip'
    print 'You may use the space below for your own work.'
    print '\\newpage'
    node.broadcast(self)
    print '\\bye'

  def forQuestion(self,node):
    print '\n\\exercise'
    print strval(node.question)
    node.broadcast(self)

  def forChoice(self,node):
    print '\\beginparts'
    node.broadcast(self)
    print '\\endparts'

  def forAnswer(self,node):
    print '\\fbox{\\hbox to 1cm{\strut\\hfil}}'

  def forItem(self,node):
    if node.expect == 'true':
      tag = '\\correct'
    else:
      tag = ''
    print '\\part %s%s' % (strval(node.answer),tag)
    if node.response:
      print '[%s]' % strval(node.response)


# -----------------------------------------------------
# Conversion routines: XML to DHTML
# -----------------------------------------------------
NoScript = """If you are reading this message either your
  browser does not support JavaScript or else JavaScript
  is not enabled.  You will need to enable JavaScript and
  then reload this page before you can use this quiz."""

CSStop = """<!--
    tr { vertical-align: top; }

    #copy {
	font-family: sans-serif, verdana, helvetica;
	font-size: 8pt; 
    }
    #copy A{
	text-decoration: none;
    }
    .SideMenu {
	color: #3333CC;
	font-family: sans-serif, verdana, helvetica;
	font-size: 10pt; 
	font-weight: bold;
	text-align: left;
        text-decoration: none;
    }
    .SideMenuB {
	color: black;
	font-family: sans-serif, verdana, helvetica;
	font-size: 10pt; 
	font-weight: bold;
	text-align: left;
        text-decoration: none;
    }
    TD.SideMenu:hover { background-color: white; }
    .TopMenu {
	color: #3333AC;
	background-color: #fff084;
	font-family: sans-serif, verdana, helvetica;
	font-size: 10pt; 
	font-weight: bold;
        text-decoration: none;
	text-align: left;
    }
    A.TopMenu:hover { background-color: #ffcc00; }
    .QuizList {
       color: #3333AC;
       font-family: sans-serif, verdana, helvetica;
       font-weight: bold;
       text-decoration: none;
       text-align: left;
    }
    A.QuizList:hover { background-color: #ffcc00; }
    TD.QuizList:hover { background-color: orange; }
    P  { font-family: verdana, helvetica, sans-serif; }
    H1 { color: blue; }
    H2 { font-family: verdana, helvetica, sans-serif; font-weight: bold; }
    H4 { font-family: verdana, helvetica, sans-serif; font-weight: bold; color: black; }

    .brown    { color: #cc3300; }
    .red      { color: red; }
    .QText    { text-align: left; }
    .RText    { color: black; text-align: left; }
    .QChoices { text-align: left; }"""

Qgeometry = """    {
      position: absolute;
      top: 160px;
      left: 180px;
      width: 75%;"""

Rgeometry = """    {
      position: absolute;
      top:  10px;
      left: 0px;
      padding: 5px;
      border: solid black 2px;
      visibility: hidden;
    }"""

QuizColour = ["purple","darkred","darkblue","darkgreen"]

# Document tree structure

#   doc.title
#      .questionList[].question
#                     .answer.type               (Choice)
#                            .itemList[].expect
#                                       .answer
#                                       .response 
#                     .answer.tag                (Answer)
#                            .whenTrue
#                            .whenFalse

def html(doc):
  """ Converts the document tree to HTML
  """
  print '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN"'
  print '    "http://www.w3.org/TR/html401/loose.dtd">'
  print '<html>\n<head>'
  print '<meta name="Copyright" content="University of Sydney 2004">' 
  print '<meta name="GENERATOR" content="%s">' % VERSION
  print '<meta name="AUTHORS" content="Andrew Mathas and Don Taylor">'
  for attr in doc.metaList:
    s = '<meta'
    for k in attr.keys():
      s += ' %s="%s"' % (k, attr[k])
    s += '/>'
    print s
  for attr in doc.linkList:
    s = '<link'
    for k in attr.keys():
      s += ' %s="%s"' % (k, attr[k])
    s += '/>'
    print s
  print '<title>%s</title>' % doc.title
  # Cascading Style Sheet code
  print """<!--
  By reading through this file you should be able to extract the
  answers to the quiz; however, you will get more out of the quiz if
  you do the questions yourself. Of course, you are free to read the
  source if you wish.
-->
<script src="/u/mathas/mathquiz/mathquiz.js" 
        type="text/javascript" 
        language="javascript">
</script>
<style type="text/css">"""
  print CSStop
  dnum=0
  if len(doc.quizList)>0:
    dnum+=1
    print '    #question-%d' % dnum
    print Qgeometry
    print '      visibility: visible;\n    }'
      
  for d in doc.discussionList:
    dnum+=1
    print '    #question-%d' % dnum
    print Qgeometry
    if dnum==1:
      print '      visibility: visible;\n    }'
    else:
      print '      visibility: hidden;\n    }'

  qnum = 0
  for q in doc.questionList:
    qnum += 1
    print '\n    #question%d' % qnum
    print Qgeometry
    if len(doc.discussionList)==0 and qnum==1:
        print '      visibility: visible;'
    else:
        print '      visibility: hidden;'
#    print '      color: %s;' % QuizColour[qnum % len(QuizColour)]
    print '    }'
    print '\n    #answer%d' % qnum
    print '    {'
    print '      position: relative;'
    print '      visibility: visible;'
    print '      width: auto;'
    print '    }'
    if isinstance(q.answer,xmlquiz.Choice):
      if q.answer.type == "multiple":
        print '\n    #q%dresponse0' % qnum
        print Rgeometry
      rnum = 0
      for s in q.answer.itemList:
        rnum += 1
        print '\n    #q%dresponse%d' % (qnum,rnum)
        print Rgeometry
    else:
      print '\n    #q%dtrue' % qnum
      print Rgeometry
      print '\n    #q%dfalse' % qnum
      print Rgeometry
  print '-->\n</style>'

  #gallery = os.environ.get("GALLERY","buttons")
  #if not gallery[-1] == '/':
  #  gallery += '/'
  gallery="/u/MOW/buttons/"

  # Additional JavaScript code:
  print '<script language="javascript" type="text/javascript">\n<!--'
  #print '  GALLERY = "/u/MOW/buttons/"' % gallery
  setPatterns(doc.questionList, doc.discussionList)
  print '// -->\n</script>'

  print '</head>'
  qTotal = len(doc.questionList)
  print '<body bgcolor="#ffffff" onload="init(%d)">' % qTotal
  print '<noscript>%s</noscript>' % NoScript

  showBanner( doc.title, doc.course[0], doc.quizList, len(doc.questionList) )

  triangle="""          <tr><td bgcolor="#fff084"><img border="0" height="21" 
          width="20" alt="" src="/img/triangle.gif"></td>"""
  space=   """          <tr><td colspan="2" bgcolor="#ffcc00">
                  <img src="/img/space.gif" alt="" width="1" 
				      height="10" border="0"></td>
          </tr>"""
  thinline="""           <tr><td colspan="2" bgcolor="#e48928">
                  <img src="/img/navy.gif" alt="" width="1" 
                       height="1" border="0"></td>
          </tr>"""
  
  print space
  print thinline
  print space

  if len(doc.discussionList)>0:
    # links for discussion items
    dnum=0
    for d in doc.discussionList:
      dnum+=1
      print triangle
      print '                 <td bgcolor="#fff084" class="SideMenu" >'
      print '                    <a HREF="javascript:void(0)" class="SideMenu"'
      print '           onMouseOver="window.status=\'%s\'; return true;"' % d.heading
      print '                       onClick="return gotoQuestion(-%d);">' % dnum
      print '                       %s</a></td></tr>' % d.heading
      print space
      
    print thinline
    print space

  if len(doc.questionList)>0:
    # button for question numbers and meaning of symbols
    print triangle
    print '                 <td class="SideMenuB" bgcolor="#fff084">'
    print '                   Questions</td>'
    print '            </tr>'
    print space
    print '            <tr><td></td><td>'
    print '               <a HREF="javascript:void(0)"'
    print '           onMouseOver="window.status=\'Question 1\'; return true;"'
    print '                  onClick="return gotoQuestion(1);">'
    if len(doc.discussionList)==0:
      firstimage='%s/border1.gif' % gallery
    else:
      firstimage='%s/clear1.gif' % gallery
    print '  <img alt="" src="%s" name="progress1" align="TOP"' % firstimage
    print '       height="31"width="31" border="0" hspace="2" vspace="2"></a>'
    for i in range(2,qTotal+1):
      if i % 2 == 1:
        print '<br>'
      print '<a HREF="javascript:void(0)" onClick="return gotoQuestion(%d)"' % i
      print '   OnMouseOver="window.status=\'Question %d\';return true">' % i
      print '<img alt="" src="%sclear%d.gif" name="progress%d" align="TOP" height="31" width="31" border="0" hspace="2" vspace="2"></a>' % (gallery,i,i)

    print '                 </td></tr>'
    print space
    imgTag = '    <tr><td bgcolor="#fff084"></td><td class="SideMenuB" bgcolor="#fff084"><img alt="" src="'+gallery+'%s.gif" align="%s" height="%d" width="%d" border="0" hspace="2" vspace="2">'
    print imgTag % ('star',"MIDDLE",12,12)
    print 'right first<br>&nbsp;&nbsp;&nbsp;&nbsp;attempt</td></tr>'
    print space
    print imgTag % ('tick',"MIDDLE",18,14)
    print 'right</td></tr>'
    print space
    print imgTag % ('cross',"MIDDLE",9,10)
    print 'wrong</td></tr>'
    print space
    print space
    print space
    print thinline
  # end of progress buttons

  print space
  print space
  print """               <tr><td colspan="2" align="center" ID="copy">
		 <br><a href="/u/mathas/mathquiz/credits.html"
		    onMouseOver="window.status='MathQuiz 3.0'; return true">
		    <font face="3DArial, ArialBlack" color="red">%s</font></a><br>
		 <a href="http://www.usyd.edu.au"
		    onMouseOver="window.status='University of Sydney'; return true">
		   <font color="black">University of Sydney</font></a><br>
		 <font color="blue"><a href="http://www.maths.usyd.edu.au"
		    onMouseOver="window.status='School of Mathematics and Statistics'; return true">
		   School of Mathematics<br> and Statistics</a></font><br>
		   &copy; Copyright 2004
		 </td></tr>
             <tr><td colspan="2"><br><br><br><br><br><br><br><br><br><br>
	       <br><br><br><br><br><br><br><br><br><br><br>
	       <br><br><br><br><br><br><br><br><br><br><br>
	       <br><br><br><br><br><br><br><br><br><br><br>
	       <br><br><br><br><br><br><br><br><br><br><br>
	       <br><br><br><br><br><br><br><br><br><br><br>
	     </td></tr>
             </tbody></table><!-- end of sidebar -->
          </td>
       </tr>
     </tbody>
   </table>

<!-- start of main page -->

""" % VERSION

  # now print the main page text
  if len(doc.quizList)>0:
    print """<div ID="question-1">
  <table valign="top" bgcolor="#ffffff" border="0" 
         cellspacing="0" cellpadding="5" summary="quiz index">
   <tbody>
   <tr><td><h2 class="brown">%s Quizzes</h2></td>
   </tr>""" % doc.course[0]['name']
    qnum=0
    for q in doc.quizList:
      qnum+=1
      print """<tr><td nowrap class="QuizList"
        onMouseOut="return menuOut('%d');" 
        onMouseOver="return menuOver('%d','%s');">
      <a class="QuizList" onMouseOut="return menuOut('%d');" 
         onMouseOver="return menuOver('%d','%s');" 
         href="%s">
         <img src="/u/MOW/images/arrow.gif" alt=">" border="0" hspace="3"
	      NAME="quiztitle%d" ID="quiztitle%d">&nbsp;%s</a>
     </td></tr>""" % (qnum,qnum,q['title'],qnum,qnum,q['title'],q['url'],qnum,qnum,q['title'])

    print '</tbody></table>\n</div>'

  # discussion(s) masquerade as negative questions
  if len(doc.discussionList)>0:
    dnum = 0
    for d in doc.discussionList:
      dnum+=1
      print '\n<div ID="question-%d">' % dnum
      print '<h2 class="brown">%s</h2>' % d.heading
      print '%s\n<p><br>\n' % strval(d.discussion)
      if len(doc.questionList)>0 and dnum==len(doc.discussionList):
        print '<input TYPE="button" NAME="next" VALUE="Start quiz"\n'
        print '       onClick="return gotoQuestion(1);">'
      print '</div>'

  if len(doc.questionList)>0:
    qnum = 0
    for q in doc.questionList:
      qnum += 1
      print '\n<div ID="question%d">' % qnum
      printQuestion(q,qnum)
      printResponse(q,qnum)
      print '</div>'

  print '</body>\n</html>'

def setPatterns(qList, dList):
  if len(dList)==0:
      print '  currentQ=1  // start showing the first question'
  else:
      print '  currentQ=-1  // start showing discussion'
  i = 0
  for q in qList:
    print '  QList[%d] = new Array()' % i
    a = q.answer
    if isinstance(a,xmlquiz.Answer):
      print '  QList[%d].value = "%s"' % (i,a.value)
      print '  QList[%d].type = "input"' % i
    else:
      print '  QList[%d].type = "%s"' % (i,a.type)
      j = 0
      for s in a.itemList:
        print '  QList[%d][%d] = %s' % (i,j,s.expect)
        j += 1
    i += 1
    
def printQuestion(Q,n):
  print '<h2 class="brown">Question %d</h2>' % n
  print '<div class="QText">'
  print strval(Q.question)
  print '</div>'
  print '<form name="Q%dForm" onSubmit="return false;">' % n
  snum = 0
  if isinstance(Q.answer,xmlquiz.Answer):
    print '<p><input TYPE="text"  onChange="checkAnswer();" SIZE="5">'
    if Q.answer.tag:
      print '<span class="QText"> ' + Q.answer.tag +'</span>'
  else:
    print '<table summary="List of question choices" cellspacing="4" cellpadding="4">'
    print '<col width="2ex"><col width="2x"><col width="*">'
    # print extra column specifications as necessary
    for c in range(1,Q.answer.cols):
      print '<col width="10ex"><col width="2ex"><col width="2x"><col width="*">'
    for s in Q.answer.itemList:
      snum += 1
      printItem(s, n, snum)
    if s.parent.type=='single':  # no default answer for question
      print '<tr><td colspan=2><input type="hidden" checked'
      print '               name="Q%dhidden"></td></tr>' % n
    print '</table>'
  print '<p>'
  print '<input TYPE="button" VALUE="Check Answer" NAME="answer" onClick="checkAnswer();">'
  print '<span style="width:40px;">&nbsp;</span>'
  print '<input TYPE="button" VALUE="Next Question" NAME="next" onClick="nextQuestion(1);">'
  print '</form>'

def strval(ustr):
  if type(ustr) == type(u''):
    str = ''
    for c in ustr:
      str += chr(ord(c))
  else:
    str = ustr
  return str

def printItem(S,q,n):
  if S.parent.cols==1 or (n % S.parent.cols)==1: 
    print '<tr valign="top">'
  else: 
    print '<td>&nbsp;</td>'
  print '    <td class="brown">%s)</td>' % alphabeta[n]
  if S.parent.type == 'single':
    print '    <td><input TYPE="radio" NAME="Q%doptions"></td>' % q
    print '    <td><span class="QChoices">%s</span></td>' % strval(S.answer)
  elif S.parent.type == 'multiple':
    print '    <td><input TYPE="checkbox" NAME="Q%doptions%d"></td>' % (q,n)
    print '    <td><span class="QChoices">%s</span></td>' % strval(S.answer)
  else:
    print '<!-- internal error: %s -->' % S.parent.type
    print >> sys.stderr, 'Unknown question type encountered:',S.parent.type
  if (n % S.parent.cols)==0 or n==len(S.parent.itemList): print '</tr>'


def printResponse(Q,n):
  snum = 0
  print '\n<div ID="answer%d">' % n
  if isinstance(Q.answer,xmlquiz.Answer):
    s = Q.answer
    print '\n<div ID="q%dtrue">' % n
    print '<B>Your answer is correct</B><br>'
    if s.whenTrue:
      print '<div class="RText">%s</div>' % strval(s.whenTrue)
    print '</div>'
    print '\n<div ID="q%dfalse">' % n
    print '<B>Not correct. You may try again.</B>'
    if s.whenFalse:
      print '<div class="RText">%s</div>' % strval(s.whenFalse)
    print '</div>'
  elif Q.answer.type == "single":
    for s in Q.answer.itemList:
      snum += 1
      print '\n<div ID="q%dresponse%d">' % (n,snum)
      print '<B>'
      if s.expect == "true":
        print 'Your answer is correct.<br>'
      else:
        print 'Not correct. Choice <span class="brown">(%s)</span>' % alphabeta[snum]
	print 'is <span class="red">%s</span>.' % s.expect
      print '</B>'
      if s.response:
        print '<div class="RText">%s</div>' % strval(s.response)
      print '</div>'
  else: # Q.answer.type == "multiple":
    for s in Q.answer.itemList:
      snum += 1
      print '\n<div ID="q%dresponse%d">' % (n,snum)
      print '<B>There is at least one mistake.</B><br>'
      print 'For example, choice <span class="brown">(%s)</span>' % alphabeta[snum]
      print 'should be <span class="red">%s</span>.' % s.expect
      if s.response:
        print '<div class="RText">%s</div>' % strval(s.response)
      print '</div>'
    print '\n<div ID="q%dresponse0">' % n
    print '<B>Your answers are correct</B>'
    print '<ol type="a">'
    for s in Q.answer.itemList:
      print '<li class="brown"><div class="RText"><b>%s</b>. %s</div>' % (strval(s.expect.capitalize()),strval(s.response))
    print '</ol>'
    print '</div>'
  print '</div>'

def showNewBanner( mainTitle, course, quizList, numQuizzes ):
  # first the top of the table
  print """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
<title>
MATH1001
    Differential Calculus
</title>
<meta name="organization" content="School of Mathematics and Statistics, University of Sydney">
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
<link rel="stylesheet" href="/u/UG/styles/base_internal.css" type="text/css">
<link rel="stylesheet" href="/u/UG/styles/menustyle.css" type="text/css">
<link rel="stylesheet" href="/u/UG/JM/MATH1902/r/m1902.css">
<style type="text/css">
<!--
span.nav { font-size: 90%; color: #999999 }
th a.tha { text-decoration: none; color: #ffffcc;}
th a:hover.tha { text-decoration: underline; color: #ffffcc;}
th a:visited.tha { color: #ffffcc;}
div.footer a:hover.global { text-decoration: underline;}
td a:hover.global { text-decoration: underline;}
-->
</style>
<script type="text/javascript">
<!--
var reslevel
var JMlevel ='Y'
    var IMlevel
    var SMlevel
var thisPage = '/u/UG/JM/MATH1001/index.html'
-->
</script>
<script type="text/javascript" src="/u/UG/newstyle/domMenu_alt.js"></script>

<script type="text/javascript" src="/u/UG/newstyle/ResearchSubmenu.js"></script>
<script type="text/javascript" src="/u/UG/newstyle/JMSubmenu.js"></script>
<script type="text/javascript" src="/u/UG/newstyle/IMSubmenu.js"></script>
<script type="text/javascript" src="/u/UG/newstyle/SMSubmenu.js"></script>
</head>
<body bgcolor="#ffffff"
      background=""
      text="#000000" style="margin: 0px">

<a name="top"></a>
<table width="100%" border="0" cellspacing="0" cellpadding="0" class="role">
  <tr>
    <td colspan="2"><img src="/img/navy.gif" width="1" height="1" alt="" hspace="375" vspace="0" class="decor"></td>

  </tr>
  <tr>
    <td width="227"><a href="http://www.usyd.edu.au"><img src="/u/UG/Images/logo_blue_01.gif" width="227" height="52" alt="The University of Sydney" border="0"  class="decor"></a></td>
    <td width="*" style="background-image: url(/u/UG/Images/logo_blue_02.gif); background-position: top left; background-repeat: no-repeat" class="role">
      <div align="right">School&nbsp;of&nbsp;Mathematics&nbsp;and&nbsp;Statistics&nbsp;&nbsp;<br>
                         Junior&nbsp;&nbsp;</div>

    </td>
  </tr>
</table>
<table cellpadding="0" cellspacing="0" border="0" width="100%">
  <tr>
    <td style="background-image: url(/u/UG/Images/breadcrumb_blend.gif)" height="21" nowrap class="breadcrumb">&nbsp;<a href="/" class="breadcrumb">Maths & Stats Home</a> /
          <a href="/u/UG/" class="breadcrumb">Teaching program</a> /
              <a href="/u/UG/JM/" class="breadcrumb">Junior</a> /
              MATH1001&nbsp;&nbsp;</td>

    <td style="background-image: url(/u/UG/Images/breadcrumb_blend.gif)" height="21" align="right">
      <table border="0" cellspacing="0">
        <tr>
          <td valign="middle"><a href="http://www.usyd.edu.au"><img src="/u/UG/Images/small_crest.gif" width="18" height="16" border="0" alt="The University of Sydney"></a></td>
          <td nowrap valign="middle" class="global"><a href="http://www.usyd.edu.au" class="global">USyd Home</a>&nbsp;</td>
          <td valign="middle"><a href="http://db.auth.usyd.edu.au/myuni/myuni.stm"><img src="/u/UG/Images/lion_sml.gif" width="18" height="18" border="0" alt="MyUni"></a></td>
          <td nowrap valign="middle" class="global"><a href="http://db.auth.usyd.edu.au/myuni/myuni.stm" class="global">MyUni</a>&nbsp;</td>
          <td nowrap valign="middle" class="global"><a href="http://www.library.usyd.edu.au/" class="global">Library</a>&nbsp;</td>

<td nowrap valign="middle" class="global"><a href="/u/SiteMap/" class="global">Sitemap</a>&nbsp;</td>
          <td nowrap valign="middle" class="search">
           <form style="margin-top: 0px; margin-bottom: 0px" method="get" action="http://search.usyd.edu.au/search/search.cgi">
             <input type="text" name="query" size="9" class="search" value="Search" onClick="this.value=''">
              <input type=hidden name="collection" value="Usyd">
              <input type=hidden name="num_ranks" value="10">
              <input type=image src="/u/UG/Images/search_go.gif" alt="Start search" name="g_search" value="Go"></form></td>
        </tr>
      </table>

    </td>
  </tr>
  <tr>
    <td colspan="2" bgcolor="#CCCC66" height="1"><img src="/img/navy.gif" width="1" height="1" hspace="100%" alt=""  class="decor"></td>
  </tr>
</table>
<table width="100%" border="0" cellspacing="0" cellpadding="0">
  <tr>
    <td colspan="20"><img src="/img/navy.gif" width="1" height="1" vspace="2" alt="" class="decor"></td>
  </tr>

  <tr>
    <td width="5"><img src="/img/navy.gif" width="1" height="1" alt="" hspace="2"></td>
    <td width="4" valign="top" class="tabnames"><img src="/u/UG/Images/tabLeftCorner.gif" width="4" height="22" alt=""></td>
    <td nowrap class="tabnames">
      <div align="center">&nbsp;<a href="/u/About/" class="tabnames">About the School</a>&nbsp;</div>
    </td>
    <td width="4" valign="top" class="tabnames"><img src="/u/UG/Images/tabRightCorner.gif" width="4" height="22" alt=""></td>
    <td width="4" valign="top" class="tabnames"><img src="/u/UG/Images/tabLeftCorner.gif" width="4" height="22" alt=""></td>

    <td nowrap class="tabnames">
      <div align="center">&nbsp;<a href="/res/Research.html" class="tabnames">Research Activities</a>&nbsp;</div>
    </td>
    <td width="4" valign="top" class="tabnames"><img src="/u/UG/Images/tabRightCorner.gif" width="4" height="22" alt=""></td>
    <td width="4" valign="top" class="tabnames"><img src="/u/UG/Images/tabLeftCorner.gif" width="4" height="22" alt=""></td>
    <td nowrap class="tabnames">
      <div align="center">&nbsp;<a href="/u/PS/" class="tabnames">For prospective students</a>&nbsp;</div>
    </td>

    <td width="4" valign="top" class="tabnames"><img src="/u/UG/Images/tabRightCorner.gif" width="4" height="22" alt=""></td>
    <td width="4" valign="top" class="tabnamesin"><img src="/u/UG/Images/tabLeftCorner.gif" width="4" height="22" alt=""></td>
    <td nowrap class="tabnamesin">
      <div align="center">&nbsp;<a href="/u/UG/" class="tabnames">For current students</a>&nbsp;</div>
    </td>
    <td width="4" valign="top" class="tabnamesin"><img src="/u/UG/Images/tabRightCorner.gif" width="4" height="22" alt=""></td>
    <td width="4" valign="top" class="tabnames"><img src="/u/UG/Images/tabLeftCorner.gif" width="4" height="22" alt=""></td>
    <td nowrap class="tabnames">

      <div align="center">&nbsp;<a href="/local.html" class="tabnames">School Internal Web Site</a>&nbsp;</div>
    </td>
    <td width="4" valign="top" class="tabnames"><img src="/u/UG/Images/tabRightCorner.gif" width="4" height="22" alt=""></td>
    <td width="1000" bgcolor="#ffffff"></td>
  </tr>
  <tr >
    <td colspan="20" bgcolor="#AD2431" class="tabnames"><img src="/img/navy.gif" width="1" height="1" alt="" hspace="250" class="decor"></td>
  </tr>

</table>
<table width="100%" border="0" cellspacing="0" cellpadding="0">
<tr>
<td width="160" valign="top" class="nav">
<table width="160" border="0" cellspacing="0" cellpadding="0" class="nav">
  <tr>
    <td height="15" colspan="3" class="decor"><img src="/img/navy.gif" width="1" height="15" alt=""></td>
  </tr>
<tr valign="top">
<td nowrap>&nbsp;<img src="/u/UG/Images/right_arrow.gif" alt="" width="9"
height="9">&nbsp;</td>
<td colspan="2"><a href="/u/About/" class="nav">About the School</a></td>
</tr>
<tr valign="top">

<td class="nav"><img src="/img/navy.gif" width="1" height="1" alt=""></td>
<td nowrap><img src="/u/UG/Images/bullet.gif" width="6" height="9" alt="" hspace="3" vspace="3"></td>
<td width="100%" class="nav"><a href="/u/About/Students.html" class="nav">More links for students</a></td>
</tr>
  <tr>
    <td height="7" colspan="3"><img src="/img/navy.gif" width="1" height="1" alt="" vspace="3" class="decor"></td>
  </tr>
<tr valign="top" bgcolor="#FFFFFF">
  <td class="menuDivLine" colspan="3"><img src="/img/navy.gif" width="1" height="2" alt="" class="decor"></td>
</tr>
  <tr>

    <td height="7" colspan="3"><img src="/img/navy.gif" width="1" height="1" alt="" vspace="3" class="decor"></td>
  </tr>
<tr valign="top">
<td nowrap>&nbsp;<img src="/u/UG/Images/right_arrow.gif" alt="" width="9"
height="9">&nbsp;</td>
<td colspan="2"><a href="/u/About/Contact.html" class="nav">Contacting us</a></td>
</tr>
  <tr>
    <td height="7" colspan="3"><img src="/img/navy.gif" width="1" height="1" alt="" vspace="3" class="decor"></td>
  </tr>
<tr valign="top" bgcolor="#FFFFFF">
  <td class="menuDivLine" colspan="3"><img src="/img/navy.gif" width="1" height="2" alt="" class="decor"></td>

</tr>
  <tr>
    <td height="7" colspan="3"><img src="/img/navy.gif" width="1" height="1" alt="" vspace="3" class="decor"></td>
  </tr>
<tr valign="top">
<td nowrap>&nbsp;<img src="/u/UG/Images/right_arrow.gif" alt="" width="9"
height="9">&nbsp;</td>
<td colspan="2"><a href="/s/memblist?bypos=1" class="nav">People</a></td>
</tr>
  <tr>
    <td height="7" colspan="3"><img src="/img/navy.gif" width="1" height="1" alt="" vspace="3" class="decor"></td>
  </tr>

<tr valign="top" bgcolor="#FFFFFF">
  <td class="menuDivLine" colspan="3"><img src="/img/navy.gif" width="1" height="2" alt="" class="decor"></td>
</tr>
  <tr>
    <td height="7" colspan="3"><img src="/img/navy.gif" width="1" height="1" alt="" vspace="3" class="decor"></td>
  </tr>
<tr valign="top">
<td nowrap>&nbsp;<img src="/u/UG/Images/right_arrow.gif" alt="" width="9"
height="9">&nbsp;</td>
<td nowrap colspan="2"><a style="visibility: hidden; line-height: 0px" class="nav" href="/res/Research.html">Research</a><div class="dropdownroot" id="ResearchSubmenu"></div>
              <script type="text/javascript">
                    domMenu_activate('ResearchSubmenu');
                          </script></td>

</tr>
  <tr>
    <td height="7" colspan="3"><img src="/img/navy.gif" width="1" height="1" alt="" vspace="3" class="decor"></td>
  </tr>
<tr valign="top" bgcolor="#FFFFFF">
  <td class="menuDivLine" colspan="3"><img src="/img/navy.gif" width="1" height="2" alt="" class="decor"></td>
</tr>
  <tr>
    <td height="7" colspan="3"
    class="decor"><img src="/img/navy.gif" width="1" height="1" alt="" vspace="3"></td>
  </tr>

  <tr valign="top">
  <td nowrap
  >&nbsp;<img src="/u/UG/Images/right_arrow.gif" alt="" width="9"
  height="9">&nbsp;</td>
  <td
  colspan="2"><a href="/u/UG/" class="nav">Undergraduate
  Teaching</a></td>
  </tr>
<tr>
<td valign="top" colspan="3" class="decor"><img src="/img/navy.gif" width="1" height="1" alt="" vspace="1"></td>
</tr>
<tr valign="top">
<td class="nav"><img src="/img/navy.gif" width="1" height="1" alt=""></td>
<td width="5" class="nav"><img src="/u/UG/Images/bullet.gif" width="6" height="9" alt="" hspace="3" vspace="3"></td>
<td width="100%" class="nav"><a class="nav" href="/u/UG/SpecialConsideration.html">Special
Consideration</a></td>

</tr>
<tr>
<td valign="top" colspan="3" class="decor"><img src="/img/navy.gif" width="1" height="5" alt="" vspace="3"></td>
</tr>
<tr valign="top" bgcolor="#FFFFFF">
  <td class="menuDivLine" colspan="3"><img src="/img/navy.gif" width="1" height="2" alt="" class="decor"></td>
</tr>
  <tr>
    <td height="7" colspan="3"
    class="navselected"><img src="/img/navy.gif" width="1" height="1" alt="" vspace="3"></td>
  </tr>
  <tr valign="top">
  <td nowrap
  class="navselected">&nbsp;<img src="/u/UG/Images/down_arrow.gif" alt="" width="9"
  height="9">&nbsp;</td>

  <td class="navselected"
  colspan="2"><a style="visibility: hidden; line-height: 0px" class="nav" href="/u/UG/JM/">Junior</a><div class="dropdownroot" id="JuniorSubmenu"></div><script type="text/javascript">
  domMenu_activate('JuniorSubmenu');
  </script></td>
  </tr>
<tr>
<td valign="top" colspan="3" class="navselected"><img src="/img/navy.gif" width="1" height="1" alt="" vspace="3"></td>
</tr>
<tr valign="top">
<td class="navselectedsub"><img src="/img/navy.gif" width="1" height="1" alt=""></td>
<td width="5" class="navselectedsub"><img src="/u/UG/Images/bullet.gif" width="6" height="9" alt="" hspace="3" vspace="3"></td>
<td width="100%" class="navselectedsub"><a class="nav" href="/u/UG/JM/#Units of Study">units</a></td>
</tr>
<tr valign="top">
<td class="navselectedsub"><img src="/img/navy.gif" width="1" height="1" alt=""></td>

<td width="5" class="navselectedsub"><img src="/u/UG/Images/bullet.gif" width="6" height="9" alt="" hspace="3" vspace="3"></td>
<td width="100%" class="navselectedsub"><a class="nav" href="/u/UG/JM/#Contact Information">contact</a></td>
</tr>
<tr><td class="navselectedsub" colspan="3" height="6"><img src="/img/navy.gif" width="1" height="1" alt="" vspace="3"></td>
</tr>
<tr valign="top" bgcolor="#FFFFFF">
  <td class="menuDivLine" colspan="3"><img src="/img/navy.gif" width="1" height="2" alt="" class="decor"></td>
</tr>
  <tr>
    <td height="7" colspan="3"
    class="decor"><img src="/img/navy.gif" width="1" height="1" alt="" vspace="3"></td>
  </tr>
<tr valign="top">

  <td nowrap
  >&nbsp;<img src="/u/UG/Images/right_arrow.gif" alt="" width="9"
  height="9">&nbsp;</td>
  <td class="nav"
  colspan="2"><a style="visibility: hidden; line-height: 0px" class="nav" href="/u/UG/IM/">Intermediate</a><div class="dropdownroot" id="InterSubmenu"></div><script type="text/javascript">
  domMenu_activate('InterSubmenu');
  </script></td>
</tr>
<tr>
<td valign="top" colspan="3" class="decor"><img src="/img/navy.gif" width="1" height="1" alt="" vspace="3"></td>
</tr>
<tr valign="top" bgcolor="#FFFFFF">
  <td class="menuDivLine" colspan="3"><img src="/img/navy.gif" width="1" height="2" alt="" class="decor"></td>
</tr>
  <tr>
    <td height="7" colspan="3"
    class="decor"><img src="/img/navy.gif" width="1" height="1" alt="" vspace="3"></td>

  </tr>
<tr valign="top">
<td nowrap
>&nbsp;<img src="/u/UG/Images/right_arrow.gif" alt="" width="9"
height="9">&nbsp;</td>
  <td class="nav"
  colspan="2"><a style="visibility: hidden; line-height: 0px" class="nav" href="/u/UG/SM/">Senior</a><div class="dropdownroot" id="SeniorSubmenu"></div><script type="text/javascript">
  domMenu_activate('SeniorSubmenu');
  </script></td>
</tr>
<tr>
<td valign="top" colspan="3" class="decor"><img src="/img/navy.gif" width="1" height="1" alt="" vspace="3"></td>
</tr>
<tr valign="top" bgcolor="#FFFFFF">
  <td class="menuDivLine" colspan="3"><img src="/img/navy.gif" width="1" height="2" alt="" class="decor"></td>
</tr>
  <tr>

    <td height="7" colspan="3"
    class="decor"><img src="/img/navy.gif" width="1" height="1" alt="" vspace="3"></td>
  </tr>
<tr valign="top">
<td nowrap
>&nbsp;<img src="/u/UG/Images/right_arrow.gif" alt="" width="9"
height="9">&nbsp;</td>
<td
colspan="2"><a href="/u/UG/HM/" class="nav">Honours
</a></td>
</tr>
<tr>
<td valign="top" colspan="3" class="decor"><img src="/img/navy.gif" width="1" height="1" alt="" vspace="3"></td>
</tr>
<tr valign="top" bgcolor="#FFFFFF">
  <td class="menuDivLine" colspan="3"><img src="/img/navy.gif" width="1" height="2" alt="" class="decor"></td>
</tr>
  <tr>

    <td height="7" colspan="3"
    class="decor"><img src="/img/navy.gif" width="1" height="1" alt="" vspace="3"></td>
  </tr>
<tr valign="top">
<td nowrap
>&nbsp;<img src="/u/UG/Images/right_arrow.gif" alt="" width="9"
height="9">&nbsp;</td>
<td
colspan="2"><a href="/u/UG/OR/" class="nav">Orange
</a></td>
</tr>
<tr>
<td valign="top" colspan="3" class="decor"><img src="/img/navy.gif" width="1" height="1" alt="" vspace="3"></td>
</tr>
<tr valign="top" bgcolor="#FFFFFF">
  <td class="menuDivLine" colspan="3"><img src="/img/navy.gif" width="1" height="2" alt="" class="decor"></td>
</tr>
  <tr>

    <td height="7" colspan="3"
    class="decor"><img src="/img/navy.gif" width="1" height="1" alt="" vspace="3"></td>
  </tr>
<tr valign="top">
<td nowrap
>&nbsp;<img src="/u/UG/Images/right_arrow.gif" alt="" width="9"
height="9">&nbsp;</td>
<td
colspan="2"><a href="/u/BC/" class="nav">Bridging Courses
</a></td>
</tr>
<tr>
<td valign="top" colspan="3" class="decor"><img src="/img/navy.gif" width="1" height="1" alt="" vspace="3"></td>
</tr>
<tr valign="top" bgcolor="#FFFFFF">
  <td class="menuDivLine" colspan="3"><img src="/img/navy.gif" width="1" height="2" alt="" class="decor"></td>
</tr>
  <tr>

    <td height="7" colspan="3"
    class="decor"><img src="/img/navy.gif" width="1" height="1" alt="" vspace="3"></td>
  </tr>
<tr valign="top">
<td nowrap
>&nbsp;<img src="/u/UG/Images/right_arrow.gif" alt="" width="9"
height="9">&nbsp;</td>
<td
colspan="2"><a href="/u/UG/common/SS/" class="nav">Summer School
</a></td>
</tr>
<tr>
<td valign="top" colspan="3" class="decor"><img src="/img/navy.gif" width="1" height="1" alt="" vspace="3"></td>
</tr>
<tr valign="top" bgcolor="#FFFFFF">
  <td class="menuDivLine" colspan="3"><img src="/img/navy.gif" width="1" height="2" alt="" class="decor"></td>
</tr>
  <tr>

    <td height="7" colspan="3"
    class="decor"><img src="/img/navy.gif" width="1" height="1" alt="" vspace="3"></td>
  </tr>
<tr valign="top">
<td nowrap
>&nbsp;<img src="/u/UG/Images/right_arrow.gif" alt="" width="9"
height="9">&nbsp;</td>
<td
colspan="2"><a href="/u/PG/" class="nav">Postgraduate
</a></td>
</tr>
<tr>
<td valign="top" colspan="3" class="decor"><img src="/img/navy.gif" width="1" height="1" alt="" vspace="3"></td>
</tr>
<tr valign="top" bgcolor="#FFFFFF">
  <td class="menuDivLine" colspan="3"><img src="/img/navy.gif" width="1" height="2" alt="" class="decor"></td>
</tr>
<tr>

    <td height="7" colspan="3"><img src="/img/navy.gif" width="1" height="1" alt="" vspace="3" class="decor"></td>
  </tr>
<tr valign="top">
<td nowrap>&nbsp;<img src="/u/UG/Images/right_arrow.gif" alt="" width="9"
height="9">&nbsp;</td>
<td colspan="2"><a href="/w/tt/lecture.html" class="nav">Lecture timetable</a></td>
</tr>
  <tr>
    <td height="7" colspan="3"><img src="/img/navy.gif" width="1" height="1" alt="" vspace="3" class="decor"></td>
  </tr>
<tr valign="top" bgcolor="#FFFFFF">
  <td class="menuDivLine" colspan="3"><img src="/img/navy.gif" width="1" height="2" alt="" class="decor"></td>

</tr>
  <tr>
    <td height="7" colspan="3"><img src="/img/navy.gif" width="1" height="1" alt="" vspace="3" class="decor"></td>
  </tr>
<tr valign="top">
<td nowrap>&nbsp;<img src="/u/UG/Images/right_arrow.gif" alt="" width="9"
height="9">&nbsp;</td>
<td colspan="2"><a href="/w/tt/tutorial.html" class="nav">Tutorial timetable</a></td>
</tr>
  <tr>
    <td height="7" colspan="3"><img src="/img/navy.gif" width="1" height="1" alt="" vspace="3" class="decor"></td>
  </tr>

<tr valign="top" bgcolor="#FFFFFF">
  <td class="menuDivLine" colspan="3"><img src="/img/navy.gif" width="1" height="2" alt="" class="decor"></td>
</tr>
  <tr>
    <td height="7" colspan="3"><img src="/img/navy.gif" width="1" height="1" alt="" vspace="3" class="decor"></td>
  </tr>
<tr valign="top">
<td nowrap>&nbsp;<img src="/u/UG/Images/right_arrow.gif" alt="" width="9"
height="9">&nbsp;</td>
<td colspan="2"><a href="/u/SiteMap/" class="nav">Sitemap</a></td>
</tr>
  <tr>

    <td height="7" colspan="3"><img src="/img/navy.gif" width="1" height="1" alt="" vspace="3" class="decor"></td>
  </tr>
<tr valign="top" bgcolor="#FFFFFF">
  <td class="menuDivLine" colspan="3"><img src="/img/navy.gif" width="1" height="2" alt="" class="decor"></td>
</tr>
  <tr>
    <td height="7" colspan="3"><img src="/img/navy.gif" width="1" height="1" alt="" vspace="3" class="decor"></td>
  </tr>
<tr valign="top">
<td nowrap>&nbsp;<img src="/u/UG/Images/right_arrow.gif" alt="" width="9"
height="9">&nbsp;</td>
<td colspan="2"><a href="/Search.html" class="nav">School Search</a></td>

</tr>
  <tr>
    <td height="7" colspan="3"><img src="/img/navy.gif" width="1" height="1" alt="" vspace="3" class="decor"></td>
  </tr>
<tr valign="top" bgcolor="#FFFFFF">
  <td class="menuDivLine" colspan="3"><img src="/img/navy.gif" width="1" height="2" alt="" class="decor"></td>
</tr>
<tr valign="top">
<td height="10" colspan="3"><img src="/img/navy.gif" class="decor" width="1" height="1" alt="" vspace="3"></td></tr>
</table>
</td>
<td class="nav">
<img src="/img/navy.gif" width="2" alt="">

</td>
<td valign="top">
<img src="/img/navy.gif" alt="" height="10">
  <table width="0*" cellspacing="0" cellpadding="6" bgcolor="#ffffff">
  <tr><td valign="top" width="0*" class="content">
            <h1>MATH1001
    Differential Calculus</h1>
<p>
"""
  if course['code']!="":
    print '           '+course['code']+': '+course['name']+'</a></font><br>'
  else:
    print '           '+course['name']+'</a></font><br>'
  print '         <font face="verdana, helvetica, sans-serif;"'
  print '               size="4" color="#cc3300">'
  print '               '+mainTitle+'</font><p></td></tr>'
  # now the horizontal navigation bar
  print '  <tr><td valign="top" bgcolor="#ffffff">'
  print '       <table summary="start of top menu: 1 row x 6 cols"'
  print '              bgcolor="#fff084" width="100%" border="0"'
  print '              cellpadding="0" cellspacing="0">'
  if ( len(quizList)>0 ):
    # top menu has "all math???? quizzes" highlighted and no "question"
    print '       <tr valign="middle"><td nowrap class="TopMenu"'
    print '               style="background-color: #ffcc00;">'
    print '               &nbsp;&nbsp;All '+course['code']+' Quizzes&nbsp;&nbsp;</td>'
    print '         <td>&nbsp;&nbsp;&nbsp;</td>'
    print '         <td nowrap>'
    print '           <a class="TopMenu" href="'+course['url']+'"'
    print '              onMouseOver="window.status=\'%s home page\'; return true">' % course['code']
    print '             '+course['code']+' home page&nbsp;</a></td>'
    print '         <td width="100%">&nbsp;</td>'
  else:
    print '     <tr valign="middle">'
    if course['quizzes']!="":
      # print "all quiz" link when it's non-empty
      print '         <td nowrap>'
      print '           <a class="TopMenu" href="'+course['quizzes']+'"'
      print '              onMouseOver="window.status=\'Index of all %s Quizzes\'; return true">' % course['code']
      print '              &nbsp;&nbsp;All '+course['code']+' Quizzes</a>'
      print '              &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>'
    if course['url']!="":
      # print "course code" link when it's non-empty
      print '         <td nowrap>'
      print '           <a class="TopMenu" href="'+course['url']+'"'
      print '              onMouseOver="window.status=\'%s home page\'; return true">' % course['code']
      print '             '+course['code']+' home page</a></td>'
    if course['quizzes']=="" and course['url']=="":
      # even with no links we still want a blank line
      print '<td>&nbsp;</td>'
    if numQuizzes>0:
      print """         <td width="100%">&nbsp;</td>
        <td><a onMouseOver="return navOver('prevpage','Previous question');" 
	       onMouseOut="return navOut('prevpage');" 
               onClick="NextQuestion(-1);" title="Previous question">
             <img src="/u/MOW/images/n-prevpage.gif" height="21" width="32" 
                  alt="Previous question" hspace="0" align="left" border="0" 
                  NAME="prevpage" ID="prevpage"></a>
        </td>
        <td class="TopMenu">&nbsp;Question&nbsp;</td>
        <td><a onMouseOver="return navOver('nextpage','Next question');" 
	       onMouseOut="return navOut('nextpage');" 
               onClick="NextQuestion(1);" title="Next question">
             <img src="/u/MOW/images/n-nextpage.gif" height="21" width="32" 
                  alt="Next question" hspace="0" align="left" border="0" 
                  NAME="nextpage" ID="nextpage"></a>
        </td>"""
  # now close of the top menu table and print the side menu
  print """       </tr>
       </table><!-- end of top menu -->
       </td></tr>
  <tr><td valign="top" bgcolor="#ffcc00"><!-- side menu -->
         <table summary="start of sidebar" bgcolor="#ffcc00" border="0"
                cellspacing="0" cellpadding="0" width="100%" ID="sidebar">
         <col width="20"><col width="*">
         <tbody>"""

def showBanner( mainTitle, course, quizList, numQuizzes ):
  # first the top of the table
  print """
<table summary="whole page: 6 rows and 5 columns" border="0" 
       cellspacing="0" cellpadding="0" width="100%%">
  <col width="10">
  <col width="140">
  <col width="8">
  <col width="*">
  <col width="12">
  <tbody>
  <tr><td bgcolor="#e48928" rowspan="6">
         <img border="0" height="100%%" width="10" alt="" 
	      src="/img/navy.gif"></td>
      <td bgcolor="#ffcc00">
         <img border="0" height="10" width="120" alt="" 
	      src="/img/navy.gif"></td>
      <td bgcolor="#ffffff" colspan="2">
         <img border="0" height="10" width="100%%" alt="" 
	      src="/img/navy.gif"></td>
      <td bgcolor="#ffffff" rowspan="6">
         <img border="0" height="100%%" width="12" alt="" 
	      src="/img/navy.gif"></td>
  </tr>
  <tr><td valign="top" align="center" bgcolor="#ffcc00" rowspan="2">
        <a href="http://www.maths.usyd.edu.au"
	   onMouseOver="window.status='University of Sydney'; return true">
          <img src="/img/unilogo.gif" height="118" width="120" 
               alt="USyd Crest" border="0"></a></td>
      <td bgcolor="#ffffff" rowspan="2">
         <img border="0" height="100%%" width="6" alt="" 
	      src="/img/navy.gif"></td>
      <td bgcolor="#ffffff">
         <font face="verdana, helvetica, sans-serif;" size="3">
	   <a style="text-decoration:none" href="%s"
              onMouseOver="window.status=\'%s home page\'; return true">
""" % (course['url'],course['name'])
  if course['code']!="":
    print '           '+course['code']+': '+course['name']+'</a></font><br>'
  else:
    print '           '+course['name']+'</a></font><br>'
  print '         <font face="verdana, helvetica, sans-serif;"'
  print '               size="4" color="#cc3300">'
  print '               '+mainTitle+'</font><p></td></tr>'
  # now the horizontal navigation bar
  print '  <tr><td valign="top" bgcolor="#ffffff">'
  print '       <table summary="start of top menu: 1 row x 6 cols"'
  print '              bgcolor="#fff084" width="100%" border="0"'
  print '              cellpadding="0" cellspacing="0">'
  if ( len(quizList)>0 ):
    # top menu has "all math???? quizzes" highlighted and no "question"
    print '       <tr valign="middle"><td nowrap class="TopMenu"'
    print '               style="background-color: #ffcc00;">'
    print '               &nbsp;&nbsp;All '+course['code']+' Quizzes&nbsp;&nbsp;</td>'
    print '         <td>&nbsp;&nbsp;&nbsp;</td>'
    print '         <td nowrap>'
    print '           <a class="TopMenu" href="'+course['url']+'"'
    print '              onMouseOver="window.status=\'%s home page\'; return true">' % course['code']
    print '             '+course['code']+' home page&nbsp;</a></td>'
    print '         <td width="100%">&nbsp;</td>'
  else:
    print '     <tr valign="middle">'
    if course['quizzes']!="":
      # print "all quiz" link when it's non-empty
      print '         <td nowrap>'
      print '           <a class="TopMenu" href="'+course['quizzes']+'"'
      print '              onMouseOver="window.status=\'Index of all %s Quizzes\'; return true">' % course['code']
      print '              &nbsp;&nbsp;All '+course['code']+' Quizzes</a>'
      print '              &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>'
    if course['url']!="":
      # print "course code" link when it's non-empty
      print '         <td nowrap>'
      print '           <a class="TopMenu" href="'+course['url']+'"'
      print '              onMouseOver="window.status=\'%s home page\'; return true">' % course['code']
      print '             '+course['code']+' home page</a></td>'
    if course['quizzes']=="" and course['url']=="":
      # even with no links we still want a blank line
      print '<td>&nbsp;</td>'
    if numQuizzes>0:
      print """         <td width="100%">&nbsp;</td>
        <td><a onMouseOver="return navOver('prevpage','Previous question');" 
	       onMouseOut="return navOut('prevpage');" 
               onClick="NextQuestion(-1);" title="Previous question">
             <img src="/u/MOW/images/n-prevpage.gif" height="21" width="32" 
                  alt="Previous question" hspace="0" align="left" border="0" 
                  NAME="prevpage" ID="prevpage"></a>
        </td>
        <td class="TopMenu">&nbsp;Question&nbsp;</td>
        <td><a onMouseOver="return navOver('nextpage','Next question');" 
	       onMouseOut="return navOut('nextpage');" 
               onClick="NextQuestion(1);" title="Next question">
             <img src="/u/MOW/images/n-nextpage.gif" height="21" width="32" 
                  alt="Next question" hspace="0" align="left" border="0" 
                  NAME="nextpage" ID="nextpage"></a>
        </td>"""
  # now close of the top menu table and print the side menu
  print """       </tr>
       </table><!-- end of top menu -->
       </td></tr>
  <tr><td valign="top" bgcolor="#ffcc00"><!-- side menu -->
         <table summary="start of sidebar" bgcolor="#ffcc00" border="0"
                cellspacing="0" cellpadding="0" width="100%" ID="sidebar">
         <col width="20"><col width="*">
         <tbody>"""

# =====================================================
if __name__ == '__main__':
  main()

