## -*- encoding: utf-8 -*-

"""
This package implements a way of writing on-line quizzes using latex.
"""

#################################################################################
#
# (c) Copyright 2016 Andrew Mathas
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

import os
import sys
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.test import test as TestCommand
from codecs import open

here = os.path.abspath(os.path.dirname(__file__))

class MathQuizInstall(install):
    r"""
    We custom install class in order to be able to dynamically set the 
    location of the web directory.
    """
    def run(self):
        install.run(self)


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

      cmdclass         = {'install': MathQuizInstall},
      entry_points     = { 'console_scripts': [ 'mathquiz=mathquiz.mathquiz:main' ], },

      license          = 'GNU General Public License, Version 3, 29 June 2007',
      classifiers      = [
        'Development Status :: 5 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
      ]
)

# To update run
# python setup.py sdist upload -r pypi
