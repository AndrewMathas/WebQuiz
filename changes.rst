=======
Changes
=======

Version 5.0:
------------
    - updated to use html5, mathjax and mathml
    - images for buttons etc replaced by css
    - python and javascript streamlined and largely rewritten
    - bash script wrapper replaced with python, making it more portable and more flexible
    - now using make4ht
    - option for pst2pdf preprocessing for quizzes using pstruicks/postscript
    - program packaged for uploading to ctan and texlive
    - better installation support
    - mathquizrc configuration file added
    - changed from using optionparser to argparse
    - using git and bitbucket for version management control
    - made compatible with setup tools, together with option to export to ctan
    - allow user configuration via .mathquizrc file in HOME directory
    - export to ctan

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
    - randomise order of questions (easy) and question parts (hard?)
    - allow variables in questions
    - (?) allow vertical/horizontal/none customisations of question buttons
    - (?) record marks of students...would need a interface for login details etc
    - (?) use vue to render and control quiz pages
    - (?) add timer to quiz

