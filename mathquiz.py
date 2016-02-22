"""  MathQuiz.py | 2001-03-21     | Don Taylor
                   2004 Version 3 | Andrew Mathas
		   2010 minor hacking by Bob Howlett

     Convert an XML quiz description file to an HTML file
     using CSS and JavaScript.

     See quiz.dtd for the DTD and mathquizXml.py for the
     Python object structure reflecting the DTD.

     27 Jan 03
     Swapped the position of the progress strip with
     the main text.  Added support for <meta> and <link>
     tags coming from the tex4ht conversion.
"""

VERSION   = 'MathQuiz 4.4'

# -----------------------------------------------------
import sys, os, mathquizXml


# -----------------------------------------------------
# Load local configuration files and set system variables
# -----------------------------------------------------
import mathquizConfig
MathQuizURL = mathquizConfig.MathQuizURL
Images = MathQuizURL + 'Images/'

# -----------------------------------------------------
alphabet = " abcdefghijklmnopqrstuvwxyz"

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
  quiz = mathquizXml.DocumentTree(f)
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
#  mathquizXml.nodeVisitor is an adaptor class with default
#  methods that do nothing except pass on the visitor
#  to their children
#
# -----------------------------------------------------
#  xmlWriter() is a visitor defined in mathquizXml.py
# -----------------------------------------------------
def xml(doc):
  doc.accept(mathquizXml.xmlWriter())
# -----------------------------------------------------
#  TeX visitor
# -----------------------------------------------------
def tex(doc):
  doc.accept(TeXWriter())

class TeXWriter(mathquizXml.nodeVisitor):
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
CSStop = """<style type="text/css">
<!--
    span.nav { font-size: 90%; color: #999999 }
    th a.tha { text-decoration: none; color: #ffffcc;}
    th a:hover.tha { text-decoration: underline; color: #ffffcc;}
    th a:visited.tha { color: #ffffcc;}
    div.footer a:hover.global { text-decoration: underline;}
    td a:hover.global { text-decoration: underline;}
    #quiz tr { vertical-align: top; }
    #menu table.controls { font-size:120%;}
    #menu table.controls td.header{ color:#ce1126; padding:10px 0px 7px 0px; font-weight:bold;}
    #menu table.controls td{padding:0px 0px 2px 20px;}
    #menu li.discussion{margin-left:20px;}
   #copy {
    font-family: sans-serif, verdana, helvetica;
    font-size:110%;
    width: 100%;
    padding:20px 0px 20px 0px;
    margin: 0px 0px 600px 0px;
    }
    #copy A{
	text-decoration: none;
    }
    .QuizList { color: #3333AC; font-family: Arial, Helvetica, sans-serif; text-decoration: none; text-align: left; }
    li.QuizList { list-style-image: url('"""+Images+"""arrow.gif'); }
    li.QuizList:hover { list-style-image: url('"""+Images+"""red_arrow.gif'); background-color: #FFFCF0; text-decoration: none; }
    .brown    { color: #cc3300; }
    .red      { color: red; }
    .QText    { text-align: left;  padding-top:20px;}
    .RText    { color: black; text-align: left; }
    .QChoices { text-align: left; padding-left:10px; padding-right:15px;}
    .question_choices td{padding-top:7px;}
    #menu div.controls { padding-top:10px;}
    span.ArrowQuestion img {vertical-align: top;}
    div.ArrowQuestion:hover {color: #000000; background-color:#f9cf66;}
    div.ArrowQuestion {color: #FFFFFF; font-size: 15px; font-weight:bold; background-color: #99CCCC; padding:5px 0px 5px 0px; float:right; margin:-32px -23px 0px 0px;}
"""

Qgeometry = """    {
      top: 60px;
      left: 230px;
      z-index: 0;
      position: absolute;
      margin: -10px 0px 0px 0px;
      padding: 5px 0px 0px 0px;
"""

