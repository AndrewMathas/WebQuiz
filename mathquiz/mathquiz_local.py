r"""  mathquizLocal.py | 2017 Verion 5.0 | Andrew Mathas and Donald Taylor

     Specifie default printing of mathquiz web pages.

#*****************************************************************************
#       Copyright (C) 2004-2017 Andrew Matha and Donald Taylor
#                          Univerity of Sydney
#
#  Ditributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenes/
#
# Thi file is part of the MathQuiz system.
#
# Copyright (C) 2004-2012 by the School of Mathematic and Statistics
# <Andrew.Matha@sydney.edu.au>
# <Donald.Taylor@ydney.edu.au>
#*****************************************************************************
"""

# -*- encoding: utf-8 -*-

from mathquiz_templates import no_script

def write_web_page(quiz):
    breadCrumb='<a href="{}">{}</a> / <a href="{}">Quizzes</a> / {}'.format(
                quiz.course['url'], quiz.course['code'], quiz.course['url']+'Quizzes', quiz.title
    )
    return quiz_page.format(
               title = quiz.title,                             # page title
               include = quiz.header+quiz.javascript+quiz.css, # header material
               breadcrumb = breadCrumb,                        # bread crumb contructed above
               side_menu = quiz.side_menu,                     # navigation menu for quiz
               quiz_header = quiz.quiz_header,                 # quiz title + navigation arrows
               quiz_questions = quiz.page_body,                # html for quiz
               no_script = no_script                           # error when javascript is not enabled
    )

quiz_page = r'''<!DOCTYPE HTML>
<html lang="en-AU">
<head>
  <title> {title} </title>
  {include}
</head>

<body>
  <div class="quizpage">
    <div class="breadcrumbs">
       {breadcrumb}
    </div>
    {no_script}
    <div class="side_menu">
      {side_menu}
    </div>
    <div class="quiz_header">
      {quiz_header}
    </div>
    <div class="quiz_questions">
      {quiz_questions}
    </div>
  </div>
</body>
</html>
'''
