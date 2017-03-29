
MathQuiz: on-line quizzes using _LaTeX
======================================

MathQuiz is a system for writing interactive web based quizzes, particularly
those that involve mathematics. The quizzes are first written in LaTeX and
then converted into HTML files using MathQuiz, which is written in python. The
conversion from LaTeX to HTML is done behind the scenes using TeX4ht.

To use the system you will need to have all of the following programs installed:
    * LaTeX_
    * TeX4ht_ (available with latest distribution of texlive_, for example)
    * Python_ 

Once the system is installed, MathQuiz is used directly from the
command line. For example, if quiz1.tex is a latex file for a quiz then:
    * latex quiz1         produces a "readable" dvi file for the quiz
    * pdflatex quiz1      produces a "readable" pdf file for the quiz
    * mathquiz quiz1      creates the web page quiz1.html


Installation
------------

MathQuiz has several different components which need to be installed into quite
different places. First, decide where you want to put the source files for MathQuiz.
This will either be in somewhere in your home directory, or something like
/usr/local/src if you want to install the system for general use. This directory
should NOT be accessible from your web server. 

Change to this directory and unpack the tar file mathquiz.tgz using 
    tar zxf mathquiz.tgz
This will create a directory called mathquiz in your current directory which contains
the files:
    README    -  this file
    latex/    -  the latex class file for running mathquiz
    mathquiz  -  the shell script that runs mathquiz
    src/      -  contains the python scripts for writing the web pages
    web/      -  contains the java script, css and image files needed by MathQuiz

To complete the installation of MathQuiz on your system you need to:
    1. Copy, or move, the directory into the directories used by your web server. This
       can either be in your own directories or in the "system" web directories. For this
       you would do something like
           cp -R web /<path to top of web server>/MathQuiz
       In particular, I recommend renaming this directory MathQuiz when you copy it and
       not calling it web!

    2. Copy, or move, the file latex/mathquiz.cls into the directories searched by latex.
       Again this can be in your own directories (in Unix you can tell tex which
       directories to search using the TEXINPUTS environment variable. If mathquiz.cls is 
       installed in a system directory then everyone will be able to use MathQuiz. 

    3. Edit the script mathquiz. At the top of the script you will find two variables:
        o MathQuizSRC = directory where you unpacked mathquiz.tgz
        o MathQuizURL = relative URL for the MathQuiz on your web server. This is the 
              URL pointing to the files in the directory web/ above. Note that this is a
              relative URL and not the full path to a directory. To access these files 
              from your browser you would go to
                http://your.web.server/<MathQuizURL>/

    4. Move the script mathquiz to somewhere in your path like /usr/local/bin.

MathQuiz should now be ready to use. To test it change to the directory on your web
server which contains the files in the directory web/ above. This directory contains
a doc directory and inside this directory you will find the file mathquiz-manual.tex
which is the documentation for using MathQuiz. You should now be able to:
    o latex mathquiz-manual     - produce a dvi version of the manual for printing
    o mathquiz mathquiz-manual  - create the web pages for the online version of the
        manual which you will be able to access by going to 
          http://your.web.server/<MathQuizURL>/doc/mathquiz-manual.html

Local configuration
-------------------

The "style" of the online quizzes is controlled by the file src/mathquizLocal.py. If you want to
change this format of the quiz pages then the easiest way to do this is to make a copy of 
mathquizLocal.py, say to mathquizMyStyle.py, and then edit this file directly. To see what the 
new style looks like you can run the mathquiz script with an optional argument which tells
mathquiz to use your style instead:
    mathquiz -l mathquizMyStyle quizfile.tex
Using mathquiz to regenerate the html files is quite time consuming, so while you are editting this
file you will find it easier if you ask mathquiz not to delete the intermediate files that it
creates each time. To do this first run mathquiz with the -x option and thereafter use -f:
    mathquiz -l mathquizMyStyle -x quizfile.tex    # tells MathQuiz not to delete intermediate files
    mathquiz -l mathquizMyStyle -f quizfile.tex    # "fast" option when intermediate files exist
Once the new page format is finalized it can be made the default by setting
    MathQuizOptions="--local=mathquizMyStyle"
at the top of the mathquiz shell script.

The easiest way to change mathquizLocal.py is simply to edit the "decorating" html that this file puts
around the quiz page. You may also need to change the CSS style sheet for mathquiz which is the file
web/mathquiz.css. More sophisticated versions of mathquizLocal.py where you change the underlying
python code are of course possible. For example, at the Unviersity of Sydney our version of this file
calls our content management system directly and uses this to create the web page for the quiz.

From a terminal, run the command:

    pip install mathquiz

and then follow the command promnpts to set the location of the web and latex
directories. See the MathQuiz_ manual for more information.

Author
======

MathQuiz_ is based on an ititial prototype that was written by Don Taylor in
2001. Since 2004 the program has been maintained and developed by Andrew
Mathas. Some of the initial code remains but quite a
`Andrew Mathas`_

Copyright (C) 2013-2017

GNU General Public License, Version 3, 29 June 2007

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU_General Public License (GPL_) as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

.. _`Andrew Mathas`: http://www.maths.usyd.edu.au/u/mathas/
.. _GPL: https://www.gnu.org/licenses/gpl-3.0.en.html
.. _LaTeX: https://www.latex-project.org/
.. _MathQuiz: http://www.maths.usyd.edu.au/u/MOW/MathQuiz/doc/mathquiz-manual.html
.. _Python: https://www.python.org
.. _TeX4ht: http://www.tug.org/tex4ht/
.. _texlive: https://www.tug.org/texlive/
