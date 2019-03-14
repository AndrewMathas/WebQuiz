r'''
-----------------------------------------------------------------------------
    webquiz_local | default layout of webquiz quiz pages.
-----------------------------------------------------------------------------

    Copyright (C) Andrew Mathas, University of Sydney

    Distributed under the terms of the GNU General Public License (GPL)
                  http://www.gnu.org/licenses/

    This file is part of the WebQuiz system.

    <Andrew.Mathas@sydney.edu.au>
-----------------------------------------------------------------------------
'''

# -*- encoding: utf-8 -*-

from webquiz_templates import no_script

# If you want to create a new version of this file to change the
# quiz web page layout then the following "dictionary" of code variables
# is likely to be useful:
#   quiz.breadcrumbs = HTML for breadcrunbs
#   quiz.css = css includes for quisz
#   quiz.department = department from \UnitDepartment
#   quiz.department_url = unit url from \UnitURL
#   quiz.header = header links for quiz
#   quiz.institution = institution from \Institution
#   quiz.institution_url = unit url from \InstitutionURL
#   quiz.javascript = javascript includes for quiz
#   quiz.quiz_header = HTMK for quiz title and navigation arrows
#   quiz.quiz_questions = html for quiz
#   quiz.side_menu = HTML for side menu, including navigation buttons
#   quiz.title = web page title from \title{...} command
#   quiz.unit_code = unit code from \UnitCode
#   quiz.unit_name = unit name from \UnitName
#   quiz.unit_url = unit url from \UnitURL
#   quiz.webquiz_init = javascript for initialising quiz page
#                       MUST appear towards the end of HTML body

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
  {no_script}{breadcrumbs}
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
