#!/usr/bin/env python3

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
__authors__  = "Andrew Mathas (and Don Taylor)"
__author_email__ = 'andrew.mathas@sydney.edu.au'
__date__    = "April 2017"
__version__ =  "5.0"

alphabet = "abcdefghijklmnopqrstuvwxyz"

# -----------------------------------------------------
import argparse
import mathquizXml
import os
import shutil
import sys

# this should no lopnger be necessary as we have switched to python 3
def strval(ustr):
    return ustr
    return ustr.encode('ascii','xmlcharrefreplace')

# -----------------------------------------------------
def main():
  global printQuizPage, MathQuizURL

  # ------------------------------
  # parse the command line options
  # ------------------------------
  parser = argparse.ArgumentParser(description='Generate web quiz from a LaTeX file')
  parser.add_argument('quiz_files', nargs='+',type=str, default=None, help='file1 [file2 ...]')

  parser.add_argument('-u','--url', action='store', type=str, dest='MathQuizURL', default="/MathQuiz/",
      help='relative URL for MathQuiz web files '
  )
  parser.add_argument('-l','--local', action='store', type=str, dest='localXML', default="mathquizLocal",
      help='local python for generating web page '
  )
  parser.add_argument('-q', '--quiet', action='store', type=str, default='',
      help='quiet mode')

  # options suppressed from the help message
  parser.add_argument('--version', action = 'version', version = '%(prog)s {}'.format(__version__), help = argparse.SUPPRESS)
  parser.add_argument('--debugging', action = 'store_true', default = False, help = argparse.SUPPRESS)

  # parse the options
  options = parser.parse_args()
  options.prog=parser.prog

  # if no filename then exit
  if options.quiz_files==[]:
    print(options.usage)
    sys.exit(1)

  # make sure that MathQuizURL ends with / and not //
  if options.MathQuizURL[-1] !='/':
      options.MathQuizURL+='/'
  elif options.MathQuizURL[-2:]=='//':
      options.MathQuizURL=options.MathQuizURL[:len(options.MathQuizURL)-1]

  # import the local page formatter
  options.ConstructorPage = __import__(options.localXML).printQuizPage

  # run through the list of quizzes and make them
  for quiz_file in options.quiz_files:
       # quiz_file is assumed to be a tex file if no extension is given
      if not '.' in quiz_file:
          quiz_file += '.tex'

      if not os.path.isfile(quiz_file):
          print('Cannot read file {}'.format(quiz_file))
          sys.exit(1)

      # the file exists and is readable so make the quiz
      MakeQuiz(quiz_file, options)

#################################################################################

## The quiz web pages are built using the following "template" strings

# Questions and responses:
#   question_css.format(<question number>, <display mode>)
#   answer_css.format(<answer number>)
#   response_css.format(<qnswer number>, <response number>)
question_css = '    #question{}{{z-index: 0; margin: 2ex 0ex 0ex 0ex; padding: 0ex 0ex 0ex 0ex; display: {};}}\n'
answer_css   = '    #answer{}{{position: relative; display: block;}}\n'
response_css = '    #q{}response{}{{padding: 0ex; border: solid black 2px; display: none;}}\n'

# question buttons
button  = r'       <div id="button{b}" class="button{cls}" content="" onClick="gotoQuestion({b})">{b}</div>'
discuss = r'       <li class="discussion" onClick="gotoQuestion(-{b}">{title}</li>'
side_menu = r'''   <h2>MathQuiz</h2>{discussionList}
       <div class="buttons"><div class="question_label">&nbsp;Questions&nbsp;</div><br>{buttons}
       </div>
       <div style="clear:left; height: 1em;"></div>
       <table class="marking_key">
          <tr><td style="color: #FFCC00; font-size:small;">&starf;</td><td>right first<br>attempt</td></tr>
          <tr><td style="color: green; font-size:medium;">&check;</td><td>right</td></tr>
          <tr><td style="color: red; font-size:medium;">&cross;</td><td>wrong</td></tr>
       </table>
       <div class="copyright">
          <a href="http://www.maths.usyd.edu.au/u/MOW/MathQuiz/doc/credits.html">
             <b>MathQuiz {version}</b>
          </a>
          <p><a href="http://www.maths.usyd.edu.au">
                 School of Mathematics<br> and Statistics</a>
          <br><a href="http://www.usyd.edu.au">University of Sydney</a>
          <br>&copy; Copyright 2004-2017
          </p>
       </div>'''

# quiz title and navigation arrows
quiz_title='''  <div id="quiz_header">
        <div class="quiz_title">{title}</div><div style="clear:both;"</div>{arrows}
      </div>
'''
navigation_arrows='''
        <div id="question_number" class="question_label">Question 1</div>
        <div class="arrows">
          <span onClick="nextQuestion(1);"><span class="tooltip">Next unanswered question</span>&#x25ba;</span>
          <div class="question_label">Questions</div>
          <span onClick="nextQuestion(-1);"><span class="tooltip">Previous unanswered question</span>&#x25c4;<span>
        </div>'''

