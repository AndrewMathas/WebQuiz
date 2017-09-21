# -*- encoding: utf-8 -*-

r'''
-----------------------------------------------------------------------------------------
    setup | mathquiz setuptools configuration
-----------------------------------------------------------------------------------------
    Copyright (C) Andrew Mathas and Donald Taylor, University of Sydney

    Distributed under the terms of the GNU General Public License (GPL)
                  http://www.gnu.org/licenses/

    This file is part of the Math_quiz system.

    <Andrew.Mathas@sydney.edu.au>
    <Donald.Taylor@sydney.edu.au>
-----------------------------------------------------------------------------------------
'''

#################################################################################
#
# (c) Copyright 2017 Andrew Mathas
#
#  This file is part of the MathQuiz package.
#
#  MathQuiz free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MathQuiz distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

# Update distribution on pypi: python setup.py sdist upload -r pypi

# ctan: python setup.py ctan --> create zup file for upload to ctan

import os, glob, sys
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
import subprocess
import zipfile

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

settings = MetaData('mathquiz/mathquiz.ini')

class MathQuizCtan(build_py):
    r"""
    Create TDS zip file for submission to ctan/texlive.

    It is necessary to subclass setuptools.command but, in fact, we do not use
    anything from setuptools.
    """
    ctan_data = {
        'contribution' : settings.program,
             'version' : settings.version,
                'name' : settings.authors,
               'email' : settings.author_email,
             'summary' : settings.description,
           'directory' : '/scripts/mathquiz, tex/latex/mathquiz and doc/latex/mathquiz',
            'announce' : 'A latex system for writing on-line quizzes',
               'notes' : 'TDS zipfile. See README file in tex/latex/mathquiz',
             'license' : 'free',
         'freeversion' : 'gpl',
                'file' : 'mathquiz.zip',
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
            - doc/mathquiz-manual.tex
            - doc/mathquiz.tex
            - css/mathquiz.css
        to ensure that they are correct for the ctan upload. We need to make
        mathquiz-manual.pdf first because it is included in mathquiz.pdf.
        '''
        self.shell_command('cd css && sass mathquiz.scss mathquiz.css')
        self.shell_command('cd doc && latex --interaction=batchmode mathquiz-online-manual && dvipdf mathquiz-online-manual')
        self.shell_command('cd doc && pdflatex --interaction=batchmode mathquiz')

    def write_zip_file(self):
        r'''
        Create a zip file for mathquiz that can be uploaded to ctan. To do
        this we use the zipfile module to write the zopfile with all files in
        their expected places.
        '''
        # if the ctan directory already exists then delete it
        if os.path.isfile('mathquiz.zip'):
            os.remove('mathquiz.zip')

        self.build_files_for_zipping()

        # save the files as a TDS (Tex directory standard) zip file
        with zipfile.ZipFile('mathquiz.zip', 'w', zipfile.ZIP_DEFLATED) as zfile:

            # now add the files
            for (src, target) in [ ('README.rst',                       ''),
                                   ('doc/*.pdf',                        'doc'),
                                   ('doc/*.tex',                        'doc'),
                                   ('mathquiz/mathquiz.ini',            'doc'),
                                   ('doc/examples/*.png',               'doc/examples'),
                                   ('doc/examples/*.tex',               'doc/examples'),
                                   ('latex/mathquiz.c*',                'latex'),
                                   ('latex/pgfsys-tex4ht-mq-fixed.def', 'latex'),
                                   ('doc/mathquiz-doc.sty',             'latex'),
                                   ('LICENCE',                          'scripts'),
                                   ('mathquiz/mathquiz*.py',            'scripts'),
                                   ('mathquiz/mathquiz.ini',            'scripts'),
                                   ('css/mathquiz.css',                 'scripts/www'),
                                   ('javascript/mathquiz.js',           'scripts/www'),
                                   ('doc/mathquiz-online-manual.tex',   'scripts/www/doc'),
                                   ('mathquiz/mathquiz.ini',            'scripts/www/doc'),
                                   ('doc/examples/*.tex',               'scripts/www/doc/examples'),
                                  ]:
                for file in glob.glob(src):
                  if file != 'mathquiz/mathquiz_sms.py':
                    zfile.write(file, os.path.join('mathquiz', target, file.split('/')[-1]))

setup(name             = settings.program,
      version          = settings.version,
      description      = settings.description,
      long_description = open('README.rst').read(),
      url              = settings.url,
      author           = settings.authors,
      author_email     = settings.author_email,

      keywords         = 'web quizzes, latex, mathematics',

      packages=find_packages(),
      include_package_data=True,
      package_data     = {'webfiles' : '/'},

      cmdclass         = {'ctan'   : MathQuizCtan },

      entry_points     = { 'console_scripts': [ 'mathquiz=mathquiz.mathquiz:main' ], },

      license          = settings.licence,
      classifiers      = [
        'Development Status :: 5 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
      ]
)
