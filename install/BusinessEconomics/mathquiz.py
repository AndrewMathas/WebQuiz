#!/usr/bin/python
"""  MathQuiz.py | 2001-03-21     | Don Taylor
                   2004 Version 3 | Andrew Mathas

     Convert an XML quiz description file to an HTML file
     using CSS and JavaScript.

     See quiz.dtd for the DTD and mathquizXml.py for the
     Python object structure reflecting the DTD.

     27 Jan 03
     Swapped the position of the progress strip with
     the main text.  Added support for <meta> and <link>
     tags coming from the tex4ht conversion.
     
     12 Apr 05
     Changed extenstions to php 
     changed showBanner to omit Math Department specific titles  
     and added hard coded html to link to the 3 quizzes for the topics 
"""

VERSION   = 'MathQuiz 4.2'

# -----------------------------------------------------
import sys, os, mathquizXml


# -----------------------------------------------------
# Load local configuration files and set system variables
# -----------------------------------------------------
import mathquizConfig
MathQuizURL = mathquizConfig.URL
Images = MathQuizURL + '/img/'

# -----------------------------------------------------
alphabet = " abcdefghijklmnopqrstuvwxyz"

TIMED = 0
if TIMED:  import time
 
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
NoScript = """If you are reading this message either your
  browser does not support JavaScript or else JavaScript
  is not enabled.  You will need to enable JavaScript and
  then reload this page before you can use this quiz."""

CSStop = """<style type="text/css">
<!--
    span.nav { font-size: 90%; color: #999999 }
    th a.tha { text-decoration: none; color: #ffffcc;}
    th a:hover.tha { text-decoration: underline; color: #ffffcc;}
    th a:visited.tha { color: #ffffcc;}
    div.footer a:hover.global { text-decoration: underline;}
    td a:hover.global { text-decoration: underline;}

    #quiz tr { vertical-align: top; }

    #copy {
    font-family: sans-serif, verdana, helvetica;
    font-size: 60%; 
    }
    #copy A{
    text-decoration: none;
    }
    .QuizList {
       color: #3333AC;
       font-family: sans-serif, verdana, helvetica;
       font-weight: bold;
       text-decoration: none;
       text-align: left;
    }
    TD.QuizList:hover { background-color: #FFFCF0; }

    .brown    { color: #cc3300; }
    .red      { color: red; }
    .QText    { text-align: left; }
    .RText    { color: black; text-align: left; }
    .QChoices { text-align: left; }"""

Qgeometry = """    {
      top: 160px;
      left: 180px;
      width: auto;"""

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
  # fudge, and hope to fix below!
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
  print """  <meta name="organization" content="School of Mathematics and Statistics, University of Sydney">
  <meta name="Copyright" content="University of Sydney 2004"> 
  <meta name="GENERATOR" content="%s"> 
  <meta name="AUTHORS" content="Clare Coleman, Andrew Mathas and Don Taylor">
  <!--
  By reading through this file you should be able to extract the
  answers to the quiz; however, you will get more out of the quiz if
  you do the questions yourself. Of course, you are free to read the
  source if you wish.
  -->""" % VERSION
  if len(doc.discussionList)==0:
    currentQ='1      // start showing first question'
  else:
    currentQ='-1     // start showing discussion'
  print """<script language="javascript" type="text/javascript">
<!--
    thisPage='%s%s.php'
    currentQ=%s
  -->
</script>
<script src="%s/javascript/mathquiz.js" type="text/javascript"></script>
""" % ( doc.course[0]['url'], doc.course[0]['src'], currentQ, MathQuizURL)

  # include any local jacascript code as required
  print mathquizConfig.QuizCss +'\n'+ mathquizConfig.QuizScripts
  if len(doc.quizList)>0:
    print mathquizConfig.IndexCss +'\n'+ mathquizConfig.IndexScripts;

  # Automatically generated css specifying the quiz page
  print CSStop
  dnum=0
  if len(doc.quizList)>0:
    dnum+=1
    print '    #question-%d' % dnum
    print Qgeometry
    print '    margin-left: 10px;\n    visibility: visible;\n    }'
      
  for d in doc.discussionList:
    dnum+=1
    print '    #question-%d' % dnum
    print Qgeometry
    if dnum==1:
      print '    margin-left: 10px;\n    visibility: visible;\n    }'
    else:
      print '    position: absolute;\n    visibility: hidden;\n    }'

  qnum = 0
  for q in doc.questionList:
    qnum += 1
    print '\n    #question%d %s' % (qnum, Qgeometry)
    if len(doc.discussionList)==0 and qnum==1:
      print '      margin-left: 10px;\n    visibility: visible;'
    else:
      print '      position: absolute;\n    visibility: hidden;'
