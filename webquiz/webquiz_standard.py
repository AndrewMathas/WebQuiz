r'''
-----------------------------------------------------------------------------
    webquiz_local | default layout of webquiz web pages.
-----------------------------------------------------------------------------

    Copyright (C) Andrew Mathas, University of Sydney

    Distributed under the terms of the GNU General Public License (GPL)
                  http://www.gnu.org/licenses/

    This file is part of the WebQuiz system.

    <Andrew.Mathas@sydney.edu.au>
    <Donald.Taylor@sydney.edu.au>
-----------------------------------------------------------------------------
'''

# -*- encoding: utf-8 -*-

from webquiz_templates import no_script


def write_web_page(quiz):
  return quiz_page.format(
    title=quiz.quiz.title,  # page title
    htmlpreamble=quiz.header + quiz.javascript + quiz.css,  # header material
    breadcrumbs=quiz.breadcrumbs,  # bread crumb constructed above
    side_menu=quiz.side_menu,  # navigation menu for quiz
    quiz_header=quiz.quiz_header,  # quiz title + navigation arrows
    quiz_questions=quiz.quiz_questions,  # html for quiz
    no_script=no_script,  # error when javascript is not enabled
    webquiz_init=quiz.webquiz_init  # parting javascript callsWebQuizInt
  )


quiz_page = r'''<!DOCTYPE HTML>
<html lang="en">
<head>
  <title> {title} </title>
  {htmlpreamble}
</head>

<body>
  {no_script}
  {breadcrumbs}
  <div class="quiz-page">
    {side_menu}
    <div class="quiz-questions">
      {quiz_header}
      {quiz_questions}
    </div>
  </div>
  {webquiz_init}
</body>
</html>
'''
