!/usr/bin/env python3

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
import glob
import os
import re
import shutil
import stat
import subprocess
import sys
import traceback

import webquiz_xml
from webquiz_templates import *

# ---------------------------------------------------------------------------------------
# Return the full path for a file in the webquiz directory
webquiz_file = lambda file: os.path.join(os.path.dirname(os.path.realpath(__file__)), file)

# ---------------------------------------------------------------------------------------
class MetaData(dict):
    r"""
    A dummy class for reading, accessing and storing key-value pairs from
    a file Any internal spaces in the key name are replaced with underscores.

    The key-value pairs are available as both attributes and items

    Usage: MetaData(filename)
    """
    def __init__(self, filename):
        dict.__init__(self)
        with open(filename, 'r') as meta:
            for line in meta:
                if '=' in line:
                    key, val = line.strip().split('=')
                    if len(key.strip()) > 0:
                        self.__setitem__(
                                key.strip().lower().replace(' ', '_'),
                                val.strip()
                        )
                        setattr(self,
                                key.strip().lower().replace(' ', '_'),
                                val.strip()
                        )


# read in basic meta data such as author, version, ...
metadata = MetaData(kpsewhich('webquiz.ini'))
metadata.debugging = False


def kpsewhich(search):
    r'''short-cut to access kpsewhich output:
    usage: kpsewhich('-var-value=TEXMFLOCAL')
    '''
    return subprocess.check_output('kpsewhich '+search,
                                   stderr=subprocess.STDOUT,
                                   shell=True
                                   ).decode('ascii').strip()


# used to label the parts of questions as a, b, c, ...
alphabet = "abcdefghijklmnopqrstuvwxyz"


###############################################################################
# Recursivey copy directory tree, fixing shutil.copytree
# from https://stackoverflow.com/questions/1868714
def copytree(src, dst, symlinks=False, ignore=None):
  if not os.path.exists(dst):
    os.makedirs(dst)
    shutil.copystat(src, dst)
  lst = os.listdir(src)
  if ignore:
    excl = ignore(src, lst)
    lst = [x for x in lst if x not in excl]
  for item in lst:
    s = os.path.join(src, item)
    d = os.path.join(dst, item)
    if symlinks and os.path.islink(s):
      if os.path.lexists(d):
        os.remove(d)
      os.symlink(os.readlink(s), d)
      try:
        st = os.lstat(s)
        mode = stat.S_IMODE(st.st_mode)
        os.lchmod(d, mode)
      except:
        pass # lchmod not available
    elif os.path.isdir(s):
      copytree(s, d, symlinks, ignore)
    else:
      shutil.copy2(s, d)

#################################################################################
def WebQuizError(msg, err=None):
    r'''
    Consistent handling of errors in magthquiz: print the message `msg` and
    exist with error code `err.errno` if it is available.abs
    '''
    print('WebQuiz error: {}'.format(msg))

    if metadata.debugging and err is not None:
        raise

    if err is not None:
        trace = traceback.extract_tb(sys.exc_info()[2])
        filename, lineno, fn, text = trace[-1]
        print('File: {}, line number: {}\nError {} in {}: {}'.format(
                       filename, lineno, err, fn, text)
        )

    if hasattr(err, 'errno'):
        sys.exit(err.errno)

    sys.exit(1)

#################################################################################
# Preprocess the latex file using pst2pdf. As we are preprocessing the file it
# is not enough to have latex pass us a flag that tells us to use pst2pdf and,
# instead, we have to extract the class file option from the tex file
# INPUTL: quiz_file should be the name of the quiz file, WITHOUT the .tex extension
def preprocess_with_pst2pdf(quiz_file):
    talk('Preprocessing {} with pst2pdsf'.format(quiz_file))
    try:
        # pst2pdf converts pspicture environments to svg images and makes a
        # new latex file quiz_file+'-pdf' that includes these
        cmd='pst2pdf --svg --imgdir={q_file} {q_file}.tex'.format(q_file=quiz_file)
        run(cmd)
    except OSError as err:
        if err.errno == os.errno.ENOENT:
            WebQuizError('pst2pdf not found. You need to install pst2pdf to use the pst2pdf option', err)
        else:
            WebQuizError('error running pst2pdf on {}'.format(quiz_file), err)

    # match \includegraphics commands
    fix_svg = re.compile(r'(\\includegraphics\[scale=1\])\{('+ quiz_file+r'-fig-[0-9]*)\}')
    # the svg images are in the quiz_file subdirectory but latex can't
    # find them so we update the tex file to look in the right place
    try:
        with codecs.open(quiz_file+'-pdf.tex', 'r', encoding='utf8') as pst_file:
            with codecs.open(quiz_file+'-pdf-fixed.tex', 'w', encoding='utf8') as pst_fixed:
                for line in pst_file:
                    pst_fixed.write(fix_svg.sub(r'\1{%s/\2.svg}' % quiz_file, line))
    except IOError as err:
        WebQuizError('there was an problem running pst2pdf for {}'.format(quiz_file), err)

