#!/usr/bin/env python3
r'''
------------------------------------------------------------------------------
    webquiz | On-line quizzes generated from LaTeX using python and TeX4ht
------------------------------------------------------------------------------
    Copyright (C) Andrew Mathas and Donald Taylor, University of Sydney

    Distributed under the terms of the GNU General Public License (GPL)
                  http://www.gnu.org/licenses/

    This file is part of the WebQuiz system.

    <Andrew.Mathas@sydney.edu.au>
    <Donald.Taylor@sydney.edu.au>
------------------------------------------------------------------------------
'''

import argparse
import codecs
import errno
import glob
import os
import re
import shutil
import signal
import subprocess
import sys

# imports of webquiz code
import webquiz_templates
from webquiz_util import *
from webquiz_settings import WebQuizSettings
from webquiz_xml import ReadWebQuizXmlFile


# ---------------------------------------------------------------------------------------
def graceful_exit(sig, frame):
    ''' exit gracefully on SIGINT and SIGTERM'''
    if metadata:
        webquiz_error('program terminated (signal {}\n  {})'.format(
            sig, frame))
    else:
        webquiz_error('program terminated (signal {})'.format(sig))

signal.signal(signal.SIGINT, graceful_exit)
signal.signal(signal.SIGTERM, graceful_exit)


#################################################################################
def preprocess_with_pst2pdf(quiz_file):
    r'''
    Preprocess the latex file using pst2pdf. As we are preprocessing the file it
    is not enough to have latex pass us a flag that tells us to use pst2pdf.
    Instead, we have to extract the class file option from the tex file

    INPUT: quiz_file should be the name of the quiz file, WITHOUT the .tex extension
    '''
    talk('Preprocessing {} with pst2pdsf'.format(quiz_file))
    try:
        # pst2pdf converts pspicture environments to svg images and makes a
        # new latex file quiz_file+'-pdf' that includes these
        cmd = 'pst2pdf --svg --imgdir={q_file} {q_file}.tex'.format(q_file=quiz_file)
        run(cmd)
    except OSError as err:
        if err.errno == errno.ENOENT:
            webquiz_error(
                'pst2pdf not found. You need to install pst2pdf to use the pst2pdf option',
                err
            )
        else:
            webquiz_error('error running pst2pdf on {}'.format(quiz_file), err)

    # match \includegraphics commands
    fix_svg = re.compile(r'(\\includegraphics\[scale=1\])\{('+quiz_file+r'-fig-[0-9]*)\}')
    # the svg images are in the quiz_file subdirectory but latex can't
    # find them so we update the tex file to look in the right place
    try:
        with codecs.open(quiz_file + '-pdf.tex', 'r', encoding='utf8') as pst_file:
            with codecs.open(quiz_file + '-pdf-fixed.tex', 'w', encoding='utf8') as pst_fixed:
                for line in pst_file:
                    pst_fixed.write(fix_svg.sub(r'\1{%s/\2.svg}' % quiz_file, line))
    except OSError as err:
        webquiz_error(
            'there was an problem running pst2pdf for {}'.format(quiz_file),
            err
        )


