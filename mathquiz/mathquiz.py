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

# -----------------------------------------------------
import argparse
import glob
import shutil
import os
import subprocess
import sys

import mathquiz_xml
from mathquiz_templates import *

# ----------------------------------------------------
# Return the full path for a file in the mathquiz directory
mathquiz_file = lambda file: os.path.join(os.path.dirname(os.path.realpath(__file__)),file)

# ----------------------------------------------------
class MetaData(dict):
    r"""
    A dummy class for reading, accessing and storing key-value pairs from a file

    Usage: MetaData(filename)
    """
    def __init__(self, filename):
        with open(filename,'r') as meta:
            for line in meta:
                if '=' in line:
                    key, val = line.strip().split('=')
                    if len(key.strip())>0:
                        setattr(self, key.strip().lower(), val.strip())

# read in basic meta data such as author, version, ...
metadata = MetaData(mathquiz_file('mathquiz.ini'))

# used to label the parts of questions as a, b, c, ...
alphabet = "abcdefghijklmnopqrstuvwxyz"

# this should no lopnger be necessary as we have switched to python 3
def strval(ustr):
    return ustr
    return ustr.encode('ascii','xmlcharrefreplace')

# -----------------------------------------------------
def main():
    # read settings from the mathquizrc file
    settings = MathQuizSettings()

    # parse the command line options
    parser = argparse.ArgumentParser(description=metadata.description)
    parser.add_argument('quiz_file', nargs='*',type=str, default=None, help='latex quiz files')

    parser.add_argument('-u','--url', action='store', type=str, dest='MathQuizURL',
                        default=settings['mathquiz_url'],
                        help='relative URL for MathQuiz web files'
    )
    parser.add_argument('-l','--local', action='store', type=str, dest='local_page',
                        default=settings['mathquiz_local'], help='local python code for generating the quiz web page '
    )
    parser.add_argument('--initialise', action='store_true', default=False, help='initialise the web directory for mathquiz')
    parser.add_argument('--build', action='store', type=str, dest='mathquiz_mk4', default=settings['mathquiz_mk4'],
                        help='override default build file for make4ht')

    # not yet available
    parser.add_argument('-q', '--quiet', action='count', help='suppress tex4ht messages')

    # options suppressed from the help message
    parser.add_argument('--version', action = 'version', version = '%(prog)s {}'.format(metadata.version), help = argparse.SUPPRESS)
    parser.add_argument('--debugging', action = 'store_true', default = False, help = argparse.SUPPRESS)

    # parse the options
    options      = parser.parse_args()
    options.prog = parser.prog

    # initialise and exit
    if options.initialise:
        settings.initialise_mathquiz()
        sys.exit()

    # if no filename then exit
    if options.quiz_file==[]:
        parser.print_help()
        sys.exit(1)

    # make sure that MathQuizURL dioes not end with a slash
    while options.MathQuizURL[-1] == '/':
        options.MathQuizURL = options.MathQuizURL[:len(options.MathQuizURL)]

    # import the local page formatter
    options.ConstructorPage = __import__(options.local_page).printQuizPage

    options.initialise_warning = (settings['mathquiz_url'] == sms_http)

    # run through the list of quizzes and make them
    for quiz_file in options.quiz_file:
        # quiz_file is assumed to be a tex file if no extension is given
        if not '.' in quiz_file:
            quiz_file += '.tex'

        if not os.path.isfile(quiz_file):
            print('Error: cannot read file {}'.format(quiz_file))
            sys.exit(1)

        # the file exists and is readable so make the quiz
        MakeMathQuiz(quiz_file, options)

    if options.initialise_warning:
        print(mathquiz_url_warning)

