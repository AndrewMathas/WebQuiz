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

# Update distribution on pypi: python setup.py sdist upload -r pypi
# Install: python setup.py develop
# Develop mode : python setup.py develop
# Create build : python setup.py build

import os, shutil, sys
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

latex_directory_message='''Please enter the directory, or folder name, where the MathQuiz LaTeX class
should go. This should be a directory that is automatically searched by
(pdf)latex such as
    /usr/local/texlive/texmf-local/tex/latex/mathquiz
or a directory listed in the TEXINPUTS environment variable on unix systems.

Latex directory [{}]: '''

web_directory_message='''MathQuiz needs to install javascript and css files on the web sever. You can put these
files into your own web directory or in a system directory. Possible system directories
include:
     /Library/WebServer/Documents/MathQuiz     (for mac os x)
     /usr/local/httpd/MathQuiz                 (SuSE unix)
     /var/www/MathQuiz                         (other flavours of unix)
     /usr/local/apache2/MathQuiz               (some apache configurations)
     c:\inetpub\wwwroot\MathQuiz               (windows?)
It is recommended that you have a separate directory for MathQuiz files.

MathQuiz web directory [{}]: '''

mathquiz_url_message='''Finally, pleaswe give the *relative* URL for the MathQuiz web directory.
In all of the examples above the root would be /MathQuiz

MathQuiz relative URL [{}]: '''

class MathQuizConfigure(object):

    # list of directories that need to be copied/linked
    directories = {
        'latex_directory' : ['latex'],
        'web_directory'   : ['css', 'doc', 'javascript']
    }

    # list of variables that need to be set
    variables = ['mathquiz_url']

    def __init__(self, action, dry_run):
        r'''
        Prompt for the local configuration settings and install system files
        '''
        self.dry_run = dry_run

        # read in the settings
        self.read_mathquiz_rc()

        print(install_introduction)
        self.copy_or_link_directories(linking = action=='develop')

        # overkill as there is currently only one!
        for var in self.variables:
            message = globals()[var+'_message']
            self.mathquiz_rc[var] = input(message.format(self.mathquiz_rc[var]))

        if not self.dry_run:
            self.write_mathquiz_rc()

    def copy_or_link_directories(self, linking):
        r'''
        Using `message`, with the `default`, prompt the user for the directory
        to copy tyhe files to and then create it, if it does not exist, and
        copy all of the files in the `directories` to the target directory. If
        something goes wrong then prompt again and repeat until all of the files are copied.
        Finally, return the target directory name.
        '''
        for dir in self.directories:
            files_copied = self.dry_run
            message = globals()[dir+'_message']
            target_dir = input(message.format(self.mathquiz_rc[dir]))
            while not files_copied:
                try:
                    # first delete existinbg directory or link if it exists
                    if os.path.isdir(target_dir):
                        shutil.rmtree(target_dir)
                    if os.path.islink(target_dir):
                        os.unlink(target_dir)
                    # now copy or link
                    if len(directories[dir]) == 1:
                        if linking:
                            os.symlink(dir, target_dir)
                        else:
                            shutil.copytree(dir, target_dir)
                    else:
                        if linking:
                            os.symlink(os.path.curdir, target_dir)
                        else:
                            os.mkdir(target)
                            for d in self.directories[dir]:
                                shutil.copytree(dir, os.path.join(target_dir, d))
                except Exception as err:
                    sys.stderr.write('There was a problem copying files to {}.  Please give a new directory.'.format(target_dir))
                    message = message.split('\n')[-1]  # truncate the message to the request for the directory
                    target_dir = input(message.format(self.mathquiz_rc[dir]))
            self.mathquiz_rc[dir] = target_dir

    def read_mathquiz_rc(self):
        r'''
        Read the settings in the mathquiz_rc file into `self.mathquiz_rc`.
        '''
        self.mathquiz_rc = {}
        try:
            with open('mathquizrc','r') as mathquizrc:
                for line in mathquizrc:
                    key,val = line.split('=')
                    if len(key.strip())>0:
                        self.mathquiz_rc[key.strip().lower()] = val.strip()
        except Exception as err:
            sys.stderr.write('There was an error reading the mathquizrc file\n  {}'.format(err))
            sys.exit(1)

    def write_mathquiz_rc(self):
        r'''
        Write the settings in self.mathquiz_rc to the mathquiz_rc file.
        '''
        try:
            with open('mathquizrc','w') as mathquizrc:
                mathquiz_rc.write('\n'.join('{:<14} = {}'.format(key, val) for (key, val) in self.mathquiz_rc))
        except Exception as err:
            sys.stderr.write('There was an error reading the mathquizrc file\n  {}'.format(err))
            sys.exit(1)


class MathQuizInstall(install):
    r"""
    We customise the install class in order to be able to determine the
    location of the system files and then copy everything to tyhe right 
    place.
    """
    def run(self):
        install.run(self)
        MathQuizConfigure('install', self.dry_run)

class MathQuizDevelop(develop):
    r"""
    We customise the install class in order to be able to determine the
    location of the system files and then copy everything to tyhe right 
    place.
    """
    def run(self):
        develop.run(self)
        MathQuizConfigure('develop', self.dry_run)


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
