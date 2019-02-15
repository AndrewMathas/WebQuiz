========
WebQuiz_
========

*This is the development version of* WebQuiz_. *Most users should use* WebQuiz_
*as a standard* LaTeX_ *package by downloading and installing the* WebQuiz_
*package from* ctan_.

WebQuiz_ makes it possible to use LaTeX_ to write interactive web based
quizzes. The quizzes are first written in LaTeX_ and then converted into
HTML files using WebQuiz_, which is written in Python3_. The conversion
from LaTeX_ to HTML is done behind the scenes using TeX4ht_.

WebQuiz_ has the following components:
 - LaTeX_ code that uses TeX4ht_ to generate an XML file
 - Python3_ code that reads the XML file and outputs an HTML file
 - `(S)CSS` for styling the web pages (using sass_)
 - `javascript` for controlling the web pages
 - documentation
 - rudimentary tests

WebQuiz_ relies on having the following programs installed: LaTeX_, TeX4ht_, (available with most LaTeX_
distributions such as TeXLive_), and Python3_. To use the development version,
particularly, for building the manual and uploading to ctan_, you will also need
mogrify_, sass_, uglifyjs_ and webkit2png_ (and ctanupload_ and rst2man_).

This README file explains how the different components of the development
version of WebQuiz_ are organised.

Installing the development version
----------------------------------

First clone or download the `WebQuiz github repository`_.  On a unix-like system,
such as linux or macosx, to set up links for the latex and web files for the
development version run::

    > python3 setup.py develop

In fact, you may want to run this as root, in which case use::

    > sudo python3 setup.py develop

This will add links from, by default, the TEXMFLOCAL directory to the WebQuiz_
latex files, create a link to the WebQuiz_ executable and add a link from a
location on your web server, which you will be prompted for, to the WebQuiz_
CSS and javascript files.  The install process assumes that kpsewhich_ is
installed on your computer. You will now be able to run WebQuiz_, however, to
view the web pages you need to generate the `CSS` files using sass_. On
unix-like systems you can use the `bash` shell-script `doc/makedoc -t`.

The structure of the files in the `WebQuiz github repository`_ is not suitable
for uploading to ctan_.  WebQuiz_ is not distributed as a Python3_ package
because it fits more naturally into the LaTeX_ ecosystem, since LaTeX_ is a hard
dependency for the program (and LaTeX_ cannot be installed with `pip`!).

Python code
-----------
There are six python source files:

webquiz.py
    processes command-line options and settings

webquiz_layout.py
    determines the final layout of the quiz web pages

webquiz_makequiz.py
    converts the XML into HTML

webquiz_templates.py
    template strings for HTML

webquiz_util.py
    utility functions

webquiz_xml.py
    read and interpret the WebQuiz_ XML file


LaTeX code
----------
The LaTeX is in the latex directory. The main components are:

webquiz.cfg
    WebQuiz_ TeX4ht configuration file => generates XML

webquiz.cls
     WebQuiz_ document class file

webquiz.ini
     WebQuiz_ initialisation data. This is used by the LaTeX_ and python components of WebQuiz_

webquiz-doc.code.tex
     macros used in the two WebQuiz_ manuals

webquiz-ini.code.tex
     code for reading and accessing the ini fle in latex

pgfsys-dvisvgm4ht.def
     a custom tikz driver for tex4ht from dvisvgm4ht_ supplied by Michal Hoftich

webquiz-\*.lang
     language support files. These are used by `webquiz_main.py` when writing
     the quiz web pages but we find them by putting them in the LaTeX search
     path

Cascading style sheets
-----------------------
The `CSS` files for WebQuiz_ are written using sass_. The main files are:

 - webquiz.scss
 - webquiz-THEME.scss

The theme files all set the colours and then load the main sass file `webquiz.scss`.
Use the `bash` shell script command::

    > doc/makedoc -t

to generate all of the `CSS` files, together with manual entries for the
themes.


