WebQuiz: a [LaTeX][LaTeX] package for on-line quizzes
=======================================================================

[WebQuiz] makes it
possible to use LaTeX to write interactive web based quizzes. The
quizzes are first written in LaTeX and then converted into HTML files
using `WebQuiz`, which is
written in python. The conversion from [LaTeX] to HTML is done behind the
scenes using [TeX4ht].


`WebQuiz` is designed to be used from the command-line.
For example, if `quiz1.tex` is a LaTeX file for a quiz then: 
* `latex quiz1` produces a "readable" dvi file for the quiz 
* `pdflatex quiz1` produces a "readable" pdf file for the quiz
* `webquiz quiz1` creates the web page quiz1.html

Installation
------------
To use [WebQuiz] you need to have a standard [LaTeX] distribution installed, such as [TeXLive], that includes [TeX4ht]. In addition, you need to have [Python3] installed.

The main executable for [WebQuiz] is the python file `webquiz/webquiz.py`.

Once the [WebQuiz] package has been installed from [ctan][ctan] then you can install the web components of [WebQuiz] using the following command, which needs to be run  from the command line:

> webquiz --initialise

If you want to install the web compnents of [WebQuiiz] into a system directory then you need to run this command from an administrators account, so using `sudo` on a unix-like system. For more details about the installation and configuration of [WebQuiz] please see Section 3.2 of the [WebQuiz] manual.

Authors
-------

The LaTeX component of [WebQuiz] was written by Andrew Mathas and the python,
css and javascript code was written by Andrew Mathas (and Don Taylor), based on
an initial protype of Don Taylor's from 2001. Since 2004 the program has been
maintained and developed by Andrew Mathas. Although the program has changed
substantially since 2004 Don's idea of using TeX 4ht, and some of his code, are
still very much in use.

Copyright (C) 2004-2019

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

[LaTeX]:    https://www.latex-project.org/
[Python3]:   https://www.python.org
[TeX4ht]:   http://www.tug.org/tex4ht/
[TeXLive]:  https://www.tug.org/texlive/
[WebQuiz]:  https://www.ctan.org/pkg/webquiz/