#################################################################################
class MathQuizSettings(object):
    r'''
    Class for initialising mathquiz. This covers both reading and writting the mathquizrc file and
    copying files into the web directories during initialisation. The settings
    themselves are stored in attribute settings, which is a dictionary. The
    class reads and writes the settings to the magthquizrc file and the
    vbalues of the settings are available as items:
        >>> mq = MathQuizSettings()
        >>> mq['mathquiz_url']
        ... /MathQuiz
        >>> mq['mathquiz_url'] = '/new_url'
    '''

    # default of settings for the mathquizrc file - a dictionart of dictionaries
    # the 'descr' field is for printing descriptions in the mathquizrc file
    settings = {
        'mathquiz_local' : {'val' : 'mathquiz_local', 'descr' : '(local) python module that writes the HTML quiz web' },
        'mathquiz_url'   : {'val' : '/MathQuiz',      'descr' : 'relative URL to mathquiz code' },
        'mathquiz_web'   : {'val' : '',               'descr' : 'system directory that contains the mathquiz web files'},
        'mathquiz_mk4'   : {'val' : '',               'descr' : 'make4ht build file'}
    }

    def __init__(self):
        '''
        If the mathquizrc file exists then read it.
        '''
        if os.path.isfile(mathquiz_file('mathquizrc')):
            self.read_mathquizrc()

    def __getitem__(self, key):
        r'''
        Return the value of the corresponding setting. That is, it returns
            self.settings[key]['val']
        and an error if the key is unknown.
        '''
        if key in self.settings:
            return self.settings[key]['val']

        print('Error: unknown setting {} in mathquizrc.'.format(key))
        sys.exit(1)

    def __setitem__(self, key, val):
        r'''
        Set the value of the corresponding setting. This is the equivalent of
            self.settings[key]['val'] = val
        and an error if the key is unknown.
        '''
        if key in self.settings:
            self.settings[key]['val'] = val
        else:
            print('Unknown setting {} in mathquizrc'.format(key))
            sys.exit(1)

    def read_mathquizrc(self):
        r'''
        Read the settings in the mathquizrc file.

        By default, there is no mathquiz initialisation file.
        '''
        try:
            print
            with open(mathquiz_file('mathquizrc'),'r') as mathquizrc:
                for line in mathquizrc:
                    if '%' in line:  # remove comments
                        line = line[:line.index('#')]
                    if '=' in line:
                        key, val = line.split('=')
                        key = key.strip().lower()
                        val = val.strip()
                        if key in self.settings:
                            self[key] = val
                        elif len(key)>0:
                            print('Unknown setting {} in mathquizrc'.format(key))
                            sys.exit(1)

        except Exception as err:
            sys.stderr.write('Error: there was an error reading the mathquizrc file\n  {}'.format(err))
            sys.exit(1)

    def write_mathquizrc(self):
        r'''
        Write the settings to the mathquizrc file.
        '''
        try:
            with open(mathquiz_file('mathquizrc'),'w') as rc_file:
                for key in self.settings:
                    if self[key] != '':
                        rc_file.write('## {}\n{:<14} = {}\n'.format(self.settings[key]['descr'], key, self[key]))

        except PermissionError:
                print('There was an error writing the mathquizrc file\n  {}'.format(err))
                print(permission_error.format(mathquiz_file('mathquirc')))
                sys.exit(1)

        except Exception as err:
            print('There was an error writing the mathquizrc file\n  {}'.format(err))
            sys.exit(1)

    def initialise_mathquiz(self):
        print(initialise_introduction)

        # prompt for directory and copy files - are these reasonable defaults
        # for each OS?
        if len(self['mathquiz_web']) > 0:
            web_root = self['mathquiz_web']
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
            self['mathquiz_web'] = 'SMS'
            self['mathquiz_url'] =  sms_http
        else:
            files_copied = False
            while not files_copied:
                try:
                    # first delete files of the form mathquiz.* files in web_dir
                    for file in glob.glob(os.path.join(web_dir, 'mathquiz.*')):
                        os.remove(file)
                    # ... now remove the doc directory
                    print('webdir = {}, full path = {}, isdir = {}.'.format(web_dir, os.path.join(web_dir, 'doc'), os.path.isdir(os.path.join(web_dir, 'doc'))))
                    web_doc = os.path.join(web_dir, 'doc')

                    if os.path.isfile(web_doc) or os.path.islink(web_doc):
                        os.remove(web_doc)
                    elif os.path.isdir(web_doc):
                        shutil.rmtree(web_doc)

                    if os.path.isdir(mathquiz_file('www')):
                        # if the www directory exists then copy it to web_dir
                        shutil.copytree('www', web_dir)
                    else:
                        # assume this is a development version and add links
                        # from the web directory to the parent directory
                        if not os.path.exists(web_dir):
                            os.makedirs(web_dir)
                        # get the root directory of the source code
                        mathquiz_src = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
                        for (src, target) in [('javascript/mathquiz.js', 'mathquiz.js'),
                                              ('css/mathquiz.css', 'mathquiz.css'),
                                              ('doc', 'doc')]:
                            os.symlink(os.path.join(mathquiz_src, src), os.path.join(web_dir, target))

                    self['mathquiz_web'] = web_dir
                    files_copied = True

                except PermissionError:
                    print(permission_error.format(web_dir))
                    sys.exit(1)

                except Exception as err:
                    print('There was a problem copying files to {}.\n  Please give a different directory.\n[Error: {}]\n'.format(web_dir, err))
                    web_dir = input('MathQuiz web directory: ')

            # now prompt for the relative url
            mq_url = input(mathquiz_url_message.format(self['mathquiz_url']))
            if mq_url != '':
                if not web_dir.ends_with(mq_url):
                    print('Error: {} does not end with {}.'.format(web_dir, mq_url))
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

      if self.options.quiet<2:
          print('MathQuiz generating web page for {}'.format(self.quiz_file))

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
            file.write( self.options.ConstructorPage(self) )

    def htlatex_quiz_file(self):
      r'''
      Process the file using htlatex/make4ht. This converts the quiz to an xml
      with markup specifying the different elements of the quiz page.
      '''
      # run htlatex only if quiz_file has a .tex textension
      if self.options.quiet<2:
          print('Processing {}.tex with TeX4ht'.format(self.quiz_file))

      try:
          cmd='make4ht --utf8 --config {config} --output-dir {quiz_file} {build}{quiz_file}.tex'.format(
                          config    = 'mathquiz.cfg',
                          quiz_file = self.quiz_file,
                          build     = '--build-file {} '.format(self.options.mathquiz_mk4) if self.options.mathquiz_mk4 !='' else ''
          ).split(' ')
          if self.options.quiet == 0:
             subprocess.call(cmd)
          elif self.options.quiet == 1:
             process = subprocess.call(cmd, stdout=open(os.devnull, 'wb'))
          else:
             process = subprocess.call(cmd, stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'))

          # htlatex generates an html file, so we rename this as an xml file
          os.rename(self.quiz_file+'.html', self.quiz_file+'.xml')
      except Exception as err:
          print('Error running htlatex on {}\n  {}.\n'.format(self.quiz_file, err))
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
            print('Error reading the xml generated for {}. Please check your latex source.\n  {}'.format(self.quiz_file, err))
            sys.exit(1)

    def add_meta_data(self):
      """ add the meta data for the web page to self.header """
      # meta tags`
      self.header += html_meta.format(version=metadata.version, authors=metadata.author, MathQuizURL=self.MathQuizURL, quiz_file=self.quiz_file)
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
      self.side_menu = side_menu.format(discussionList=discussionList, buttons=buttons, version=metadata.version)

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
              print('Error writing quiz specifications:\n {}.'.format(err))
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
        options=input_answer.format(tag=Q.answer.tag if Q.answer.tag else '')
      else:
        options=choice_answer.format(choices='\n'.join(self.printItem(opt, n, optnum) for (optnum, opt) in enumerate(Q.answer.itemList)),
                                    hidden=hidden_choice.format(qnum=n) if Q.answer.type=="single" else '')
      return question_text.format(qnum=n, question=Q.question, questionOptions=options)

    def printItem(self,opt,qnum,optnum):
      item='<tr>' if opt.parent.cols==1 or (optnum % opt.parent.cols)==0 else '<td>&nbsp;</td>'
      item+= '<td class="brown" >%s)</td>' % alphabet[optnum]
      if opt.parent.type == 'single':
          item+=single_item.format(qnum=qnum, answer=opt.answer)
      elif opt.parent.type == 'multiple':
          item+=multiple_item.format(qnum=qnum, optnum=optnum, answer=opt.answer)
      else:
          item+= '<!-- internal error: %s -->\n' % opt.parent.type
          sys.stderr.write('Unknown question type encountered: {}'.format(opt.parent.type))
      if (optnum % opt.parent.cols)==1 or (optnum+1) % opt.parent.cols==0:
          item+= '   </tr>\n'
      return item

    def printResponse(self,question,qnum):
        r'''
        Generate the HTML for displaying the response help text when the user
        answers a question.
        '''
        if isinstance(question.answer,mathquiz_xml.Answer):
            s = question.answer
            response=tf_response_text.format(choice=qnum, response='true', answer='Correct!', text=s.whenTrue if s.whenTrue else '')
            response+=tf_response_text.format(choice=qnum, response='false', answer='Incorrect. Please try again.', text=s.whenFalse if s.whenFalse else '')
        elif question.answer.type == "single":
            response='\n'+'\n'.join(single_response.format(qnum=qnum, part=snum+1,
                                                      answer='correct! ' if s.expect=='true' else 'incorrect ',
                                                      alpha=alphabet[snum],
                                                      response=s.response)
                                for (snum, s) in enumerate(question.answer.itemList)
            )
        else: # question.answer.type == "multiple":
            response='\n'+'\n'.join(multiple_response.format(qnum=qnum, part=snum+1,alpha=alphabet[snum], answer=s.expect.capitalize(), response=s.response)
                                for (snum, s) in enumerate(question.answer.itemList)
            )
            response+=multiple_response_correct.format(qnum=qnum,
                responses='\n'.join(multiple_response_answer.format(answer=s.expect.capitalize(), reason=s.response) for s in question.answer.itemList)
            )
        return '<div class="answer">'+response+'</div>'

# =====================================================
if __name__ == '__main__':
    main()
