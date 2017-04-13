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

sms_quiz_specifications = '  <script type="text/javascript">var QuizURI="{}Quzzes";var QuizContents="{}";</script>\n'
sms_research_menu  = '  <script type="text/javascript" src="/u/SMS/web2015/js/ResearchSubmenu.js"></script>\n'
sms_qsubmenu = '  <script type="text/javascript" src="/u/SMS/web2015/js/QSubmenu.js"></script>\n'
sms_course_qsubmenu = '  <script type="text/javascript" src="/u/SMS/web2015/js/CourseQSubmenu.js"></script>\n'
quiz_titlesx= r'''// construct customMenu for the fancy pull-down menu on narrow screens
var customMenu='<ul role="menu" class="togglemenu" style="height:0px; transition:height 1s;">\n'
for (q=0; q<QuizTitles.length; q++) {
    if (thisPage != QuizTitles[q][1]) {
       customMenu +='<li role="menuitem">\n<a href="'+QuizTitles[q][1]+'">'+QuizTitles[q][0]+'</a>\n</li>\n';
    }
}
customMenu +='</ul>\n'
document.getElementById("custom-menu").innerHTML=customMenu;
menulist.push('custom');
'''

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
  hd=sms_quiz_specifications.format(web_page.course['url'],content)
  if web_page.quiz_file=="index":
    hd += sms_research_menu+sms_qsubmenu
  elif web_page.quiz_file in [ 'mathquiz-manual','credits']:
    hd += sms_qsubmenu
  else:
    hd += sms_course_qsubmenu

  return hd

# breadcrumbs line
def SMS_breadcrumbs(doc):
  if doc.course['code']=="MathQuiz":
    level = 'MOW'
    year  = 'GEM'
  elif len(doc.course['code'])>4:
    level={'1':'JM', '2':'IM', '3':'SM', 'o':'', 'Q':''}[doc.course['code'][4]]
    year ={'JM':'Junior', 'IM':'Intermediate', 'SM':'Senior', '':''}[level]
    level='UG/'+level
  else:
    level=''
    year=''

  bc = """<div class="breadcrumb moved"><b>You are here: &nbsp;&nbsp;</b><a href="/">Maths &amp; Stats Home</a> /"""
  if doc.quiz_file=="mathquiz-manual":
    bc += """<a href="/u/MOW/">GEM</a> / MathQuiz"""
  elif doc.quiz_file=="credits":
    bc += """<a href="/u/MOW/">GEM</a> /
             <a href="/u/MOW/MathQuiz/doc/mathquiz-manual.html">MathQuiz</a> /
	     Credits"""
  else:
    bc += """
             <a href="/u/UG/">Teaching program</a> /
             <a href="/u/%s/">%s</a> /
             <a href="%s">%s</a> /
""" % ( level, year, doc.course['url'] , doc.course['code'])
    if doc.quiz_file=="index":
      bc += "             Quizzes\n"
    else:
      bc += """             <a href="%s">Quizzes</a> / %s
""" % (doc.course['quizzes_url'],doc.quiz.bread_crumb)

  bc += "</div>"
  return bc+no_script

# the left side menu
def SMS_menu(doc):
    # append the quiz_titlesx string to the quiztitles.js
    if len(doc.quiz.quiz_list)>0:
        with open('quiztitles.js','a') as quiztitles:
            quiztitles.write('\n'+quiz_titlesx)

    menu = ''
    if len(doc.quiz.course['name'])>0:
        menu_name = 'MathQuiz'
        if len(doc.quiz.quiz_list)==0:  # not on a quiz index page
            if  doc.quiz_file in ["mathquiz-manual","credits"]: 
                type="QSubmenu"
            else: 
                type="CourseQSubmenu"
            heading = 'Manual contents' if doc.quiz_file=='mathquiz-manual' else \
                      'Discussion' if len(doc.quiz.discussion_list)>0 else ''
            menu += nav_menu.format(menu=type, heading='' if heading=='' else '<li>{}</li>'.format(heading))
    else:
        menu_name = "Current Students"
        menu += '[@@ URLplus=[^^~currentmenu^^] @@]\n'
    return menu_name, menu

def write_web_page(doc):
    sms_menu_name, sms_menu=SMS_menu(doc)
    page=dict(
      meta_string = doc.header,
      head_data_string =  doc.javascript+initialise_SMS_Menus(doc)+doc.css,
      breadcrumbs_string = SMS_breadcrumbs(doc),
      menu_string = sms_menu+doc.side_menu,
      page_body_string = doc.quiz_header+doc.quiz_questions+doc.mathquiz_init,
      nopreview = ''
    )
    for (key, value) in [('CODE','QUIZ'),
                         ('menuname', sms_menu_name),
                         ('pagetitle', doc.title), ('title',''),
                         ('no-compmenu', 'y'),
                         ('tablevel', 'internal' if doc.quiz_file in ['mathquiz-manual','credits'] else '')]:
      page['UNIT_OF_STUDY,'+key] = value

    # doc.course['quizzes_url'][3:][:-1] looks like '/u/UG/JM/MATH1003/Quizzes/'
    # using [3:][:-1] we doctor it to look like 'UG/JM/MATH1003/Quizzes'
    return sms_write_page(page, {}, doc.course['quizzes_url'][3:][:-1], doc.quiz_file+'.html')[0]
