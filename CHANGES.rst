===============
WebQuiz Changes
===============

Version 5.2:
------------
    - compatibility with both MikTeX and TeXLive under windows

Version 5.1:
------------
    - code reorganised n zip file for TeXLive inclusion
    - \dref, \qref and \Qref commands
    - error and debugging code reorganised
    - javascript session history following Hendrik Suess
    - unix man page

Version 5.0:
------------
    - added button for hiding/showing question buttons
    - added colour theme support
    - added language support
    - added support for colour and listings in the quiz files
    - added lualatex and xelatex engine support
    - added displayasimage
    - added more comparison options for inputted answers
    - all files converted to utf8  using codecs
    - bash script wrapper replaced with python, using argparser, making it more portable and more flexible
    - better installation support
    - changed name from mathquiz to webquiz
    - drop-down menu for quiz index file
    - export to ctan in setup.py
    - images for buttons etc replaced by css
    - implemented a suggestion of Michal Hoftich to workaround tikz/pgf bugs
    - implemented a suggestion to Herbert Voss to fix a pstricks issue using pst2pdf
    - made compatible with setup tools, together with option to export to ctan
    - many more document class options
    - new (off-line) manual with automatically generated images via makeimages script
    - now using make4ht
    - option for pst2pdf preprocessing for quizzes using pstricks/postscript
    - option for tikz that fixes a few bugs of pgf/tikz
    - program packaged for uploading to ctan and texlive
    - programmable breadcrumbs
    - python and javascript streamlined and largely rewritten
    - randomorder and onepage options added
    - replaced Choice environment with smarter choice environment
    - rewrote xml parser
    - side menu and breadcrumbs automatically disappear on small screens
    - system webquizrc configuration file added wiith optional user .webquizrc file
    - thechoice controls the labels for multiple choice options
    - updated to use html5, mathjax and mathml
    - using git and bitbucket for version management control
    - using pgfkeys for processing document class and environment options
    - using sass to generate css for different themes
    - various webquiz defaults can be stored in the rc-file
    - windows batch file

Version 4.6:
------------
    - Updated to use MathML

Version 4.5:
------------
    - Updated and streamlined many aspects of the code

Version 4.0:
------------
    - separated allowed default and localised versions for the quiz page payout
      with the SMS versiion calling Bob Howlett's update programs to generate
      the quiz web pages

Version 3:
----------
    - code taken over by Andrew Mathas
    - latex class file, mathquiz.cls, written and integrated with tex4ht code
    - documentation written
    - SMS quizzes converted to mathquiz format

Versions 1 and 2:
-----------------
2001-03-21  Don Taylor -  initial prototype by Don Taylor


To do
-----
Rather than a to-do list, here are some possible future improvements:
    - (?) improve quiz "security" (would be a side-effect of moving to vue...)
    - (?) randomise order of questions parts with document-class option randomorder
    - (?) allow variables in questions (hardest part is finding a good syntax)
    - (?) rewrite javascript to use vue to render and control quiz pages
    - (?) allow vertical/horizontal/none customisations of question buttons
    - (?) record marks of students...would need a interface for login details etc
    - (?) add timer and/or time limits to quiz
    - (?) responsive columns to replace columns=? in choice environments
    - (?) dynamic themes (easy)
    - (?) dynamic languages (harder)

