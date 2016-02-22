r"""  mathquizLocal.py | 2010 Version 4.5 | Andrew Mathas and Donald Taylor

     Specifies default printing of mathquiz web pages.

#*****************************************************************************
#       Copyright (C) 2004-2010 Andrew Mathas and Donald Taylor
#                          University of Sydney
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#
# This file is part of the MathQuiz system.
#
# Copyright (C) 2004-2010 by the School of Mathematics and Statistics
# <Andrew.Mathas@sydney.edu.au>
# <Donald.Taylor@sydney.edu.au>
#*****************************************************************************
"""

import string

# -----------------------------------------------------

NoScript = """
<noscript><div style="margin:0px 10px 0px 10px; padding:0"><b>If you are reading this message either your
    browser does not support JavaScript or else JavaScript
    is not enabled.  You will need to enable JavaScript and
    then reload this page before you can use this quiz.</b></div></noscript>
"""

def printQuizPage(html, doc):
  breadCrumb='<a href="%s">%s</a> / <a href="%s">Quizzes</a> / %s' % (
                html.course['url'],html.course['code'],html.course['url']+'Quizzes', doc.title)
  quizPage="""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<title>
  %s
</title>
%s 
<style type="text/css">
  <!--
  #content h1 {
    clear:left;
    font-size:1.545em;
    margin:0em 0 0 0;
    color:#3300FF;
   }
   #content div.ArrowQuestion {
     margin: 0 -20em 0 0; 
   }
  -->
</style>
</head>

<body class="" onload="">
  <div class="breadcrumb" style="display:block;margin:0;padding:.3em 0 .3em 0;border-bottom:1px solid #ccc;font-size:10px;">
     %s
  </div>
  %s
  <div id='menu' style="float:left;width:180px;margin:20px 10px 0 20px;text-align:left;font-size:10px;">
    <dl style="margin:0; padding:0; border:0; text-align:center;">
      <dt style="font:bold 1.1em Arial,Helvetica,sans-serif;color:#3300FF;font-variant:small-caps;">MathQuiz</dt>
       <dd>
       %s
       </dd>
    </dl>
  </div>
  <div id="content" style="float:left;margin:10px 10px 0 30px;text-align:left;">
     %s
  </div>
</body>

</html>""" % (doc.title,  # page title
              html.header+html.javascript+html.css,  # header material
              breadCrumb,                            # bread crumb constructed above
              NoScript,                              # warning to enable javascript
              html.side_menu,                        # navigation menu for quiz
              html.pagebody )                        # html for quiz
  print string.replace(quizPage,'/>','>')
