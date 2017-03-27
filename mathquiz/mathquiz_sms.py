r"""  mathquizSMS.py | Version 5.0 | Andrew Mathas
      2010 made "update" compatible by Bob Howlett

     Python configuration file for the mathquiz system. This
     file controls the local components of the quiz page.

#*****************************************************************************
#  Copyright (C) 2004-2017 Andrew Mathas
#  University of Sydney
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#
#  This file is part of the MathQuiz system.
#
#  Copyright (C) 2004-2017 by the School of Mathematics and Statistics
#  <Andrew.Mathas@sydney.edu.au>
#*****************************************************************************
"""

# -*- encoding: utf-8 -*-

# -----------------------------------------------------
from mathquiz_templates import no_script
from wp import processtemplate as sms_write_page

sms_javascript=''' <link rel="stylesheet" href="/u/SMS/web2015/styles/SMS-mq.css" type="text/css">
  <script type="text/javascript">var QuizURI="{}Quizzes";var QuizContents="{}";</script>
'''
index_javascript ="""  <script type="text/javascript" src="/u/SMS/web2010/js/ResearchSubmenu.js"></script>
  <script type="text/javascript" src="/u/SMS/web2010/js/QSubmenu.js"></script>
"""

nav_menu = r"""  <ul class="navmenu">
    <li>
      <div class="dropdownroot" id="{menu}"></div>
      <script type="text/javascript"> domMenu_activate('{menu}'); </script>
    </li>{heading}
  </ul>
"""
# -----------------------------------------------------
# stuff to go in the <head> ... </head> section of the page
def initialise_SMS_Menus(quiz):
  if quiz.course['code'] in ["MATH1001", "MAGTH1002", "MATH1005"]:
    content="MATH100{0}/190{0}<br/>Quizzes".format(quiz.course['code'][-1])
  else:
    content="%s Quizzes" % quiz.course['code']
  hd=sms_javascript.format(quiz.course['url'],content)
  if quiz.quiz_file=="index":
    hd += index_javascript
  elif quiz.quiz_file in [ 'mathquiz-manual','credits']:
    hd += '  <script type="text/javascript" src="/u/SMS/web2010/js/QSubmenu.js"></script>\n'
  else:
    hd += '  <script type="text/javascript" src="/u/SMS/web2010/js/CourseQSubmenu.js"></script>\n'
  return hd

# breadcrumbs line
def SMS_breadcrumbs(quiz):
  if quiz.course['code']=="MathQuiz":
    level = 'MOW'
    year  = 'GEM'
  elif len(quiz.course['code'])>4:
    level={'1':'JM', '2':'IM', '3':'SM', 'o':'', 'Q':''}[quiz.course['code'][4]]
    year ={'JM':'Junior', 'IM':'Intermediate', 'SM':'Senior', '':''}[level]
    level='UG/'+level
  else:
    level=''
    year=''

  bc = """<div class="breadcrumb moved"><b>You are here: &nbsp;&nbsp;</b><a href="/">Maths &amp; Stats Home</a> /"""
  if quiz.quiz_file=="mathquiz-manual":
    bc += """<a href="/u/MOW/">GEM</a> / MathQuiz"""
  elif quiz.quiz_file=="credits":
    bc += """<a href="/u/MOW/">GEM</a> /
             <a href="/u/MOW/MathQuiz/doc/mathquiz-manual.html">MathQuiz</a> /
	     Credits"""
  else:
    bc += """
             <a href="/u/UG/">Teaching program</a> /
             <a href="/u/%s/">%s</a> /
             <a href="%s">%s</a> /
""" % ( level, year, quiz.course['url'] , quiz.course['code'])
    if quiz.quiz_file=="index":
      bc += "             Quizzes\n"
    else:
      bc += """             <a href="%s">Quizzes</a> / %s
""" % (quiz.course['quizzes'],quiz.quiz.bread_crumb)

  bc += "</div>"
  return bc+no_script

# the left side menu
def SMS_menu(quiz):
  menu = ''
  if len(quiz.course['name'])>0:
      menu_name = 'MathQuiz'
      if len(quiz.quiz.quiz_list)==0:  # not on a quiz index page
          if  quiz.quiz_file in ["mathquiz-manual","credits"]: 
              type="QSubmenu"
          else: 
              type="CourseQSubmenu"
          heading = 'Manual contents' if quiz.quiz_file=='mathquiz-manual' else 
                    'Discussion' if len(quiz.quiz.discussion_list)>0 else ''
          menu += nav_menu.format(menu=type, heading='' if heading=='' else '<li>{}</li>'.format(heading))
  else:
      menu_name = "Current Students"
      menu += '[@@ URLplus=[^^~currentmenu^^] @@]\n'
  return menu_name, menu

def write_web_page(quiz):
  sms_menu_name, sms_menu=SMS_menu(quiz)
  page=dict(
      meta_string = quiz.header,
      head_data_string =  quiz.javascript+initialise_SMS_Menus(quiz)+quiz.css,
      breadcrumbs_string = SMS_breadcrumbs(quiz),
      menu_string = sms_menu+quiz.side_menu,
      page_body_string = quiz.page_body,
      nopreview = ''
  )
  for (key, value) = [('CODE','QUIZ'), ('menuname', sms_menu_name),
                      ('pagetitle', page.title), ('title',''),
                      ('tablevel', 'internal' if self.quiz_file in ['mathquiz-manual','credits'])]:
      page['UNIT_OF_STUDY,CODE,'+key] = value
  return sms_write_page(page, {}, quiz.course['url;'], quiz.quiz_file+'.html;')[0]
