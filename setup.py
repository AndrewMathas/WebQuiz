# -*- encoding: utf-8 -*-

r'''
-----------------------------------------------------------------------------------------
    setup | webquiz setuptools configuration
-----------------------------------------------------------------------------------------
    Copyright (C) Andrew Mathas, University of Sydney

    Distributed under the terms of the GNU General Public License (GPL)
                  http://www.gnu.org/licenses/

    This file is part of the WebQuiz system.

    <Andrew.Mathas@sydney.edu.au>
-----------------------------------------------------------------------------------------
'''

# ctan: python setup.py ctan --> create zup file for upload to ctan )

import glob
import os
import subprocess
import sys
import zipfile

from setuptools import setup, find_packages, Command
from webquiz.webquiz_util import kpsewhich

class MetaData(dict):
    r"""
    A dummy class for reading and storing key-value pairs that are read from a file
    """
    def __init__(self, filename):
        with open(filename,'r') as meta:
            for line in meta:
                key, val = line.split('=')
                if len(key.strip())>0:
                    setattr(self, key.strip().lower(), val.strip())

settings = MetaData('latex/webquiz.ini')

class WebQuizDevelop(Command):
    r"""
    Custom develop command to install links for latex code
    and for the web files.
    """

    description = 'Setup links for latex files and web files for code development'
    user_options = []

    def ask(self, message, default):
        r'''
        Prompt the user for input using the message `message` and with default
        `default` and return the result.
        '''
        value = input('\n{}{}[{}] '.format(message,
                                         '\n' if len(message)>50 else ' ',
                                         default)
        ).strip()
        return default if value=='' else value

    def run(self):
        r'''
        Install links for the latex files, executable and web files
        '''
        texmflocal = kpsewhich('-var TEXMFLOCAL')
        cwd = os.path.dirname(os.path.realpath(__file__))

        try:

            # add a link to the latex files
            texdir = self.ask('Install links to latex files in directory', texmflocal)
            webquiz_tex = os.path.join(texdir,'tex', 'webquiz')
            if os.path.exists(webquiz_tex):
                print('Not installing tex files as {} already exists'.format(webquiz_tex))
            else:
                os.symlink(os.path.join(cwd,'latex'), webquiz_tex)

                # update the tex search paths if not installed in home directory
                subprocess.call('mktexlsr '+webquiz_tex, shell=True)

            # add a link from /usr/local/bin/webquiz to executable
            bindir = self.ask('Directory for executable', '/usr/local/bin')
            webquiz = os.path.join(bindir, 'webquiz')

            if os.path.exists(webquiz):
                print('Not installing executable as {} already exists'.format(webquiz_tex))
            else:
                os.symlink(os.path.join(cwd,'webquiz','webquiz.py'), webquiz)

            # now add links for web files
            subprocess.call('{} --initialise'.format(webquiz), shell=True)

        except PermissionError as err:
            print('Insufficient permissions. Try running using sudo')
            raise err

        except OSError as err:
            print('There was a problem copying files or adding links')
            raise err

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