#################################################################################
class MakeWebQuiz(object):
    """
    Convert a webquiz latex file to an on-line quiz.

    There are several steps:
      1. If given a LaTeX file then run htlatex/make4ht on the latex file to generate an
         xml file for the quiz that has all LaTeS markup converted to html.
      2. Read in the xml file version of the quiz
      3. Spit out the html version

    The HTMl is constructed using the template strings in webquiz_templates
    """
    # attributes that will form part of the generated web page
    header         = ''  # page header: title, meta data, links
    css            = ''  # css specifications
    javascript     = ''  # javascript code
    quiz_questions = ''  # the main quiz page
    side_menu      = ''  # the left hand quiz menu

    def __init__(self, quiz_name, quiz_file, options, settings):
        self.options = options
        self.settings = settings
        self.quiz_name = quiz_name.split('.')[0]
        self.quiz_file, extension = quiz_file.split('.')
        self.webquiz_url = settings['webquiz_url']
        if  self.webquiz_url[-1] == '/':
            self.webquiz_url =  self.webquiz_url[:len(self.webquiz_url)-1]

        # run htlatex only if quiz_file has a .tex extension
        if extension == 'tex':
            self.htlatex_quiz_file()

        self.read_xml_file()

        # determine language settings
        language = self.quiz.language

        try:
            language_file = kpsewhich('webquiz-{}.lang'.format(language))
        except subprocess.CalledProcessError:
            try:
                language_file = kpsewhich(language)
            except subprocess.CalledProcessError:
                webquiz_error(
                    'kpsewhich is unable to find language file for "{}"'.format(language)
                )

        self.language = MetaData(language_file)

        # initialise number of quiz and discussion items
        self.number_discussions = len(self.quiz.discussion_list)
        self.number_quizzes = len(self.quiz.question_list)

        self.add_meta_data()
        self.add_question_javascript()
        self.add_side_menu()
        self.add_quiz_header_and_questions()
        self.add_breadcrumbs()

        # add the initialisation warning if webquiz has not been initialised
        if self.settings.initialise_warning != '':
            self.breadcrumbs = self.settings.initialise_warning + self.breadcrumbs

        # now write the quiz to the html file
        with codecs.open(self.quiz_name + '.html', 'w', encoding='utf8') as file:
            # write the quiz in the specified format
            file.write(self.options.write_web_page(self))

    def add_breadcrumbs(self):
        r'''
        Build the breadcrumbs by appropriately parsing the magic crumbs
        '''
        self.breadcrumbs = ''
        if self.quiz.breadcrumbs != '':
            # build the bread crumbs
            crumbs = ''
            for crumb in self.quiz.breadcrumbs.split('|'):
                crumb = crumb.strip()

                if crumb == 'breadcrumb':
                    crumbs += self.add_breadcrumb_line(self.quiz.breadcrumb, missing='breadcrumb')

                elif crumb == 'department':
                    crumbs += self.add_breadcrumb_line(
                        text=self.quiz.department,
                        url=self.quiz.department_url,
                        missing='department')

                elif crumb == 'institution':
                    crumbs += self.add_breadcrumb_line(
                        text=self.quiz.institution,
                        url=self.quiz.institution_url,
                        missing='institution')

                elif crumb == 'quizindex':
                    if self.quiz.quiz_index == []:
                        crumbs += webquiz_templates.breadcrumb_quizlist.format(
                            quizzes_url=self.quiz.quizzes_url,
                            **self.language)
                    else:
                        crumbs += self.add_breadcrumb_line('Quizzes')

                elif crumb == 'Title':
                    crumbs += self.add_breadcrumb_line(text = self.quiz.title, missing='title')

                elif crumb == 'title':
                    title = self.quiz.title
                    crumbs += self.add_breadcrumb_line(
                                  text = title[:title.index(':')] if ':' in title else title,
                                  missing='title'
                              )

                elif crumb == 'unitcode':
                    crumbs += self.add_breadcrumb_line(
                        text=self.quiz.unit_code,
                        url=self.quiz.unit_url,
                        missing='unit code')

                elif crumb == 'unitname':
                    crumbs += self.add_breadcrumb_line(
                        text=self.quiz.unit_name,
                        url=self.quiz.unit_url,
                        missing='unit name')

                elif crumb != '':
                    lastSpace = crumb.rfind(' ')
                    url = crumb[lastSpace:].strip()
                    if url[0] == '/' or url.lower()[:4] == 'http':
                        crumbs += self.add_breadcrumb_line(text=crumb[:lastSpace], url=url)
                    else:
                        crumbs += self.add_breadcrumb_line(crumb)

            self.breadcrumbs = webquiz_templates.breadcrumbs.format(crumbs=crumbs)

    def add_breadcrumb_line(self, text, url='', missing='??'):
        r'''
        Return a line to add the bread crumbs, with errors if necessary
        '''
        if url == '':
            return webquiz_templates.breadcrumb_line_text.format(
                        text=text if text != '' else '?? ' + missing)

        return webquiz_templates.breadcrumb_line_url.format(
                    url=url, text=text if text != '' else '?? ' + missing)

    def htlatex_quiz_file(self):
        r'''
        Process the file using htlatex/make4ht. This converts the quiz to an xml
        with markup specifying the different elements of the quiz page.
        '''
        # at the minimum we put a css file into a <quiz_name> subdirectory
        if not os.path.exists(self.quiz_name):
            os.makedirs(self.quiz_name)

        try:
            talk('Processing {}.tex with TeX4ht'.format(self.quiz_name))
            # there is a slightly torturous process to convert the engine
            # settings into a command line option that make4ht understands
            cmd = 'make4ht --utf8 --config webquiz.cfg {engine} {escape} {make4ht_options} {quiz_file}.tex'.format(
                engine=self.settings.settings['engine']['values'][self.options.engine],
                escape='--shell-escape' if self.options.shell_escape else '',
                make4ht_options=self.options.make4ht_options,
                quiz_file=self.quiz_file
            )
            run(cmd)

            # move the css file into the quiz_file subdirectory
            if os.path.exists(self.quiz_file + '.css'):
                shutil.move(
                    self.quiz_file + '.css',
                    os.path.join(self.quiz_name, self.quiz_name + '.css'))

            # Now move any images that were created into the quiz_name
            # subdirectory and update the links in the html file As htlatex
            # generates an html file, we rename this as an xml file at the same
            # time - in the cfg file, \Preamable{ext=xml} should lead to an xml
            # file being created but this doesn't seem to work ??
            try:
                fix_img = re.compile(r'^src="([0-9]a-za-z]*.svg)" (.*)$')
                with codecs.open(self.quiz_file + '.html', 'r', encoding='utf8') as make4ht_file:
                    with codecs.open(self.quiz_name + '.xml', 'w', encoding='utf8') as xml_file:
                        for line in make4ht_file:
                            match = fix_img.match(line)
                            if match is None:
                                xml_file.write(line)
                            else:
                                # update html link and move file
                                image, rest_of_line = match.groups()
                                xml_file.write(r'src="{}/{}" {}'.format(
                                    self.quiz_name, image, rest_of_line))
                                shutil.move(
                                    image, os.path.join(self.quiz_name, image))

            except OSError as err:
                webquiz_error(
                    'there was a problem moving the image files for {}'.format(
                        self.quiz_name), err)

        except Exception as err:
            webquiz_error(
                'something when wrong when running htlatex on {}'.format(
                    self.quiz_file), err)

    def read_xml_file(self):
        r'''
        Read in the webquiz xml file for the quiz and store the xml document
        tree in ``self.quiz``.
        '''
        try:
            # read in the xml version of the quiz
            if not os.path.isfile(self.quiz_name + '.xml'):
                webquiz_error('{}.xml does not exist!?'.format(self.quiz_name))
            self.quiz = ReadWebQuizXmlFile(self.quiz_name + '.xml', self.settings)
        except Exception as err:
            webquiz_error('error reading the xml generated for {}. Please check your latex source.'
                .format(self.quiz_name), err)

    def add_meta_data(self):
        """ add the meta data for the web page to self.header """
        # meta tags`
        self.header += webquiz_templates.html_meta.format(
            version=metadata.version,
            authors=metadata.authors,
            webquiz_url=self.webquiz_url,
            description=metadata.description,
            copyright=metadata.copyright,
            department=self.quiz.department,
            institution=self.quiz.institution,
            quiz_file=self.quiz_name,
            theme=self.quiz.theme)
        if self.quiz.mathjs:
            self.header += webquiz_templates.mathjs

    def add_side_menu(self):
        """ construct the left hand quiz menu """
        if self.quiz.discussion_list != []:  # links for discussion items
            discussion_list = '\n       <ul>\n   {}\n       </ul>'.format(
                '\n   '.join(
                    webquiz_templates.discuss.format(b=q + 1, title=d.short_heading)
                    for (q, d) in enumerate(self.quiz.discussion_list)))
        else:
            discussion_list = ''

        # department and institution links
        department = '''<a href="{0.department_url}">{0.department}</a>'''.format(self.quiz)
        institution = '''<a href="{0.institution_url}">{0.institution}</a>'''.format(self.quiz)

        # question buttons
        if self.number_quizzes == 0:
            question_buttons = ''
        else:
            buttons = '\n' + '\n'.join(
                webquiz_templates.button.format(b=q,
                    cls=' button-selected' if self.quiz.discussion_list == [] and q == 1 else ''
                )
                for q in range(1, self.number_quizzes + 1))
            question_buttons=webquiz_templates.question_buttons.format(
                buttons=buttons, **self.language
            )

        # the full side menu
        self.side_menu = webquiz_templates.side_menu.format(
            discussion_list=discussion_list,
            version=metadata.version,
            department=department,
            institution=institution,
            side_questions=self.language['questions'] if self.number_quizzes>0 else '',
            question_buttons=question_buttons,
            copyright_years=metadata.copyright[:metadata.copyright.index(' ')],
            **self.language)

    def add_question_javascript(self):
        """
        Add the javascript for the questions to self and write the javascript
        initialisation file, <quiz>/quiz_specs.js, for the quiz.  When the quiz
        page is loaded, WebQuizInit reads the quiz_specs initialisation file to
        load the answers to the questions,  and the headers for the discussion
        items. We don't explicitly list quiz_specs.js in the meta data for the
        quiz page because we want to hide this information from the student,
        although they can easily get this if they open by the javascript
        console and know what to look for.
        """

        try:
            os.makedirs(self.quiz_name, exist_ok=True)
            os.chmod(self.quiz_name, mode=0o755)
            with codecs.open(os.path.join(self.quiz_name, 'wq-' + self.quiz_name + '.js'), 'w', encoding='utf8') as quiz_specs:
                if self.number_discussions > 0:
                    for (i, d) in enumerate(self.quiz.discussion_list):
                        quiz_specs.write('Discussion[{}]="{}";\n'.format(i, d.heading))
                if self.number_quizzes > 0:
                    for (i, question) in enumerate(self.quiz.question_list):
                        # QuizSpecifications is a 0-based array
                        quiz_specs.write('QuizSpecifications[%d]=[];\n' % i)
                        quiz_specs.write('QuizSpecifications[%d].type="%s";\n' % (i, question.type))
                        if question.type == 'input':
                            quiz_specs.write('QuizSpecifications[{}].value="{}";\n'.format(i,
                                question.answer.lower() if question.comparison=='lowercase'
                                                        else question.answer
                              )
                            )
                            quiz_specs.write('QuizSpecifications[%d].comparison="%s";\n' % (i, question.comparison))
                        else:
                            quiz_specs.write(''.join(
                                    'QuizSpecifications[%d][%d]=%s;\n' % (i, j, s.correct)
                                    for (j, s) in enumerate(question.items)
                                )
                            )

                if self.quiz.hide_side_menu:
                    quiz_specs.write('toggle_side_menu();\n')
                if self.quiz.one_page:
                    quiz_specs.write('onePage = true;\n')
                if self.quiz.random_order:
                    quiz_specs.write('questionOrder = shuffle(questionOrder);\n')
                quiz_specs.write('if (qTotal+dTotal>0) { showQuestion( (dTotal > 0) ? -1 : 1 ); }')

        except Exception as err:
            webquiz_error('error writing quiz specifications', err)

        self.javascript = webquiz_templates.questions_javascript.format(
            webquiz_url=self.webquiz_url,
            mathjax=self.settings['mathjax']
        )
        self.webquiz_init = webquiz_templates.webquiz_init.format(
            number_quizzes=self.number_quizzes,
            number_discussions=self.number_discussions,
            quiz_file=self.quiz_name,
        )

    def add_quiz_header_and_questions(self):
        r'''
        Write the quiz head and the main body of the quiz.
        '''
        if self.number_quizzes==0 or self.quiz.one_page:
            arrows = ''
        else:
            arrows = webquiz_templates.navigation_arrows.format(
                        question_number=self.quiz.discussion_list[0].heading
                                    if self.quiz.discussion_list != []
                                    else '1' if self.quiz.question_list > []
                                    else '',
                        **self.language
                    )

        # specify the quiz header - this will be wrapped in <div class="question-header>...</div>
        self.quiz_header = webquiz_templates.quiz_header.format(
            title=self.quiz.title,
            arrows=arrows,
            **self.language
        )

        # index for quiz
        if self.quiz.quiz_index != []:
            # add index to the web page
            self.quiz_questions += webquiz_templates.quiz_index_div.format(
                title=self.quiz.title if self.quiz.title!='' else self.quiz.unit_name,
                quiz_index='\n          '.join(
                    webquiz_templates.index_item.format(url=q.url, title=q.title)
                    for q in self.quiz.quiz_index),
                **self.language)
            # write a javascript file for displaying the menu
            # quizmenu = the index file for the quizzes in this directory
            with codecs.open('quiztitles.js', 'w', encoding='utf8') as quizmenu:
                quizmenu.write('var QuizTitles = [\n{titles}\n];\n'.format(
                    titles=',\n'.join("  ['{}', '{}']".format(q.title, q.url)
                                      for q in self.quiz.quiz_index)
                    )
                )
                quizmenu.write(webquiz_templates.create_dropdown)

        # now comes the main page text
        # discussion(s) masquerade as negative questions
        if self.quiz.discussion_list != []:
            dnum = 0
            for d in self.quiz.discussion_list:
                dnum += 1
                self.quiz_questions += webquiz_templates.discussion.format(
                    dnum=dnum,
                    discussion=d,
                    display='table' if self.quiz.one_page else 'none',
                )

        # finally we print the questions
        if self.quiz.question_list != []:
            self.quiz_questions += ''.join(
                webquiz_templates.question_wrapper.format(
                    qnum=qnum + 1,
                    question_number='{}. '.format(qnum+1) if self.quiz.one_page else '',
                    display='table' if self.quiz.one_page else 'none',
                    question=self.print_question(quiz_question, qnum + 1),
                    response=self.print_responses(quiz_question, qnum + 1)
                )
                for (qnum, quiz_question) in enumerate(self.quiz.question_list))

    def print_question(self, question, qnum):
        r'''Here:
            - question is the question
            - qnum is the number of the question
        '''
        if question.type == 'input':
            debugging('Q{}: after_text={}.'.format(qnum, question.after_text))
            question_options = webquiz_templates.input_answer.format(
                                 size=5+len('{}'.format(question.answer)),
                                 after_text=question.after_text,
                                 **self.language
            )
        elif question.type in ['single', 'multiple']:
            question_options = webquiz_templates.choice_answer.format(
                    after_text=question.after_text,
                    choices='\n'.join(self.print_choices(qnum, question, choice)
                        for choice in range(len(question.items)))
            )
        else:
            webquiz_error('Unknown question type "{}" in question {}'.format(question.type, qnum))
        return webquiz_templates.question_text.format(
            qnum=qnum,
            question_text=question.text,
            nextquestion='' if self.quiz.one_page else webquiz_templates.nextquestion.format(**self.language),
            question_options=question_options,
            **self.language)

    def print_choices(self, qnum, question, part):
        r'''
        Here:
            - qnum     = question number
            - question = current question
            - part     = number of the option we need to process.
        We put the parts into question.columns multicolumn format, so we have
        to add '<tr>' and '</tr>' tags depending on part.
        '''
        choice = question.items[part]
        item = '<tr>' if question.columns == 1 or (part % question.columns) == 0 else '<td>&nbsp;</td>'
        if question.type == 'single':
            item += webquiz_templates.single_item.format(choice=choice.symbol, qnum=qnum, text=choice.text)
        elif question.type == 'multiple':
            item += webquiz_templates.multiple_item.format(
                choice=choice.symbol,
                qnum=qnum,
                optnum=part,
                text=choice.text
            )
        else:
            item += '<!-- internal error: %s -->\n' % question.type
            webquiz_error('Unknown question type "{}" in question {}'.format(question.type, qnum))

        if question.columns == 1 or (part+1) % question.columns == 0 or part == len(question.items) - 1:
            item += '   </tr><!-- part={}, cols={}, # answers = {} -->\n'.format(
                part, question.columns, len(question.items))
        return item

    def print_responses(self, question, qnum):
        r'''
        Generate the HTML for displaying the response help text when the user
        answers a question.
        '''
        if question.type == 'input':
            response = webquiz_templates.tf_response_text.format(
                choice=qnum,
                response='true',
                correct_answer=self.language.correct,
                answer2='',
                text=question.when_right)
            response += webquiz_templates.tf_response_text.format(
                choice=qnum,
                response='false',
                correct_answer=self.language.incorrect,
                answer2=self.language.try_again,
                text=question.when_wrong)
        elif question.type == "single":
            response = '\n' + '\n'.join(
                webquiz_templates.single_response.format(
                    qnum=qnum,
                    part=snum + 1,
                    correct_answer=self.language.correct if s.correct == 'true' else self.language.incorrect,
                    alpha_choice=self.language.choice.format(s.symbol),
                    response=s.response,
                    **self.language)
                for (snum, s) in enumerate(question.items))
        elif question.type == "multiple":
            response = '\n' + '\n'.join(webquiz_templates.multiple_response.format(
                qnum=qnum,
                part=snum + 1,
                correct_answer=s.correct.capitalize(),
                response=s.response,
                multiple_choice_opener=self.language.multiple_incorrect.
                format(s.symbol),
                **self.language)
                for (snum, s) in enumerate(question.items)
            )
            response += webquiz_templates.multiple_response_correct.format(
                qnum=qnum,
                responses='\n'.join(
                    webquiz_templates.multiple_response_answer.format(
                        correct_answer=s.correct.capitalize(), reason=s.response)
                    for s in question.items),
                **self.language)
        else:
            webquiz_error('Unknown question type "{}" in question {}'.format(question.type, qnum))

        return '<div class="answer">' + response + '</div>'


