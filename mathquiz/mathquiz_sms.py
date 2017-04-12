r'''
----------------------------------------------------------------------
    mathquiz_sms | sms layout of mathquiz web pages.
----------------------------------------------------------------------

    Copyright (C) Andrew Mathas and Donald Taylor, University of Sydney

    Distributed under the terms of the GNU General Public License (GPL)
                  http://www.gnu.org/licenses/

    This file is part of the Math_quiz system.

    <Andrew.Mathas@sydney.edu.au>
    <Donald.Taylor@sydney.edu.au>
#----------------------------------------------------------------------
'''

# -*- encoding: utf-8 -*-

# -----------------------------------------------------
from mathquiz_templates import no_script
from wp import processtemplate as sms_write_page

sms_quiz_specifications = '  <script type="text/javascript">var QuizURI="{}Quizzes";var QuizContents="{}";</script>\n'
sms_research_menu  = '  <script type="text/javascript" src="/u/SMS/web2010/js/ResearchSubmenu.js"></script>\n'
sms_qsubmenu = '  <script type="text/javascript" src="/u/SMS/web2010/js/QSubmenu.js"></script>\n'
sms_course_qsubmenu = '  <script type="text/javascript" src="/u/SMS/web2010/js/CourseQSubmenu.js"></script>\n'

nav_menu = r"""  <ul class="navmenu">
    <li>
      <div class="dropdownroot" id="{menu}"></div>
      <script type="text/javascript"> domMenu_activate('{menu}'); </script>
    </li>{heading}
  </ul>
"""
# -----------------------------------------------------
# stuff to go in the <head> ... </head> section of the page
def initialise_SMS_Menus(web_page):
  if web_page.course['code'] in ["MATH1001", "MAGTH1002", "MATH1005"]:
    content="MATH100{0}/190{0}<br/>Quizzes".format(web_page.course['code'][-1])
  else:
    content="%s Quizzes" % web_page.course['code']
  hd=sms_web_page.format(web_page.course['url'],content)
  if web_page.quiz_file=="index":
    hd += sms_research_menu+sms_qsubmenu
  elif web_page.quiz_file in [ 'mathquiz-manual','credits']:
    hd += sms_qsubmenu
  else:
    hd += sms_course_qsubmenu

  return hd

# breadcrumbs line
def SMS_breadcrumbs(web_page):
  if web_page.course['code']=="MathQuiz":
    level = 'MOW'
    year  = 'GEM'
  elif len(web_page.course['code'])>4:
    level={'1':'JM', '2':'IM', '3':'SM', 'o':'', 'Q':''}[web_page.course['code'][4]]
    year ={'JM':'Junior', 'IM':'Intermediate', 'SM':'Senior', '':''}[level]
    level='UG/'+level
  else:
    level=''
    year=''

  bc = """<div class="breadcrumb moved"><b>You are here: &nbsp;&nbsp;</b><a href="/">Maths &amp; Stats Home</a> /"""
  if web_page.quiz_file=="mathquiz-manual":
    bc += """<a href="/u/MOW/">GEM</a> / MathQuiz"""
  elif web_page.quiz_file=="credits":
    bc += """<a href="/u/MOW/">GEM</a> /
             <a href="/u/MOW/MathQuiz/doc/mathquiz-manual.html">MathQuiz</a> /
	     Credits"""
  else:
    bc += """
             <a href="/u/UG/">Teaching program</a> /
             <a href="/u/%s/">%s</a> /
             <a href="%s">%s</a> /
""" % ( level, year, web_page.course['url'] , web_page.course['code'])
    if web_page.quiz_file=="index":
      bc += "             Quizzes\n"
    else:
      bc += """             <a href="%s">Quizzes</a> / %s
""" % (web_page.course['quizzes'],web_page.quiz.bread_crumb)

  bc += "</div>"
  return bc+no_script

# the left side menu
def SMS_menu(quiz):
    # write a javascript file for displaying the menu
    # quizmenu = the index file for the quizzes in this directory
    if len(quiz.quiz_list)>0:
        with open('quiztitles.js','w') as quizmenu:
            quizmenu.write('var QuizTitles = [\n{titles}\n];\n'.format(
                  titles = ',\n'.join("  ['{:<60}', '{}/Quizzes/{}']".format(
                             q['title'],self.course['url'],q['url']
                  ) for q in quiz.quiz_list)
            )
         )

    menu = ''
    if len(course['name'])>0:
      menu_name = 'MathQuiz'
      if len(quiz.quiz_list)==0:  # not on a quiz index page
          if  quiz_file in ["mathquiz-manual","credits"]: 
              type="QSubmenu"
          else: 
              type="CourseQSubmenu"
          heading = 'Manual contents' if quiz_file=='mathquiz-manual' else \
                    'Discussion' if len(quiz.discussion_list)>0 else ''
          menu += nav_menu.format(menu=type, heading='' if heading=='' else '<li>{}</li>'.format(heading))
    else:
      menu_name = "Current Students"
      menu += '[@@ URLplus=[^^~currentmenu^^] @@]\n'

  return menu_name, menu

def write_web_page(web_page):
  sms_menu_name, sms_menu=SMS_menu(web_page.web_pagequiz)
  page=dict(
      meta_string = web_page.header,
      head_data_string =  web_page.javascript+initialise_SMS_Menus(web_page)+web_page.css,
      breadcrumbs_string = SMS_breadcrumbs(web_page),
      menu_string = sms_menu+web_page.side_menu,
      page_body_string = web_page.quiz_header+web_page.quiz_questions,
      nopreview = ''
  )
  for (key, value) in [('CODE','QUIZ'),
                       ('menuname', sms_menu_name),
                       ('pagetitle', web_page.title), ('title',''),
                       ('no-compmenu', 'y'),
                       ('tablevel', 'internal' if web_page.quiz_file in ['mathquiz-manual','credits'] else '')]:
      page['UNIT_OF_STUDY,'+key] = value
  return sms_write_page(page, {}, web_page.course['url'], web_page.quiz_file+'.html;')[0]