# discussion item
discussion='''     <div id="question-{dnum}"><h2>{discussion.heading}</h2>
        <p>{discussion.discussion}</p>{input_button}
      </div>
'''
input_button='<input type="button" name="next" value="Start quiz" onClick="return gotoQuestion(1);"/>\n'

#quiz index
quiz_list='''     <div class="quiz_list"><h2>{course} Quizzes</h2>
        <ul>
          {quizindex}
        </ul>
      </div>'''
quiz_list_item='''<li><a href={url}>{title}</a></li>'''

# now we come to the question wrappers
question_wrapper='''      <div id="question{qnum}" class="question" {display}>
      {question}
      {response}
      </div>
'''
question_text='''  <div class="question_text">
        {question}
      </div>
      <form id="Q{qnum}Form" action="" onSubmit="return false;">
        {questionOptions}
        <p><input type="button" value="Check Answer" name="answer" onClick="checkAnswer();"/>
        <span style="width:40px;">&nbsp;</span>
        <input type="button" value="Next Question" title="Next unanswered question" name="next" onClick="nextQuestion(1);"/></p>
      </form>
'''
input_answer='<input type="text"  onChange="checkanswer();" size="5"/>{tag}'
choice_answer='<table class="question_choices">{choices}</table>{hidden}'
hidden_choice='\n<input type="hidden" checked="checked" name="Q{qnum}hidden"/>'

# html meta statements
html_meta = r"""<meta name="generator" content="MathQuiz {version} (http://www.maths.usyd.edu.au/u/MOW/MathQuiz/doc/mathquiz-manual.html)">
  <meta name="organization" content="School of Mathematics and Statistics, University of Sydney">
  <meta name="Copyright" content="University of Sydney 2004-2017">
  <meta name="keywords" content="mathquiz, TeX4ht, make4ht, latex, python, quiz, mathematics">
  <meta name="description" content="Interative quiz generated using MathQuiz from latex using TeX4ht ">
  <meta name="authors" content="{authors}">
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <link href="{MathQuizURL}mathquiz.css" type="text/css" rel="stylesheet">
  <link href="{quiz_file}.css" type="text/css" rel="stylesheet">
"""


# Previously used
#   <script type="text/javascript" src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>
# but this case rendering errors

# javascript for setting up the questions
questions_javascript = r"""  <script src="{MathQuizURL}mathquiz.js" type="text/javascript"></script>
  <script src="quiz_titles.js" type="text/javascript"></script>
  <script type="text/javascript" src="https://c328740.ssl.cf1.rackcdn.com/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML" ></script>
  <style type="text/css"> .MathJax_MathML {{text-indent: 0;}}</style>
  <script type="text/javascript">window.onLoad=MathQuizInit({qTotal},'{quiz}');</script>"""

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