Rgeometry = """    {
      position: absolute;
      top:  10px;
      left: 0px;
      padding: 5px;
      border: solid black 2px;
      visibility: hidden;
    }
"""

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
  course=doc.course[0]

  meta = ''
  for attr in doc.metaList:
    meta += '<meta'
    for k in attr.keys():
      meta += ' %s="%s"' % (k, attr[k])
    meta += '>\n'
  meta +="""<meta name="organization" content="School of Mathematics and Statistics, University of Sydney">
  <meta name="Copyright" content="University of Sydney 2004">
  <meta name="GENERATOR" content="%s">
  <meta name="AUTHORS" content="Andrew Mathas and Don Taylor">
  <!--
  By reading through this file you should be able to extract the
  answers to the quiz; however, you will get more out of the quiz if
  you do the questions yourself. Of course, you are free to read the
  source if you wish.
  -->""" % VERSION
  headData = ''
  # fudge, and hope to fix below!
  for attr in doc.linkList:
    headData += '<link'
    for k in attr.keys():
      headData += ' %s="%s"' % (k, attr[k])
    headData += '>\n'
  qTotal = len(doc.questionList)
  if len(doc.discussionList)==0:
    currentQ='1'
  else:
    currentQ='-1     // start showing discussion'
  headData += mathquizConfig.headData(doc.src,course,currentQ,qTotal)
  headData += CSStop
  if len(doc.quizList)>0:       # index listing
    headData += '    #question-0\n'
    headData +=  Qgeometry
    headData += '    visibility: visible;\n    }\n'
  dnum=0
  for d in doc.discussionList:  # discussion
    dnum+=1
    headData += '    #question-%d\n' % dnum
    headData +=  Qgeometry
    if dnum==1:
      headData += '      visibility: visible;\n    }\n'
    else:
      headData += '      visibility: hidden;\n    }\n'
  qnum = 0
  for q in doc.questionList:     # questions
    qnum += 1
    headData += '\n    #question%d %s\n' % (qnum, Qgeometry)
    if len(doc.discussionList)==0 and qnum==1:
      headData += '      visibility: visible;\n'
    else:
      headData += '      visibility: hidden;\n'
