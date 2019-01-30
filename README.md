WebQuiz: on-line quizzes using [LaTeX](https://www.latex-project.org/)
=======================================================================

`WebQuiz` makes it
possible to use LaTeX to write interactive web based quizzes. The
quizzes are first written in LaTeX and then converted into HTML files
using `WebQuiz`, which is
written in python. The conversion from LaTeX to HTML is done behind the
scenes using [TeX4ht](http://www.tug.org/tex4ht/).

To use `WebQuiz` you need 
to have the following programs installed:

    -   [LaTeX](https://www.latex-project.org/)
    -   [TeX4ht](http://www.tug.org/tex4ht/) (available with latest
        distribution of [texlive](https://www.tug.org/texlive/), for
        example)
    -   [Python](https://www.python.org) (python3)

`WebQuiz` is designed to be used from the command-line.
For example, if `quiz1.tex` is a LaTeX file for a quiz then: 
* `latex quiz1` produces a "readable" dvi file for the quiz 
* `pdflatex quiz1` produces a "readable" pdf file for the quiz
* `webquiz quiz1` creates the web page quiz1.html

Installation
------------

`WebQuiz` has three
different components that need to be installed:

- LaTeX files: all of the files in the `latex` directory, such as webquiz.cls and 
  webquiz.cfg, need to be in the LaTeX search path
- python files: the main python file is webquiz.py. On unix systems
  create a link to it using something like:

        ln -s <path to webquiz directory>/webquiz.py /usr/local/bin/webquiz

- web files: although not strictly necessary, the files in the css and
  javascript direcxtories need to be placed on local web server

Once `WebQuiz` is available from ctan only the web files will need to be
installed, which can be done using the command:

> webquiz --initialise

For more details about installation, configuration and use please see the
`WebQuiz` manual and the `WebQuiz` on-line manual.

Distribution
------------

To organisation of the code in the `WebQuiz` repository is not suitable for
distribution to ctan. To upload the package to ctan use:

> python3 setup.py ctan

To set up the system for development:

> python3 setup.py develop

Authors
=======

The LaTeX component of `WebQuiz` was written by Andrew Mathas and the python,
css and javascript code was written by Andrew Mathas (and Don Taylor), based on
an initial protype of Don Taylor's from 2001. Since 2004 the program has been
maintained and developed by Andrew Mathas. Although the program has changed
substantially since 2004 Don's idea of using TeX 4ht, and some of his code, are
still very much in use.

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
