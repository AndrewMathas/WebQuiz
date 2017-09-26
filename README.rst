MathQuiz: on-line quizzes using LaTeX_
======================================

MathQuiz_ makes it possible to use LaTeX to write interactive web based
quizzes. The quizzes are first written in LaTeX and then converted into
HTML files using MathQuiz_, which is written in python. The conversion
from LaTeX to HTML is done behind the scenes using TeX4ht_.

To use MathQuiz_ you need to have the following programs installed:
    * LaTeX_
    * TeX4ht_ (available with latest distribution of texlive_, for example)
    * Python_ (python3)

Once the system is installed, MathQuiz_ is used directly from the
command line. For example, if quiz1.tex is a latex file for a quiz then:
    * latex quiz1         produces a "readable" dvi file for the quiz
    * pdflatex quiz1      produces a "readable" pdf file for the quiz
    * mathquiz quiz1      creates the web page quiz1.html

Installation
------------

MathQuiz_ has three different components that need to be installed:

 - LaTeX files: mathquiz.cls and mathquiz.cfg need to be in the LaTeX
   search path
 - python files: the main python is mathquiz.py. On unix systems create
   a link to it using something like
       ln -s <path to mathquiz directory>/mathquiz.py /usr/local/bin/mathquiz
 - web files: although not strictly necessary, the files in the scripts 
   web directory www should be put on the local web server

Once MathQuiz_ is available from ctan only the web files will need to be
installed and this can be done using the command:

    mathquiz --initialise

MathQuiz_ will still work if the web files are not installed locally,
however, the quiz pages will display a warning message. For more details
about installation, configuration and use please see the MathQuiz_ manual
and the MathQuiz_ on-line manual.

Distrubution
------------

To organisation of the the code in the MathQuiz_ repository is not suitable 
for distribution. To upload the package to ctan use:

    python3 setup.py ctan


Authors
=======

The LaTeX component of MathQuiz_ was written by Andrew Mathas and
the python, css and javascript code was written by Andrew Mathas (and
Don Taylor), based on an initial protype of Don Taylor's from 2001.
Since 2004 the program has been maintained and developed by Andrew
Mathas. Although the program has changed substantially since 2004 some
of Don's code and his idea of using TeX 4ht are still very much in use.

Copyright (C) 2004-2017

GNU General Public License, Version 3, 29 June 2007

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU_General Public License (GPL_) as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

.. _GPL: https://www.gnu.org/licenses/gpl-3.0.en.html
.. _LaTeX: https://www.latex-project.org/
.. _MathQuiz: https://bitbucket.org/AndrewsBucket/mathquiz
.. _Python: https://www.python.org
.. _TeX4ht: http://www.tug.org/tex4ht/
.. _texlive: https://www.tug.org/texlive/
