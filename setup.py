## -*- encoding: utf-8 -*-

"""
MathQuiz implements a way of writing on-line quizzes using latex.
"""

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

# To update run
# python setup.py sdist upload -r pypi

import os, sys
from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
from setuptools.command.test import test as TestCommand
from codecs import open

install_introduction='''

--------------------------------------------------------------------------
MathQuiz is a system for writing interactive web quizzes. particularly, for
mathematics. The idea is to separate writing the content of the quizzes from
constructing the more complicated web pages. This is achieved by writing the
quizzes in LaTeX. MathQuiz then converts the LaTeX file to a web page for an
interactive quiz. Under the hood, the quizzes use javascript.

To use MathQuiz you will need to have the following installed on your systems:
  o latex, tex4ht and make4ht (available using texlive, for example)
  o python3
  o javascript
  o an up to date web server

In order for MathQuiz to work the program needs:
  o A (system) directory, searched by LaTeX, in which to install LaTeX class files.
  o A directory on your local file system that is visible from your web server
  o A relative URL to the web directory above.
You will be prompted for each of these directories in turn.

'''

tex_local_message=''' Please enter the directory, or folder name, where the MathQuiz LaTeX class
should go. This should be a directory that is automatically searched by
(pdf)latex such as
    /usr/local/texlive//texmf-local/tex/latex/mathquiz
or a directory listed in the TEXINPUTS environment variable on unix systems.

Latex directory [{tex_local}]: '''

web_directory_message='''MathQuiz needs to install javascript and css files on the web sever. You can put these
files into your own web directory or in a system directory. Possible system directories
include:
     /Library/WebServer/Documents/MathQuiz     (for mac os x)
     /usr/local/httpd/MathQuiz                 (SuSE unix)
     /var/www/MathQuiz                         (other flavours of unix)
     /usr/local/apache2/MathQuiz               (some apache configurations)
     c:\inetpub\wwwroot\MathQuiz               (windows?)
It is recommended that you have a separate directory for MathQuiz files.

MathQuiz web directory [{web_dir}]: '''

web_url_message='''Finally, pleaswe give the *relative* URL for the MathQuiz web directory.
In all of the examples above the root would be /MathQuiz

MathQuiz relative URL [{MathQuizURL}]: '''

class MathQuizConfigure(object):
    r'''
    Prompt for the local configuration settings and install system files
    '''
    def __init__(self, dry_run):
        self.read_defaults()
        sys.stdout.write(install_introduction)
        tex_local = input(tex_local_message)

class MathQuizInstall(install):
    r"""
    We customise the install class in order to be able to determine the
    location of the system files and then copy everything to tyhe right 
    place.
    """
    def run(self):
        install.run(self)
        MathQuizConfigure(self.dry_run)

class MathQuizDevelop(develop):
    r"""
    We customise the install class in order to be able to determine the
    location of the system files and then copy everything to tyhe right 
    place.
    """
    def run(self):
        install.run(self)
        MathQuizConfigure(self.dry_run)


setup(name             = 'MathQuiz',
      version          = '5.0',
      description      = 'Writing online quizzes using latex',
      long_description = open('README.rst').read(),
      url              = 'http://www.maths.usyd.edu.au/u/MOW/MathQuiz/doc/mathquiz-manual.html',
      author           = 'Andrew Mathas',
      author_email     = 'andrew.mathas@sydney.edu.au',

      keywords         = 'web quizzes, latex, mathematics',

      packages=find_packages(),
      include_package_data=True,
      package_data     = {'webfiles' : '/'},

      cmdclass         = {'install': MathQuizInstall,
                          'develop': MathQuizDevelop },

      entry_points     = { 'console_scripts': [ 'mathquiz=mathquiz.mathquiz:main' ], },

      license          = 'GNU General Public License, Version 3, 29 June 2007',
      classifiers      = [
        'Development Status :: 5 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
      ]
)
