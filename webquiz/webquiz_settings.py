#!/usr/bin/env python3
r'''
------------------------------------------------------------------------------
    webquiz_settings | process web quiz settings
------------------------------------------------------------------------------
    Copyright (C) Andrew Mathas, University of Sydney

    Distributed under the terms of the GNU General Public License (GPL)
                  http://www.gnu.org/licenses/

    This file is part of the WebQuiz system.

    <Andrew.Mathas@sydney.edu.au>
    <Donald.Taylor@sydney.edu.au>
------------------------------------------------------------------------------
'''

import codecs
import glob
import os
import shutil
import sys

# imports of webquiz code
import webquiz_util
import webquiz_templates
from webquiz_util import copytree, metadata, webquiz_error, webquiz_file

class WebQuizSettings:
    r'''
    Class for initialising webquiz. This covers both reading and writting the webquizrc file and
    copying files into the web directories during initialisation. The settings
    themselves are stored in attribute settings, which is a dictionary. The
    class reads and writes the settings to the webquizrc file and the
    values of the settings are available as items:
        >>> mq = WebQuizSettings()
        >>> mq['webquiz_url']
        ... /WebQuiz
        >>> mq['webquiz_url'] = '/new_url'
    '''

    # default of settings for the webquizrc file - a dictionary of dictionaries
    # the 'help' field is for printing descriptions of the settings to help the
    # user - they are also printed in the webquizrc file
    settings = dict(
        webquiz_url={
            'default': '',
            'advanced': False,
            'help': 'Relative URL for webquiz web directory',
        },
        webquiz_www={
            'default': '',
            'advanced': False,
            'help': 'Full path to WebQuiz web directory',
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
        webquiz_layout={
            'default': 'webquiz_layout',
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
            'help': 'WebQuiz version number for webquizrc settings',
        })

    # to stop execution from command-line options after initialised() has been called
    just_initialise = False

    def __init__(self):
        '''
        First read the system webquizrc file and then read the
        to use some system settings and to override others.

        By default, there is no webquiz initialisation file. We first
        look for webquizrc in the webquiz source directory and then
        for .webquizrc file in the users home directory.
        '''
        self.settings['version']['default'] = metadata.version,
        for key in self.settings:
            self.settings[key]['value'] = self.settings[key]['default']
            self.settings[key]['changed'] = False
            if not 'editable' in self.settings[key]:
                self.settings[key]['editable'] = False

        # define user and system rc file and load the ones that exist

        self.system_rc_file = webquiz_file('webquizrc')
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
        if os.path.isfile(self.user_rc_file):
            self.read_webquizrc(self.user_rc_file)

        # if webquiz_url is empty then assume that we need to initialise
        self.initialise_warning = ''
        if self['webquiz_url'] == '':
            self['webquiz_url'] = 'http://www.maths.usyd.edu.au/u/mathas/WebQuiz'
            self.initialise_warning = webquiz_templates.web_initialise_warning
            initialise = input(webquiz_templates.initialise_invite)
            if initialise == '' or initialise.strip().lower()[0] == 'y':
                self.initialise_webquiz()

    def __getitem__(self, key):
        r'''
        Return the value of the corresponding setting. That is, it returns
            self.settings[key]['value']
        and an error if the key is unknown.
        '''
        if key in self.settings:
            return self.settings[key]['value']

        webquiz_error('(get) unknown setting "{}" in webquizrc.'.format(key))

    def __setitem__(self, key, value):
        r'''
        Set the value of the corresponding setting. This is the equivalent of
            self.settings[key]['value'] = value
        and an error if the key is unknown.
        '''
        if key in self.settings:
            self.settings[key]['value'] = value
        else:
            webquiz_error('(set) unknown setting "{}" in webquizrc'.format(key))

    def read_webquizrc(self, rc_file, external=False):
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
                                    self.settings[key]['changed'] = True
                            elif key != '':
                                webquiz_error('unknown setting "{}" in {}'.format(
                                    key, rc_file))

                # record the rc_file for later use
                self.rc_file = rc_file

            except OSError as err:
                webquiz_error(
                    'there was a problem reading the rc-file {}'.format(
                        rc_file), err)

            except Exception as err:
                webquiz_error('there was an error reading the webquizrc file,',
                             err)

        elif external:
            # this is only an error if we have been asked to read this file
            webquiz_error('the rc-file {} does not exist'.format(rc_file))

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

        file_not_written = True
        while file_not_written:
            try:
                dire, file = os.path.split(self.rc_file)
                if dire != '' and not os.path.isdir(dire):
                    os.makedirs(dire, exist_ok=True)
                with codecs.open(self.rc_file, 'w', encoding='utf8') as rcfile:
                    for key in self.keys():
                        # Only save settings in the rcfile if they have changed
                        # Note that changed means changed from the last read
                        # rcfile rather than from the default (of course, the
                        # defaults serve as the "initial rcfile")
                        if key == 'version' or self.settings[key]['changed']:
                            rcfile.write('# {}\n{:<15} = {}\n'.format(
                                           self.settings[key]['help'],
                                           key.replace('_','-'),
                                           self[key])
                            )

                print('\nWebQuiz settings saved in {}\n'.format( self.rc_file))
                input('Press return to continue... ')
                file_not_written = False

            except (OSError, PermissionError) as err:
                # if writing to the system_rc_file then try to write to user_rc_file
                alt_rc_file = self.user_rc_file if self.rc_file != self.user_rc_file else self.system_rc_file
                response = input(
                    webquiz_templates.rc_permission_error.format(
                        error=err,
                        rc_file=self.rc_file,
                        alt_rc_file=alt_rc_file))
                if response.startswith('2'):
                    self.rc_file = alt_rc_file
                elif response.startswith('3'):
                    rc_file = input('rc_file: ')
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
            print(
                'Please initialise WebQuiz using the command: webquiz --initialise\n'
            )

        if setting not in ['all', 'verbose', 'help']:
            setting = setting.replace('-', '_')
            if setting in self.settings:
                print(self.settings[setting]['value'])
            else:
                webquiz_error('{} is an invalid setting'.format(setting))

        elif setting=='all':
            print('WebQuiz settings from {}'.format(self.rc_file))
            for key in self.keys():
                print('{:<15} = {}'.format(key.replace('_', '-'), self[key]))

        elif setting=='help':
            for key in self.keys():
                print('{:<15} {}'.format(key.replace('_', '-'), self.settings[key]['help'].lower()))

        else:
            print('WebQuiz settings from {}'.format(self.rc_file))
            for key in self.keys():
                print('# {}{}\n{:<15} = {:<15}  {}'.format(
                        self.settings[key]['help'],
                        ' (advanced)' if self.settings[key]['advanced'] else '',
                        key.replace('_', '-'),
                        self[key],
                        '(default)' if self[key]==self.settings[key]['default'] else ''
                        )
                )

    def initialise_webquiz(self):
        r'''
        Set the root for the WebQuiz web directory and copy the www files into
        this directory. Once this is done save the settings to webquizrc.
        This method should only be used when WebQuiz is being set up.
        '''
        if self.just_initialise:  # stop initialising twice with webquiz --initialise
            return

        # prompt for directory and copy files - are these reasonable defaults
        # for each OS?
        elif sys.platform == 'darwin':
            default_root = '/Library/WebServer/Documents/WebQuiz'
            platform = 'Mac OSX'
        elif sys.platform.startswith('win'):
            default_root = ' c:\inetpub\wwwroot\WebQuiz'
            platform = 'Windows'
        else:
            default_root = '/var/www/html/WebQuiz'
            platform = sys.platform.capitalize()

        if self['webquiz_www'] != '':
            webquiz_root = self['webquiz_www']
        else:
            webquiz_root = default_root

        print(webquiz_templates.initialise_introduction)
        input('Press return to continue... ')

        print(webquiz_templates.webroot_request.format(
                platform=platform,
                webquiz_dir = webquiz_root)
        )
        input('Press return to continue... ')

        files_copied = False
        while not files_copied:
            web_dir = input('\nWebQuiz web directory:\n[{}] '.format(webquiz_root))
            if web_dir == '':
                web_dir = webquiz_root
            else:
                web_dir = os.path.expanduser(web_dir)

            print('Web directory set to {}'.format(web_dir))
            if web_dir == 'SMS':
                # undocumented: allow links to SMS web pages
                self['webquiz_www'] = 'SMS'
                self['webquiz_url'] = 'http://www.maths.usyd.edu.au/u/mathas/WebQuiz'

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

                    if os.path.isdir(webquiz_file('www')):
                        # if the www directory exists then copy it to web_dir
                        print('\nCopying web files to {} ...\n'.format(web_dir))
                        copytree(webquiz_file('www'), web_dir)
                    else:
                        # get the root directory of the source code
                        webquiz_src = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

                        # assume this is a development version and add links
                        # from the web directory to the parent directory
                        print('\nLinking web files {} -> {} ...\n'.format(web_dir, webquiz_src))
                        if not os.path.exists(web_dir):
                            os.makedirs(web_dir)

                        for (src, target) in [('javascript/webquiz.js', 'webquiz.js'),
                                              ('css', 'css'),
                                              ('doc', 'doc')]:
                            newlink = os.path.join(web_dir, target)
                            try:
                                os.remove(newlink)
                            except FileNotFoundError:
                                pass
                            os.symlink(os.path.join(webquiz_src,src), newlink)

                    self['webquiz_www'] = web_dir
                    self.settings['webquiz_www']['changed'] = True
                    files_copied = True

                except PermissionError as err:
                    print(webquiz_templates.permission_error.format(web_dir))

                except OSError as err:
                    print(webquiz_templates.oserror_copying.format(web_dir=web_dir, err=err))

        if self['webquiz_www'] != 'SMS':
            # now prompt for the relative url
            mq_url = input(webquiz_templates.webquiz_url_message.format(self['webquiz_url']))
            if mq_url != '':
                # removing trailing slashes from mq_url
                while mq_url[-1] == '/':
                    mq_url = mq_url[:len(mq_url) - 1]

                if mq_url[0] != '/':  # force URL to start with /
                    print("  ** prepending '/' to webquiz_url **")
                    mq_url = '/' + mq_url

                if not web_dir.endswith(mq_url):
                    print(webquiz_templates.webquiz_url_warning)
                    input('Press return to continue... ')

                self['webquiz_url'] = mq_url

        self.settings['webquiz_url']['changed'] = (self['webquiz_url']!=self.settings['webquiz_url']['default'])

        # save the settings and exit
        self.write_webquizrc()
        print(webquiz_templates.initialise_ending.format(web_dir=self['webquiz_www']))
        self.just_initialise = True

    def edit_settings(self, ignored_settings=['webquiz_www', 'version']):
        r'''
        Change current default values for the WebQuiz settings
        '''
        advanced_not_started = True
        for key in self.keys():
            if key not in ignored_settings:
                if advanced_not_started and self.settings[key]['advanced']:
                    print(webquiz_templates.advanced_settings)
                    advanced_not_started = False

                skey = '{}'.format(self[key])
                setting = input('{}{}[{}]: '.format(
                                    self.settings[key]['help'],
                                    ' ' if len(skey)<40 else '\n',
                                    skey
                          )
                ).strip()
                if setting != '':
                    if key == 'webquiz_url' and setting[0] != '/':
                        print("  ** prepending '/' to webquiz_url **")
                        setting = '/' + setting

                    elif key == 'webquiz_layout':
                        setting = os.path.expanduser(setting)
                        if setting.endswith('.py'):
                            print("  ** removing .py extension from webquiz_layout **")
                            setting = setting[:-3]

                    elif key == 'engine' and setting not in self.settings['engine'].values:
                        print('setting not changed: {} is not a valid TeX engine'.format(setting))
                        setting = self['engine']

                    elif key in ['hide_side_menu', 'random_order']:
                        setting = setting.lower()
                        if setting not in ['true', 'false']:
                            print('setting not changed: {} must be True or False'.format(key))
                            setting = self[key]

                    self[key] = setting
                    self.settings[key]['changed'] = True

        # save the settings, print them and exit
        self.write_webquizrc()
        self.list_settings()

    def uninstall_webquiz(self):
        r'''
        Remove all of the webquiz files from the webserver
        '''

        if os.path.isdir(self['webquiz_www']):
            remove = input('Do you really want to remove the WebQuiz from your web server [N/yes]? ')
            if remove != 'yes':
                print('WebQuiz unistall aborted!')
                return

            try:
                shutil.rmtree(self['webquiz_www'])
                print('Webquiz files successfully removed from {}'.format(self['webquiz_www']))

            except OSError as err:
                webquiz_error('There was a problem removing webquiz files from {}'.format(self['webquiz_www']), err)

            # now reset and save the locations of the webquiz files and URL
            self['webquiz_url'] = ''
            self['webquiz_www'] = ''
            self.write_webquizrc()

        else:
            webquiz_error('uninstall: no webwquiz files are installed on your web server??')

#################################################################################