#    headData += '      color: %s;' % QuizColour[qnum % len(QuizColour)]
    headData += '    }\n'
    headData += '\n    #answer%d\n' % qnum
    headData += """    {
      position: relative;
      visibility: visible;
    }
"""
    if isinstance(q.answer,mathquizXml.Choice):
      if q.answer.type == "multiple":
        headData += '\n    #q%dresponse0\n' % qnum
        headData +=  Rgeometry
      rnum = 0
      for s in q.answer.itemList:
        rnum += 1
        headData += '\n    #q%dresponse%d\n' % (qnum,rnum)
        headData += Rgeometry
    else:
      headData += '\n    #q%dtrue\n' % qnum
      headData += Rgeometry
      headData += '\n    #q%dfalse\n' % qnum
      headData += Rgeometry
  headData += '-->\n</style>'
  # print the javascript variables holding the quiz solutions and responses
  headData += setPatterns(doc.questionList, doc.discussionList)

  menuname = mathquizConfig.menu(doc, course)[0]
  menu = mathquizConfig.menu(doc, course)[1]
  if len(doc.discussionList)>0:
    # links for discussion items
    dnum=0
    for d in doc.discussionList:
      dnum+=1
      menu += """<li class="discussion">
     <a href="javascript:void(0);"
        onMouseOver="window.status=\'%s\'; return true;"
        onMouseOut="window.status=\'\'; return true;"
        onClick="return gotoQuestion(-%d);">
          %s
     </a>
  </li>
""" % (d.heading, dnum, d.heading)
  menu += '</ul>\n'
  menu += '<table class="controls">\n'

  if len(doc.questionList)>0:
    menu += """  <tr valign="top">
      <td colspan="3" class="header">Questions:</td>
</tr>
<tr valign="top">
  <td ><a HREF="javascript:void(0);" onMouseOver="window.status=\'Question 1\';return true;"
        onClick="return gotoQuestion(1);">
"""
    if len(doc.discussionList)==0:
      firstimage='%sborder1.gif' % Images
    else:
      firstimage='%sclear1.gif' % Images
    menu += '  <img alt="" src="%s" name="progress1" align="TOP"\n' % firstimage
    menu += '       height="31"width="31" border="0" hspace="2" vspace="2"></a>\n'
    for i in range(2,qTotal+1):
      if i % 2 == 1:
        menu += '<br>\n'
      menu += '<a HREF="javascript:void(0);" onClick="return gotoQuestion(%d);"\n' % i
      menu += '   OnMouseOver="window.status=\'Question %d\';return true;">\n' % i
      menu += '<img alt="" src="%sclear%d.gif" name="progress%d" align="TOP" height="31" width="31" border="0" hspace="2" vspace="2"></a>\n' % (Images,i,i)

    menu += '                 </td></tr>\n'
    imgTag = '    <tr>  <td %s><img alt="" src="'+Images+'%s.gif" %s>\n'
    menu += imgTag % ('style="line-height:95%; padding-top:10px;"','star','style="vertical-align:-40%;"')
    menu += 'right first<br>&nbsp;&nbsp;&nbsp;&nbsp;attempt</td></tr>\n'
    menu += imgTag % ('','tick','')
    menu += 'right</td></tr>\n'
    menu += imgTag % ('style="padding-top:7px;"','cross','')
    menu += 'wrong</td></tr>\n'
  # end of progress buttons

  menu += """  </tbody></table>
  <div align="center" ID="copy">
    <a href="/u/MOW/MathQuiz/doc/credits.html"
       onMouseOver="window.status='%s'; return true">
       <B>%s</B></a><br>
         <a href="http://www.usyd.edu.au"
            onMouseOver="window.status='University of Sydney'; return true">
            University of Sydney
	 </a><br>
	   <a href="http://www.maths.usyd.edu.au"
              onMouseOver="window.status='School of Mathematics and Statistics'; return true">
         School of Mathematics<br> and Statistics
           </a>
	<br>
	&copy; Copyright 2004-2006
  </div>
  <!-- end of side menu -->""" % ( VERSION, VERSION )

  pagebody = """<h1 class="top">
    %s</h1>
 """ % doc.title

  if len(doc.questionList)>0:
      pagebody += """<div  class="ArrowQuestion">
    <span class="ArrowQuestion">
    <a onmouseover="return navOver('prevpage','Last unanswered question');"
       onmouseout="return navOut('prevpage');" onclick="NextQuestion(-1);"
       title="Last unanswered question">
     <img src=\""""+Images+"""n-prevpage.gif" alt="Last unanswered question"
          name="prevpage" id="prevpage" style="vertical-align:-20%; border:0; height:15px;"
          hspace="0" width="32">
   </a> &nbsp;Question&nbsp;
   <a onmouseover="return navOver('nextpage','Next unanswered question');"
      onmouseout="return navOut('nextpage');" onclick="NextQuestion(1);"
      title="Next unanswered question">
     <img src=\""""+Images+"""n-nextpage.gif" alt="Next unanswered question"
          name="nextpage" id="nextpage" style="vertical-align:-20%; border:0; height:15px;"
          hspace="0" width="32">
   </a>
   </span>
  </div>"""

  # now comes the main page text
  if len(doc.quizList)>0:
    pagebody += '<div ID="question-0">\n'
    pagebody += '<h2>' +course['name'] + ' Quizzes</h2>\n'
    pagebody += '<ul>\n'
    qnum=0
    quizmenu=open('quiztitles.js','w')
    quizmenu.write("var QuizTitles = [\n")
    for q in doc.quizList:
      qnum+=1
      pagebody += """<li class="QuizList"><a href="%s" onMouseOver="window.status='%s'; return true" onMouseOut="window.status=''; return true">
  %s
</a></li>
""" % (q['url'], q['title'], q['title'])
      quizmenu.write("  ['%s','%sQuizzes/%s']" %(q['title'],course['url'],q['url']))
      if qnum<len(doc.quizList):
	quizmenu.write(",\n");
      else:
	quizmenu.write("\n");


    pagebody += '</ul>\n</div>\n'
    quizmenu.write("];\n");
    quizmenu.close();

  # discussion(s) masquerade as negative questions
  if len(doc.discussionList)>0:
    dnum = 0
    for d in doc.discussionList:
      dnum+=1
      pagebody += '\n<div ID="question-%d">\n' % dnum
      pagebody += '<h2>' + d.heading + '</h2>\n<p>\n'
      pagebody += '%s\n</p>\n\n' % strval(d.discussion)
      if len(doc.questionList)>0 and dnum==len(doc.discussionList):
        pagebody += '<input TYPE="button" NAME="next" VALUE="Start quiz"\n\n'
        pagebody += '       onClick="return gotoQuestion(1);">\n'
      pagebody += '</div>\n'

  if len(doc.questionList)>0:
    qnum = 0
    for q in doc.questionList:
      qnum += 1
      pagebody += '\n<div ID="question%d">\n' % qnum
      pagebody += printQuestion(q,qnum)
      pagebody += printResponse(q,qnum)
      pagebody += '</div>\n'

  mathquizConfig.printQuizPage(doc,meta,headData,menuname,menu,course,pagebody)

def setPatterns(questionList, discussionList):
  patterns = '<script language="javascript" type="text/javascript">\n<!--\n'
  i = 0
  for q in questionList:
    patterns+= '  QList[%d] = new Array()\n' % i
    a = q.answer
    if isinstance(a,mathquizXml.Answer):
      patterns += '  QList[%d].value = "%s"\n' % (i,a.value)
      patterns += '  QList[%d].type = "input"\n' % i
    else:
      patterns += '  QList[%d].type = "%s"\n' % (i,a.type)
      j = 0
      for s in a.itemList:
        patterns += '  QList[%d][%d] = %s\n' % (i,j,s.expect)
        j += 1
    i += 1
  patterns += '// -->\n</script>\n'
  return patterns

