## -*- encoding: utf-8 -*-

"""
MathQuiz: write on-line quizzes using LaTeX
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

import os, glob, shutil, sys
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
from setuptools.command.develop import develop
from setuptools.command.install import install
import subprocess
import zipfile
#from codecs import open

class MathQuizConfigure(object):
    '''
    This class, which is now largely redundant, was written to streamline the
    uploading of mathquiz to pypi. Rather than using this, the class
    MathQuizCtan defined below can be used to upload mathquiz to ctan, which
    is a better place to host mathquiz because latex and friends are an
    essential dependency.
    '''

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
        self.read_mathquizrc()

        print(install_introduction)
        self.copy_or_link_directories(linking = action=='develop')

        # overkill as there is currently only one!
        for var in self.variables:
            message = globals()[var+'_message']
            self.mathquizrc[var] = self.read_input(var, message)

        if not self.dry_run:
            self.write_mathquizrc()

    def dry_command(self, command, message):
        r'''
        Print `message` and execute `command` unless self.dry_run is true.
        '''
        print(message)
        if not self.dry_run:
            command

    def read_input(self, var, message):
        va = input(message.format(self.mathquizrc[var]))
        print('{} --> |{}|: {}'.format(var, va,len(va)))
        return va.strip() if len(va)>0 else self.mathquizrc[var]

    def copy_or_link_directories(self, linking):
        r'''
        Using `message`, with the `default`, prompt the user for the directory
        to copy tyhe files to and then create it, if it does not exist, and
        copy all of the files in the `directories` to the target directory. If
        something goes wrong then prompt again and repeat until all of the files are copied.
        Finally, return the target directory name.
        '''
        for dir in self.directories:
            files_copied = False
            message = globals()[dir+'_message']
            target_dir = self.read_input(dir, message)
            while not files_copied:
                try:
                    # first delete existing directory or link if it exists
                    if os.path.isdir(target_dir):
                        shutil.rmtree(target_dir)
                    if os.path.islink(target_dir):
                        os.unlink(target_dir)
                    # now copy or link
                    if len(self.directories[dir]) == 1:
                        if linking:
                            self.dry_command(os.symlink(dir, target_dir),
                                             'Linking: {} -> {}'.format(target_dir, dir))
                        else:
                            self.dry_command(shutil.copytree(dir, target_dir),
                                             'Copying: {} -> {}'.format(dir, target_dir))
                    else:
                        if linking:
                            os.symlink(os.path.curdir, target_dir)
                        else:
                            os.mkdir(target)
                            for d in self.directories[dir]:
                                shutil.copytree(dir, os.path.join(target_dir, d))
                    files_copied = True
                except Exception as err:
                    sys.stderr.write('There was a problem copying files to {}.\n  Please give a new directory.\n[Error: {}]\n'.format(target_dir, err))
                    message = message.split('\n')[-1]  # truncate the message to the request for the directory
                    target_dir = self.read_input(dir, message)
            self.mathquizrc[dir] = target_dir

    def read_mathquizrc(self):
        r'''
        Read the settings in the mathquizrc file into `self.mathquizrc`.
        '''
        self.mathquizrc = {}
        try:
            with open('mathquizrc','r') as mathquizrc:
                for line in mathquizrc:
                    key,val = line.split('=')
                    if len(key.strip())>0:
                        self.mathquizrc[key.strip().lower()] = val.strip()
        except Exception as err:
            sys.stderr.write('There was an error reading the mathquizrc file\n  {}'.format(err))
            sys.exit(1)

    def write_mathquizrc(self):
        r'''
        Write the settings in self.mathquizrc to the mathquizrc file.
        '''
        try:
            with open('mathquizrc','w') as mathquizrc:
                mathquizrc.write('\n'.join('{:<14} = {}'.format(key, val) for (key, val) in self.mathquizrc))
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


class MathQuizCtan(build_py):
    r"""
    Create TDS zip file for submission to ctan/texlive.

    It is necessary to subclass setuptools.command but, in fact, we do not use
    anything from setuptools.
    """
    ctanupload_data = {
        'contribution' : 'mathquiz',
             'version' : '5.0',
                'name' : 'Andrew Mathas',
               'email' : 'andrew.mathas@sydney.edu.au',
             'summary' : 'Write on-line quizzes using latex',
           'directory' : '/scripts/mathquiz, tex/latex/mathquiz and doc/latex/mathquiz',
            'announce' : 'A latex system for writing on-line quizzes',
               'notes' : 'TDS zipfile. See README file in tex/latex/mathquiz',
             'license' : 'free',
         'freeversion' : 'gpl',
                'file' : 'mathquiz.zip',
    }
    # (source target) pairs for directories to be copied
    def run(self):
        # write the zip file for uploading to ctan
        self.write_zip_file()

        # upload the zip file to ctan using ctanupload
        subprocess.call('ctanupload -v {options}'.format(
             options = ' '.join('--{}="{}"'.format(key, val) for (key, val) in self.ctanupload_data.items())
        ), shell = True)

    def write_zip_file(self):
        r'''
        Create a  TDS (Tex directory standard) zip file for mathquiz.
        For this we use the zipfile module to write the zopfile with all files
        in their expected places.
        '''
        # if the ctan directory already exists then delete it
        if os.path.isfile('mathquiz.zip'):
            os.remove('mathquiz.zip')

        # save the files as a TDS (Tex directory standard) zip file
        with zipfile.ZipFile('mathquiz.zip', 'w', zipfile.ZIP_DEFLATED) as zfile:

            # now add the files
            for (src, target) in [ ('README.rst', ''),
                                   ('latex/mathquiz.*', 'tex/latex/mathquiz'),
                                   ('doc/mathquiz.{tex,pdf}', 'doc'),
                                   ('mathquiz/mathquiz*.py', 'scripts/mathquiz'),
                                   ('javascript/mathquiz.js', 'scripts/www'),
                                   ('css/mathquiz.css', 'scripts/www'),
                                   ('doc/mathquiz-manual.tex', 'scripts/mathquiz/www/doc'),
                                   ('LICENCE', 'scripts'),
                                  ]:
                for file in glob.glob(src):
                    zfile.write(file, os.path.join('mathquiz', target, file.split('/')[-1]))


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
                          'develop': MathQuizDevelop,
                          'ctan'   : MathQuizCtan
                         },

      entry_points     = { 'console_scripts': [ 'mathquiz=mathquiz.mathquiz:main' ], },

      license          = 'GNU General Public License, Version 3, 29 June 2007',
      classifiers      = [
        'Development Status :: 5 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
      ]
)