Javascript
----------
There is one javascript file, `webquiz.js`, in the javascript directory. In
addition, the `quizindex` environment generates the javascript file
`quizindex.js`, that generates a drop-down menu for the quizzes in the current
directory. This file is automatically loaded at the end of each quiz HTML file,
if it exits.  For each quiz, WebQuiz_ writes another javascript file,
`wq-file.js`, that specified the questions in the quiz. This file is
automatically loaded by the quiz page.

It would be goods to add some javascript unit tests....

Documentation
-------------
Once WebQuiz_ is installed you can build the documentation for the package
using the `bash` shelll-script::

    > doc/makedoc

This generates the WebQuiz_ `CSS` files and all of the screen shots in the
manual. It requires webkit2png_ and mogrify_.

The main files in the documentation directory are:

webquiz.tex
    LaTeX source for the WebQuiz_ manual

webquiz-online-manual.tex
    LaTeX source for the online WebQuiz_ manual

credits.tex
    LaTeX source for the credits file

makedoc
    bash shell script that automatically generates the many different
    components of the manual. There are various options; use `makedoc -h` to see
    a summary

examples
    directory of WebQuiz_ code snippets that are included in the manual

examples/makeimages
    python script for generating the images used in the manual. Requires
    webkit2png_ and mogrify_. As with `makedoc`, `makeimages -h` prints a
    summary of the command-line options

examples/\*.tex
    LaTeX source files for manual. Use `makeimages -f` to automatically
    generate the corresponding `png` files that are required for the manual


Tests
-----
Very simple syntax tests for WebQuiz_. The main tests are really the files in
the doc/examples directory. The files here are:

\*.tex
    latex source files that generate errors when run through WebQuiz_

\*.expected
    expected log output from source files

tester
    Shell script for comparing the expected and actual output for all of the
    test files. This checks only for syntax errors

The main sets of tests for WebQuiz_ check that all of the WebQuiz_ quizzes in
the doc/examples directory compile properly *and* that they produce appropriate images in
the manual, for example using::

    > doc/examples/makeimages -f

Unfortunately, this test is not completely automatic because it is not
sufficient to check that all of these files compile. In addition, it is
necessary to eyeball all of the images in the manual and make sure that
every one of them is correct. In addition::

    doc/makedoc --check-examples

uses gvim to open a three-way diff for checking that all of the source files in
the `doc/examples` directory are being used in the manual.

Authors
=======

The LaTeX_ component of WebQuiz_ was written by Andrew Mathas and the python,
`CSS` and `javascript` code was written by Andrew Mathas (and Don Taylor), based on
an initial prototype of Don Taylor's from 2001. Since 2004 the program has been
maintained and developed by Andrew Mathas. Although the program has changed
substantially since 2004 Don's idea of using TeX 4ht, and some of his code, is
still very much in use.

Copyright (C) 2004-2019

License
-------
GNU General Public License, Version 3, 29 June 2007

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU\_General Public License (GPL_) as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
Public License for more details.

.. _GPL:        https://www.gnu.org/licenses/gpl-3.0.en.html
.. _LaTeX:      https://www.latex-project.org/
.. _Python3:    https://wwdw.python.org/
.. _TeX4ht:     http://www.tug.org/tex4ht/
.. _TeXLive:    https://www.tug.org/texlive/
.. _WebQuiz:    https://www.ctan.org/pkg/webquiz/
.. _`WebQuiz github repository`: https://github.com/AndrewAtLarge/WebQuiz
.. _ctan:       https://www.ctan.org/
.. _ctanupload: https://ctan.org/pkg/ctanupload
.. _dvisvgm4ht: https://github.com/michal-h21/dvisvgm4ht
.. _kpsewhich:  https://linux.die.net/man/1/kpsewhich
.. _mogrify:    https://imagemagick.org/script/mogrify.php
.. _rst2man:    http://docutils.sourceforge.net/sandbox/manpage-writer/rst2man.txt
.. _sass:       https://sass-lang.com/
.. _uglifyjs:   https://www.npmjs.com/package/uglify-js
.. _webkit2png: http://www.paulhammond.org/webkit2png/