def printQuestion(Q,n):
  question = '<h2>Question %d</h2>\n' % n
  question += '<div class="QText">\n<p>'
  question += strval(Q.question)
  question += '\n</div>\n'
  question += '<form name="Q%dForm" action="" onSubmit="return false;">\n' % n
  snum = 0
  if isinstance(Q.answer,mathquizXml.Answer):
    question += '<p><input TYPE="text"  onChange="checkAnswer();" SIZE="5">\n'
    if Q.answer.tag:
      question += '<span class="QText"> ' + Q.answer.tag +'</span>\n'
  else:
    question += '<table summary="List of question choices" class="question_choices">\n'
    question += '<col width="2"><col width="2"><col width="*">\n'
    # print extra column specifications as necessary
    for c in range(1,Q.answer.cols):
      question += '<col width="10"><col width="2"><col width="2"><col width="*">\n'
    for s in Q.answer.itemList:
      snum += 1
      question += printItem(s, n, snum)
    if s.parent.type=='single':  # no default answer for question
      question += '<tr>  <td colspan=2><input type="hidden" checked\n'
      question +=  '               name="Q%dhidden"></td></tr>\n' % n
    question += '</table>\n'
  question += '<p>\n'
  question += '<input TYPE="button" VALUE="Check Answer" NAME="answer" onClick="checkAnswer();">\n'
  question += '<span style="width:40px;">&nbsp;</span>\n'
  question += '<input TYPE="button" VALUE="Next Question" NAME="next" onClick="nextQuestion(1);">\n'
  question += '</form>\n'
  return question

#def strval(ustr):
#  if type(ustr) == type(u''):
#    str = ''
#    for c in ustr:
 #     str += chr(ord(c))
#      str += c.encode('ascii','xmlcharrefreplace')
#  else:
#    str = ustr
#  return str

def strval(ustr):
  return ustr.encode('ascii','xmlcharrefreplace')

def printItem(S,q,n):
  if S.parent.cols==1 or (n % S.parent.cols)==1:
    item = '<tr valign="top">\n'
  else:
    item = '  <td>&nbsp;</td>\n'
  item += '      <td class="brown">%s)</td>\n' % alphabet[n]
  if S.parent.type == 'single':
    item += '      <td><input TYPE="radio" NAME="Q%doptions"></td>\n' % q
    item += '      <td><div class="QChoices">%s</div></td>\n' % strval(S.answer)
  elif S.parent.type == 'multiple':
    item += '      <td><input TYPE="checkbox" NAME="Q%doptions%d"></td>\n' % (q,n)
    item += '      <td><div class="QChoices">%s</div></td>\n' % strval(S.answer)
  else:
    item += '<!-- internal error: %s -->\n' % S.parent.type
    print >> sys.stderr, 'Unknown question type encountered:',S.parent.type
  if (n % S.parent.cols)==0 or n==len(S.parent.itemList): item += '</tr>'
  return item

def printResponse(Q,n):
  snum = 0
  response = '\n<div ID="answer%d">\n' % n
  if isinstance(Q.answer,mathquizXml.Answer):
    s = Q.answer
    response += '\n<div ID="q%dtrue">\n' % n
    response += '<B>Your answer is correct</B><br>\n'
    if s.whenTrue:
      response += '<div class="RText">%s</div>\n' % strval(s.whenTrue)
    response += '</div>\n'
    response += '\n<div ID="q%dfalse">\n' % n
    response += '<B>Not correct. You may try again.</B>\n'
    if s.whenFalse:
      response += '<div class="RText">%s</div>\n' % strval(s.whenFalse)
    response += '</div>\n'
  elif Q.answer.type == "single":
    for s in Q.answer.itemList:
      snum += 1
      response += '\n<div ID="q%dresponse%d">\n' % (n,snum)
      response += '<B>\n'
      if s.expect == "true":
        response += 'Your answer is correct.<br>\n'
      else:
        response += 'Not correct. Choice <span class="brown">(%s)</span>\n' % alphabet[snum]
	response += 'is <span class="red">%s</span>.\n' % s.expect
      response += '</B>\n'
      if s.response:
        response += '<div class="RText">%s</div>\n' % strval(s.response)
      response += '</div>\n'
  else: # Q.answer.type == "multiple":
    for s in Q.answer.itemList:
      snum += 1
      response += '\n<div ID="q%dresponse%d">\n' % (n,snum)
      response += '<B>There is at least one mistake.</B><br>\n'
      response += 'For example, choice <span class="brown">(%s)</span>\n' % alphabet[snum]
      response += 'should be <span class="red">%s</span>.\n' % s.expect
      if s.response:
        response += '<div class="RText">%s</div>\n' % strval(s.response)
      response += '</div>\n'
    response += '\n<div ID="q%dresponse0">\n' % n
    response += '<B>Your answers are correct</B>\n'
    response += '<ol type="a">\n'
    for s in Q.answer.itemList:
      response += '<li class="brown"><div class="RText"><b>%s</b>. %s</div>\n' % (strval(s.expect.capitalize()),strval(s.response))
    response += '</ol>\n'
    response += '</div>\n'
  response += '</div>\n'
  return response

# =====================================================
if __name__ == '__main__':
  main()
