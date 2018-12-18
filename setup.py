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

settings = MetaData('webquiz.ini')

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
        for css_file in glob.glob('webquiz-*.scss'):
            self.shell_command('sass --style compress {} {}.css'.format(css_file, css_file[:-4]))
        # auto generate all of the data used in the manual and build the manuals
        self.shell_command('cd doc && ./makedoc --fast --make-manual')

    def write_zip_file(self):
        r'''
        Create a zip file for webquiz that can be uploaded to ctan. To do
        this we use the zipfile module to write the zopfile with all files in
        their expected places.
        '''
        # if the ctan directory already exists then delete it
        if os.path.isfile('webquiz.zip'):
            os.remove('webquiz.zip')

        self.build_files_for_zipping()

        # save the files as a TDS (Tex directory standard) zip file
        with zipfile.ZipFile('webquiz.zip', 'w', zipfile.ZIP_DEFLATED) as zfile:

            # now add the files
            for (src, target) in [ ('README.md',                       ''),
                                   ('LICENCE',                         'scripts'),
                                   ('css/webquiz-*.css',               'scripts/www/css'),
                                   ('doc/webquiz*.pdf',                'doc'),
                                   ('doc/webquiz*.tex',                'doc'),
                                   ('doc/webquiz-online-manual.tex',   'scripts/www/doc'),
                                   ('doc/webquiz.languages',           'doc'),
                                   ('doc/webquiz.settings',            'doc'),
                                   ('doc/webquiz.themes',              'doc'),
                                   ('doc/webquiz.usage',               'doc'),
                                   ('doc/examples/*.png',              'doc/examples'),
                                   ('doc/examples/*.tex',              'scripts/www/doc/examples'),
                                   ('javascript/webquiz.js',           'scripts/www'),
                                   ('latex/pgfsys-tex4ht-mq-fixed.def','latex'),
                                   ('latex/webquiz-*.lang',            'latex'),
                                   ('latex/webquiz-doc.sty',           'latex'),
                                   ('latex/webquiz.c*',                'latex'),
                                   ('webquiz.ini',                     'latex'),
                                   ('webquiz.ini',                     'scripts'),
                                   ('webquiz/webquiz*.py',             'scripts'),
                                   ('webquiz/webquiz.bat',             'scripts'),
                ]:
                for file in glob.glob(src):
                    print('{} --> {}'.format(file, target if target !='' else '.'))
                    zfile.write(file, os.path.join('webquiz', target, file.split('/')[-1]))

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

      cmdclass         = {'ctan'   : WebQuizCtan },

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
