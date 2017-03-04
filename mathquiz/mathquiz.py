r"""  MathQuiz.py | 2001-03-21       | Don Taylor
                    2004 Version 3   | Andrew Mathas
                    2010 Version 4.5 | Updated and streamlined in many respects
                    2012 Version 4.6 | Updated to use MathML
                    2017 Version 5.0 | Updated to use MathJax

#*****************************************************************************
#       Copyright (C) 2004-2017 Andrew Mathas and Donald Taylor
#                          University of Sydney
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#
# This file is part of the MathQuiz system.
#
# Copyright (C) 2004-2017 by the School of Mathematics and Statistics
# <Andrew.Mathas@sydney.edu.au>
# <Donald.Taylor@sydney.edu.au>
#*****************************************************************************

"""

# ----------------------------------------------------
VERSION   = 'MathQuiz 5.0'
alphabet = " abcdefghijklmnopqrstuvwxyz"

# -----------------------------------------------------
import sys, os, mathquizXml
from optparse import OptionParser


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
  usage="Usage: %s [--local <local xml file>] [--format format] --url MathQuizURL <directory>" % sys.argv[0]
  parser = OptionParser(usage='Usage: mathquiz [--local <local page file>] --url MathQuizURL <xmlfile> <target>',
                        version=VERSION)
  parser.add_option('-u','--url',action='store',type='string',dest='MathQuizURL',default="/MathQuiz/",
      help='relative URL for MathQuiz web files '
  )
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

  # make sure that MathQuizURL ends with / and not //
  MathQuizURL=options.MathQuizURL
  if MathQuizURL[-1] !='/':
      MathQuizURL+='/'
  elif MathQuizURL[-2:]=='//':
      MathQuizURL=MathQuizURL[:len(MathQuizURL)-1]
  # images
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
      z-index: 0;
      margin: 2ex 0ex 0ex 0ex;
      padding: 0ex 0ex 0ex 0ex;
"""

Rgeometry = """    {
      padding: 0ex;
      border: solid black 2px;
      display: none;
    }
