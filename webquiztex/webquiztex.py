#!/usr/bin/env python3
r'''
------------------------------------------------------------------------------
    webquiztex | Online quizzes generated from LaTeX using python and TeX4ht
               | This module mainly deals with command-line options and
               | settings and then calls MakeWebQuiz to build the quiz
------------------------------------------------------------------------------
    Copyright (C) Andrew Mathas and Donald Taylor, University of Sydney

    Distributed under the terms of the GNU General Public License (GPL)
                  http://www.gnu.org/licenses/

    This file is part of the WebQuizTeX system.

    <Andrew.Mathas@sydney.edu.au>
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

# imports of webquizTeX code
import webquiztex_templates
from webquiztex_makequiz import MakeWebQuiz
from webquiztex_util import copytree, debugging, kpsewhich, webquiztex_error, webquiztex_file, MetaData

#################################################################################
# read in basic meta data such as author, version, ... and set debugging=False

try:
    metadata = MetaData(kpsewhich('webquiztex.ini'), debugging=False)
except subprocess.CalledProcessError:
    print('webquiztex installation error: unable to find webquiztex.ini')
    sys.exit(1)

# ---------------------------------------------------------------------------------------
def graceful_exit(sig, frame):
    ''' exit gracefully on SIGINT and SIGTERM'''
    if metadata:
        webquiztex_error('program terminated (signal {}\n  {})'.format(
            sig, frame))
    else:
        webquiztex_error('program terminated (signal {})'.format(sig))

signal.signal(signal.SIGINT, graceful_exit)
signal.signal(signal.SIGTERM, graceful_exit)


#################################################################################
def preprocess_with_pst2pdf(options, quiz_file):
    r'''
    Preprocess the latex file using pst2pdf. As we are preprocessing the file it
    is not enough to have latex pass us a flag that tells us to use pst2pdf.
    Instead, we have to extract the class file option from the tex file

    INPUT: quiz_file should be the name of the quiz file, WITHOUT the .tex extension
    '''
    options.talk('Preprocessing {} with pst2pdsf'.format(quiz_file))
    try:
        # pst2pdf converts pspicture environments to svg images and makes a
        # new latex file quiz_file+'-pdf' that includes these
        cmd = 'pst2pdf --svg --imgdir={q_file} {q_file}.tex'.format(q_file=quiz_file)
        options.run(cmd)
    except OSError as err:
        if err.errno == errno.ENOENT:
            webquiztex_error(
                'pst2pdf not found. You need to install pst2pdf to use the pst2pdf option',
                err
            )
        else:
            webquiztex_error('error running pst2pdf on {}'.format(quiz_file), err)

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
        webquiztex_error(
            'there was an problem running pst2pdf for {}'.format(quiz_file),
            err
        )

class WebQuizTeXSettings:
    r'''
    Class for initialising webquiztex. This covers both reading and writting
    the webquizrc file and copying files into the web directories during
    initialisation. The settings themselves are stored in attribute settings,
    which is a dictionary. The class reads and writes the settings to the
    webquizrc file and the values of the settings are available as items:
        >>> mq = WebQuizTeXSettings()
        >>> mq['webquiztex_url']
        ... /WebQuizTeX
        >>> mq['webquiztex_url'] = '/new_url'
    '''

    # default of settings for the webquizrc file - a dictionary of dictionaries
    # the 'help' field is for printing descriptions of the settings to help the
    # user - they are also printed in the webquizrc file
    settings = dict(
        webquiztex_url={
            'default': '',
            'advanced': False,
            'help': 'Relative URL for the webquiztex web directory',
        },
        webquiztex_www={
            'default': '',
            'advanced': False,
            'help': 'Full path to WebQuizTeX web directory',
        },
        language={
            'default': 'english',
            'advanced': False,
            'help': 'Default language used on web pages'
        },
        engine = {
            'default': 'latex',
            'advanced': False,
            'help': 'Default TeX engine used to compile web pages',
            'values': dict(latex='', lua='--lua', xelatex='--xetex')
        },
        theme={
            'default': 'default',
            'advanced': False,
            'help': 'Default colour theme used on web pages'
        },
        breadcrumbs={
            'default': '',
            'advanced': False,
            'help': 'Breadcrumbs at the top of quiz page',
        },
        department={
            'default': '',
            'advanced': False,
            'help': 'Name of department',
        },
        department_url={
            'default': '/',
            'advanced': False,
            'help': 'URL for department',
        },
        institution={
            'default': '',
            'advanced': False,
            'help': 'Institution or university',
        },
        institution_url={
            'default': '/',
            'advanced': False,
            'help': 'URL for institution or university',
        },
        hide_side_menu={
            'default': 'false',
            'advanced': False,
            'help': 'Do not display the side menu at start of quiz',
        },
        one_page={
            'default': 'false',
            'advanced': False,
            'help': 'Display questions on one page',
        },
        random_order={
            'default': 'false',
            'advanced': False,
            'help': 'Randomly order the quiz questions',
        },
        webquiztex_layout={
            'default': 'webquiztex_layout',
            'advanced': True,
            'help': 'Name of python module that formats the quizzes',
        },
        make4ht={
            'default': '',
            'advanced': True,
            'help': 'Build file for make4ht',
        },
        mathjax={
            'default':
            'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js',
            'advanced':
            True,
            'help':
            'URL for mathjax',
        },
        version={
            'advanced': False,
            'help': 'WebQuizTeX version number for webquizrc settings',
        })

    # to stop execution from command-line options after initialised() has been called
    just_initialised = False

    def __init__(self):
        '''
        First read the system webquizrc file and then read the
        to use some system settings and to override others.

        By default, there is no webquiztex initialisation file. We first
        look for webquizrc in the webquiztex source directory and then
        for .webquizrc file in the users home directory.
        '''
        self.settings['version']['default'] = metadata.version
        for key in self.settings:
            self.settings[key]['value'] = self.settings[key]['default']
            if not 'editable' in self.settings[key]:
                self.settings[key]['editable'] = False

        # define user and system rc file and load the ones that exist

        self.system_rc_file = os.path.join(kpsewhich('-var TEXMFLOCAL'),
                                           'scripts',
                                           'webquiztex',
                                           'webquiztexrc'
        )
        self.read_webquizrc(self.system_rc_file)

        # the user rc file defaults to:
        #   ~/.dotfiles/config/webquizrc if .dotfiles/config exists
        #   ~/.config/webquizrc if .config exists
        # and otherwise to ~/.webquizrc
        if os.path.isdir(os.path.join(os.path.expanduser('~'), '.dotfiles', 'config')):
            self.user_rc_file = os.path.join(os.path.expanduser('~'), '.dotfiles', 'config', 'webquizrc')
        elif os.path.isdir(os.path.join(os.path.expanduser('~'), '.config')):
            self.user_rc_file = os.path.join(os.path.expanduser('~'), '.config', 'webquizrc')
        else:
            self.user_rc_file = os.path.join(os.path.expanduser('~'), '.webquizrc')

        self.read_webquizrc(self.user_rc_file)

        # if webquiztex_url is empty then assume that we need to initialise
        self.initialise_warning = ''
        if self['webquiztex_url'] == '':
            self.initialise_warning = webquiztex_templates.web_initialise_warning
            initialise = input(webquiztex_templates.initialise_invite)
            if initialise == '' or initialise.strip().lower()[0] == 'y':
                self['webquiztex_url'] = '/WebQuizTeX'
                self.initialise_webquiztex()
            else:
                self['webquiztex_url'] = 'http://www.maths.usyd.edu.au/u/mathas/WebQuizTeX'

    def Debugging(self, msg):
        r'''
            Customised debugging message for the MakeSettings module
        '''
        debugging(self.settings.debugging, 'Make settings error: ', msg)

    def __getitem__(self, key):
        r'''
        Return the value of the corresponding setting. That is, it returns
            self.settings[key]['value']
        and an error if the key is unknown.
        '''
        if key in self.settings:
            return self.settings[key]['value']

        webquiztex_error('getitem: unknown setting "{}" in webquizrc.'.format(key))

    def __setitem__(self, key, value):
        r'''
        Set the value of the corresponding setting. This is the equivalent of
            self.settings[key]['value'] = value
        and an error if the key is unknown.
        '''
        if key in self.settings:
            self.settings[key]['value'] = value
        else:
            webquiztex_error('setitem: unknown setting "{}" in webquizrc'.format(key))

    def read_webquizrc(self, rc_file, must_exist=False):
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
                            key = key.strip().lower().replace('-','_')
                            value = value.strip()
                            if key in self.settings:
                                if value != self[key]:
                                    self[key] = value
                            elif key != '':
                                webquiztex_error('unknown setting "{}" in {}'.format(
                                    key, rc_file))

                # record the rc_file for later use
                self.rc_file = rc_file

            except OSError as err:
                webquiztex_error('there was a problem reading the rc-file {}'.format(
                              rc_file), err)

            except Exception as err:
                webquiztex_error('there was an error reading the webquizrc file,', err)

        elif must_exist:
            # this is only an error if we have been asked to read this file
            webquiztex_error('the rc-file "{}" does not exist'.format(rc_file))

    def keys(self):
        r'''
        Return a list of keys for all settings, ordered alphabetically with the
        advanced options last/
        '''
        return sorted(self.settings.keys(), key=lambda k: '{}{}'.format(self.settings[k]['advanced'], k))

    def write_webquizrc(self):
        r'''
        Write the settings to the webquizrc file, defaulting to the user
        rc_file if unable to write to the system rc_file
        '''
        if not hasattr(self, 'rc_file'):
            # when initialising an rc_file will not exist yet
            self.rc_file = self.system_rc_file

        debugging('Writing to rcfile {}'.format(self.rc_file))
        file_not_written = True
        while file_not_written:
            try:
                dire = os.path.dirname(self.rc_file)
                if dire != '' and not os.path.isdir(dire):
                    os.makedirs(dire, exist_ok=True)
                with codecs.open(self.rc_file, 'w', encoding='utf8') as rcfile:
                    for key in self.keys():
                        # Only save settings in the rcfile if they have changed
                        # Note that changed means changed from the last read
                        # rcfile rather than from the default (of course, the
                        # defaults serve as the "initial rcfile")
                        if key == 'version' or self.settings[key]['default']!=self[key]:
                            debugging('Writing {}={} to rcfile={}'.format(key, self[key], self.rc_file))
                            rcfile.write('# {}\n{:<17} = {}\n'.format(
                                           self.settings[key]['help'],
                                           key.replace('_','-'),
                                           self[key])
                            )

                print('\nWebQuizTeX settings saved in {}\n'.format( self.rc_file))
                input('Press return to continue... ')
                file_not_written = False

            except (OSError, PermissionError) as err:
                # if writing to the system_rc_file then try to write to user_rc_file
                alt_rc_file = self.user_rc_file if self.rc_file != self.user_rc_file else self.system_rc_file
                response = input(
                    webquiztex_templates.rc_permission_error.format(
                        error=err,
                        rc_file=self.rc_file,
                        alt_rc_file=alt_rc_file))
                if response.startswith('2'):
                    self.rc_file = alt_rc_file
                elif response.startswith('3'):
                    rc_file = input('WebQuizTeX rc-file: ')
                    print('\nTo access this rc-file you will need to use: webquiztex --rcfile {} ...'.format(rc_file))
                    self.rc_file = os.path.expanduser(rc_file)
                elif not response.startswith('1'):
                    print('exiting...')
                    sys.exit(1)

    def list_settings(self, setting='all'):
        r'''
        Print the non-default settings for webquiztex from the webquizrc
        '''
        if not hasattr(self, 'rc_file'):
            print(
                'Please initialise WebQuizTeX using the command: webquiztex --initialise\n'
            )

        if setting not in ['all', 'verbose', 'help']:
            setting = setting.replace('-', '_')
            if setting in self.settings:
                print(self.settings[setting]['value'])
            else:
                webquiztex_error('{} is an invalid setting'.format(setting))

        elif setting=='all':
            dash = '-'*len('WebQuizTeX rc-file: {}'.format(self.rc_file))
            print('{dash}\nWebQuizTeX rc-file: {rcfile}\n{dash}'.format(rcfile=self.rc_file, dash=dash))
            for key in self.keys():
                print('{:<17} = {}'.format(key.replace('_', '-'), self[key]))
            print('{dash}'.format(dash=dash))

        elif setting=='help':
            for key in self.keys():
                print('{:<17} {}'.format(key.replace('_', '-'), self.settings[key]['help'].lower()))

        else:
            print('WebQuizTeX settings from {}'.format(self.rc_file))
            for key in self.keys():
                print('# {}{}\n{:<17} = {:<17}  {}'.format(
                        self.settings[key]['help'],
                        ' (advanced)' if self.settings[key]['advanced'] else '',
                        key.replace('_', '-'),
                        self[key],
                        '(default)' if self[key]==self.settings[key]['default'] else ''
                        )
                )

    def initialise_webquiztex(self):
        r'''
        Set the root for the WebQuizTeX web directory and copy the www files into
        this directory. Once this is done save the settings to webquizrc.
        This method should only be used when WebQuizTeX is being set up.
        '''
        if self.just_initialised:  # stop initialising twice with webquiztex --initialise
            return

        # prompt for directory and copy files - are these reasonable defaults
        # for each OS?
        elif sys.platform == 'darwin':
            default_root = '/Library/WebServer/Documents/WebQuizTeX'
            platform = 'Mac OSX'
        elif sys.platform.startswith('win'):
            default_root = ' c:\inetpub\wwwroot\WebQuizTeX'
            platform = 'Windows'
        else:
            default_root = '/var/www/html/WebQuizTeX'
            platform = sys.platform.capitalize()

        if self['webquiztex_www'] != '':
            webquiztex_root = self['webquiztex_www']
        else:
            webquiztex_root = default_root

        print(webquiztex_templates.initialise_introduction)
        input('Press return to continue... ')

        print(webquiztex_templates.webroot_request.format(
                platform=platform,
                webquiztex_dir = webquiztex_root)
        )
        input('Press return to continue... ')

        files_copied = False
        while not files_copied:
            web_dir = input('\nWebQuizTeX web directory:\n[{}] '.format(webquiztex_root))
            if web_dir == '':
                web_dir = webquiztex_root
            else:
                web_dir = os.path.expanduser(web_dir)

            print('Web directory set to {}'.format(web_dir))
            if web_dir == 'SMS':
                # undocumented: allow links to SMS web pages
                self['webquiztex_www'] = 'SMS'
                self['webquiztex_url'] = 'http://www.maths.usyd.edu.au/u/mathas/WebQuizTeX'

            else:
                try:
                    # ...remove the doc directory
                    web_doc = os.path.join(web_dir, 'doc')
                    if os.path.isfile(web_doc) or os.path.islink(web_doc):
                        os.remove(web_doc)
                    elif os.path.isdir(web_doc):
                        shutil.rmtree(web_doc)

                    if os.path.isdir(webquiztex_file('www')):
                        # if the www directory exists then copy it to web_dir
                        print('\nCopying web files to {} ...\n'.format(web_dir))
                        copytree(webquiztex_file('www'), web_dir)
                    else:
                        # get the root directory of the source code
                        webquiztex_src = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

                        # assume this is a development version and add links
                        # from the web directory to the parent directory
                        print('\nLinking web files {} -> {} ...\n'.format(web_dir, webquiztex_src))
                        if not os.path.exists(web_dir):
                            os.makedirs(web_dir)

                        for (src, target) in [('javascript', 'js'), ('css', 'css'), ('doc', 'doc')]:
                            newlink = os.path.join(web_dir, target)
                            try:
                                os.remove(newlink)
                            except FileNotFoundError:
                                pass
                            os.symlink(os.path.join(webquiztex_src,src), newlink)

                    self['webquiztex_www'] = web_dir
                    files_copied = True

                except PermissionError:
                    print(webquiztex_templates.permission_error.format(web_dir))

                except OSError as err:
                    print(webquiztex_templates.oserror_copying.format(web_dir=web_dir, err=err))

        if self['webquiztex_www'] != 'SMS':
            # now prompt for the relative url
            mq_url = input(webquiztex_templates.webquiztex_url_message.format(self['webquiztex_url']))
            if mq_url != '':
                # removing trailing slashes from mq_url
                while mq_url[-1] == '/':
                    mq_url = mq_url[:len(mq_url) - 1]

                if mq_url[0] != '/':  # force URL to start with /
                    print("  ** prepending '/' to webquiztex_url **")
                    mq_url = '/' + mq_url

                if not web_dir.endswith(mq_url):
                    print(webquiztex_templates.webquiztex_url_warning)
                    input('Press return to continue... ')

                self['webquiztex_url'] = mq_url

        # save the settings and exit
        self.write_webquizrc()
        print(webquiztex_templates.initialise_ending.format(web_dir=self['webquiztex_www']))
        self.just_initialised = True

    def edit_settings(self):
        r'''
        Change current default values for the WebQuizTeX settings
        '''
        advanced_not_started = True
        for key in self.keys():
            if key not in ['webquiztex_www', 'version']:
                if advanced_not_started and self.settings[key]['advanced']:
                    print(webquiztex_templates.advanced_settings)
                    advanced_not_started = False

                skey = '{}'.format(self[key])
                setting = input('{}{}[{}]: '.format(
                                    self.settings[key]['help'],
                                    ' ' if len(skey)<40 else '\n',
                                    skey
                          )
                ).strip()
                if setting != '':
                    if key == 'webquiztex_url' and setting[0] != '/':
                        print("  ** prepending '/' to webquiztex_url **")
                        setting = '/' + setting

                    elif key == 'webquiztex_layout':
                        setting = os.path.expanduser(setting)
                        if setting.endswith('.py'):
                            print("  ** removing .py extension from webquiztex_layout **")
                            setting = setting[:-3]

                    elif key == 'engine' and setting not in self.settings['engine'].values:
                        print('setting not changed: {} is not a valid TeX engine'.format(setting))
                        setting = self['engine']

                    elif key in ['hide_side_menu', 'random_order']:
                        setting = setting.lower()
                        if setting not in ['true', 'false']:
                            print('setting not changed: {} must be True or False'.format(key))
                            setting = self[key]

                    elif setting=='NONE':
                        setting = ''

                    self[key] = setting

        # save the settings, print them and exit
        self.write_webquizrc()
        self.list_settings()

    def uninstall_webquiztex(self):
        r'''
        Remove all of the webquiztex files from the webserver
        '''

        if os.path.isdir(self['webquiztex_www']):
            remove = input('Do you really want to remove the WebQuizTeX from your web server [N/yes]? ')
            if remove != 'yes':
                print('WebQuizTeX unistall aborted!')
                return

            try:
                shutil.rmtree(self['webquiztex_www'])
                print('WebquizTeX files successfully removed from {}'.format(self['webquiztex_www']))

            except OSError as err:
                webquiztex_error('There was a problem removing webquiztex files from {}'.format(self['webquiztex_www']), err)

            # now reset and save the locations of the webquiztex files and URL
            self['webquiztex_url'] = ''
            self['webquiztex_www'] = ''
            self.write_webquizrc()

        else:
            webquiztex_error('uninstall: no webwquiz files are installed on your web server??')


# =====================================================
if __name__ == '__main__':
    try:
        settings = WebQuizTeXSettings()
        if settings.just_initialised:
            sys.exit()

        # parse the command line options
        parser = argparse.ArgumentParser(description=metadata.description)

        parser.add_argument(
            'quiz_file',
            nargs='*',
            type=str,
            default=None,
            help='latex quiz files')

        parser.add_argument(
            '-q',
            '--quiet',
            action='count',
            default=0,
            help='Suppress tex4ht messages (also -qq etc)')

        parser.add_argument(
            '-d', '--draft',
            action='store_true',
            default=False,
            help='Use make4ht draft mode')

        parser.add_argument(
            '-s',
            '--shell-escape',
            action='store_true',
            default=False,
            help='Shell escape for tex4ht/make4ht')

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

        parser.add_argument(
            '-r',
            '--rcfile',
            action='store',
            default=None,
            help='Specify location of the webquiztex rc-file ')

        settings_parser = parser.add_mutually_exclusive_group()
        settings_parser.add_argument(
            '-i',
            '--initialise',
            action='store_true',
            default=False,
            help='Install web components of webquiztex')
        settings_parser.add_argument(
            '-e', '--edit-settings',
            action='store_true',
            default=False,
            help='Edit default settings for webquiztex')
        settings_parser.add_argument(
            '--settings',
            action='store',
            const='all',
            default='',
            nargs='?',
            type=str,
            help='List default settings for webquiztex'
        )

        # options suppressed from the help message
        parser.add_argument(
            '-m',
            '--make4ht',
            action='store',
            type=str,
            dest='make4ht_options',
            default=settings['make4ht'],
            help=argparse.SUPPRESS
        )

        parser.add_argument(
            '--webquiztex_layout',
            action='store',
            type=str,
            dest='webquiztex_layout',
            default=settings['webquiztex_layout'],
            help=argparse.SUPPRESS
        )

        parser.add_argument(
            '--uninstall',
            action='store_true',
            default=False,
            help=argparse.SUPPRESS
        )

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
        settings.debugging = options.debugging

        # read the rcfile and throw an error if we are not adjusting the settings
        if options.rcfile is not None:
            rcfile = os.path.expanduser(options.rcfile)
            if options.initialise or options.edit_settings:
                settings.read_webquizrc(rcfile, must_exist=False)
                settings.rc_file = rcfile
            else:
                settings.read_webquizrc(rcfile, must_exist=True)

        # initialise and exit
        if options.initialise:
            settings.initialise_webquiztex()
            sys.exit()

        # list settings and exit
        if options.settings != '':
            settings.list_settings(options.settings)
            sys.exit()

        # edit settings and exit
        if options.edit_settings:
            settings.edit_settings()
            sys.exit()

        # uninstall and exit
        if options.uninstall:
            settings.uninstall_webquiztex()
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
        mod_dir, mod_layout = os.path.split(options.webquiztex_layout)
        if mod_dir != '':
            sys.path.insert(0, mod_dir)
        options.write_web_page = __import__(mod_layout).write_web_page

        # run() is a shorthand for executing system commands depending on the quietness
        #       - we need to use shell=True because otherwise pst2pdf gives an error
        # options.talk() is a shorthand for letting the user know what is happening
        if options.quiet == 0:
            options.run = lambda cmd: subprocess.call(cmd, shell=True)
            options.talk = lambda msg: print(msg)
        elif options.quiet == 1:
            options.run  = lambda cmd: subprocess.call(cmd, shell=True, stdout=open(os.devnull, 'wb'))
            options.talk = lambda msg: print(msg)
        else:
            options.run  = lambda cmd: subprocess.call(cmd, shell=True, stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'))
            options.talk = lambda msg: None

        # run through the list of quizzes and make them
        for quiz_file in options.quiz_file:
            if len(options.quiz_file) > 1 and options.quiet < 3:
                print('Making web page for {}'.format(quiz_file))
            # quiz_file is assumed to be a tex file if no extension is given
            if not '.' in quiz_file:
                quiz_file += '.tex'

            if not os.path.isfile(quiz_file):
                print('WebQuizTeX error: cannot read file {}'.format(quiz_file))

            else:

                # the quiz name and the quiz_file will be if pst2pdf is used
                quiz_name = quiz_file
                if options.quiet < 2:
                    print('WebQuizTeX generating web page for {}'.format(quiz_file))

                # If the pst2podf option is used then we need to preprocess
                # the latex file BEFORE passing it to MakeWebQuiz. Set
                # options.pst2pdf = True if pst2pdf is given as an option to
                # the webquiztex documentclass
                with codecs.open(quiz_file, 'r', encoding='utf8') as q_file:
                    doc = q_file.read()

                options.pst2pdf = False
                try:
                    brac = doc.index(r'\documentclass[') + 15  # start of class options
                    if 'pst2pdf' in [
                            opt.strip()
                            for opt in doc[brac:brac+doc[brac:].index(']')].split(',')
                    ]:
                        preprocess_with_pst2pdf(options, quiz_file[:-4])
                        options.pst2pdf = True
                        # now run webquiztex on the modified tex file
                        quiz_file = quiz_file[:-4] + '-pdf-fixed.tex'  
                except ValueError:
                    pass

                # the file exists and is readable so make the quiz
                MakeWebQuiz(quiz_name, quiz_file, options, settings, metadata)

                quiz_name = quiz_name[:quiz_name.index('.')]  # remove the extension

                # move the css file into the directory for the quiz
                css_file = os.path.join(quiz_name, quiz_name + '.css')
                if os.path.isfile(quiz_name + '.css'):
                    if os.path.isfile(css_file):
                        os.remove(css_file)
                    shutil.move(quiz_name + '.css', css_file)

                # now clean up unless debugging
                if not options.debugging:
                    for ext in ['4ct', '4tc', 'dvi', 'idv', 'lg', 'log',
                        'ps', 'pdf', 'tmp', 'xml', 'xref'
                    ]:
                        if os.path.isfile(quiz_name + '.' + ext):
                            os.remove(quiz_name + '.' + ext)

                    # files created when using pst2pdf
                    if options.pst2pdf:
                        for file in glob.glob(quiz_name + '-pdf.*'):
                            os.remove(file)
                        for file in glob.glob(quiz_name + '-pdf-fixed.*'):
                            os.remove(file)
                        for extention in ['.preamble', '.plog', '-tmp.tex',
                                '-pst.tex', '-fig.tex'
                        ]:
                            if os.path.isfile(quiz_name + extention):
                                os.remove(quiz_name + extention)
                        if os.path.isdir(os.path.join(quiz_name, quiz_name)):
                            shutil.rmtree(os.path.join(quiz_name, quiz_name))

        if settings.initialise_warning != '':
            print(webquiztex_templates.text_initialise_warning)

    except Exception as err:
        webquiztex_error(
            'unknown problem.\n\nIf you think this is a bug please report it by creating an issue at\n    {}\n'
            .format(metadata.repository), err)
