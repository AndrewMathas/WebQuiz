r"""  mathquizLocal.py | 2016 Version 4.7 | Andrew Mathas and Donald Taylor

     Specifies default printing of mathquiz web pages.

#*****************************************************************************
#       Copyright (C) 2004-2016 Andrew Mathas and Donald Taylor
#                          University of Sydney
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#
# This file is part of the MathQuiz system.
#
# Copyright (C) 2004-2012 by the School of Mathematics and Statistics
# <Andrew.Mathas@sydney.edu.au>
# <Donald.Taylor@sydney.edu.au>
#*****************************************************************************
"""

def printQuizPage(html, doc):
    breadCrumb='<a href="%s">%s</a> / <a href="%s">Quizzes</a> / %s' % (
                html.course['url'],html.course['code'],html.course['url']+'Quizzes', doc.title)
    return QuizPage.format(
            title = doc.title,                               # page title
            includes = html.header+html.javascript+html.css, # header material
            breadcrumb = breadCrumb,                         # bread crumb constructed above
            side_menu = html.side_menu,                      # navigation menu for quiz
            quiz_questions = html.page_body                  # html for quiz
    )

QuizPage = r'''<!DOCTYPE HTML>
<html lang="en-AU">
<head>
  <title> {title} </title>
  {includes}
</head>

<body>
  <div class="quizpage">
    <div class="breadcrumb" style="display:block;margin:0;padding:.3em 0 .3em 0;border-bottom:1px solid #ccc;font-size:10px;">
         {breadcrumb}
    </div>
    <noscript>
      <div class="warning"><b>
        If you are reading this message either your browser does not support
        JavaScript or else JavaScript is not enabled.  You will need to enable
        JavaScript and then reload this page before you can use this quiz.</b>
       </div>
    </noscript>
    <div class="side_menu">
    {side_menu}
    </div>
    <div class="quiz_questions">
    {quiz_questions}
    </div>
  </div>
</body>
</html>
'''