class WebQuizCtan(Command):
    r"""
    Create TDS zip file for submission to ctan/texlive.
    """

    description = 'Build and publish the package.'
    user_options = []

    ctan_data = {
        'contribution' : settings.program,
             'version' : settings.version,
                'name' : settings.authors,
               'email' : settings.author_email,
             'summary' : settings.description,
           'directory' : '/scripts/webquiz, tex/latex/webquiz and doc/latex/webquiz',
            'announce' : settings.description,
               'notes' : 'See README file in tex/latex/webquiz',
             'license' : 'free',
         'freeversion' : 'gpl',
                'file' : 'webquiz.zip',
    }

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # write the zip file for uploading to ctan
        self.write_zip_file()

        # upload the zip file to ctan using ctanupload
        subprocess.call('ctanupload -v {options}'.format(
                options = ' '.join('--{}="{}"'.format(key, val) for key,val in self.ctan_data.items())
            ),
            shell=True
        )

    def shell_command(self, cmd):
        r'''
        Run the system command `cmd` and print any output to stdout indented
        by two spaces.
        '''
        print('Executing {}'.format(cmd))
        for line in  subprocess.getoutput(cmd).split('\n'):
            if line.strip() != '':
                print('  {}'.format(line.rstrip()))

    def build_files_for_zipping(self):
        r'''
        Rebuilds the documentation files and css for inclusion in the zip file:
            - doc/webquiz-manual.tex
            - doc/webquiz.tex
            - css/webquiz-*.css
        to ensure that they are correct for the ctan upload. We need to make
        webquiz-manual.pdf first because it is included in webquiz.pdf.
        '''
        # auto generate all of the data used in the manual and build the manuals
        makedoc = input('Run makedoc [Y/n]? ')
        if makedoc.lower() != 'n':
            self.shell_command('doc/makedoc --all --fast')

        try:
            os.remove('javasript/webquiz-min.js')
        except OSError:
            pass
        # minify the javascript code
        self.shell_command('cd javascript && uglifyjs --output webquiz-min.js --compress sequences=true,conditionals=true,booleans=true  webquiz.js ')

    def write_zip_file(self):
        r'''
        Create a zip file for webquiz that can be uploaded to ctan. To do
        this we use the zipfile module to write the zopfile with all files in
        their expected places.
        '''
        # if the ctan directory already exists then delete it
        try:
            os.remove('webquiz.zip')
        except OSError:
            pass

        self.build_files_for_zipping()

        # save the files as a TDS (Tex directory standard) zip file
        with zipfile.ZipFile('webquiz.zip', 'w', zipfile.ZIP_DEFLATED) as zfile:

            # now add the files
            for (src, target) in [ ('README.md',                       ''),
                                   ('LICENCE',                         'scripts'),
                                   ('CHANGES.rst',                     'scripts'),
                                   ('css/webquiz-*.css',               'scripts/www/css'),
                                   ('doc/webquiz*.pdf',                'doc'),
                                   ('doc/webquiz*.tex',                'doc'),
                                   ('doc/webquiz-online-manual.tex',   'scripts/www/doc'),
                                   ('doc/webquiz.languages',           'doc'),
                                   ('doc/webquiz.settings',            'doc'),
                                   ('doc/webquiz.themes',              'doc'),
                                   ('doc/webquiz.usage',               'doc'),
                                   ('doc/examples/[-a-z]*.png',        'doc/examples'),
                                   ('doc/examples/*.tex',              'scripts/www/doc/examples'),
                                   ('doc/examples/README-examples',    'scripts/www/doc/examples'),
                                   ('doc/README-doc',                  'doc'),
                                   ('javascript/webquiz-min.js',       'scripts/www/webquiz.js'),
                                   ('latex/pgfsys-dvisvgm4ht.def',     'latex'),
                                   ('latex/webquiz.ini',               'latex'),
                                   ('latex/webquiz-*.lang',            'latex'),
                                   ('latex/webquiz.c*',                'latex'),
                                   ('latex/webquiz-*.code.tex',        'latex'),
                                   ('webquiz/webquiz*.py',             'scripts'),
                                   ('webquiz/webquiz.bat',             'scripts'),
                                   ('webquiz/README-scripts',          'scripts'),
                ]:
                for file in glob.glob(src):
                    if '.' in target:
                        zfile.write(file, os.path.join('webquiz', target))
                    else:
                        zfile.write(file, os.path.join('webquiz', target, file.split('/')[-1]))


#----------------------------------------------------------------------------------------
setup(name             = settings.program,
      version          = settings.version,
      description      = settings.description,
      long_description = open('README.md').read(),
      long_description_content_type='text/markdown',
      url              = settings.url,
      author           = settings.authors,
      author_email     = settings.author_email,

      keywords         = 'web quizzes, latex, mathematics',

      packages=find_packages(),
      include_package_data=True,
      package_data     = {'webfiles' : '/'},

      cmdclass         = {'ctan': WebQuizCtan, 'develop': WebQuizDevelop},

      provides         = 'webquiz',
      entry_points     = { 'console_scripts': [ 'webquiz=webquiz.webquiz:main' ], },

      license          = settings.licence,

      classifiers      = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Education',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Education :: Testing',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Scientific/Engineering',
        'Topic :: Text Processing :: Markup :: HTML',
        'Topic :: Text Processing :: Markup :: LaTeX',
        'Topic :: Text Processing :: Markup :: XML',
      ]
)
