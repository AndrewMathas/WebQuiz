#!/usr/bin/env python3
r'''
------------------------------------------------------------------------------
    webquiz_makequiz | build and generate the quiz page using webquiz_xml
                        | and webquiz_layout
------------------------------------------------------------------------------
    Copyright (C) Andrew Mathas, University of Sydney

    Distributed under the terms of the GNU General Public License (GPL)
                  http://www.gnu.org/licenses/

    This file is part of the WebQuiz system.

    <Andrew.Mathas@sydney.edu.au>
    <Donald.Taylor@sydney.edu.au>
------------------------------------------------------------------------------
'''
import subprocess
import codecs
import shutil
import os
import re

import webquiz_templates
import webquiz_util
import webquiz_xml

#################################################################################
class MakeWebQuiz(object):
    """
    Convert a webquiz latex file to an online quiz.

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

    def __init__(self, quiz_name, quiz_file, options, settings, metadata):
        self.options = options
        self.settings = settings
        self.metadata = metadata
        self.quiz_file, extension = os.path.splitext(quiz_file)
        self.quiz_name = os.path.basename(self.quiz_file)
        self.webquiz_url = settings['webquiz_url']
        if self.webquiz_url[-1] == '/':
            self.webquiz_url =  self.webquiz_url[:len(self.webquiz_url)-1]

        # run htlatex only if quiz_file has a .tex extension
        if extension == '.tex':
            self.htlatex_quiz_file()

        self.read_xml_file()

        # use kpsewhich to fine the webquiz language file
        try:
            language_file = webquiz_util.kpsewhich('webquiz-{}.lang'.format(self.quiz.language))
        except subprocess.CalledProcessError:
            self.webquiz_error(
                'kpsewhich is unable to find language file for "{}"'.format(self.quiz.language)
            )
        # read the language file and store as a dictonary
        self.language = webquiz_util.MetaData(language_file)

        # initialise number of quiz and discussion items
        self.number_discussions = len(self.quiz.discussion_list)
        self.number_questions = len(self.quiz.question_list)

        # build the different components of the quiz web page
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

    def webquiz_debug(self, msg):
        r'''
            Customised debugging message for the makequiz module
        '''
        webquiz_util.webquiz_debug(self.settings.debugging, 'makequiz: '+msg)

    def webquiz_error(self, msg, err=None):
        r'''
            Customised eror message for the makequiz module
        '''
        webquiz_util.webquiz_error(self.settings.debugging, 'makequiz: '+msg, err)

    def add_breadcrumbs(self):
        r'''
        Build the breadcrumbs by appropriately parsing the magic crumbs
        '''
        self.breadcrumbs = ''
        if self.quiz.breadcrumbs != '':
            # build the bread crumbs
            crumbs = '\n  '
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
                        crumbs += webquiz_templates.breadcrumb_quizindex.format(
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
            self.options.talk('Processing {}.tex with TeX4ht'.format(self.quiz_name))
            # there is a slightly torturous process to convert the engine
            # settings into a command line option that make4ht understands
            cmd = 'make4ht --utf8 --config webquiz.cfg {draft} {engine} {escape} {make4ht_options} {quiz_file}.tex'.format(
                draft='--mode draft' if self.options.draft else '',
                engine=self.settings.settings['engine']['values'][self.options.engine],
                escape='--shell-escape' if self.options.shell_escape else '',
                make4ht_options=self.options.make4ht_options,
                quiz_file=self.quiz_file
            )
            self.options.run(cmd)

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
                fix_img = re.compile(r'^(|.* )\b(data|src)="([-0-9a-zA-Z]*\.(?:png|svg))" (.*)$')
                with codecs.open(self.quiz_file + '.html', 'r', encoding='utf8') as make4ht_file:
                    with codecs.open(self.quiz_name + '.xml', 'w', encoding='utf8') as xml_file:
                        for line in make4ht_file:
                            match = fix_img.match(line)
                            if match is None:
                                xml_file.write(line)
                            else:
                                # update html link and move file
                                start, src, image, rest_of_line = match.groups()
                                xml_file.write(r'{}{}="{}/{}" {}'.format(
                                    start, src, self.quiz_name, image, rest_of_line))
                                shutil.move(image, os.path.join(self.quiz_name, image))

            except OSError as err:
                self.webquiz_error(
                    'there was a problem moving the image files for {}'.format(
                        self.quiz_name), err)

        except Exception as err:
            self.webquiz_error( 'something went wrong when running htlatex on {}'.format(self.quiz_file), err)

    def read_xml_file(self):
        r'''
        Read in the webquiz xml file for the quiz and store the xml document
        tree in ``self.quiz``.
        '''
        try:
            # read in the xml version of the quiz
            if not os.path.isfile(self.quiz_name + '.xml'):
                self.webquiz_error('{}.xml does not exist!?'.format(self.quiz_name))
            self.quiz = webquiz_xml.ReadWebQuizXmlFile(self.quiz_name + '.xml', self.settings)
        except Exception as err:
            self.webquiz_error('error reading the xml generated for {}. Please check your latex source.'
                .format(self.quiz_name), err)

    def add_meta_data(self):
        """ add the meta data for the web page to self.header """
        # meta tags`
        self.header += webquiz_templates.html_meta.format(
            version=self.metadata.version,
            authors=self.metadata.authors,
            webquiz_url=self.webquiz_url,
            description=self.metadata.description,
            copyright=self.metadata.copyright,
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
        if self.number_questions == 0:
            question_buttons = ''
        else:
            buttons = '\n' + '\n'.join(
                webquiz_templates.button.format(b=q,
                    cls='button-selected' if self.quiz.discussion_list==[] and q==1 else 'blank'
                )
                for q in range(1, self.number_questions + 1))
            question_buttons=webquiz_templates.question_buttons.format(
                buttons=buttons, **self.language
            )

        # the full side menu
        self.side_menu = webquiz_templates.side_menu.format(
            discussion_list=discussion_list,
            version=self.metadata.version,
            department=department,
            institution=institution,
            side_questions=self.language['questions'] if self.number_questions>0 else '',
            question_buttons=question_buttons,
            copyright_years=self.metadata.copyright[:self.metadata.copyright.index(' ')],
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
            with codecs.open(os.path.join(self.quiz_name, 'wq-' + self.quiz_name + '.js'), 'w',
                             encoding='utf8') as quiz_specs:
                if self.number_discussions > 0:
                    for (i, d) in enumerate(self.quiz.discussion_list):
                        quiz_specs.write('Discussion[{}]="{}";\n'.format(i+1, d.heading))
                if self.number_questions > 0:
                    for (i, question) in enumerate(self.quiz.question_list):
                        # QuizSpecifications is a 0-based array
                        quiz_specs.write('QuizSpecifications[{}]=[];\n'.format(i+1))
                        quiz_specs.write('QuizSpecifications[{}].type="{}";\n'.format(i+1, question.type))
                        if question.type == 'input':
                            quiz_specs.write('QuizSpecifications[{}].value="{}";\n'.format(i+1,
                                question.answer.lower() if question.comparison=='lowercase'
                                                        else question.answer
                              )
                            )
                            quiz_specs.write('QuizSpecifications[{}].comparison="{}";\n'.format(i+1, question.comparison))
                        else:
                            quiz_specs.write(''.join(
                                    'QuizSpecifications[{}][{}]={};\n'.format(i+1, j, s.correct)
                                    for (j, s) in enumerate(question.items)
                                )
                            )

                if self.quiz.hide_side_menu:
                    quiz_specs.write('toggle_side_menu();\n')
                if self.quiz.one_page:
                    quiz_specs.write('onePage = true;\n')
                if self.quiz.random_order:
                    quiz_specs.write('shuffleQuestions();\n')
                quiz_specs.write('initSession();\n')
                if self.number_discussions+self.number_questions>0:
                    quiz_specs.write('gotoQuestion({});'.format(
                        -1 if self.number_discussions>0 else 1)
                    )

        except Exception as err:
            self.webquiz_error('error writing quiz specifications', err)

        self.javascript = webquiz_templates.questions_javascript.format(
            webquiz_url=self.webquiz_url,
            mathjax=self.settings['mathjax']
        )
        self.webquiz_init = webquiz_templates.webquiz_init.format(
            number_questions=self.number_questions,
            number_discussions=self.number_discussions,
            quiz_file=self.quiz_name,
        )

    def add_quiz_header_and_questions(self):
        r'''
        Write the quiz head and the main body of the quiz.
        '''
        if self.quiz.one_page:
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
                    webquiz_templates.index_item.format(
                        url=q.url,
                        title='{} {}. {}'.format(self.language['quiz'],num+1,q.title)
                                if q.prompt else q.title,
                    ) for (num, q) in enumerate(self.quiz.quiz_index)),
                **self.language)
            # write a javascript file for displaying the menu
            # quizmenu = the index file for the quizzes in this directory
            with codecs.open('quizindex.js', 'w', encoding='utf8') as quizmenu:
                quizmenu.write('var QuizTitles = [\n{titles}\n];\n'.format(
                    titles=',\n'.join("  ['{}', '{}']".format(
                             '{} {}. {}'.format(self.language['quiz'],num+1,q.title) 
                                       if q.prompt else q.title,
                              q.url)
                        for (num,q) in enumerate(self.quiz.quiz_index))
                    )
                )
                quizmenu.write(webquiz_templates.create_quizindex_menu)

        # now comes the main page text
        # discussion(s) masquerade as negative questions
        if self.quiz.discussion_list != []:
            dnum = 0
            for d in self.quiz.discussion_list:
                dnum += 1
                self.quiz_questions += webquiz_templates.discussion.format(
                    dnum=dnum,
                    discussion=d,
                    display='inline' if self.quiz.one_page else 'none',
                    heading=webquiz_templates.discussion_heading.format(d.heading)
                            if self.quiz.one_page else ''
                )

        # finally we print the questions
        if self.quiz.question_list != []:
            self.quiz_questions += ''.join(
                webquiz_templates.question_wrapper.format(
                    qnum=qnum + 1,
                    question_number='{} {}. '.format(self.language.question, qnum+1)
                                    if self.quiz.one_page else '',
                    display='inline' if self.quiz.one_page else 'none',
                    question=self.print_question(quiz_question, qnum + 1),
                    feedback=self.print_feedback(quiz_question, qnum + 1)
                )
                for (qnum, quiz_question) in enumerate(self.quiz.question_list))

    def print_question(self, question, qnum):
        r'''Here:
            - question is the question
            - qnum is the number of the question
        '''
        if question.type == 'input':
            self.webquiz_debug('Q{}: after_text={}.'.format(qnum, question.after_text))
            question_options = webquiz_templates.input_answer.format(
                                 size=5+len('{}'.format(question.answer)),
                                 after_text=question.after_text,
                                 qnum=qnum,
                                 answer=self.language['answer']+':' if question.prompt else ''
            )
        elif question.type in ['single', 'multiple']:
            question_options = webquiz_templates.choice_answer.format(
                    after_text=question.after_text,
                    choices='\n'.join(self.print_choices(qnum, question, choice)
                        for choice in range(len(question.items)))
            )
        else:
            self.webquiz_error('Unknown question type "{}" in question {}'.format(question.type, qnum))
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
            self.webquiz_error('Unknown question type "{}" in question {}'.format(question.type, qnum))

        if question.columns == 1 or (part+1) % question.columns == 0 or part == len(question.items) - 1:
            item += '   </tr><!-- part={}, cols={}, # answers = {} -->\n'.format(
                part, question.columns, len(question.items))
        return item

    def print_feedback(self, question, qnum):
        r'''
        Generate the HTML for displaying the feedback help text when the user
        answers a question.
        '''
        if question.type == 'input':
            feedback = webquiz_templates.tf_feedback_text.format(
                choice=qnum,
                feedback='true',
                correct_answer=self.language.correct,
                answer2='',
                text=question.feedback_right)
            feedback += webquiz_templates.tf_feedback_text.format(
                choice=qnum,
                feedback='false',
                correct_answer=self.language.incorrect,
                answer2=self.language.try_again,
                text=question.feedback_wrong)
        elif question.type == "single":
            feedback = '\n' + '\n'.join(
                webquiz_templates.single_feedback.format(
                    qnum=qnum,
                    part=snum + 1,
                    correct_answer=self.language.correct if s.correct == 'true' else self.language.incorrect,
                    alpha_choice=self.language.choice.format(s.symbol),
                    feedback=s.feedback,
                    **self.language)
                for (snum, s) in enumerate(question.items))
        elif question.type == "multiple":
            feedback = '\n' + '\n'.join(webquiz_templates.multiple_feedback.format(
                qnum=qnum,
                part=snum + 1,
                correct_answer=getattr(self.language, s.correct).capitalize(),
                feedback=s.feedback,
                multiple_choice_opener=self.language.multiple_incorrect.
                format(s.symbol),
                **self.language)
                for (snum, s) in enumerate(question.items)
            )
            feedback += webquiz_templates.multiple_feedback_correct.format(
                qnum=qnum,
                feedback='\n'.join(webquiz_templates.multiple_feedback_answer.format(
                                        correct_answer=getattr(self.language, s.correct).capitalize(),
                                        reason=s.feedback) for s in question.items),
                                    **self.language)
        else:
            self.webquiz_error('Unknown question type "{}" in question {}'.format(question.type, qnum))

        return '<div class="answer">' + feedback + '</div>'
