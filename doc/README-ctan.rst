.. README file to be distributed with the LaTeX package

============================================
WebQuiz: a LaTeX_ package for online quizzes
============================================

WebQuiz_ makes it possible to use LaTeX_ to write interactive online quizzes.
The quizzes are first written in LaTeX and then converted into HTML using
WebQuiz_, which is written in python. The conversion from LaTeX_ to HTML is
done behind the scenes using TeX4ht_. The idea is that you should be able to
produce nice online quizzes using WebQuiz_ and basic knowledge of LaTeX_.

WebQuiz_ is designed to be used from the command-line.  For example, if
`quiz1.tex` is a LaTeX file for a quiz then:

* `latex quiz1`    produces a "readable" DVI file for the quiz
* `pdflatex quiz1` produces a "readable" PDF file for the quiz
* `webquiz quiz1`  creates the web page `quiz1.html`

If you prefer to use LaTeX_ from a GUI for LaTeX_ then it should be possible to
configure it to use WebQuiz_ directly. As an example, the manual provides some
details about how to do this for TeXShop.

Usage
-----

usage: webquiz [-h] [-q] [-d] [-s] [--latex | -l | -x] [-r RCFILE]
               [-i | -e | --settings [SETTINGS]]
               [quiz_file [quiz_file ...]]

A LaTeX package for writing online quizzes

positional arguments:

  quiz_file             latex quiz files

optional arguments:

  -h, --help            show this help message and exit
  -q, --quiet           Suppress tex4ht messages (also -qq etc)
  -d, --draft           Use make4ht draft mode
  -s, --shell-escape    Shell escape for tex4ht/make4ht
  --latex               Use latex to compile document with make4ht (default)
  -l, --lua             Use lualatex to compile the quiz
  -x, --xelatex         Use xelatex to compile the quiz
  -r RCFILE, --rcfile RCFILE
                        Specify location of the webquiz rc-file
  -i, --initialise      Install web components of webquiz
  -e, --edit-settings   Edit default settings for webquiz
  --settings SETTINGS_  List default settings for webquiz


Installation
------------
To use WebQuiz_ you need to have a standard LaTeX_ distribution installed, such as TeXLive_, that includes TeX4ht_. In addition, you need to have Python3_ installed. As WebQuiz_ uses scalable vector graphics (SVG) you should check that all of the dependencies of dvisvgm_ are installed on your system, especially if you plan on using graphics or images.

Once the WebQuiz_ package has been installed from ctan_ then you can install the web components of WebQuiz_ using the following command, which needs to be run  from the command line:

> webquiz --initialise

If you want to install the web components of WebQuiz_ into a system directory then you need to run this command from an administrators account, so using `sudo` on a unix-like system. For more details about the installation and configuration of WebQuiz_ please see Section 3.2 of the WebQuiz_ manual.

Please see the manual for more details about initialising and using WebQuiz_.

Authors
-------
The LaTeX component of WebQuiz_ was written by Andrew Mathas and the python, css and javascript code was written by Andrew Mathas (and Don Taylor), based on an initial protype of Don Taylor's from 2001. Since 2004 the program has been maintained and developed by Andrew Mathas. Although the program has changed substantially since 2004 Don's idea of using TeX 4ht, and some of his code, are still very much in use.

Copyright (C) 2004-2019

License
-------
GNU General Public License, Version 3, 29 June 2007

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU\_General Public License
(GPL_) as published by
the Free Software Foundation, either version 3 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
Public License for more details.

.. _GPL:      https://www.gnu.org/licenses/gpl-3.0.en.html
.. _LaTeX:    https://www.latex-project.org/
.. _Python3:  https://www.python.org
.. _TeX4ht:   http://www.tug.org/tex4ht/
.. _TeXLive:  https://www.tug.org/texlive/
.. _WebQuiz:  https://github.com/AndrewAtLarge/WebQuiz/
.. _ctan:     https://ctan.org/
.. _dvisvgm:  https://ctan.org/pkg/dvisvgm