# =====================================================
if __name__ == '__main__':
    try:
        settings = WebQuizSettings()
        if settings.just_initialise:
            sys.exit()

        # parse the command line options
        parser = argparse.ArgumentParser(
            description=metadata.description,
            epilog=webquiz_templates.webquiz_help_message
        )

        parser.add_argument(
            'quiz_file',
            nargs='*',
            type=str,
            default=None,
            help='latex quiz files')

        parser.add_argument(
            '-e', '--edit-settings',
            action='store_true',
            default=False,
            help='Edit webquiz settings')

        parser.add_argument(
            '-i',
            '--initialise',
            action='store_true',
            default=False,
            help='Initialise files and settings for webquiz')

        parser.add_argument(
            '-m',
            '--make4ht',
            action='store',
            type=str,
            dest='make4ht_options',
            default=settings['make4ht'],
            help='Options for make4ht')

        parser.add_argument(
            '-q',
            '--quiet',
            action='count',
            default=0,
            help='suppress tex4ht messages (also -qq etc)')

        parser.add_argument(
            '-r',
            '--rcfile',
            action='store',
            type=str,
            dest='rcfile',
            default='',
            help='Set rcfile')

        parser.add_argument(
            '--settings',
            nargs='?',
            type=str,
            const='all',
            action='store',
            dest='setting',
            default='',
            help='List system settings for webquiz')

        parser.add_argument(
            '-s',
            '--shell-escape',
            action='store_true',
            default=False,
            help='Shell escape for tex4ht/make4ht')

        parser.add_argument(
            '--webquiz_format',
            action='store',
            type=str,
            dest='webquiz_format',
            default=settings['webquiz_format'],
            help='Local python code for generating the quiz web page')

        engine = parser.add_mutually_exclusive_group()
        engine.add_argument(
            '--latex',
            action='store_const',
            const='latex',
            default=settings['engine'],
            dest='engine',
            help='Use latex to compile document with make4ht (default)')

        engine.add_argument(
            '-l',
            '--lua',
            action='store_const',
            const='lua',
            dest='engine',
            help='Use lualatex to compile the quiz')

        engine.add_argument(
            '-x',
            '--xelatex',
            action='store_const',
            const='xelatex',
            dest='engine',
            help='Use xelatex to compile the quiz')

        # options suppressed from the help message
        parser.add_argument(
            '--version',
            action='version',
            version='%(prog)s {}'.format(metadata.version),
            help=argparse.SUPPRESS)

        parser.add_argument(
            '--debugging',
            action='store_true',
            default=False,
            help=argparse.SUPPRESS)

        parser.add_argument(
            '--shorthelp',
            action='store_true',
            default=False,
            help=argparse.SUPPRESS)

        # parse the options
        options = parser.parse_args()
        options.prog = parser.prog

        # set debugging mode from options
        metadata.debugging = options.debugging

        # set the rcfile to be used
        if options.rcfile != '':
            settings.read_webquizrc(options.rcfile, external=True)

        # initialise and exit
        if options.initialise:
            settings.initialise_webquiz()
            sys.exit()

        # initialise and exit
        if options.setting != '':
            settings.list_settings(options.setting)
            sys.exit()

        # initialise and exit
        if options.edit_settings:
            settings.edit_settings()
            sys.exit()

        # print short help and exit
        if options.shorthelp:
            parser.print_usage()
            sys.exit()

        # if no filename then exit
        if options.quiz_file == []:
            parser.print_help()
            sys.exit(1)

        # import the local page formatter
        mod_dir, mod_format = os.path.split(options.webquiz_format)
        if mod_dir != '':
            sys.path.insert(0, mod_dir)
        options.write_web_page = __import__(mod_format).write_web_page

        # run() is a shorthand for executing system commands depending on the quietness
        #       - we need to use shell=True because otherwise pst2pdf gives an error
        # talk() is a shorthand for letting the user know what is happening
        if options.quiet == 0:
            run = lambda cmd: subprocess.call(cmd, shell=True)
            talk = lambda msg: print(msg)
        elif options.quiet == 1:
            run  = lambda cmd: subprocess.call(cmd, shell=True, stdout=open(os.devnull, 'wb'))
            talk = lambda msg: print(msg)
        else:
            run  = lambda cmd: subprocess.call(cmd, shell=True, stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'))
            talk = lambda msg: None

        # run through the list of quizzes and make them
        for quiz_file in options.quiz_file:
            if len(options.quiz_file) > 1 and options.quiet < 3:
                print('Making web page for {}'.format(quiz_file))
            # quiz_file is assumed to be a tex file if no extension is given
            if not '.' in quiz_file:
                quiz_file += '.tex'

            if not os.path.isfile(quiz_file):
                print('WebQuiz error: cannot read file {}'.format(quiz_file))

            else:

                # the quiz name and the quiz_file will be if pst2pdf is used
                quiz_name = quiz_file  
                if options.quiet < 2:
                    print('WebQuiz generating web page for {}'.format(quiz_file))

                # If the pst2podf option is used then we need to preprocess
                # the latex file BEFORE passing it to MakeWebQuiz. Set
                # options.pst2pdf = True if pst2pdf is given as an option to
                # the webquiz documentclass
                with codecs.open(quiz_file, 'r', encoding='utf8') as q_file:
                    doc = q_file.read()

                options.pst2pdf = False
                try:
                    brac = doc.index(
                        r'\documentclass[') + 15  # start of class options
                    if 'pst2pdf' in [
                            opt.strip()
                            for opt in doc[brac:brac +
                                           doc[brac:].index(']')].split(',')
                    ]:
                        preprocess_with_pst2pdf(quiz_file[:-4])
                        options.pst2pdf = True
                        quiz_file = quiz_file[:-4] + '-pdf-fixed.tex'  # now run webquiz on modified tex file
                except ValueError:
                    pass

                # the file exists and is readable so make the quiz
                MakeWebQuiz(quiz_name, quiz_file, options, settings)

                quiz_name = quiz_name[:quiz_name.index(
                    '.')]  # remove the extension

                # move the css file into the directory for the quiz
                css_file = os.path.join(quiz_name, quiz_name + '.css')
                if os.path.isfile(quiz_name + '.css'):
                    if os.path.isfile(css_file):
                        os.remove(css_file)
                    shutil.move(quiz_name + '.css', css_file)

                # now clean up unless debugging
                if not options.debugging:
                    for ext in [
                            '4ct', '4tc', 'dvi', 'idv', 'lg', 'log', 'ps',
                            'pdf', 'tmp', 'xml', 'xref'
                    ]:
                        if os.path.isfile(quiz_name + '.' + ext):
                            os.remove(quiz_name + '.' + ext)

                    # files created when using pst2pdf
                    if options.pst2pdf:
                        for file in glob.glob(quiz_name + '-pdf.*'):
                            os.remove(file)
                        for file in glob.glob(quiz_name + '-pdf-fixed.*'):
                            os.remove(file)
                        for extra in ['.preamble', '.plog', '-tmp.tex', '-pst.tex', '-fig.tex']:
                            if os.path.isfile(quiz_name + extra):
                                os.remove(quiz_name + extra)
                        if os.path.isdir(os.path.join(quiz_name, quiz_name)):
                            shutil.rmtree(os.path.join(quiz_name, quiz_name))

        if settings.initialise_warning != '':
            print(webquiz_templates.text_initialise_warning)

    except Exception as err:
        webquiz_error(
            'unknown problem.\n\nIf you think this is a bug please report it by creating an issue at\n    {}\n'
            .format(metadata.repository), err)
