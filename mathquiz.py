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
from optparse import OptionParser

# -----------------------------------------------------
alphabet = " abcdefghijklmnopqrstuvwxyz"

TIMED = 0
if TIMED: import time

def strval(ustr): return ustr.encode('ascii','xmlcharrefreplace')

# -----------------------------------------------------
def main():
  global printQuizPage, MathQuizURL, Images

  # ------------------------------
  # available formats
  # ------------------------------
  formats={
    'html'    : html,
    'xml'     : xml,
    'tex'     : tex,
    'text'    : text,
    }
  # ------------------------------
  # parse the command line options
  # ------------------------------
  usage="Usage: %s [--local <local xml file>] [--format format] <filename>" % sys.argv[0]
  parser = OptionParser(usage='Usage: mathquiz [-local <local page file>] <xmlfile> <target>',
                        version=VERSION)
  parser.add_option('-l','--local',action='store',type='string',dest='localXML',default="mathquizLocal",
      help='local python for generating web page '
  )
  parser.add_option('-f','--format',action='store',type='choice',dest='format',default="html",
      choices=formats.keys(), help='local python for generating web page '
  )
  (options, args) = parser.parse_args()
  # if no filename then exit
  if len(args)!=1: 
    print usage
    sys.exit(1)
  format_quiz=formats[options.format]
  quiz_file=args[0]

  # -----------------------------------------------------
  # Load local configuration files and set system variables
  # -----------------------------------------------------
  localPageStyle=__import__(options.localXML)
  printQuizPage = localPageStyle.printQuizPage
  MathQuizURL = localPageStyle.MathQuizURL
  Images = MathQuizURL + 'Images/'

  try:
    quiz_file = open(quiz_file)
  except IOError,e:
    print >> sys.stderr, e
    sys.exit(1)

  if TIMED: start = time.clock()
  quiz = mathquizXml.DocumentTree(quiz_file)
  if TIMED: print >> sys.stderr, 'Parse time:',time.clock()-start
  quiz_file.close()

  if TIMED: start = time.clock()
  format_quiz(quiz)
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

# Generic CSS templates for the questions and responses
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