#################################################################################
class WebQuizSettings(object):
    r'''
    Class for initialising webquiz. This covers both reading and writting the webquizrc file and
    copying files into the web directories during initialisation. The settings
    themselves are stored in attribute settings, which is a dictionary. The
    class reads and writes the settings to the webquizrc file and the
    vbalues of the settings are available as items:
        >>> mq = WebQuizSettings()
        >>> mq['webquiz_url']
        ... /WebQuiz
        >>> mq['webquiz_url'] = '/new_url'
    '''

    # default of settings for the webquizrc file - a dictionary of dictionaries
    # the 'help' field is for printing descriptions of the settings to help the
    # user - they are also printed in the webquizrc file
    settings = dict(
      webquiz_url = {
        'default'  : '',
        'advanced' : False,
        'help'     : 'Relative URL for webquiz web directory',
      },
      webquiz_www = {
        'default'  : '',
        'advanced' : False,
        'help'     : 'Full path to WebQuiz web directory',
      },
      language  = {
        'default'  : 'english',
        'advanced' : False,
        'help'     : 'Default language used on web pages'
      },
      theme  = {
        'default'  : 'webquiz-light',
        'advanced' : False,
        'help'     : 'Default colour theme used on web pages'
      },
      breadcrumbs  = {
        'default'  : 'department|unitcode|quiz_index|breadcrumb',
        'advanced' : False,
        'help'     : 'Breadcrumbs at the top of quiz page',
      },
      department  = {
        'default'  : 'Mathematics',
        'advanced' : False,
        'help'     : 'Name of department',
      },
      department_url  = {
        'default'  : '/',
        'advanced' : False,
        'help'     : 'URL for department',
      },
      institution  = {
        'default'  : '',
        'advanced' : False,
        'help'     : 'Institution or university',
      },
      institution_url = {
        'default'  : '',
        'advanced' : False,
        'help'     : 'URL for institution or university',
      },
      webquiz_format  = {
        'default'  : 'webquiz_standard',
        'advanced' : True,
        'help'     : 'Name of python module that formats the quizzes',
      },
      make4ht = {
        'default'  : '',
        'advanced' : True,
        'help'     : 'Build file for make4ht',
      },
      mathjax  = {
        'default'  : 'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js',
        'advanced' : True,
        'help'     : 'URL for mathjax',
      },
      version  = {
        'default': metadata.version,
        'advanced' : True,
        'help'     : 'WebQuiz version number for webquizrc settings',
      }
    )

    # to stop execution from command-line options after initialised() has been called
    just_initialised = False

    def __init__(self):
        '''
        First read the system webquizrc file and then read the
        user .webquizrc file, if it exists. This allows the user
        to use some system settings and to override others.

        By default, there is no webquiz initialisation file. We first
        look for webquizrc in the webquiz source directory and then
        for .webquizrc file in the users home directory.
        '''
        for key in self.settings:
            self.settings[key]['value'] = self.settings[key]['default']
            self.settings[key]['changed'] = False
            if not 'editable' in self.settings[key]:
                self.settings[key]['editable'] = False


        # define a user and system rc file and load the ones that exist

        tex_local = kpsewhich('-var-value=TEXMFLOCAL')
        self.system_rc_file =  os.path.join( tex_local, 'scripts', 'webquiz', 'webquizrc')
        self.read_webquizrc( self.system_rc_file )

        self.user_rc_file = os.path.join(os.path.expanduser('~'),'.webquizrc')
        if os.path.isfile( self.user_rc_file ):
            self.read_webquizrc( self.user_rc_file )

        # if webquiz_url is empty then assume that we need to initialise
        self.initialise_warning = ''
        if self['webquiz_url'] == '':
            self['webquiz_url'] = 'http://www.maths.usyd.edu.au/u/mathas/WebQuiz/'
            self.initialise_warning = web_initialise_warning
            initialise = input('Do you want to initialise WebQuiz [Y/n]? ')
            if initialise=='' or initialise.strip().lower()[0]=='y':
                self.initialise_webquiz()

    def __getitem__(self, key):
        r'''
        Return the value of the corresponding setting. That is, it returns
            self.settings[key]['value']
        and an error if the key is unknown.
        '''
        if key in self.settings:
            return self.settings[key]['value']

        WebQuizError('unknown setting {} in webquizrc.'.format(key))

    def __setitem__(self, key, value):
        r'''
        Set the value of the corresponding setting. This is the equivalent of
            self.settings[key]['value'] = value
        and an error if the key is unknown.
        '''
        if key in self.settings:
            self.settings[key]['value'] = value
        else:
            WebQuizError('unknown setting {} in webquizrc'.format(key))

    def read_webquizrc(self, rc_file, external = False):
        r'''
        Read the settings from the specified webquizrc file - if it exists, in
        which case set self.rc_file equal to this directory. If the file does
        not exist then return without changing the current settings.
        '''
        if os.path.isfile(rc_file):
            try:
                with codecs.open(rc_file, 'r', encoding='utf8') as webquizrc:
                    for line in webquizrc:
                        if '#' in line:  # remove comments
                            line = line[:line.index('#')]
                        if '=' in line:
                            key, value = line.split('=')
                            key = key.strip().lower()
                            value = value.strip()
                            if key in self.settings:
                                if value != self[key]:
                                    self[key] = value
                                    self.settings[key]['changed'] = True
                            elif len(key)>0:
                                WebQuizError('unknown setting {} in {}'.format(key, rc_file))

                # record the rc_file for later use
                self.rc_file = rc_file

            except IOError as err:
                WebQuizError('there was a problem reading the rc-file {}'.format(rc_file), err)

            except Exception as err:
                WebQuizError('there was an error reading the webquizrc file,', err)

        elif external:
            # this is only an error if we have been asked to read this file
            WebQuizError('the rc-file {} does not exist'.format(rc_file))

    def write_webquizrc(self):
        r'''
        Write the settings to the webquizrc file, defaulting to the user
        rc_file if unable to write to the system rc_file
        '''
        if not hasattr(self, 'rc_file'):
            # when initialising an rc_file will not exist yet
            self.rc_file = self.system_rc_file

        file_not_written = True

        while file_not_written:
            try:
                dir, file = os.path.split(self.rc_file)
                if dir != '' and not os.path.isdir(dir):
                    os.makedirs(dir, exist_ok=True)
                with codecs.open(self.rc_file, 'w', encoding='utf8') as rcfile:
                    for key in self.settings:
                        # Only save settings in the rcfile if they have changed
                        # Note that changed means changed from the last read
                        # rcfile rather than from the default (of course, the
                        # defaults serve as the "initial rcfile")
                        if key == 'version' or self.settings[key]['changed']:
                            rcfile.write('# {}\n{:<15} = {}\n'.format(self.settings[key]['help'], key, self[key]))

                print('\nNon-default WebQuiz settings saved in {}\n'.format(self.rc_file))
                input('Press return to continue... ')
                file_not_written = False

            except (OSError, IOError, PermissionError) as err:
                # if writing to the system_rc_file then try to write to user_rc_file
                alt_rc_file =self.user_rc_file if self.rc_file != self.user_rc_file else self.system_rc_file
                response = input(rc_permission_error.format(
                                  error = err,
                                  rc_file = self.rc_file,
                                  alt_rc_file = alt_rc_file
                                )
                )
                if response.startswith('2'):
                    self.rc_file = alt_rc_file
                elif response.startswith('3'):
                    self.rc_file = os.path.expanduser(rc_file)
                elif not response.startswith('1'):
                    print('exiting...')
                    sys.exit(1)

                # if still here then try to write the rc-file again
                self.write_webquizrc()

    def list_settings(self, setting='all'):
        r'''
        Print the non-default settings for webquiz from the webquizrc
        '''
        if not hasattr(self, 'rc_file'):
            print('Please initialise WebQuiz using the command: webquiz --initialise\n')

        if setting != 'all':
            if setting in self.settings:
                print(self.settings[setting]['value'])
            else:
                WebQuizError('{} is an invalid setting'.format(setting))

        else:
            print('WebQuiz settings from {}\n'.format(self.rc_file))
            for key in self.settings:
                if self[key] != '':
                    print('# {}{}\n{:<15} = {}\n'.format(
                              self.settings[key]['help'],
                              ' (default)' if self[key] == self.settings[key]['default'] else '',
                              key,
                              self[key]
                          )
                    )

    def initialise_webquiz(self):
        r'''
        Set the root for the WebQuiz web directory and copy the www files into
        this directory. Once this is done save the settings to webquizrc.
        This method should only be used when WebQuiz is being set up.
        '''
        if self.just_initialised:  # stop initialising twice with webquiz --initialise
            return

        print(initialise_introduction)

        # prompt for directory and copy files - are these reasonable defaults
        # for each OS?
        if len(self['webquiz_www']) > 0:
            web_root = self['webquiz_www']
        elif sys.platform == 'linux':
            web_root = '/usr/local/httpd/WebQuiz'
        elif sys.platform == 'darwin':
            web_root = '/Library/WebServer/Documents/WebQuiz'
        else:
            web_root = '/Local/Library/WebServer'

        files_copied = False
        print(web_directory_message)
        while not files_copied:
            web_dir = input('WebQuiz web directory [{}] '.format(web_root))
            if web_dir == '':
                web_dir = web_root
            else:
                web_dir = os.path.expanduser(web_dir)

            print('Web directory set to {}'.format(web_dir))
            if web_dir == 'SMS':
                # undocumented: allow links to SMS web pages
                self['webquiz_www'] = 'SMS'
                self['webquiz_url'] =  'http://www.maths.usyd.edu.au/u/MOW/WebQuiz/'

            else:
                try:
                    # first delete files of the form webquiz.* files in web_dir
                    for file in glob.glob(os.path.join(web_dir, 'webquiz.*')):
                        os.remove(file)
                    # ... now remove the doc directory
                    web_doc = os.path.join(web_dir, 'doc')
                    if os.path.isfile(web_doc) or os.path.islink(web_doc):
                        os.remove(web_doc)
                    elif os.path.isdir(web_doc):
                        shutil.rmtree(web_doc)

                    print('**** About to copy www directory {} to {} ****'.format(webquiz_file('www'), web_dir))
                    if os.path.isdir(webquiz_file('www')):
                        # if the www directory exists then copy it to web_dir
                        print('Copying files to {}...\n'.format(web_dir))
                        copytree(webquiz_file('www'), web_dir)
                    else:
                        # assume this is a development version and add links
                        # from the web directory to the parent directory
                        if not os.path.exists(web_dir):
                            os.makedirs(web_dir)
                        # get the root directory of the source code
                        webquiz_src = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
                        for (src, target) in [('javascript/webquiz.js', 'webquiz.js'),
                                              ('css/webquiz.css', 'webquiz.css'),
                                              ('doc', 'doc')]:
                            os.symlink(os.path.join(webquiz_src, src), os.path.join(web_dir, target))

                    self['webquiz_www'] = web_dir
                    self.settings['webquiz_www']['changed'] = True
                    files_copied = True

                except PermissionError as err:
                    print(permission_error.format(web_dir))

                except IOError as err:
                    print('There was a problem copying files to {}.\n  Error: {}]\n'.format(web_dir, err))
                    print('Please give a different directory.\n')

        if self['webquiz_www'] != 'SMS':
            # now prompt for the relative url
            mq_url = input(webquiz_url_message.format(self['webquiz_url']))
            if mq_url != '':
                # removing trailing slashes from mq_url
                while mq_url[-1] == '/':
                    mq_url = mu_url[:len(mq_url)-1]

                if mq_url[0] != '/': # force URL to start with /
                    print("  ** prepending '/' to webquiz_url **")
                    mq_url = '/' + mq_url

                if not web_dir.endswith(mq_url):
                    print(webquiz_url_warning)
                    input('Press return to continue... ')

                self['webquiz_url'] = mq_url

        self.settings['webquiz_url']['changed'] = (self['webquiz_url']!=self.settings['webquiz_url']['default'])

        # read and save the rest of the settings and exit
        print(edit_settings)
        input('Press return to continue... ')
        self.edit_settings(ignored_settings = ['webquiz_url', 'webquiz_www', 'version'])
        print(initialise_ending.format(web_dir=self['webquiz_www']))
        self.just_initialised = True

    def edit_settings(self, ignored_settings = ['webquiz_www', 'version']):
        r'''
        Change current default values for the WebQuiz settings
        '''
        for key in self.settings:
            if key not in ignored_settings:
                if self.settings[key]['advanced']:
                    print('\n** This is an advanced setting that you probably do not want to change **')
                else:
                    print('')

                setting = input('{}{}: '.format(self.settings[key]['help'],
                    '' if self[key] == '' else ' ['+self[key]+'] ')
                )
                if setting != '':
                    if key == 'webquiz_url' and setting[0] != '/':
                        print("  ** prepending '/' to webquiz_url **")
                        setting = '/'+setting

                    if key == 'webquiz_format':
                        setting = os.path.expanduser(setting)
                        if setting.endswith('.py'):
                            print("  ** removing .py extension from webquiz_format **")
                            setting = setting[:-3]

                    self[key] = setting
                    self.settings[key]['changed'] = True

        # save the settings, print them and exit
        self.write_webquizrc()
        self.list_settings()