#    print '      color: %s;' % QuizColour[qnum % len(QuizColour)]
    print '    }'
    print '\n    #answer%d' % qnum
    print '    {'
    print '      position: relative;'
    print '      visibility: visible;'
    print '      width: auto;'
    print '    }'
    if isinstance(q.answer,mathquizXml.Choice):
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

  # print the javascript variables holding the quiz solutions and responses
  setPatterns(doc.questionList, doc.discussionList)

  print '</head>'
  qTotal = len(doc.questionList)
  print """<body bgcolor="#ffffff" background="" text="#000000" 
                 style="margin: 0px" onload="init(%d)">""" % qTotal
  print '<noscript>%s</noscript>' % NoScript

  # changed showBanner to omit Math Department specific titles  and hard coded quizzes 1- 3
  showBanner( )

  triangle="""  <tr valign="top">
      <td nowrap>&nbsp;<img src=\""""+Images+"""right_arrow.gif" alt="" width="9"
        height="9">&nbsp;</td>"""

  space=   """    <tr>  <td height="5" colspan="3"><img src=\""""+Images+"""navy.gif" width="1" 
           height="1" alt="" vspace="5" class="decor"></td>
   </tr>"""

  thinline="""  <tr valign="top" bgcolor="#FFFFFF">
         <td class="menuDivLine" colspan="3"><img src=\""""+Images+"""navy.gif" width="1" height="2" 
           alt="" class="decor"></td>
   </tr>"""

  if len(doc.course[0]['name'])>0:
    # button for question numbers and meaning of symbols
    if len(doc.quizList)==0:
      print """  <tr valign="top">
      <td nowrap>&nbsp;<img src=\""""+Images+"""right_arrow.gif" alt="" width="9" height="9">&nbsp;</td>
      <td colspan="2" class="headerblue"><a href="%sindex.php" class="nav">%s</a></td>
  </tr>""" % ( doc.course[0]['url'], doc.course[0]['name'] )
      print space
      if  doc.course[0]['name']!="MathQuiz manual":
        print """<tr valign="top">
    <td class="nav"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt=""></td>
    <td width="9" class="nav"><img src=\""""+Images+"""bullet.gif" width="6" height="9" alt=""hspace="3" vspace="3"></td>
    <td width="100%" class="nav"><a href ="quiz1.php" class="nav">Quiz 1</a></td><tr>
    <tr valign="top">
    <td class="nav"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt=""></td>
    <td width="9" class="nav"><img src=\""""+Images+"""bullet.gif" width="6" height="9" alt="" hspace="3" vspace="3"></td>
    <td width="100%" class="nav"><a href ="quiz2.php" class="nav">Quiz 2</a></td><tr>
    <tr valign="top">
    <td class="nav"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt=""></td>
    <td width="9" class="nav"><img src=\""""+Images+"""bullet.gif" width="6" height="9" alt="" hspace="3" vspace="3"></td>
    <td width="100%" class="nav"><a href ="quiz3.php" class="nav">Quiz 3</a></td><tr>
    </tr>"""
        print space
        print thinline
        print space

    else:
      mathquizConfig.printIndexSideMenu()
      print thinline

  if len(doc.discussionList)>0:
    # links for discussion items
    dnum=0
    for d in doc.discussionList:
      dnum+=1
      print """<tr valign="top">
  <td class="navselectedsub"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt=""></td>
  <td width="5" class="navselectedsub">
     <img src=\""""+Images+"""bullet.gif" width="6" height="9" alt="" hspace="3" vspace="3">
  </td>
  <td width="100%%" class="navselectedsub">
     <a class="nav" href="javascript:void(0)" 
        onMouseOver="window.status=\'%s\'; return true;"
        onClick="return gotoQuestion(-%d);">
          %s
     </a>
  </td>""" % (d.heading, dnum, d.heading)
    print space
    print thinline
    print space

  if len(doc.questionList)>0:
    print """  <tr valign="top">
      <td nowrap>&nbsp;<img src=\""""+Images+"""right_arrow.gif" alt="" width="9" height="9">&nbsp;</td>
      <td colspan="2" class="headerright"><B>Questions</B></td>
  </tr>"""
    print space
    print """  <tr valign="top">
     <td class="navselectedsub"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt=""></td>
     <td class="navselectedsub" colspan="2">
     <a HREF="javascript:void(0)" onMouseOver="window.status=\'Question 1\';return true;"
        onClick="return gotoQuestion(1);">"""
    if len(doc.discussionList)==0:
      firstimage='%sborder1.gif' % Images
    else:
      firstimage='%sclear1.gif' % Images
    print '  <img alt="" src="%s" name="progress1" align="TOP"' % firstimage
    print '       height="31"width="31" border="0" hspace="2" vspace="2"></a>'
    for i in range(2,qTotal+1):
      if i % 2 == 1:
        print '<br>'
      print '<a HREF="javascript:void(0)" onClick="return gotoQuestion(%d)"' % i
      print '   OnMouseOver="window.status=\'Question %d\';return true">' % i
      print '<img alt="" src="%sclear%d.gif" name="progress%d" align="TOP" height="31" width="31" border="0" hspace="2" vspace="2"></a>' % (Images,i,i)

    print '                 </td></tr>'
    print space
    imgTag = '    <tr>  <td class="nav"></td><td class="nav" colspan="2"><img alt="" src="'+Images+'%s.gif" align="%s" height="%d" width="%d" border="0" hspace="2" vspace="2">'
    print imgTag % ('star',"MIDDLE",12,12)
    print 'right first<br>&nbsp;&nbsp;&nbsp;&nbsp;attempt</td></tr>'
    print space
    print imgTag % ('tick',"MIDDLE",18,14)
    print 'right</td></tr>'
    print space
    print imgTag % ('cross',"MIDDLE",9,10)
    print 'wrong</td></tr>'
    print space
    print thinline
  # end of progress buttons

  print space
  print """               <tr height="*" valign="bottom">  <td colspan="3" align="center" ID="copy">
         <br><a href="http://www.maths.usyd.edu.au/u/MOW/MathQuiz/doc/credits.html"
            onMouseOver="window.status='%s'; return true">
            <font face="3DArial, ArialBlack" color="red">%s</font></a><br>
         <a href="http://www.usyd.edu.au"
            onMouseOver="window.status='University of Sydney'; return true">
           <font color="black">University of Sydney</font></a><br>
         <font color="blue"><a href="http://www.maths.usyd.edu.au"
            onMouseOver="window.status='School of Mathematics and Statistics'; return true">
           School of Mathematics<br> and Statistics</a></font><br>
           &copy; Copyright 2004
         </td></tr>
  %s
  %s
  <!-- end of side menu -->""" % ( VERSION, VERSION, space, space )
  print """</table>
</td>
  <td class="nav"><img src=\""""+Images+"""navy.gif" width="2" alt=""></td>
  <td valign="top" width="100%%"><img src=\""""+Images+"""navy.gif" alt="" height="10">
    <!-- start of main page -->
    <table width="100%%" cellspacing="0" cellpadding="6" bgcolor="#ffffff">
    <tr><td valign="top" width="0*" class="content">
<p>"""

  print """
      <table width="100%%" border="0" cellspacing="0" cellpadding="1">
      <tr>
      <td><table width="100%%" border="0" cellspacing="0" cellpadding="0" >
          <tr>
        <td class="header"  valign="middle" style="padding-left: 10px;" nowrap>%s</td>
        <td width="1*">&nbsp;</td>""" % doc.title
  if len(doc.questionList)>0:
    print """       <td align="right"  valign="middle" class="header" nowrap>
            <a onMouseOver="return navOver('prevpage','Last unanswered question');" 
               onMouseOut="return navOut('prevpage');" 
               onClick="NextQuestion(-1);" title="Last unanswered question">
               <img src=\""""+Images+"""n-prevpage.gif" height="21" width="32" 
                    alt="Last unanswered question" hspace="0" border="0" align="middle" 
                    NAME="prevpage" ID="prevpage"></a>
            &nbsp;Question&nbsp;
            <a onMouseOver="return navOver('nextpage','Next unanswered question');" 
               onMouseOut="return navOut('nextpage');" 
               onClick="NextQuestion(1);" title="Next unanswered question">
               <img src=\""""+Images+"""n-nextpage.gif" height="21" width="32" 
                    alt="Next unanswered question" hspace="0" border="0" align="middle"
                    NAME="nextpage" ID="nextpage"></a>
          </td>"""
  print """          </tr>
        </table>
      </td>
      </tr>
      </table>
  <p>"""

  # now print the main page text
  if len(doc.quizList)>0:
    print '<div ID="question-1">'
    printHeading( doc.course[0]['name'] + ' Quizzes' )
    print """<table bgcolor="#ffffff" border="0" cellspacing="0" cellpadding="5" summary="quiz index">
  <tbody>"""
    qnum=0
    for q in doc.quizList:
      qnum+=1
      print """<tr>  <td nowrap class="QuizList"
        onMouseOut="return menuOut('%d');" 
        onMouseOver="return menuOver('%d','%s');">
      <a class="QuizList" onMouseOut="return menuOut('%d');" 
         onMouseOver="return menuOver('%d','%s');" 
         href="%s">""" % (qnum,qnum,q['title'],qnum,qnum,q['title'],q['url'])
      print """<img src="%sarrow.gif" alt=">" border="0" hspace="3"
          NAME="quiztitle%d" ID="quiztitle%d">&nbsp;%s</a>
     </td></tr>""" % (Images, qnum,qnum,q['title'])

    print '</tbody></table>\n</div>'

  # discussion(s) masquerade as negative questions
  if len(doc.discussionList)>0:
    dnum = 0
    for d in doc.discussionList:
      dnum+=1
      print '\n<div ID="question-%d">' % dnum
      printHeading(d.heading)
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

  print """</table></td>
  </table>
</body>
</html>"""

