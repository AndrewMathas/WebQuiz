WebQuiz has the following components:
 - latex code that uses TeX4ht to generate an XML file
 - python code that reads the XML file and outputs an HTML file
 - CSS for styling the web pages
 - javascript for controlling the web pages
 - documentation
 - rudimentary tests

This file quickly explains how the different components are organised. For
developer installation instructions see the next section on setup tools.


Setup tools
-----------
Python setup tools are used for packaging to CTAN:
    > python3 setup.py ctan
creates a zipfile, webquiz.zip, and optionally uploads it to ctan
using ctanupload, which is packaged with TeXLive.

On a unix-like system, such as linux or macosx, to set up links for the latex
and web files for the development version run:
    > python3 setup.py develop
In fact, you may want to run this as root, in which case you want:
    > sudo python3 setup.py develop
By default, links for the latex files will be put into the TEXMFLOCAL directory
but this can be customised. You will then be prompted for links for the
executable and the web components of WebQuiz. The install process assumes that
kpsewhich and sass are both installed. It is unlikely that this will work on
a windows PC.


Python code
-----------
There are six python source files:
 - webquiz.py*           = processes command-line options and settings
 - webquiz_layout.py     = determines the final layout of the web pages
 - webquiz_makequiz.py   = converts the XML into HTML
 - webquiz_templates.py  = template strings for HTML and
 - webquiz_util.py       = utility functions
 - webquiz_xml.py        = read and interpret the webquiz XML file


LaTeX code
----------
The LaTeX is in the latex directory. The main components are:
 - webquiz.cfg             = webquiz TeX4ht configuration file => generates XML
 - webquiz.cls             = webquiz document class file
 - webquiz.ini             = webquiz initialisation data. This is
                             also used by the python code
 - webquiz-doc.code.tex    = macros used in the manuals
 - webquiz-ini.code.tex    = code for reading and accessing the ini fle in latex
 - pgfsys-dvisvgm4ht.def   = custom tikz driver for tex4ht
                             from https://github.com/michal-h21/dvisvgm4ht
 - webquiz-*.lang          = language support files. These are
      actually used by webquiz_main.py when writing the web pages
      but we find them by putting them in the LaTeX search path


Cascading style sheets
-----------------------
The CSS for WebQuiz are written using sass (https://sass-lang.com/). The main
files are:
 - webquiz.scss
 - webquiz-THEME.scss
The theme files all set the colours and then load the main sass file webquiz.scss.
Use the shell script command
    makedoc -t
to generate all of the css files.


Javascript
----------
There is one javascript file, webquiz.js, in the javascript directory. In
addition, the quizindex environment generates the javascript file quizindex.js,
that generates a drop-down menu for the quizzes in the current directory. This
file is automatically loaded at the end of each quiz HTML file, if it exits.
For each quiz, WebQuiz writes another javascript file, wq-file.js, that
specified the questions in the quiz. This is also automatically by the quiz
page.


Documentation
-------------
The main files in the documentation directory are:
 - webquiz.tex    = LateX source for the WebQuiz manual
 - webquiz-on-line-manual.tex = LaTeX source for the on-line Webquiz manual
 - credits.tex    = LaTeX source for the credits
 - makedoc        = bash shell script that automatically generates the many
                    different components of the manual. There are various
                    options; use makedoc -h to see a summary
 - examples       = directory of WebQuiz code snippets that are included in the manual
 - examples/makeimages = python script for generating the images used in the
                    manual. Requires webkit2png and mogrify. As with makedoc,
                    makeimages -h summaries the command-line options
 - examples/makeimages/*.tex = LaTeX source files for manual


Tests
-----
Simple syntax checking tests for WebQuiz. The main tests are really the files
in the doc/examples directory. The files here are:
 - *.tex       = latex source files that generate errors when run through webquiz
 - *.expected  = expected log output from source files
 - tester      = shell script for comparing the expected and actual output for
                 all of the test files

The main test for webquiz is to see if the quizzes in the doc/examples
directory compile properly and produce appropriate images in the manual,
for example using
    doc/examples/makeimages -f
Unfortunately, this s not automatic and requires eyeballing all of the
images in the manual.