#################################################################################
class MakeWebQuiz(object):
    """
    Convert a webquiz latex file to an on-line quiz.

    There are several steps:
      1. If given a LaTeX file then run htlatex/make4ht on the latex file to generate an
         xml file for the quiz that has all LaTeS markup converted to html.
      2. Read in the xml file version of the quiz
      3. Spit out the html version

    The HTMl is contructed using the template strings in webquiz_templates
    """
    # attributes that will form part of the generated web page
    header=''         # everything printed in the page header: meta data, includes, javascript, CSS, ...
    css=''            # css specifications
    javascript=''     # javascript code
    quiz_questions='' # the main quiz page
    side_menu=''      # the left hand quiz menu

    def __init__(self, quiz_name, quiz_file, options, settings):
        self.options = options
        self.settings = settings
        self.quiz_name = quiz_name.split('.')[0]
        self.quiz_file, extension = quiz_file.split('.')
        self.webquiz_url = settings['webquiz_url']

        # run htlatex only if quiz_file has a .tex extension
        if extension == 'tex':
            self.htlatex_quiz_file()

        self.read_xml_file()

        # determine language settings
        language = self.quiz.language
        if language == '':
            language = self.settings['language']

        try:
            language_file = kpsewhich('webquiz-{}.lang'.format(language))
        except subprocess.CalledProcessError:
            try:
                language_file = kpsewhich( language )
            except subprocess.CalledProcessError:
                WebQuizError('kpsewhich is unable to find language file for "{}"'.format(language))

        self.language = MetaData( language_file )

        self.theme = self.quiz.theme
        if self.theme == '':
            self.theme = self.settings['theme']

        # initialise number of quiz and discussion items
        self.dTotal = len(self.quiz.discussion_list)
        self.qTotal = len(self.quiz.question_list)

        # take school defaults from settings if they are not set in the quiz file
        self.unit = self.quiz.unit
        self.school = self.quiz.school
        for opt in ['department', 'department_url', 'institution', 'institution_url']:
            if self.school[opt] == '' and settings[opt] != '':
                self.school[opt] = settings[opt]

        self.title = self.quiz.title
        self.add_meta_data()
        self.add_question_javascript()
        self.add_side_menu()
        self.add_quiz_header_and_questions()

        # build the bread crumbs - take crumbs from settings if not specified by the quiz
        if self.quiz.breadcrumbs == ['none']:
            self.quiz.breadcrumbs = ['']
        elif self.quiz.breadcrumbs == [''] and self.settings['breadcrumbs']!='':
            self.quiz.breadcrumbs = [crumb.strip() for crumb in self.settings['breadcrumbs'].split('|')]

        self.breadcrumbs = ''
        if self.quiz.breadcrumbs != ['']:
            crumbs=''
            for crumb in  self.quiz.breadcrumbs:
                if   crumb == 'department':
                    crumbs += self.add_breadcrumb_line(text=self.school['department'],
                                                       url=self.school['department_url'],
                                                       missing='department'
                    )
                elif crumb == 'institution':
                    crumbs += self.add_breadcrumb_line(text=self.school['institution'],
                                                       url=self.school['institution_url'],
                                                       missing='insitution'
                    )
                elif crumb == 'unitcode':
                    crumbs += self.add_breadcrumb_line(text=self.unit['code'],
                                                       url=self.unit['url'],
                                                       missing='unit code'
                    )
                elif crumb == 'unitname':
                    crumbs += self.add_breadcrumb_line(text=self.unit['name'],
                                                       url=self.unit['url'],
                                                       missing='unit name'
                    )
                elif crumb == 'quiz_index':
                    if len(self.quiz.quiz_list)==0:
                        crumbs += breadcrumb_quizlist.format(quizzes_url = self.unit['quizzes_url'], **self.language)
                    else:
                        crumbs += self.add_breadcrumb_line('Quizzes')
                elif crumb == 'breadcrumb':
                    crumbs += self.add_breadcrumb_line(self.quiz.breadcrumb, missing='breadcrumb')
                elif crumb != '':
                    lastSpace = crumb.rfind(' ')
                    url = crumb[lastSpace:].strip()
                    if url[0] == '/' or url.lower()[:4]=='http':
                        crumbs += self.add_breadcrumb_line(text=crumb[:lastSpace], url=url)
                    else:
                        crumbs += self.add_breadcrumb_line(crumb)

            if crumbs != '':
                self.breadcrumbs = breadcrumbs.format(crumbs = crumbs)

        if self.settings.initialise_warning != '':
            self.breadcrumbs = self.settings.initialise_warning + self.breadcrumbs

        # now write the quiz to the html file
        with codecs.open(self.quiz_name+'.html', 'w', encoding='utf8') as file:
            # write the quiz in the specified format
            file.write( self.options.write_web_page(self) )

    def add_breadcrumb_line(self,  text, url='', missing='??'):
        r'''
        Return a line to add the bread crumbs, with errors if necessary
        '''
        if url == '':
            return breadcrumb_line_text.format(text=text if text != '' else '?? '+missing)
        else:
            return  breadcrumb_line_url.format(url=url, text=text if text != '' else '?? '+missing)

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
            cmd='make4ht --utf8 --config webquiz.cfg {make4ht_options} {escape} {quiz_file}.tex'.format(
                    quiz_file = self.quiz_file,
                    make4ht_options  = self.options.make4ht_options,
                    escape = '--shell-escape' if self.options.shell_escape else ''
            )
            run(cmd)

            # move the css file into the quiz_file subdirectory
            if os.path.exists(self.quiz_file+'.css'):
                shutil.move(self.quiz_file+'.css', os.path.join(self.quiz_name, self.quiz_name+'.css'))

            # Now move any images that were created into the quiz_name
            # subdirectory and update the links in the html file As htlatex
            # generates an html file, we rename this as an xml file at the same
            # time - in the cfg file, \Preamable{ext=xml} should lead to an xml
            # file being created but this doesn't seem to work ??
            try:
                fix_img = re.compile(r'^src="([0-9]a-za-z]*.svg)" (.*)$')
                with codecs.open(self.quiz_file+'.html', 'r', encoding='utf8') as make4ht_file:
                    with codecs.open(self.quiz_name+'.xml', 'w', encoding='utf8') as xml_file:
                        for line in make4ht_file:
                            match = fix_img.match(line)
                            if match is None:
                                xml_file.write(line)
                            else:
                                # update html link and move file
                                image, rest_of_line = match.groups()
                                xml_file.write(r'src="{}/{}" {}'.format(self.quiz_name, image, rest_of_line))
                                shutil.move(image, os.path.join(self.quiz_name, image))

            except IOError as err:
                WebQuizError('there was a problem moving the image files for {}'.format(self.quiz_name), err)

        except Exception as err:
            WebQuizError('something when wrong when running htlatex on {}'.format(self.quiz_file), err)

    def read_xml_file(self):
        r'''
        Read in the webquiz xml file for the quiz and store the xml document
        tree in ``self.quiz``.
        '''
        try:
            # read in the xml version of the quiz
            print('quiz name = {}, quiz file = {}'.format(self.quiz_name, self.quiz_file))
            if not os.path.isfile(self.quiz_name+'.xml'):
                WebQuizError('{}.xml does not exist!?'.format(self.quiz_name))
            self.quiz = webquiz_xml.ReadWebQuizXmlFile(self.quiz_name+'.xml', self.options.debugging)
        except Exception as err:
            WebQuizError('error reading the xml generated for {}. Please check your latex source.'.format(self.quiz_name), err)

    def add_meta_data(self):
        """ add the meta data for the web page to self.header """
        # meta tags`
        self.header += html_meta.format(version      = metadata.version,
                                        authors      = metadata.authors,
                                        webquiz_url  = self.webquiz_url,
                                        description  = metadata.description,
                                        copyright    = metadata.copyright,
                                        department   = self.school['department'],
                                        institution  = self.school['institution'],
                                        quiz_file    = self.quiz_name,
                                        theme        = self.theme
        )

        # we don't need any of the links or metas from the latex file
        # self.header += ''.join('  <meta {}>\n'.format(' '.join('{}="{}"'.format(k, meta[k]) for k in meta)) for meta in self.quiz.meta_list)
        # self.header += ''.join('  <link {}>\n'.format(' '.join('{}="{}"'.format(k, link[k]) for k in link)) for link in self.quiz.link_list)

    def add_side_menu(self):
        """ construct the left hand quiz menu """
        if len(self.quiz.discussion_list)>0: # links for discussion items
            discussion_list = '\n       <ul>\n   {}\n       </ul>'.format(
                  '\n   '.join(discuss.format(b=q+1, title=d.short_heading) for (q, d) in enumerate(self.quiz.discussion_list)))
        else:
            discussion_list = ''

        buttons = '\n'+'\n'.join(button.format(b=q, cls=' button-selected' if len(self.quiz.discussion_list)==0 and q==1 else '')
                                   for q in range(1, self.qTotal+1))

        if self.school['department_url']=='':
            department = self.school['department']
        else:
            department = '''<a href="{department_url}">{department}</a>'''.format(**self.school)

        if self.school['institution_url']=='':
            institution = self.school['institution']
        else:
            institution = '''<a href="{institution_url}">{institution}</a>'''.format(**self.school)

        # end of progress buttons, now for the credits
        self.side_menu = side_menu.format(discussion_list=discussion_list,
                                          buttons=buttons,
                                          version=metadata.version,
                                          department=department,
                                          institution=institution,
                                          **self.language
        )

    def add_question_javascript(self):
        """
        Add the javascript for the questions to self and write the javascript
        initialisation file, <quiz>/quiz_list.js, for the quiz.  When the quiz
        page is loaded, WebQuizInit reads the quiz_list initialisation file to
        load the answers to the questions,  and the headers for the discussion
        items. We don't explicitly list quiz_list.js in the meta data for the
        quiz page because we want to hide this information from the student,
        although they can easily get this if they open by the javascript
        console and know what to look for.
        """

        try:
            os.makedirs(self.quiz_name, exist_ok=True)
            with codecs.open(os.path.join(self.quiz_name,'wq-'+self.quiz_name+'.js'), 'w', encoding='utf8') as quiz_list:
                if self.dTotal>0:
                    for (i, d) in enumerate(self.quiz.discussion_list):
                        quiz_list.write('Discussion[{}]="{}";\n'.format(i, d.heading))
                if self.qTotal >0:
                    for (i, q) in enumerate(self.quiz.question_list):
                        quiz_list.write('QuizSpecifications[%d]=[];\n' % i)# QuizSpecifications is a 0-based array
                        a = q.answer
                        quiz_list.write('QuizSpecifications[%d].label="%s %s";\n' % (i, self.language.question, i+1))
                        if isinstance(a, webquiz_xml.Answer):
                             quiz_list.write('QuizSpecifications[%d].value="%s";\n' % (i, a.value))
                             quiz_list.write('QuizSpecifications[%d].type="input";\n' % i)
                        else:
                             quiz_list.write('QuizSpecifications[%d].type="%s";\n' % (i, a.type))
                             quiz_list.write(''.join('QuizSpecifications[%d][%d]=%s;\n' % (i, j, s.expect) for (j, s) in enumerate(a.item_list)))

        except Exception as err:
            WebQuizError('error writing quiz specifications', err)

        self.javascript = questions_javascript.format(
                              webquiz_url = self.webquiz_url,
                              mathjax = self.settings['mathjax']
        )
        self.webquiz_init = webquiz_init.format(
                              qTotal = self.qTotal,
                              dTotal = self.dTotal,
                              quiz_file = self.quiz_name,
                              hide_side_menu = self.quiz.hide_side_menu
        )

    def add_quiz_header_and_questions(self):
        r'''
        Write the quiz head and the main body of the quiz.
        '''
        if self.qTotal == 0:
            arrows = ''
        else:
            arrows = navigation_arrows.format(**self.language)

        # specify the quiz header - this will be wrapped in <div class="question-header>...</div>
        self.quiz_header=quiz_header.format(title=self.title,
                                            question_number=self.quiz.discussion_list[0].heading if len(self.quiz.discussion_list)>0
                                                else self.language.question+' 1' if len(self.quiz.question_list)>0 else '',
                                            arrows = arrows
        )

        # now comes the main page text
        # discussion(s) masquerade as negative questions
        if len(self.quiz.discussion_list)>0:
          dnum = 0
          for d in self.quiz.discussion_list:
            dnum+=1
            self.quiz_questions+=discussion.format(dnum=dnum, discussion=d,
                               display='style="display: table;"' if dnum==1 else '',
                               input_button=input_button if len(self.quiz.question_list)>0 and dnum==len(self.quiz.discussion_list) else '')

        # index for quiz
        if len(self.quiz.quiz_list)>0:
          # add index to the web page
          self.quiz_questions+=quiz_list_div.format(
                 unit=self.unit['name'],
                 quiz_index='\n          '.join(quiz_list_item.format(url=q['url'], title=q['title'])
                                                for q in self.quiz.quiz_list),
                 **self.language
          )
          # write a javascript file for displaying the menu
          # quizmenu = the index file for the quizzes in this directory
          with codecs.open('quiztitles.js','w', encoding='utf8') as quizmenu:
             quizmenu.write('var QuizTitles = [\n{titles}\n];\n'.format(
                 titles = ',\n'.join("  ['{}', '/{}/Quizzes/{}']".format(
                                     q['title'],
                                     self.unit['url'],
                                     q['url']) for q in self.quiz.quiz_list
                                    )
                 )
             )

        # finally we print the questions
        if len(self.quiz.question_list)>0:
          self.quiz_questions+=''.join(question_wrapper.format(qnum=qnum+1,
                                                display='style="display: table;"' if qnum==0 and len(self.quiz.discussion_list)==0 else '',
                                                question=self.print_question(q, qnum+1),
                                                response=self.print_responses(q, qnum+1))
                                for (qnum, q) in enumerate(self.quiz.question_list)
          )

    def print_question(self, Q, Qnum):
        r'''Here:
            - Q is a class containing the question
            - Qnum is the number of the question
        '''
        if isinstance(Q.answer, webquiz_xml.Answer):
            options=input_answer.format(tag=Q.answer.tag if Q.answer.tag else '')
        else:
            options=choice_answer.format(choices='\n'.join(self.print_choices(Qnum, Q.answer.item_list, choice) for choice in range(len(Q.answer.item_list))))
                                        #hidden=input_single.format(qnum=Qnum) if Q.answer.type=="single" else '')
        return question_text.format(qnum=Qnum, question_text=Q.question, question_options=options, **self.language)

    def print_choices(self, qnum, answers, choice):
        r'''
        Here:
            - qnum     = question number
            - answers = listr of answers to this question
            - choice  = number of the option we need to process.
        We put the parts into ans.parent.cols multicolumn format, so we have
        to add '<tr>' and '</tr>' tags depending on choice.
        '''
        ans = answers[choice]
        item  ='<tr>' if ans.parent.cols==1 or (choice % ans.parent.cols)==0 else '<td>&nbsp;</td>'
        if ans.parent.type == 'single':
            item+=single_item.format(choice=alphabet[choice], qnum=qnum, answer=ans.answer)
        elif ans.parent.type == 'multiple':
            item+=multiple_item.format(choice=alphabet[choice], qnum=qnum, optnum=choice, answer=ans.answer)
        else:
            item+= '<!-- internal error: %s -->\n' % ans.parent.type
            sys.stderr.write('Unknown question type encountered: {}'.format(ans.parent.type))
        if ans.parent.cols == 1 or (choice+1) % ans.parent.cols == 0 or choice == len(answers)-1:
            item+= '   </tr><!-- choice={}, cols={}, # answers = {} -->\n'.format(choice, ans.parent.cols, len(answers))
        return item

    def print_responses(self, question, qnum):
        r'''
        Generate the HTML for displaying the response help text when the user
        answers a question.
        '''
        if isinstance(question.answer, webquiz_xml.Answer):
            s = question.answer
            response  = tf_response_text.format(
                                           choice=qnum,
                                           response='true',
                                           answer=self.language.correct,
                                           answer2='',
                                           text=s.when_right
            )
            response += tf_response_text.format(
                                           choice=qnum,
                                           response='false',
                                           answer=self.language.incorrect,
                                           answer2=self.language.try_again,
                                           text=s.when_wrong)
        elif question.answer.type == "single":
            response='\n'+'\n'.join(single_response.format(
                                             qnum=qnum, part=snum+1,
                                             answer=self.language.correct if s.expect=='true' else self.language.incorrect,
                                             alpha_choice = self.language.choice.format(alphabet[snum]),
                                             response=s.response,
                                             **self.language
                                ) for (snum, s) in enumerate(question.answer.item_list)
            )
        else: # question.answer.type == "multiple":
            response='\n'+'\n'.join(multiple_response.format(
                                      qnum=qnum,
                                      part=snum+1,
                                      answer=s.expect.capitalize(),
                                      response=s.response,
                                      multiple_choice_opener=self.language.multiple_choice_incorrect.format(alphabet[snum]),
                                      **self.language
                                ) for (snum, s) in enumerate(question.answer.item_list)
            )
            response+=multiple_response_correct.format(
                qnum=qnum,
                responses='\n'.join(multiple_response_answer.format(
                                     answer=s.expect.capitalize(),
                                     reason=s.response) for s in question.answer.item_list),
                **self.language
            )
        return '<div class="answer">'+response+'</div>'