def setPatterns(questionList, discussionList):
  print '<script language="javascript" type="text/javascript">\n<!--'
  i = 0
  for q in questionList:
    print '  QList[%d] = new Array()' % i
    a = q.answer
    if isinstance(a,mathquizXml.Answer):
      print '  QList[%d].value = "%s"' % (i,a.value)
      print '  QList[%d].type = "input"' % i
    else:
      print '  QList[%d].type = "%s"' % (i,a.type)
      j = 0
      for s in a.itemList:
        print '  QList[%d][%d] = %s' % (i,j,s.expect)
        j += 1
    i += 1
  print '// -->\n</script>'
    
def printHeading(title):
  heading="""  <table width="100%%" border="0" cellspacing="0" cellpadding="1" class="subheader">
  <tr>
      <td><table width="100%%" border="0" cellspacing="0" cellpadding="0" >
        <tr><th width="100%%" class="subheader" style="padding-left:5px;" valign="middle">
           %s</th>
              <td width="133" bgcolor="#F9F6E7"><img src=\""""+Images+"""lion_banner3.gif" width="133" height="24" alt="lion">
        </td>
        </tr>
      </table>
    </td>
  </tr>
  </table>
  <p>"""
  print heading % title

def printQuestion(Q,n):
  printHeading( 'Question %d' % n )
  print '<div class="QText">'
  print strval(Q.question) 
  print '</div>'
  print '<form name="Q%dForm" onSubmit="return false;">' % n
  snum = 0
  if isinstance(Q.answer,mathquizXml.Answer):
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
      print '<tr>  <td colspan=2><input type="hidden" checked'
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
    print '  <td>&nbsp;</td>'
  print '      <td class="brown">%s)</td>' % alphabet[n]
  if S.parent.type == 'single':
    print '      <td><input TYPE="radio" NAME="Q%doptions"></td>' % q
    print '      <td><span class="QChoices">%s</span></td>' % strval(S.answer)
  elif S.parent.type == 'multiple':
    print '      <td><input TYPE="checkbox" NAME="Q%doptions%d"></td>' % (q,n)
    print '      <td><span class="QChoices">%s</span></td>' % strval(S.answer)
  else:
    print '<!-- internal error: %s -->' % S.parent.type
    print >> sys.stderr, 'Unknown question type encountered:',S.parent.type
  if (n % S.parent.cols)==0 or n==len(S.parent.itemList): print '</tr>'


def printResponse(Q,n):
  snum = 0
  print '\n<div ID="answer%d">' % n
  if isinstance(Q.answer,mathquizXml.Answer):
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
        print 'Not correct. Choice <span class="brown">(%s)</span>' % alphabet[snum]
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
      print 'For example, choice <span class="brown">(%s)</span>' % alphabet[snum]
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

def showBanner( ):
  #if len(course['code'])>4:
  #  level={'1':'JM', '2':'IM', '3':'SM', 'o':'', 'Q':''}[course['code'][4]]
  #  year ={'JM':'Junior', 'IM':'Intermediate', 'SM':'Senior', '':''}[level]
  #else:
  #level=''
  #year=''
  # print the top of the table (according to local configuration)
  mathquizConfig.printTableTop()

# =====================================================
if __name__ == '__main__':
  main()
