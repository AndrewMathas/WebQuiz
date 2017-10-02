=======
Changes
=======

Version 5.0:
------------
    - "programable" breadcrumbs
    - added button for hiding/showing question buttons
    - added colour theme support
    - added language support
    - added support for colour and listings in the quiz files
    - all files converted to utf8  using codecs
    - bash script wrapper replaced with python, using argparser, making it more portable and more flexible
    - better installation support
    - changed name to webquiz
    - drop-down menu for quiz index file
    - export to ctan
    - images for buttons etc replaced by css
    - implemented a suggestion of Michal Hoftich to workaround tikz/pgf bugs
    - implemented a suggestion to Herbert Voss to fix a pstricks issue using pst2pdf
    - made compatible with setup tools, together with option to export to ctan
    - new (off-line) manual with automatically generated images via makeimages script
    - now using make4ht
    - option for pst2pdf preprocessing for quizzes using pstruicks/postscript
    - option for tikz that fixes a few bugs of pgf/tikz
    - program packaged for uploading to ctan and texlive
    - python and javascript streamlined and largely rewritten
    - replaced Choice environment with smarter choice environment
    - side menu and breadcrumbs automatically disappear on small screens
    - system webquizrc configuration file added wiith optional user .webquizrc file
    - updated to use html5, mathjax and mathml
    - using git and bitbucket for version management control
    - various magthquiz defaults can be stored in the rc-file
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
------
    - finish writing documentation
    - (?) improve quiz "security"
    - (?) randomise order of questions (easy) and question parts (hard?)
    - (?) allow variables in questions
    - (?) rewrite javascript to use vue to render and control quiz pages
    - (?) allow vertical/horizontal/none customisations of question buttons
    - (?) record marks of students...would need a interface for login details etc
    - (?) add timer and/or time limits to quiz
    - (?) allow question groups

