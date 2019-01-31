========
WebQuiz_
========

*This is the development version of* WebQuiz_. *Most users should use* WebQuiz_
*as a standard* LaTeX_ *package by downloading and installing* WebQuiz_ *from*
ctan_.

WebQuiz_ makes it possible to use LaTeX_ to write interactive web based
quizzes. The quizzes are first written in LaTeX_ and then converted into
HTML files using WebQuiz_, which is written in Python3_. The conversion
from LaTeX_ to HTML is done behind the scenes using TeX4ht_.

WebQuiz_ has the following components:
 - LaTeX_ code that uses TeX4ht_ to generate an XML file
 - Python3_ code that reads the XML file and outputs an HTML file
 - CSS for styling the web pages
 - javascript for controlling the web pages
 - documentation
 - rudimentary tests

WebQuiz_ relies on having the following programs installed: LaTeX_, TeX4ht_, (available with most LaTeX_
distributions such as TeXLive_), and Python3_. To use the development version,
particularly, for building the manual and uploading to ctan_, you will also need
mogrify_, sass_, uglifyjs_ and webkit2png_

The README file explains how the different components of WebQuiz_ are organised. For
installation instructions see the next section on setup tools.

Installing the development version
----------------------------------

First clone or download the WebQuiz_ github repository.  On a unix-like system,
such as linux or macosx, to set up links for the latex and web files for the
development version run::

    > python3 setup.py develop

In fact, you may want to run this as root, in which case you want::

    > sudo python3 setup.py develop

By default, links for the latex files will be put into the TEXMFLOCAL directory
but this can be customised. You will then be prompted for links for the
executable and the web components of WebQuiz_. The install process assumes that
kpsewhich_ and sass_ are both installed. It is unlikely that installation via
setuptools will work on a windows PC.

WebQuiz_ distribution on ctan_
------------------------------
The organisation of the code in the WebQuiz_ repository is not suitable for
distribution to ctan_. To upload the package to ctan_ use::

    > python3 setup.py ctan

creates a zipfile, `webquiz.zip`, and optionally uploads it to ctan_ using
ctanupload_, which is packaged with TeXLive_::

    > python3 setup.py ctan

WebQuiz_ is not distributed as a Python3_ package because it fits more
naturally into the LaTeX_ ecosystem, which is a hard dependency for the
program.

Python code
-----------
There are six python source files:

webquiz.py
    processes command-line options and settings

webquiz_layout.py
    determines the final layout of the web pages

webquiz_makequiz.py
    converts the XML into HTML

webquiz_templates.py
    template strings for HTML and

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
     WebQuiz_ initialisation data. This is also used by the python code

webquiz-doc.code.tex
     macros used in the manuals

webquiz-ini.code.tex
     code for reading and accessing the ini fle in latex

pgfsys-dvisvgm4ht.def
     custom tikz driver for tex4ht from dvisvgm4ht_

webquiz-\*.lang
     language support files. These are actually used by webquiz_main.py when
     writing the web pages but we find them by putting them in the LaTeX search
     path


Cascading style sheets
-----------------------
The CSS for WebQuiz_ are written using sass (https://sass-lang.com/). The main
files are:

webquiz.scss
webquiz-THEME.scss

The theme files all set the colours and then load the main sass file webquiz.scss.
Use the shell script command::

    > makedoc -t

to generate all of the css files.


Javascript
----------
There is one javascript file, `webquiz.js`, in the javascript directory. In
addition, the quizindex environment generates the javascript file `quizindex.js`,
that generates a drop-down menu for the quizzes in the current directory. This
file is automatically loaded at the end of each quiz HTML file, if it exits.
For each quiz, WebQuiz_ writes another javascript file, `wq-file.js`, that
specified the questions in the quiz. This is also automatically by the quiz
page.

It would be goods to add some javascript unit tests....

Documentation
-------------
The main files in the documentation directory are:

webquiz.tex
    LaTeX source for the WebQuiz_ manual

webquiz-on-line-manual.tex
    LaTeX source for the on-line Webquiz_ manual

credits.tex
    LaTeX source for the credits

makedoc
    bash shell script that automatically generates the many
                    different components of the manual. There are various
                    options; use makedoc -h to see a summary

examples
    directory of WebQuiz_ code snippets that are included in the manual

examples/makeimages
    python script for generating the images used in the
                    manual. Requires webkit2png and mogrify. As with makedoc,
                    makeimages -h summaries the command-line options

examples/makeimages/\*.tex
    LaTeX source files for manual


Tests
-----
Simple syntax checking tests for WebQuiz_. The main tests are really the files
in the doc/examples directory. The files here are:


\*.tex
    latex source files that generate errors when run through WebQuiz_

\*.expected
    expected log output from source files

tester
    shell script for comparing the expected and actual output for
                 all of the test files

The main test for WebQuiz_ is to see if the quizzes in the doc/examples
directory compile properly and produce appropriate images in the manual,
for example using::

    > doc/examples/makeimages -f

Unfortunately, this s not automatic and requires eyeballing all of the
images in the manual.


Authors
=======

The LaTeX_ component of WebQuiz_ was written by Andrew Mathas and the python,
css and javascript code was written by Andrew Mathas (and Don Taylor), based on
an initial prototype of Don Taylor's from 2001. Since 2004 the program has been
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

.. _LaTeX: https://www.latex-project.org/
.. _Python3: https://wwdw.python.org/
.. _TeX4ht: http://www.tug.org/tex4ht/
.. _TeXLive: https://www.tug.org/texlive/
.. _WebQuiz: https://www.ctan.org/pkg/webquiz/
.. _ctan: https://www.ctan.org/
.. _ctanupload: https://ctan.org/pkg/ctanupload
.. _kpsewhich: https://linux.die.net/man/1/kpsewhich
.. _mogrify: https://imagemagick.org/script/mogrify.php
.. _sass: https://sass-lang.com/
.. _uglifyjs: https://www.npmjs.com/package/uglify-js
.. _webkit2png: http://www.paulhammond.org/webkit2png/
.. _dvisvgm4ht: https://github.com/michal-h21/dvisvgm4ht
