#!/usr/bin/env python3

r"""  MathQuiz.py | 2001-03-21       | Don Taylor
                    2004 Version 3   | Andrew Mathas
                    2010 Version 4.5 | Updated and streamlined in many respects
                    2012 Version 4.6 | Updated to use MathML
                    2017 Version 5.0 | Updated to use MathJax

#*****************************************************************************
# Copyright (C) 2004-2017 Andrew Mathas and Donald Taylor
#                          University of Sydney
#
# Distributed under the terms of the GNU General Public License (GPL)
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
import glob
import shutil
import os
import subprocess
import sys

import mathquiz_xml
from mathquiz_templates import *

# this should no lopnger be necessary as we have switched to python 3
def strval(ustr):
    return ustr
    return ustr.encode('ascii','xmlcharrefreplace')

# -----------------------------------------------------
def main():
    # read settings from the mathquizrc file
    settings = MathQuizSettings()

    # parse the command line options
    parser = argparse.ArgumentParser(description='Generate web quiz from a LaTeX file')
    parser.add_argument('quiz_files', nargs='*',type=str, default=None, help='file1 [file2 ...]')

    parser.add_argument('-u','--url', action='store', type=str, dest='MathQuizURL',
                        default=settings.mathquiz_url['val'],
                        help='relative URL for MathQuiz web files'
    )
    parser.add_argument('-l','--local', action='store', type=str, dest='localXML',
                        default=settings.mathquiz_local['val'], help='local python for generating web page '
    )
    parser.add_argument('--initialise', action='store_true', default=False, help='initialise the web directory for mathquiz')

    # not yet available
    parser.add_argument('-q', '--quiet', action='store_true', default=False, help='suppress most tex4ht messages')

    # options suppressed from the help message
    parser.add_argument('--version', action = 'version', version = '%(prog)s {}'.format(__version__), help = argparse.SUPPRESS)
    parser.add_argument('--debugging', action = 'store_true', default = False, help = argparse.SUPPRESS)

    # parse the options
    options      = parser.parse_args()
    options.prog = parser.prog

    # initialise and exit
    if options.initialise:
        settings.initialise_mathquiz()
        sys.exit()

    # if no filename then exit
    if options.quiz_files==[]:
        print(options.usage)
        sys.exit(1)

    # make sure that MathQuizURL dioes not end with a slash
    while options.MathQuizURL[-1] == '/':
        options.MathQuizURL = options.MathQuizURL[:len(options.MathQuizURL)]

    # import the local page formatter
    options.ConstructorPage = __import__(options.localXML).printQuizPage

    options.initialise_warning = (settings.mathquiz_url['val'] == sms_http)

    # run through the list of quizzes and make them
    for quiz_file in options.quiz_files:
        # quiz_file is assumed to be a tex file if no extension is given
        if not '.' in quiz_file:
          quiz_file += '.tex'

        if not os.path.isfile(quiz_file):
          print('Cannot read file {}'.format(quiz_file))
          sys.exit(1)

        # the file exists and is readable so make the quiz
        MakeMathQuiz(quiz_file, options)

    if options.initialise_warning:
        print(mathquiz_url_warning)

#################################################################################
class MathQuizSettings(object):
    r'''
    Class for initialising mathquiz. This covers both reading and writting the mathquizrc file and
    copying files into the web directories during initialisation.
    '''

    # default of settings for the mathquizrc file
    mathquiz_url    = {'val' : '/MathQuiz',      'help' : 'relative URL to mathquiz code' }
    mathquiz_local  = {'val' : 'mathquiz_local', 'help' : 'python module that determines the quiz web page layout' }
    mathquiz_web    = {'val' : '',               'help' : 'system directory containing mathquiz web files'}

    def __init__(self):
        '''
        If the mathquizrc file exists then read it.
        '''
        self.mq_dir = os.path.dirname(os.path.realpath(__file__))    # directory containing source files
        self.mq_file = lambda file: os.path.join(self.mq_dir, file)  # shorthand for files in mq_dir
        if os.path.isfile(self.mq_file('mathquizrc')):
            self.read_mathquizrc()

    def read_mathquizrc(self):
        r'''
        Read the settings in the mathquizrc file.

        By default, there is no mathquiz initialisation file.
        '''
        try:
            print
            with open(self.mq_file('mathquizrc'),'r') as mathquizrc:
                for line in mathquizrc:
                    if '%' in line:  # remove comments
                        line = line[:line.index('%')]
                    if '=' in line:
                        key, val = line.split('=')
                        key = key.strip().lower()
                        val = val.strip()
                        if len(key)>0 and hasattr(self, key):
                            getattr(self, key)['val'] = val
                        else:
                            print('Unknown setting {} in mathquizrc'.format(key))
                            sys.exit(1)

        except Exception as err:
            sys.stderr.write('There was an error reading the mathquizrc file\n  {}'.format(err))
            raise

    def write_mathquizrc(self):
        r'''
        Write the settings to the mathquizrc file.
        '''
        try:
            with open(self.mq_file('mathquizrc'),'w') as rc_file:
                for setting in ['mathquiz_web', 'mathquiz_url', 'mathquiz_local']:
                    s=getattr(self, setting)
                    rc_file.write('%% {}\n{:<14} = {}\n'.format(s['help'], setting, s['val']))

        except PermissionError:
                print('There was an error writing the mathquizrc file\n  {}'.format(err))
                print(permission_error.format(self.mq_file('mathquirc')))
                sys.exit(1)

        except Exception as err:
            print('There was an error writing the mathquizrc file\n  {}'.format(err))
            sys.exit(1)

    def initialise_mathquiz(self):
        print(initialise_introduction)

        # prompt for directory and copy files - are these reasonable defaults
        # for each OS?
        if len(self.mathquiz_web['val']) > 0:
            web_root = self.mathquiz_web['val']
        elif sys.platform == 'linux':
            web_root = '/usr/local/httpd/MathQuiz'
        elif sys.platform == 'darwin':
            web_root = '/Library/WebServer/Documents/MathQuiz'
        else:
            web_root = '/Local/Library/WebServer'

        import readline
        web_dir = input(web_directory_message.format(web_root))
        if web_dir == '':
            web_dir = web_root
        if web_dir == 'SMS':
            # undocumented: allow links to SMS web pages
            self.mathquiz_web['val'] = 'SMS'
            self.mathquiz_url['val'] =  sms_http
        else:
            files_copied = False
            while not files_copied:
                try:
                    # first delete files of the form mathquiz.* files in web_dir
                    for file in glob.glob(os.path.join(web_dir, 'mathquiz.*')):
                            os.remove(file)
                    if os.path.isdir(self.mq_file('www')):
                        # if the www directory exists then copy it to web_dir
                        shutil.copytree('www', web_dir)
                    else:
                        # assume this is a development version and add links
                        # from the web directory to the parent directory
                        if not os.path.exists(web_dir):
                            os.makedirs(web_dir)
                        elif os.path.isdir(os.path.join(web_dir,'doc')):
                            shutil.rmtree(os.path.join(web_dir,'doc'))
                        elif os.path.isfile(os.path.join(web_dir,'doc')):
                            os.remove(os.path.join(web_dir,'doc'))
                        src = os.path.dirname(self.mq_dir)
                        os.symlink(os.path.join(src, 'javascript/mathquiz.js'), os.path.join(web_dir, 'mathquiz.js'))
                        os.symlink(os.path.join(src, 'css/mathquiz.css'), os.path.join(web_dir, 'mathquiz.css'))
                        if not os.path.exists(os.path.join(web_dir, 'doc')):
                            os.symlink(os.path.join(src, 'doc'), os.path.join(web_dir, 'doc'))

                    self.mathquiz_web['val'] = web_dir
                    files_copied = True

                except PermissionError:
                    print(permission_error.format(web_dir))
                    sys.exit(1)

                except Exception as err:
                    print('There was a problem copying files to {}.\n  Please give a new directory.\n[Error: {}]\n'.format(web_dir, err))
                    web_dir = input('MathQuiz web directory: ')
                    raise

            # now prompt for the relative url
            mq_url = input(mathquiz_url_message.format(self.mathquiz_url['val']))
            if mq_url != '':
                if not wed_dir.ends_with(mq_url):
                    print('Error! {} does not end with {}'.format(web_dir, mq_url))
                    sys.exit(1)
                # removing trailing slashes from mq_url
                while mq_url[-1] == '/':
                    mq_url = mu_url[:len(mq_url)-1]
                self.mathquizrc['mathquiz_url'] = mq_url

        # save the settings and exit
        self.write_mathquizrc()
        print(initialise_ending)

#################################################################################
class MakeMathQuiz(object):
    """
    Convert a mathquiz latex file to an on-line quiz.

    There are several steps:
      1. If given a LaTeX file then run htlatex/make4ht on the latex file to generate an
         xml file for the quiz that has all LaTeS markup converted to html.
      2. Read in the xml file version of the quiz
      3. Spit out the html version

    The HTMl is contructed using the template strings in mathquiz_templates
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

    def htlatex_quiz_file(self):
      r'''
      Process the file using htlatex/make4ht. This converts the quiz to an xml
      with markup specifying the different elements of the quiz page.
      '''
      # run htlatex only if quiz_file has a .tex textension
      try:
          os.system('make4ht --utf8 {quiet} --config {config} --output-dir {quiz_file}/ --build-file {build} {quiz_file}.tex'.format(
                  config    = '/Users/andrew/Code/MathQuiz/latex/mathquiz.cfg',
                  quiz_file = self.quiz_file,
                  quiet     = '--quiet' if self.options.quiet else '',
                  build     = 'makequiz.mk4')
          )
          # htlatex generates an html file, so we rename this as an xml file
          os.rename(self.quiz_file+'.html', self.quiz_file+'.xml')
      except Exception as err:
          print('Running htlatex on {} resulted in the error\n  {}'.format(self.quiz_file, err))
          sys.exit(1)

    def read_xml_file(self):
        r'''
        Read in the mathquiz xml file for the quiz and store the xml document
        tree in ``self.quiz``.
        '''
        try:
            # read in the xml version of the quiz
            self.quiz = mathquiz_xml.ReadXMLTree(self.quiz_file+'.xml')
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
          discussionList = '\n       <ul>\n   {}\n       </ul>'.format(
                '\n   '.join(discuss.format(b=q+1, title=d.heading) for (q,d) in enumerate(self.quiz.discussionList)))
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
            if isinstance(a,mathquiz_xml.Answer):
              quiz_specs +='QuizSpecifications[%d].value="%s";\n' % (i,a.value)
              quiz_specs += 'QuizSpecifications[%d].type="input";\n' % i
            else:
              quiz_specs += 'QuizSpecifications[%d].type="%s";\n' % (i,a.type)
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
                                                   dTotal = len(self.quiz.discussionList),
                                                   quiz = self.quiz_file)

    def add_page_body(self):
      """ Write the page body! """
      self.page_body=quiz_title.format(title=self.quiz.title,
              initialise_warning=initialise_warning if self.options.initialise_warning else '',
              arrows='' if len(self.quiz.questionList)==0
                        else navigation_arrows.format(subheading='Question 1' if len(self.quiz.discussionList)==0 else 'Discussion'))
      # now comes the main page text
      # discussion(s) masquerade as negative questions
      if len(self.quiz.discussionList)>0:
        dnum = 0
        for d in self.quiz.discussionList:
          dnum+=1
          self.page_body+=discussion.format(dnum=dnum, discussion=d,
                             display='style="display: block;"' if dnum==1 else '',
                             input_button=input_button if len(self.quiz.questionList)>0 and dnum==len(self.quiz.discussionList) else '')

      # index for quiz
      if len(self.quiz.quiz_list)>0:
        # add index to the web page
        self.page_body+=quiz_list.format(course=self.quiz.course[0]['name'],
                                         quiz_index='\n          '.join(quiz_list_item.format(url=q['url'], title=q['title']) for q in self.quiz.quiz_list)
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
                                              display='style="display: block;"' if qnum==0 and len(self.quiz.discussionList)==0 else '',
                                              question=self.printQuestion(q,qnum+1),
                                              response=self.printResponse(q,qnum+1))
                              for (qnum,q) in enumerate(self.quiz.questionList)
        )

    def printQuestion(self,Q,n):
      if isinstance(Q.answer,mathquiz_xml.Answer):
        options=input_answer.format(tag='<span class="question_text">' + Q.answer.tag +'</span>' if Q.answer.tag else '')
      else:
        options=choice_answer.format(choices='\n'.join(self.printItem(opt, n, optnum) for (optnum, opt) in enumerate(Q.answer.itemList)),
                                    hidden=hidden_choice.format(qnum=n) if Q.answer.type=="single" else '')
      return question_text.format(qnum=n, question=Q.question, questionOptions=options)

    def printItem(self,opt,qnum,optnum):
      item='<tr>' if opt.parent.cols==1 or (optnum % opt.parent.cols)==0 else '<td>&nbsp;</td>'
      item+= '<td class="brown" >%s)</td>' % alphabet[optnum]
      if opt.parent.type == 'single':
        item+='<td><input type="radio" name="Q{qnum}option"/></td><td><div class="question_choices">{answer}</div></td>'.format(qnum=qnum, answer=opt.answer)
      elif opt.parent.type == 'multiple':
        item+='<td><input type="checkbox" name="Q{qnum}option{optnum}"/></td><td><div class="question_choices">{answer}</div></td>'.format(
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
      if isinstance(Q.answer,mathquiz_xml.Answer):
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
            response+= '    Choice (%s) is <span class="red">%s</span>.\n' % (alphabet[snum-1], s.expect)
          if s.response:
            response+= '  <div class="response_text">%s</div>\n' % strval(s.response)
          response+= '  </div>\n'
      else: # Q.answer.type == "multiple":
        for s in Q.answer.itemList:
          snum+= 1
          response+= '\n<div id="q%dresponse%d"  class="response">\n' % (n,snum)
          response+= '<em>There is at least one mistake.</em><br/>\n'
          response+= 'For example, choice <span class="brown">(%s)</span>\n' % alphabet[snum-1]
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
