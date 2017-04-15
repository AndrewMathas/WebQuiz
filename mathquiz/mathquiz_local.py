r'''
-----------------------------------------------------------------------------
    mathquiz_local | default layout of mathquiz web pages.
-----------------------------------------------------------------------------

    Copyright (C) Andrew Mathas and Donald Taylor, University of Sydney

    Distributed under the terms of the GNU General Public License (GPL)
                  http://www.gnu.org/licenses/

    This file is part of the Math_quiz system.

    <Andrew.Mathas@sydney.edu.au>
    <Donald.Taylor@sydney.edu.au>
-----------------------------------------------------------------------------
'''

# -*- encoding: utf-8 -*-

from mathquiz_templates import no_script

def write_web_page(quiz):
    return quiz_page.format(
               title          = quiz.title,                           # page title
               include        = quiz.header+quiz.javascript+quiz.css, # header material
               breadcrumbs    = quiz.bread_crumbs,                    # bread crumb constructed above
               side_menu      = quiz.side_menu,                       # navigation menu for quiz
               quiz_header    = quiz.quiz_header,                     # quiz title + navigation arrows
               quiz_questions = quiz.quiz_questions,                  # html for quiz
               no_script      = no_script,                            # error when javascript is not enabled
               mathquiz_init  = quiz.mathquiz_init                    # parting javascript callsMathQuizInt
    )

quiz_page = r'''<!DOCTYPE HTML>
<html lang="en-AU">
<head>
  <title> {title} </title>
  {include}
</head>

<body>
  {breadcrumbs}
  {no_script}
  <div class="quiz_page">
    {side_menu}
    <div class="quiz_questions">
      {quiz_header}
      {quiz_questions}
  </div>
  {mathquiz_init}
</body>
</html>
'''