"""


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
  <meta name="Copyright" content="University of Sydney 2004-2017">
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
      self.header+= '/>\n'

  def add_question_css(self,doc):
    """ add the CSS for the questions to self """
    self.header+='<style type="text/css">\n<!--\n'
    dnum=0
    for d in doc.discussionList:  # discussion
      dnum+=1
      self.header+= '    #question-%d\n' % dnum
      self.header+=Qgeometry
      if dnum==1: self.header+= '      display: block;\n    }\n'
      else: self.header+= '      display: none;\n    }\n'
    if len(doc.quizList)>0:       # index listing
      self.header+= '    #quizList\n'
      self.header+=Qgeometry
      self.header+= '    display: block;\n    }\n'
    qnum = 0
    for q in doc.questionList:     # questions
      qnum+= 1
      self.header+= '\n    #question%d %s\n' % (qnum, Qgeometry)
      if len(doc.discussionList)==0 and qnum==1: self.header+= '      display: block;\n'
      else: self.header+= '      display: none;\n'
      self.header+= '    }\n'
      self.header+= '\n    #answer%d\n' % qnum
      self.header+= """    {
        position: relative;
        display: block;
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
      self.side_menu+="\n <!-- start of discussion lists -->\n<ul>"
      for d in doc.discussionList:
        dnum+=1
        self.side_menu+= """  <li class="discussion">
     <a href="javascript:void(0);"
        onMouseOver="window.status=\'%s\'; return true;"
        onMouseOut="window.status=\'\'; return true;"
        onClick="return gotoQuestion(-%d);">
          %s
     </a>
  </li>
""" % (d.heading, dnum, d.heading)
      self.side_menu+="\n </ul><!-- end of discussion lists -->"
    if len(doc.questionList)>0:
      self.side_menu+= """  <table class="controls">
  <tr valign="top">
        <td colspan="3" class="header">Questions:</td>
  </tr>
  <tr valign="top">
    <td ><a href="javascript:void(0);" onMouseOver="window.status=\'Question 1\';return true;" onClick="return gotoQuestion(1);">
  """
      if len(doc.discussionList)==0: firstimage='%sborder1.gif' % Images
      else: firstimage='%sclear1.gif' % Images
      self.side_menu+= '  <img alt="" src="%s" id="progress1" \n' % firstimage
      self.side_menu+= '       style="height:31px;width:31px;padding:2px;"/></a>\n'
      for i in range(2,self.qTotal+1):
        if i % 2 == 1: self.side_menu+= '<br/>\n'
        self.side_menu+= '''<a href="javascript:void(0);" onClick="return gotoQuestion(%d);"\n''' % i
        self.side_menu+= '   onMouseOver="window.status=\'Question %d\';return true;">\n' % i
        self.side_menu+= '<img alt="" src="%sclear%d.gif" id="progress%d" style="height:31px;width:31px;padding:2px;"/></a>\n' % (Images,i,i)
      self.side_menu+= '                 </td></tr>\n'
      imgTag = '    <tr><td %s><img alt="" src="'+Images+'%s.gif" %s/>\n'
      self.side_menu+= imgTag % ('style="line-height:95%; padding-top:10px;"','star','style="vertical-align:-40%;"')
      self.side_menu+= 'right first<br/>&nbsp;&nbsp;&nbsp;&nbsp;attempt</td></tr>\n'
      self.side_menu+= imgTag % ('','tick','')
      self.side_menu+= 'right</td></tr>\n'
      self.side_menu+= imgTag % ('style="padding-top:7px;"','cross','')
      self.side_menu+= 'wrong</td></tr>\n</table>'
    # end of progress buttons, now for the credits
    self.side_menu+= """
    <div style="text-align:center;" id="copy">
      <a href="http://www.maths.usyd.edu.au/u/MOW/MathQuiz/doc/credits.html"
         onMouseOver="window.status='%s'; return true">
         <b>%s</b></a><br/>
           <a href="http://www.usyd.edu.au"
              onMouseOver="window.status='University of Sydney'; return true">
              University of Sydney
  	 </a><br/>
  	   <a href="http://www.maths.usyd.edu.au"
                onMouseOver="window.status='School of Mathematics and Statistics'; return true">
           School of Mathematics<br/> and Statistics
             </a>
  	<br/>
  	&copy; Copyright 2004-2017
    </div>
    <!-- end of side self.side_menu -->""" % ( VERSION, VERSION )

  def add_question_javascript(self,doc):
    """ add the javascript for the questions to self """
    self.qTotal = len(doc.questionList)
    if len(doc.discussionList)==0: currentQ='1'
    else: currentQ='-1     // start showing discussion'
    # added MathML support 3/2/12
    self.javascript+="""  <script src="%smathquiz.js" type="text/javascript"></script>
  <script src="quiztitles.js" type="text/javascript"></script>
  <script type="text/javascript" src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML">
  </script>
  <script type="text/javascript">
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
      self.pagebody+= '''  <div  class="ArrowQuestion">
    <span class="ArrowQuestion">
    <a onMouseOver="return navOver('prevpage','Last unanswered question');"
       onmouseout="return navOut('prevpage');" onClick="NextQuestion(-1);"
       title="Last unanswered question"><img src=\"'''+Images+'''nn-prevpage.gif" alt="Last unanswered question"
          id="prevpage" name="prevpage" style="vertical-align:-20%; border:0; height:15px;width:32px;"/></a> &nbsp;Question&nbsp;
     <a onMouseOver="return navOver('nextpage','Next unanswered question');"
        onmouseout="return navOut('nextpage');" onClick="NextQuestion(1);"
        title="Next unanswered question"><img src=\"'''+Images+'''nn-nextpage.gif" alt="Next unanswered question"
          id="nextpage" name="nextpage" style="vertical-align:-20%; border:0; height:15px;width:32px;"/></a>
     </span>
  </div>'''
    # now comes the main page text
    # discussion(s) masquerade as negative questions
    if len(doc.discussionList)>0:
      dnum = 0
      for d in doc.discussionList:
        dnum+=1
        self.pagebody+= '  <div id="question-%d">\n' % dnum
        self.pagebody+= '  <h2>' + d.heading + '</h2>\n\n'
        self.pagebody+= '    <p>%s</p>\n\n\n' % strval(d.discussion)
        if len(doc.questionList)>0 and dnum==len(doc.discussionList):
          self.pagebody+= '  <input type="button" name="next" value="Start quiz"\n\n'
          self.pagebody+= '''       onClick="return gotoQuestion(1);"/>\n'''
        self.pagebody+= '  </div>\n'
    # index for quiz
    if len(doc.quizList)>0:
      self.pagebody+= '  <div id="quizList">\n'
      self.pagebody+= '  <h2>' +doc.course[0]['name'] + ' Quizzes</h2>\n'
      self.pagebody+= '  <ul>\n'
      qnum=0
      # quizmenu = the index file for the quizzes in this directory
      quizmenu=open('quiztitles.js','w')
      quizmenu.write("var QuizTitles = [\n")
      for q in doc.quizList:
        qnum+=1
        self.pagebody+= """    <li class="QuizList"><a href="%s" onMouseOver="window.status='%s'; return true" onmouseout="window.status=''; return true">
    %s
  </a></li>
  """ % (q['url'], q['title'], q['title'])
        quizmenu.write("  ['%s','%sQuizzes/%s']" %(q['title'],doc.course[0]['url'],q['url']))
        if qnum<len(doc.quizList): quizmenu.write(",\n");
        else: quizmenu.write("\n");
      quizmenu.write("];\n");
      quizmenu.close();
      self.pagebody+= '  </ul>\n</div>\n'
    if len(doc.questionList)>0:
      qnum = 0
      for q in doc.questionList:
        qnum+= 1
        self.pagebody+= '\n<div id="question%d">\n' % qnum
        self.pagebody+= self.printQuestion(q,qnum)
        self.pagebody+= self.printResponse(q,qnum)
        self.pagebody+= '</div>\n'

  def printQuestion(self,Q,n):
    question="""    <h2>Question %d</h2>
    <div class="QText">
      %s
    </div>
    <form id="Q%dForm" action="" onSubmit="return false;">
    <div>
"""% (n,strval(Q.question),n)
    snum = 0
    if isinstance(Q.answer,mathquizXml.Answer):
      question+= '    <p/><input type="text"  onChange="checkanswer();" size="5"/>\n'
      if Q.answer.tag: question+= '    <span class="QText"> ' + Q.answer.tag +'</span>\n'
    else:
      question+= '    <table summary="List of question choices" class="question_choices">\n'
      question+= '    <col width="2"/><col width="2"/><col width="*"/>\n'
      # print extra column specifications as necessary
      for c in range(1,Q.answer.cols):
        question+= '    <col width="10"/><col width="2"/><col width="2"/><col width="*"/>\n'
      for s in Q.answer.itemList:
        snum+= 1
        question+=self.printItem(s, n, snum)
      if s.parent.type=='single':  # no default answer for question
        question+= """    <tr><td colspan="2">
      <input type="hidden" checked="checked" name="Q%dhidden"/>
    </td></tr>
""" % n
      question+="    </table>\n"
    question+="""    <p>
    <input type="button" value="Check Answer" name="answer" onClick="checkAnswer();"/>
    <span style="width:40px;">&nbsp;</span>
    <input type="button" value="Next Question" name="next" onClick="nextQuestion(1);"/></p>
    </div></form>
"""
    return question

  def printItem(self,S,q,n):
    if S.parent.cols==1 or (n % S.parent.cols)==1:
      item = '    <tr valign="top">\n'
    else:
      item = '      <td>&nbsp;</td>\n'
    item+= '        <td class="brown">%s)</td>\n' % alphabet[n]
    if S.parent.type == 'single':
      item+= '      <td><input type="radio" name="Q%doptions"/></td>\n' % q
      item+= '      <td><div class="QChoices">%s</div></td>\n' % strval(S.answer)
    elif S.parent.type == 'multiple':
      item+= '      <td><input type="checkbox" name="Q%doptions%d"/></td>\n' % (q,n)
      item+= '      <td><div class="QChoices">%s</div></td>\n' % strval(S.answer)
    else:
      item+= '<!-- internal error: %s -->\n' % S.parent.type
      print >> sys.stderr, 'Unknown question type encountered:',S.parent.type
    if (n % S.parent.cols)==0 or n==len(S.parent.itemList): item+= '    </tr>\n'
    return item

  def printResponse(self,Q,n):
    snum = 0
    response = '\n<div id="answer%d">\n' % n
    if isinstance(Q.answer,mathquizXml.Answer):
      s = Q.answer
      response+= '\n<div id="q%dtrue">\n' % n
      response+= '<b>Your answer is correct</b><br/>\n'
      if s.whenTrue:
        response+= '<div class="RText">%s</div>\n' % strval(s.whenTrue)
      response+= '</div>\n'
      response+= '\n<div id="q%dfalse">\n' % n
      response+= '<b>Not correct. You may try again.</b>\n'
      if s.whenFalse:
        response+= '<div class="RText">%s</div>\n' % strval(s.whenFalse)
      response+= '</div>\n'
    elif Q.answer.type == "single":
      for s in Q.answer.itemList:
        snum+= 1
        response+= '\n<div id="q%dresponse%d">\n' % (n,snum)
        response+= '<b>\n'
        if s.expect == "true":
          response+= 'Your answer is correct.<br/>\n'
        else:
          response+= 'Not correct. Choice <span class="brown">(%s)</span>\n' % alphabet[snum]
          response+= 'is <span class="red">%s</span>.\n' % s.expect
        response+= '</b>\n'
        if s.response:
          response+= '<div class="RText">%s</div>\n' % strval(s.response)
        response+= '</div>\n'
    else: # Q.answer.type == "multiple":
      for s in Q.answer.itemList:
        snum+= 1
        response+= '\n<div id="q%dresponse%d">\n' % (n,snum)
        response+= '<b>There is at least one mistake.</b><br/>\n'
        response+= 'For example, choice <span class="brown">(%s)</span>\n' % alphabet[snum]
        response+= 'should be <span class="red">%s</span>.\n' % s.expect
        if s.response:
          response+= '<div class="RText">%s</div>\n' % strval(s.response)
        response+= '</div>\n'
      response+= '\n<div id="q%dresponse0">\n' % n
      response+= '<b>Your answers are correct</b>\n'
      response+= '<ol style="list-style-type:lower-alpha;">\n'
      for s in Q.answer.itemList:
        response+= '<li class="brown"><div class="RText"><b>%s</b>. %s</div></li>\n' % (strval(s.expect.capitalize()),strval(s.response))
      response+= '</ol>\n'
      response+= '</div>\n'
    response+= '</div>\n'
    return response

# =====================================================
if __name__ == '__main__':
  main()
