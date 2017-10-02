WebQuiz: on-line quizzes using [LaTeX](https://www.latex-project.org/)
=======================================================================

[WebQuiz](https://bitbucket.org/AndrewsBucket/webquiz) makes it
possible to use LaTeX to write interactive web based quizzes. The
quizzes are first written in LaTeX and then converted into HTML files
using [WebQuiz](https://bitbucket.org/AndrewsBucket/webquiz), which is
written in python. The conversion from LaTeX to HTML is done behind the
scenes using [TeX4ht](http://www.tug.org/tex4ht/).

To use [WebQuiz](https://bitbucket.org/AndrewsBucket/webquiz) you need to have the following programs installed:

:   -   [LaTeX](https://www.latex-project.org/)
    -   [TeX4ht](http://www.tug.org/tex4ht/) (available with latest
        distribution of [texlive](https://www.tug.org/texlive/), for
        example)
    -   [Python](https://www.python.org) (python3)

Once the system is installed,
[WebQuiz](https://bitbucket.org/AndrewsBucket/webquiz) is used
directly from the command line. For example, if quiz1.tex is a latex
file for a quiz then: \* latex quiz1 produces a "readable" dvi file for
the quiz \* pdflatex quiz1 produces a "readable" pdf file for the quiz
\* webquiz quiz1 creates the web page quiz1.html

Installation
------------

[WebQuiz](https://bitbucket.org/AndrewsBucket/webquiz) has three
different components that need to be installed:

> -   LaTeX files: webquiz.cls and webquiz.cfg need to be in the LaTeX
>     search path
> -   python files: the main python is webquiz.py. On unix systems
>     create a link to it using something like ln -s &lt;path to
>     webquiz directory&gt;/webquiz.py /usr/local/bin/webquiz
> -   web files: although not strictly necessary, the files in the
>     scripts web directory www should be put on the local web server

Once [WebQuiz](https://bitbucket.org/AndrewsBucket/webquiz) is
available from ctan only the web files will need to be installed and
this can be done using the command:

> webquiz --initialise

[WebQuiz](https://bitbucket.org/AndrewsBucket/webquiz) will still work
if the web files are not installed locally, however, the quiz pages will
display a warning message. For more details about installation,
configuration and use please see the
[WebQuiz](https://bitbucket.org/AndrewsBucket/webquiz) manual and the
[WebQuiz](https://bitbucket.org/AndrewsBucket/webquiz) on-line manual.

Distrubution
------------

To organisation of the the code in the
[WebQuiz](https://bitbucket.org/AndrewsBucket/webquiz) repository is
not suitable for distribution. To upload the package to ctan use:

> python3 setup.py ctan

Authors
=======

The LaTeX component of
[WebQuiz](https://bitbucket.org/AndrewsBucket/webquiz) was written by
Andrew Mathas and the python, css and javascript code was written by
Andrew Mathas (and Don Taylor), based on an initial protype of Don
Taylor's from 2001. Since 2004 the program has been maintained and
developed by Andrew Mathas. Although the program has changed
substantially since 2004 some of Don's code and his idea of using TeX
4ht are still very much in use.

Copyright (C) 2004-2017

GNU General Public License, Version 3, 29 June 2007

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU\_General Public License
([GPL](https://www.gnu.org/licenses/gpl-3.0.en.html)) as published by
the Free Software Foundation, either version 3 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
Public License for more details.
