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
import sys

sys.path.insert(0,'/users/misc/httpd/ub/bobh/loc/teaching/') 
import wp

sms_javascript=''' <link rel="stylesheet" href="/u/SMS/web2015/styles/SMS-mq.css" type="text/css">
  <script type="text/javascript">var QuizURI="{}Quizzes";var QuizContents="{}";</script>
'''
index_javascript ="""  <script type="text/javascript" src="/u/SMS/web2010/js/ResearchSubmenu.js"></script>
  <script type="text/javascript" src="/u/SMS/web2010/js/QSubmenu.js"></script>
"""
# -----------------------------------------------------
# stuff to go in the <head> ... </head> section of the page
def initialise_SMS_Menus(quiz,course):
  if course['code'] in ["MATH1001", "MAGTH1002", "MATH1005"]:
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
    menuname = 'MATHQUIZ'
    if len(quiz.quiz.quiz_list)==0:  # not on a quiz index page
      if  quiz.quiz_file in ["mathquiz-manual","credits"]: type="QSubmenu"
      else: type="CourseQSubmenu"
      menu += """  <ul class="navmenu">
    <li>
      <div class="dropdownroot" id="%s"></div>
      <script type="text/javascript"> domMenu_activate('%s'); </script>
    </li>
""" % (type,type)
      if quiz.quiz_file == "mathquiz-manual":
        menu+='    <li class="heading"> Manual Contents: </li>'
      elif len(quiz.quiz.discussion_list)>0:
        menu+= '<li class="heading"> Discussion: </li>'
      menu+='  </ul>\n'
    else:
      menuname = "Current Students"
      menu += '[@@ URLplus=[^^~currentmenu^^] @@]\n'
  return menuname, menu

def write_web_page(quiz):
  page={}
  page['UNIT_OF_STUDY,CODE']='QUIZ'
  pagename=quiz.quiz_file+'.html'
  courseurl=quiz.course['url']+'Quizzes'
  sms_menu_name, sms_menu=SMS_menu(quiz)
  if pagename in [ 'mathquiz-manual.html','credits.html']:
    page['UNIT_OF_STUDY,tablevel']='internal'
  else:
    page['UNIT_OF_STUDY,tablevel']='current'
  page['UNIT_OF_STUDY,menuname']=sms_menu_name
  page['UNIT_OF_STUDY,pagetitle']=quiz.title
  page['UNIT_OF_STUDY,title']= ''
  page['meta_string']=quiz.header
  page['head_data_string']= quiz.javascript+initialise_SMS_Menus(quiz)+quiz.css
  page['breadcrumbs_string']=SMS_breadcrumbs(quiz)
  page['menu_string']=sms_menu+quiz.side_menu
  page['page_body_string']=quiz.page_body
  page['nopreview'] = ''
  return wp.processtemplate(page,{},courseurl[3:],pagename)[0]
