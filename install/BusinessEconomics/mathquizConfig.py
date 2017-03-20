#!/usr/bin/python
"""  mathquizConfig.py | 2005 Version 4.2 | Andrew Mathas

     Python configuration file for the mathquiz system. This
     file controls the local components of the quiz page.
     
     This now uses php heading and sidemenu bars and standard_redwide.css - Clare
"""

# -----------------------------------------------------

# A relative URL which specifies the location of mathquizzes
# system files on the web server.
MathQuizURL=""

# Local css for layout of quiz pages.
QuizCss="""<link rel="stylesheet" href="%s/css/standard_redwide.css" type="text/css">""" % URL

# Local javascript to be included on every quiz page.
QuizScripts="" 

# Local css to be included on the index page.
IndexCss=""

# Local javascript to be included on the index page.
IndexScripts=""

def PrintInitialization(quiz,course,currentQ,qTotal,level):
  print """
<script src="%s/javascript/mathquiz.js" type="text/javascript"></script>
<script language="javascript" type="text/javascript">
<!--
    thisPage='%s%s.php'
    currentQ=%s
  -->
</script>
""" % ( course['url'], course['src'], currentQ, MathQuizURL)

# -----------------------------------------------------
# I now use php and can change the heading as I see fit 12 Apr 05
# the top of the quiz pages
def printTableTop():
  Images=URL+'img/'
  print """<?php
  include("../php/heading.php");
  ?>"""
   

# I now use php and can change the sidemenu as I see fit 12 Apr 05
# the left hand menu for the index page
def printIndexSideMenu():
  Images=URL+'img/'
  print """<?php
  include("../php/sidemenu.php");
  ?>"""