# =====================================================
if __name__ == '__main__':
    try:
        settings = WebQuizSettings()
        if settings.just_initialised:
            sys.exit()

        # parse the command line options
        parser = argparse.ArgumentParser(description = metadata.description,
                                         epilog      = webquiz_help_message
        )
        parser.add_argument('quiz_file', nargs='*', type=str, default=None, help='latex quiz files')
        parser.add_argument('-i', '--initialise', action='store_true', default=False,
                            help='Initialise files and setings for webquiz')
        parser.add_argument('-q', '--quiet', action='count', default=0, help='suppress tex4ht messages (also -qq etc)')
        parser.add_argument('--settings', nargs='?', type=str, const='all', action='store', dest='setting',
                            default='', help='List system settings for webquiz')
        parser.add_argument('--edit-settings', action='store_true', default=False, help='Edit webquiz settings')
        parser.add_argument('-s', '--shell-escape', action='store_true', default=False,
                            help='Shell escape for htlatex/make4ht')
        parser.add_argument('-r', '--rcfile', action='store', type=str, dest='rcfile',
                            default='', help='Set rcfile')
        parser.add_argument('--make4ht', action='store', type=str, dest='make4ht_options', default=settings['make4ht'],
                            help='Options for make4ht'
        )
        parser.add_argument('--webquiz_format', action='store', type=str, dest='webquiz_format',
                            default=settings['webquiz_format'],
                            help='Local python code for generating the quiz web page'
        )

        # options suppressed from the help message
        parser.add_argument('--version', action = 'version', version = '%(prog)s {}'.format(metadata.version), help = argparse.SUPPRESS)
        parser.add_argument('--debugging', action = 'store_true', default = False, help = argparse.SUPPRESS)

        # parse the options
        options      = parser.parse_args()
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
            settings.list_settings( options.setting )
            sys.exit()

        # initialise and exit
        if options.edit_settings:
            settings.edit_settings()
            sys.exit()

        # if no filename then exit
        if options.quiz_file==[]:
            parser.print_help()
            sys.exit(1)

        # import the local page formatter
        mod_dir, mod_format = os.path.split(options.webquiz_format)
        if mod_dir !='':
            sys.path.insert(0, mod_dir)
        options.write_web_page = __import__(mod_format).write_web_page

        # run() is a shorthand for executing system commands depending on the quietness
        #       - we need to use shell=True because otherwise pst2pdf gives an error
        # talk() is a shorthand for letting the user know what is happening
        if options.quiet == 0:
            run  = lambda cmd: subprocess.call(cmd, shell=True)
            talk = lambda msg: print(msg)
        elif options.quiet == 1:
            run  = lambda cmd: subprocess.call(cmd, shell=True, stdout=open(os.devnull, 'wb'))
            talk = lambda msg: print(msg)
        else:
            run  = lambda cmd: subprocess.call(cmd, shell=True, stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'))
            talk = lambda msg: None


        # run through the list of quizzes and make them
        for quiz_file in options.quiz_file:
            if len(options.quiz_file)>1 and options.quiet<3:
                print('Making web page for {}'.format(quiz_file))
            # quiz_file is assumed to be a tex file if no extension is given
            if not '.' in quiz_file:
                quiz_file += '.tex'

            if not os.path.isfile(quiz_file):
                print('WebQuiz error: cannot read file {}'.format(quiz_file))

            else:

                quiz_name = quiz_file # the quiz name and the quiz_file will be if pst2pdf is used
                if options.quiet<2:
                    print('WebQuiz generating web page for {}'.format( quiz_file))

                # set options.pst2pdf = True if pst2pdf is given as an option to the webquiz documentclass
                with codecs.open(quiz_file, 'r', encoding='utf8') as q_file:
                    doc = q_file.read()

                options.pst2pdf = False
                try:
                    brac = doc.index(r'\documentclass[') + 15 # start of class options
                    if 'pst2pdf' in [ opt.strip() for opt in doc[brac:brac+doc[brac:].index(']')].split(',')]:
                        preprocess_with_pst2pdf( quiz_file[:-4] )
                        options.pst2pdf = True
                        quiz_file = quiz_file[:-4] + '-pdf-fixed.tex' # now run webquiz on modified tex file
                except ValueError:
                    pass

                # the file exists and is readable so make the quiz
                MakeWebQuiz(quiz_name, quiz_file, options, settings)

                quiz_name = quiz_name[:quiz_name.index('.')]  # remove the extension

                # move the css file into the directory for the quiz
                css_file = os.path.join(quiz_name, quiz_name+'.css')
                if os.path.isfile(quiz_name +'.css'):
                    if os.path.isfile(css_file):
                        os.remove(css_file)
                    shutil.move(quiz_name+'.css', css_file)

                # now clean up unless debugging
                if not options.debugging:
                    for ext in [ '4ct', '4tc', 'dvi', 'idv', 'lg', 'log', 'ps', 'pdf', 'tmp', 'xml', 'xref']:
                        if os.path.isfile(quiz_name +'.' +ext):
                            os.remove(quiz_name +'.' +ext)

                    # files created when using pst2pdf
                    if options.pst2pdf:
                        for file in glob.glob(quiz_name+'-pdf.*'):
                            os.remove(file)
                        for file in glob.glob(quiz_name+'-pdf-fixed.*'):
                            os.remove(file)
                        for extra in ['.preamble', '.plog', '-tmp.tex', '-pst.tex', '-fig.tex']:
                            if os.path.isfile(quiz_name+extra):
                                os.remove(quiz_name+extra)
                        if os.path.isdir(os.path.join(quiz_name, quiz_name)):
                            shutil.rmtree(os.path.join(quiz_name, quiz_name))

        if settings.initialise_warning != '':
            print(text_initialise_warning)

    except Exception as err:
        WebQuizError('unknown problem.\n\nIf you think this is a bug please report it by creating an issue at\n    {}\n'.format(
                       metadata.repository) , err
        )