class MakeQuiz(dict):
    """
    Convert a mathquiz latex file to an on-line quiz.

    There are several steps:
      1. If given a LaTeX file then run htlatex/make4ht on the latex file to generate an
         xml file for the quiz that has all LaTeS markup converted to html.
      2. Read in the xml file version of the quiz
      3. Spit out the html version
    """
    # attributes that will form part of the generated web page
    header=''      # everything printed in the page header: meta data, includes, javascript, CSS, ...
    css=''         # css specifications
    javascript=''  # javascript code
    page_body=''   # the main page
    side_menu=''   # the left hand quiz menu

    def __init__(self, quiz_file, options):
      self.options = options
      self.quiz_file, extension = quiz_file.split('.')
      self.MathQuizURL = options.MathQuizURL

      if extension == 'tex':
          self.htlatex_quiz_file()

      self.read_xml_file()

      # generate the variuous components ofthe web page
      self.course = self.quiz.course[0]
      self.title = self.quiz.title
      self.add_meta_data()
      self.add_question_javascript()
      self.add_side_menu()
      self.add_page_body()

      # now write the quiz to the html file
      with open(self.quiz_file+'.html', 'w') as file:
            # write the quiz in the specified format
            file.write( options.ConstructorPage(self) )

    def htlatex_file(self):
      r'''
      Process the file using htlatex/make4ht. This converts the quiz to an xml
      with markup specifying the different elements of the quiz page.
      '''
      # run htlatex only if quiz_file has a .tex textension
      try:
          print('make4ht --utf8 --config {config} --output-dir {quiz_file}/ --build-file {build} {quiz_file}.tex'.format(
                  config='/Users/andrew/Code/MathQuiz/latex/mathquiz.cfg',
                  quiz_file=quiz,
                  build='/Users/andrew/Code/MathQuiz/latex/svgpng.mk4'))
          from subprocess import call
          os.system('make4ht --utf8 --config {config} --output-dir {quiz_file}/ --build-file {build} {quiz_file}.tex'.format(
                  config='/Users/andrew/Code/MathQuiz/latex/mathquiz.cfg',
                  quiz_file=quiz,
                  build='/Users/andrew/Code/MathQuiz/latex/svgpng.mk4')
          )
          shutil.copy2(quiz+'.html', quiz+'.xml')
      except Exception as err:
          print('Running htlatex on {} resulted in the error\n  {}'.format(quiz_file, err))
          sys.exit(1)

    def read_xml_file(self):
        r'''
        Read in the mathquiz xml file for the quiz and store the xml document
        tree in ``self.quiz``.
        '''
        try:
            # read in the xml version of the quiz
            self.quiz = mathquizXml.ReadXMLTree(self.quiz_file+'.xml')
        except Exception as err:
            print('There was an error reading the xml generated for {}. Please check your latex source.\n  {}'.format(self.quiz_file, err))
            sys.exit(1)

    def add_meta_data(self):
      """ add the meta data for the web page to self.header """
      # meta tags`
      self.header += html_meta.format(version=__version__, authors=__authors__, MathQuizURL=self.MathQuizURL, quiz_file=self.quiz_file)
      print('{}'.format('\n'.join('{}'.format(m) for m in self.quiz.metaList)))
      for met in self.quiz.metaList:
          self.header+= '  <meta {}/>\n'.format(' '.join('%s="%s"' %(k, met[k]) for k in met))
      # links
      for link in self.quiz.linkList:
          self.header+= '  <link {}/>\n'.format(' '.join('%s="%s"' %(k, link[k]) for k in link))

    def add_side_menu(self):
      """ construct the left hand quiz menu """
      if len(self.quiz.discussionList)>0: # links for discussion items
          discussionList = '\n        <ul>'+'        \n'.join(discuss.format(b=q, title=d.heading) for (q,d) in enumerate(self.quiz.discussionList))+'</ul>'
      else:
          discussionList = ''

      buttons = '\n'+'\n'.join(button.format(b=q, cls=' button-selected' if len(self.quiz.discussionList)==0 and q==1 else '')
                                 for q in range(1, self.qTotal+1))
      # end of progress buttons, now for the credits
      self.side_menu = side_menu.format(discussionList=discussionList, buttons=buttons, version=__version__)

    def add_question_javascript(self):
      """ add the javascript for the questions to self """
      self.qTotal = len(self.quiz.questionList)
      if len(self.quiz.discussionList)==0: currentQ='1'
      else: currentQ='-1     // start showing discussion'

      if self.qTotal >0:
          i=0
          quiz_specs=''
          for (i,q) in enumerate(self.quiz.questionList):
            quiz_specs += 'QuizSpecifications[%d]=new Array();\n' % i
            a = q.answer
            if isinstance(a,mathquizXml.Answer):
              quiz_specs +='QuizSpecifications[%d].value="%s";\n' % (i,a.value)
              quiz_specs += 'QuizSpecifications[%d].type="input";\n' % i
            else:
              quiz_specs += 'QuizSpecifications[%d].type="%s";' % (i,a.type)
              quiz_specs += '\n'.join('QuizSpecifications[%d][%d]=%s;' % (i,j,s.expect) for (j,s) in enumerate(a.itemList))
            quiz_specs+='\n\n'

          try:
              os.makedirs(self.quiz_file, exist_ok=True)
              with open(os.path.join(self.quiz_file,'quiz_list.js'), 'w') as quiz_list:
                  quiz_list.write(quiz_specs)
          except Exception as err:
              print('Error writing quiz specifications:\n {}'.format(err))
              sys.exit(1)

      self.javascript += questions_javascript.format(MathQuizURL = self.MathQuizURL,
                                                   currentQ = currentQ,
                                                   qTotal = self.qTotal,
                                                   quiz = self.quiz_file)

    def add_page_body(self):
      """ Write the page body! """
      self.page_body=quiz_title.format(title=self.quiz.title, arrows='' if len(self.quiz.questionList)==0 else navigation_arrows)
      # now comes the main page text
      # discussion(s) masquerade as negative questions
      if len(self.quiz.discussionList)>0:
        dnum = 0
        for d in self.quiz.discussionList:
          dnum+=1
          self.page_body+=discussion.format(dnum=dnum, discussion=d,
                             input_button=input_button if len(self.quiz.questionList)>0 and dnum==len(self.quiz.discussionList) else '')

      # index for quiz
      if len(self.quiz.quiz_list)>0:
        # add index to the web page
        self.page_body+=quiz_list.format(course=self.quiz.course[0]['name'],
                                         quizindex='\n          '.join(quiz_list_item.format(url=q['url'], title=q['title']) for q in self.quiz.quiz_list)
        )
        # write a javascript file for displaying the menu
        # quizmenu = the index file for the quizzes in this directory
        with open('quiztitles.js','w') as quizmenu:
           quizmenu.write('var QuizTitles = [\n{titles}\n];\n'.format(
              titles = ',\n'.join("  ['{}', '{}Quizzes/{}']".format(q['title'],self.quiz.course[0]['url'],q['url']) for q in self.quiz.quiz_list)
           ))

      # finally we print the quesions
      if len(self.quiz.questionList)>0:
        self.page_body+=''.join(question_wrapper.format(qnum=qnum+1,
                                              display='style="display: block;"' if qnum==0 else '',
                                              question=self.printQuestion(q,qnum+1),
                                              response=self.printResponse(q,qnum+1))
                              for (qnum,q) in enumerate(self.quiz.questionList)
        )

    def printQuestion(self,Q,n):
      if isinstance(Q.answer,mathquizXml.Answer):
        options=input_answer.format(tag='<span class="question_text">' + Q.answer.tag +'</span>' if Q.answer.tag else '')
      else:
        options=choice_answer.format(choices='\n'.join(self.printItem(opt, n, optnum) for (optnum, opt) in enumerate(Q.answer.itemList)),
                                    hidden=hidden_choice.format(qnum=n) if Q.answer.type=="single" else '')
      return question_text.format(qnum=n, question=Q.question, questionOptions=options)

    def printItem(self,opt,qnum,optnum):
      item='<tr>' if opt.parent.cols==1 or (optnum % opt.parent.cols)==0 else '<td>&nbsp;</td>'
      item+= '<td class="brown" >%s)</td>' % alphabet[optnum]
      if opt.parent.type == 'single':
        item+='<td><input type="radio" name="Q{qnum}option"/></td><td><div class="QChoices">{answer}</div></td>'.format(qnum=qnum, answer=opt.answer)
      elif opt.parent.type == 'multiple':
        item+='<td><input type="checkbox" name="Q{qnum}option{optnum}"/></td><td><div class="QChoices">{answer}</div></td>'.format(
                     qnum=qnum, optnum=optnum, answer=opt.answer)
      else:
        item+= '<!-- internal error: %s -->\n' % opt.parent.type
        sys.stderr.write('Unknown question type encountered: {}'.format(opt.parent.type))
      if (optnum % opt.parent.cols)==1 or (optnum+1) % opt.parent.cols==0:
        item+= '   </tr>\n'
      return item

    def printResponse(self,Q,n):
      snum = 0
      response = '  <div class="answer">\n'
      if isinstance(Q.answer,mathquizXml.Answer):
        s = Q.answer
        response+= '  <div id="q%dtrue" class="response">\n' % n
        response+= '    <em>Correct!</em><br/>\n'
        if s.whenTrue:
          response+= '  <div class="response_text">%s</div>\n' % strval(s.whenTrue)
        response+= '  </div>\n  <div id="q%dfalse" class="response"><em>Incorrect. Please try again.</em>\n' % n
        if s.whenFalse:
          response+= '  <div class="response_text">%s</div>\n' % strval(s.whenFalse)
        response+= '  </div>\n'
      elif Q.answer.type == "single":
        for s in Q.answer.itemList:
          snum+= 1
          response+= '  <div id="q%dresponse%d" class="response">\n<em>Correct!</em>' % (n,snum)
          if s.expect != "true":
            response+= '    Choice (%s) is <span class="red">%s</span>.\n' % (alphabet[snum], s.expect)
          if s.response:
            response+= '  <div class="response_text">%s</div>\n' % strval(s.response)
          response+= '  </div>\n'
      else: # Q.answer.type == "multiple":
        for s in Q.answer.itemList:
          snum+= 1
          response+= '\n<div id="q%dresponse%d"  class="response">\n' % (n,snum)
          response+= '<em>There is at least one mistake.</em><br/>\n'
          response+= 'For example, choice <span class="brown">(%s)</span>\n' % alphabet[snum]
          response+= 'should be <span class="red">%s</span>.\n' % s.expect
          if s.response:
            response+= '<div class="response_text">%s</div>\n' % strval(s.response)
          response+= '</div>\n'
        response+= '\n<div id="q%dresponse0" class="response"><em>Correct!</em>\n' % n
        response+= '<ol style="list-style-type:lower-alpha;">\n'
        for s in Q.answer.itemList:
          response+= '<li class="brown"><div class="response_text"><em>%s</em>. %s</div></li>\n' % (strval(s.expect.capitalize()),strval(s.response))
        response+= '</ol>\n'
        response+= '</div>\n'
      response+= '</div>\n'
      return response

# =====================================================
if __name__ == '__main__':
    main()
