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

from setuptools import setup, find_packages
from setuptools.command.build_py import build_py

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

class WebQuizCtan(build_py):
    r"""
    Create TDS zip file for submission to ctan/texlive.

    It is necessary to subclass setuptools.command.build_py but, in fact,
    we do not use anything from setuptools.
    """
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
            - css/webquiz.css
        to ensure that they are correct for the ctan upload. We need to make
        webquiz-manual.pdf first because it is included in webquiz.pdf.
        '''
        for css_file in glob.glob('webquiz-*.scss'):
            self.shell_command('sass --style compress {} {}.css'.format(css_file, css_file[:-4]))
        self.shell_command('cd doc && ./mklanguages && latex --interaction=batchmode webquiz-online-manual && dvipdf webquiz-online-manual')
        self.shell_command('cd doc && pdflatex --interaction=batchmode webquiz')

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
                                   ('doc/webquiz*.tex',                'doc'),
                                   ('doc/webquiz.lang',                'doc'),
                                   ('doc/webquiz*.pdf',                'doc'),
                                   ('doc/examples/*.png',              'doc/examples'),
                                   ('latex/webquiz.c*',                'latex'),
                                   ('latex/pgfsys-tex4ht-mq-fixed.def','latex'),
                                   ('webquiz.ini',                     'latex'),
                                   ('latex/webquiz-doc.sty',           'latex'),
                                   ('latex/webquiz-*.lang',            'latex'),
                                   ('LICENCE',                         'scripts'),
                                   ('webquiz/webquiz*.py',             'scripts'),
                                   ('webquiz.ini',                     'scripts'),
                                   ('webquiz/webquiz.bat',             'scripts'),
                                   ('css/webquiz-*.css',               'scripts/www'),
                                   ('javascript/webquiz.js',           'scripts/www'),
                                   ('doc/webquiz-online-manual.tex',   'scripts/www/doc'),
                                   ('webquiz.ini',                     'scripts/www/doc'),
                                   ('doc/examples/*.tex',              'scripts/www/doc/examples')
                ]:
                for file in glob.glob(src):
                    print('{} --> {}'.format(file, target))
                    zfile.write(file, os.path.join('webquiz', target, file.split('/')[-1]))

setup(name             = settings.program,
      version          = settings.version,
      desription       = settings.description,
      long_description = open('README.md').read(),
      url              = settings.url,
      author           = settings.authors,
      author_email     = settings.author_email,

      keywords         = 'web quizzes, latex, mathematics',

      packages=find_packages(),
      include_package_data=True,
      package_data     = {'webfiles' : '/'},

      cmdclass         = {'ctan'   : WebQuizCtan },

      entry_points     = { 'console_scripts': [ 'webquiz=webquiz.webquiz:main' ], },

      license          = settings.licence,
      classifiers      = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
      ]
)