class html(dict):
  """ Converts the document tree to HTML """

  def __init__(self, doc):
    self.course=doc.course[0]
    self.header=''      # everything printed in the page header: meta data, includes, javascript, CSS, ...
    self.css=''         # css specifications
    self.javascript=''  # javascript code
    self.pagebody=''    # the main page
    self.side_menu=''   # the left hand quiz menu

    self.add_meta_data(doc)
    self.add_question_javascript(doc)
    self.add_question_css(doc)
    self.add_side_menu(doc)
    self.add_page_body(doc)
    printQuizPage(self,doc)

  def add_meta_data(self,doc):
    """ add the meta data for the web page to self.header """
    for attr in doc.metaList:
      self.header+= '<meta'
      for k in attr.keys():
        self.header+= ' %s="%s"' % (k, attr[k])
      self.header+= '>\n'
    self.header+="""  <meta name="organization" content="School of Mathematics and Statistics, University of Sydney">
  <meta name="Copyright" content="University of Sydney 2004">
  <meta name="GENERATOR" content="%s">
  <meta name="AUTHORS" content="Andrew Mathas and Don Taylor">
  <link href="%smathquiz.css" type="text/css" rel="stylesheet">
  <!--
  By reading through this file you should be able to extract the
  answers to the quiz; however, you will get more out of the quiz if
  you do the questions yourself. Of course, you are free to read the
  source if you wish.
  -->
""" % (VERSION,MathQuizURL)
    # links
    for attr in doc.linkList:
      self.header+= '<link'
      for k in attr.keys():
        self.header+= ' %s="%s"' % (k, attr[k])
      self.header+= '>\n'

  def add_question_css(self,doc):
    """ add the CSS for the questions to self """
    self.header+='<style type="text/css">\n<!--\n'
    if len(doc.quizList)>0:       # index listing
      self.header+= '    #question-0\n'
      self.header+=Qgeometry
      self.header+= '    visibility: visible;\n    }\n'
    dnum=0
    for d in doc.discussionList:  # discussion
      dnum+=1
      self.header+= '    #question-%d\n' % dnum
      self.header+=Qgeometry
      if dnum==1: self.header+= '      visibility: visible;\n    }\n'
      else: self.header+= '      visibility: hidden;\n    }\n'
    qnum = 0
    for q in doc.questionList:     # questions
      qnum+= 1
      self.header+= '\n    #question%d %s\n' % (qnum, Qgeometry)
      if len(doc.discussionList)==0 and qnum==1: self.header+= '      visibility: visible;\n'
      else: self.header+= '      visibility: hidden;\n'
  #    self.header+= '      color: %s;' % QuizColour[qnum % len(QuizColour)]
      self.header+= '    }\n'
      self.header+= '\n    #answer%d\n' % qnum
      self.header+= """    {
        position: relative;
        visibility: visible;
      }
"""
      if isinstance(q.answer,mathquizXml.Choice):
        if q.answer.type== "multiple":
          self.header+='\n    #q%dresponse0\n' % qnum
          self.header+=Rgeometry
        rnum = 0
        for s in q.answer.itemList:
          rnum+= 1
          self.header+= '\n    #q%dresponse%d\n' % (qnum,rnum)
          self.header+= Rgeometry
      else:
        self.header+= '\n    #q%dtrue\n' % qnum
        self.header+= Rgeometry
        self.header+= '\n    #q%dfalse\n' % qnum
        self.header+= Rgeometry
    self.header+='  -->\n</style>\n'
  # print the javascript variables holding the quiz solutions and responses
  
  def add_side_menu(self,doc):
    """ construct the left hand quiz menu """
    if len(doc.discussionList)>0: # links for discussion items
      dnum=0
      for d in doc.discussionList:
        dnum+=1
        self.side_menu+= """  <ul><li class="discussion">
     <a href="javascript:void(0);"
        onMouseOver="window.status=\'%s\'; return true;"
        onMouseOut="window.status=\'\'; return true;"
        onClick="return gotoQuestion(-%d);">
          %s
     </a>
  </li>
  </ul>
""" % (d.heading, dnum, d.heading)
    self.side_menu+= '  <table class="controls">\n'
    if len(doc.questionList)>0:
      self.side_menu+= """  <tr valign="top">
        <td colspan="3" class="header">Questions:</td>
  </tr>
  <tr valign="top">
    <td ><a HREF="javascript:void(0);" onMouseOver="window.status=\'Question 1\';return true;" onClick="return gotoQuestion(1);">
  """
      if len(doc.discussionList)==0: firstimage='%sborder1.gif' % Images
      else: firstimage='%sclear1.gif' % Images
      self.side_menu+= '  <img alt="" src="%s" name="progress1" align="TOP"\n' % firstimage
      self.side_menu+= '       height="31"width="31" border="0" hspace="2" vspace="2"></a>\n'
      for i in range(2,self.qTotal+1):
        if i % 2 == 1: self.side_menu+= '<br>\n'
        self.side_menu+= '<a HREF="javascript:void(0);" onClick="return gotoQuestion(%d);"\n' % i
        self.side_menu+= '   OnMouseOver="window.status=\'Question %d\';return true;">\n' % i
        self.side_menu+= '<img alt="" src="%sclear%d.gif" name="progress%d" align="TOP" height="31" width="31" border="0" hspace="2" vspace="2"></a>\n' % (Images,i,i)
      self.side_menu+= '                 </td></tr>\n'
      imgTag = '    <tr><td %s><img alt="" src="'+Images+'%s.gif" %s>\n'
      self.side_menu+= imgTag % ('style="line-height:95%; padding-top:10px;"','star','style="vertical-align:-40%;"')
      self.side_menu+= 'right first<br>&nbsp;&nbsp;&nbsp;&nbsp;attempt</td></tr>\n'
      self.side_menu+= imgTag % ('','tick','')
      self.side_menu+= 'right</td></tr>\n'
      self.side_menu+= imgTag % ('style="padding-top:7px;"','cross','')
      self.side_menu+= 'wrong</td></tr>\n'
    # end of progress buttons, now for the credits
    self.side_menu+= """  </tbody></table>
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
    <!-- end of side self.side_menu -->""" % ( VERSION, VERSION )

  def add_question_javascript(self,doc):
    """ add the javascript for the questions to self """
    self.qTotal = len(doc.questionList)
    if len(doc.discussionList)==0: currentQ='1'
    else: currentQ='-1     // start showing discussion'
    self.javascript+="""  <script src="%smathquiz.js" type="text/javascript"></script>
  <script src="quiztitles.js" type="text/javascript"></script>
  <script language="javascript" type="text/javascript">
  <!--
    var currentQ=%s;
    MathQuizInit(%d);
""" % (MathQuizURL,currentQ,self.qTotal)
    i=0
    for q in doc.questionList:
      self.javascript+= '    QList[%d] = new Array()\n' % i
      a = q.answer
      if isinstance(a,mathquizXml.Answer):
        self.javascript+='    QList[%d].value = "%s"\n' % (i,a.value)
        self.javascript+= '    QList[%d].type = "input"\n' % i
      else:
        self.javascript+= '    QList[%d].type = "%s"\n' % (i,a.type)
        j=0
        for s in a.itemList:
          self.javascript+= '    QList[%d][%d] = %s\n' % (i,j,s.expect)
          j+=1
      i+= 1
    self.javascript+= '  -->\n</script>\n'

  def add_page_body(self,doc):
    """ Write the page body! """
    self.pagebody+='  <h1 class="quiz_title" >%s</h1>\n' % doc.title
    if len(doc.questionList)>0:
      self.pagebody+= """  <div  class="ArrowQuestion">
    <span class="ArrowQuestion">
    <a onmouseover="return navOver('prevpage','Last unanswered question');"
       onmouseout="return navOut('prevpage');" onclick="NextQuestion(-1);"
       title="Last unanswered question"><img src=\""""+Images+"""nn-prevpage.gif" alt="Last unanswered question"
          name="prevpage" id="prevpage" style="vertical-align:-20%; border:0; height:15px;"
          hspace="0" width="32"></a> &nbsp;Question&nbsp;
     <a onmouseover="return navOver('nextpage','Next unanswered question');"
        onmouseout="return navOut('nextpage');" onclick="NextQuestion(1);"
        title="Next unanswered question"><img src=\""""+Images+"""nn-nextpage.gif" alt="Next unanswered question"
          name="nextpage" id="nextpage" style="vertical-align:-20%; border:0; height:15px;"
          hspace="0" width="32"></a>
     </span>
  </div>"""
    # now comes the main page text
    if len(doc.quizList)>0:
      self.pagebody+= '  <div ID="question-0">\n'
      self.pagebody+= '  <h2>' +course['name'] + ' Quizzes</h2>\n'
      self.pagebody+= '  <ul>\n'
      qnum=0
      # quizmenu = the index file for the quizzes in this directory
      quizmenu=open('quiztitles.js','w')
      quizmenu.write("var QuizTitles = [\n")
      for q in doc.quizList:
        qnum+=1
        self.pagebody+= """    <li class="QuizList"><a href="%s" onMouseOver="window.status='%s'; return true" onMouseOut="window.status=''; return true">
    %s
  </a></li>
  """ % (q['url'], q['title'], q['title'])
        quizmenu.write("  ['%s','%sQuizzes/%s']" %(q['title'],course['url'],q['url']))
        if qnum<len(doc.quizList): quizmenu.write(",\n");
        else: quizmenu.write("\n");
      quizmenu.write("];\n");
      quizmenu.close();
      self.pagebody+= '  </ul>\n</div>\n'
    # discussion(s) masquerade as negative questions
    if len(doc.discussionList)>0:
      dnum = 0
      for d in doc.discussionList:
        dnum+=1
        self.pagebody+= '  <div ID="question-%d">\n' % dnum
        self.pagebody+= '  <h2>' + d.heading + '</h2>\n<p>\n'
        self.pagebody+= '    %s\n</p>\n\n' % strval(d.discussion)
        if len(doc.questionList)>0 and dnum==len(doc.discussionList):
          self.pagebody+= '  <input TYPE="button" NAME="next" VALUE="Start quiz"\n\n'
          self.pagebody+= '       onClick="return gotoQuestion(1);">\n'
          self.pagebody+= '  </div>\n'
    if len(doc.questionList)>0:
      qnum = 0
      for q in doc.questionList:
        qnum+= 1
        self.pagebody+= '\n<div ID="question%d">\n' % qnum
        self.pagebody+= self.printQuestion(q,qnum)
        self.pagebody+= self.printResponse(q,qnum)
        self.pagebody+= '</div>\n'

  def printQuestion(self,Q,n):
    question="""    <h2>Question %d</h2>
    <div class="QText">
      <p>%s
    </div>
    <form name="Q%dForm" action="" onSubmit="return false;">
"""% (n,strval(Q.question),n)
    snum = 0
    if isinstance(Q.answer,mathquizXml.Answer):
      question+= '    <p><input TYPE="text"  onChange="checkAnswer();" SIZE="5">\n'
      if Q.answer.tag: question+= '    <span class="QText"> ' + Q.answer.tag +'</span>\n'
    else:
      question+= '    <table summary="List of question choices" class="question_choices">\n'
      question+= '    <col width="2"><col width="2"><col width="*">\n'
      # print extra column specifications as necessary
      for c in range(1,Q.answer.cols):
        question+= '    <col width="10"><col width="2"><col width="2"><col width="*">\n'
      for s in Q.answer.itemList:
        snum+= 1
        question+=self.printItem(s, n, snum)
      if s.parent.type=='single':  # no default answer for question
        question+= """    <tr><td colspan="2">
      <input type="hidden" checked name="Q%dhidden">
    </td></tr>
""" % n
      question+="    </table>\n"
    question+="""    <p>
    <input TYPE="button" VALUE="Check Answer" NAME="answer" onClick="checkAnswer();">
    <span style="width:40px;">&nbsp;</span>
    <input TYPE="button" VALUE="Next Question" NAME="next" onClick="nextQuestion(1);">
    </form>
"""
    return question

  def printItem(self,S,q,n):
    if S.parent.cols==1 or (n % S.parent.cols)==1:
      item = '    <tr valign="top">\n'
    else:
      item = '      <td>&nbsp;</td>\n'
    item+= '        <td class="brown">%s)</td>\n' % alphabet[n]
    if S.parent.type == 'single':
      item+= '      <td><input TYPE="radio" NAME="Q%doptions"></td>\n' % q
      item+= '      <td><div class="QChoices">%s</div></td>\n' % strval(S.answer)
    elif S.parent.type == 'multiple':
      item+= '      <td><input TYPE="checkbox" NAME="Q%doptions%d"></td>\n' % (q,n)
      item+= '      <td><div class="QChoices">%s</div></td>\n' % strval(S.answer)
    else:
      item+= '<!-- internal error: %s -->\n' % S.parent.type
      print >> sys.stderr, 'Unknown question type encountered:',S.parent.type
    if (n % S.parent.cols)==0 or n==len(S.parent.itemList): item+= '    </tr>\n'
    return item
  
  def printResponse(self,Q,n):
    snum = 0
    response = '\n<div ID="answer%d">\n' % n
    if isinstance(Q.answer,mathquizXml.Answer):
      s = Q.answer
      response+= '\n<div ID="q%dtrue">\n' % n
      response+= '<B>Your answer is correct</B><br>\n'
      if s.whenTrue:
        response+= '<div class="RText">%s</div>\n' % strval(s.whenTrue)
      response+= '</div>\n'
      response+= '\n<div ID="q%dfalse">\n' % n
      response+= '<B>Not correct. You may try again.</B>\n'
      if s.whenFalse:
        response+= '<div class="RText">%s</div>\n' % strval(s.whenFalse)
      response+= '</div>\n'
    elif Q.answer.type == "single":
      for s in Q.answer.itemList:
        snum+= 1
        response+= '\n<div ID="q%dresponse%d">\n' % (n,snum)
        response+= '<B>\n'
        if s.expect == "true":
          response+= 'Your answer is correct.<br>\n'
        else:
          response+= 'Not correct. Choice <span class="brown">(%s)</span>\n' % alphabet[snum]
          response+= 'is <span class="red">%s</span>.\n' % s.expect
        response+= '</B>\n'
        if s.response:
          response+= '<div class="RText">%s</div>\n' % strval(s.response)
        response+= '</div>\n'
    else: # Q.answer.type == "multiple":
      for s in Q.answer.itemList:
        snum+= 1
        response+= '\n<div ID="q%dresponse%d">\n' % (n,snum)
        response+= '<B>There is at least one mistake.</B><br>\n'
        response+= 'For example, choice <span class="brown">(%s)</span>\n' % alphabet[snum]
        response+= 'should be <span class="red">%s</span>.\n' % s.expect
        if s.response:
          response+= '<div class="RText">%s</div>\n' % strval(s.response)
        response+= '</div>\n'
      response+= '\n<div ID="q%dresponse0">\n' % n
      response+= '<B>Your answers are correct</B>\n'
      response+= '<ol type="a">\n'
      for s in Q.answer.itemList:
        response+= '<li class="brown"><div class="RText"><b>%s</b>. %s</div>\n' % (strval(s.expect.capitalize()),strval(s.response))
      response+= '</ol>\n'
      response+= '</div>\n'
    response+= '</div>\n'
    return response

# =====================================================
if __name__ == '__main__':
  main()
