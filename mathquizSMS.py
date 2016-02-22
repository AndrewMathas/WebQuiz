#!/usr/bin/python
"""  mathquizConfig.py | 2005 Version 4.3 | Andrew Mathas
     2010 minor hacking by Bob Howlett

     Python configuration file for the mathquiz system. This
     file controls the local components of the quiz page.
"""
import writepagenew, string

# -----------------------------------------------------

# A relative URL which specifies the location of mathquizzes
# system files on the web server.
MathQuizURL="/u/MOW/MathQuiz/"
Images=MathQuizURL+'Images/'

NoScript = """
<noscript><div style="margin:0px 10px 0px 10px; padding:0"><b>If you are reading this message either your
    browser does not support JavaScript or else JavaScript
    is not enabled.  You will need to enable JavaScript and
    then reload this page before you can use this quiz.</b></div></noscript>
"""


# -----------------------------------------------------
# stuff to go in the <head> ... </head> section of the page
def initialise_SMS_Menus(quiz,course):
  if course['code']=="MATH1001":
    content="MATH1001/1901<br>Quizzes"
  elif course['code']=="MATH1002":
    content="MATH1002/1902<br>Quizzes"
  elif course['code']=="MATH1005":
    content="MATH1005/1905<br>Quizzes"
  else:
    content="%s Quizzes" % course['code']
  hd="""  <script language="javascript" type="text/javascript">
  <!--
    var QuizURI='%sQuizzes'
    var QuizContents='%s'
  -->
  </script>
""" % (course['url'],content)
  if quiz=="index":
    hd += """  <script type="text/javascript" language="javascript" src="/u/SMS/web2010/js/ResearchSubmenu.js"></script>
  <script type="text/javascript" language="javascript" src="/u/SMS/web2010/js/JMSubmenu.js"></script>
  <script type="text/javascript" language="javascript" src="/u/SMS/web2010/js/IMSubmenu.js"></script>
  <script type="text/javascript" language="javascript" src="/u/SMS/web2010/js/SMSubmenu.js"></script>
  <script type="text/javascript" src="/u/SMS/web2010/js/QSubmenu.js"></script>
"""
  elif quiz in [ 'mathquiz-manual','credits']:
    hd += '  <script type="text/javascript" src="/u/SMS/web2010/js/QSubmenu.js"></script>\n'
  else:
    hd += '  <script type="text/javascript" src="/u/SMS/web2010/js/CourseQSubmenu.js"></script>\n'
  return hd

# breadcrumbs line
def SMS_breadcrumbs(doc, course):
  if course['code']=="MathQuiz":
    level = 'MOW'
    year  = 'GEM'
  elif len(course['code'])>4:
    level={'1':'JM', '2':'IM', '3':'SM', 'o':'', 'Q':''}[course['code'][4]]
    year ={'JM':'Junior', 'IM':'Intermediate', 'SM':'Senior', '':''}[level]
    level='UG/'+level
  else:
    level=''
    year=''

  bc = """<div class="breadcrumb moved"><b>You are here: &nbsp;&nbsp;</b><a href="/">Maths &amp; Stats Home</a> /"""
  if doc.src=="mathquiz-manual":
    bc += """<a href="/u/MOW/">GEM</a> / MathQuiz"""
  elif doc.src=="credits":
    bc += """<a href="/u/MOW/">GEM</a> /
             <a href="/u/MOW/MathQuiz/doc/mathquiz-manual.html">MathQuiz</a> /
	     Credits"""
  else:
    bc += """
             <a href="/u/UG/">Teaching program</a> /
             <a href="/u/%s/">%s</a> /
             <a href="%s">%s</a> /
""" % ( level, year, course['url'] , course['code'])
    if doc.src=="index":
      bc += "             Quizzes\n"
    else:
      bc += """             <a href="%s">Quizzes</a> / %s
""" % (course['quizzes'],doc.breadCrumb)
  bc += "</div>"
  return bc+NoScript

# the left side menu
def SMS_menu(doc,course):
  menu = ''
  if len(course['name'])>0:
    menuname = 'MATHQUIZ'
    if len(doc.quizList)==0:  # not on a quiz index page
      if  doc.src in ["mathquiz-manual","credits"]: type="QSubmenu"
      else: type="CourseQSubmenu"
      menu += """  <ul class="navmenu">
    <li>
      <div class="dropdownroot" id="%s"></div>
      <script type="text/javascript"> domMenu_activate('%s'); </script>
    </li>
""" % (type,type)
      if doc.src == "mathquiz-manual":
        menu+="""    <li class="heading">
       Manual Contents:
    </li>
"""
      elif len(doc.discussionList)>0:
	  menu+= """<li class="heading">G
       Discussion:
    </li>
"""
      menu+='  </ul>\n'
    else:
      menuname = "Current Students"
      menu += '[@@ URLplus=[^^~currentmenu^^] @@]\n'
  return menuname, menu

def printQuizPage(html, doc):
  page={}
  page['UNIT_OF_STUDY,CODE']='QUIZ'
  pagename=doc.src+'.html'
  courseurl=html.course['url']+'Quizzes'
  sms_menu_name, sms_menu=SMS_menu(doc, html.course)
  if pagename in [ 'mathquiz-manual.html','credits.html']:
    page['UNIT_OF_STUDY,tablevel']='internal'
  else:
    page['UNIT_OF_STUDY,tablevel']='current'
  page['UNIT_OF_STUDY,menuname']=sms_menu_name
  page['UNIT_OF_STUDY,pagetitle']=doc.title
  page['UNIT_OF_STUDY,title']= ''
  page['meta_string']=html.header
  page['head_data_string']= html.javascript+initialise_SMS_Menus(doc.src,html.course)+html.css
  page['breadcrumbs_string']=SMS_breadcrumbs(doc, html.course)
  page['menu_string']=sms_menu+html.side_menu
  page['page_body_string']=html.pagebody
  page['nopreview'] = ''
  print string.replace(writepagenew.processtemplate(page,{},courseurl[3:],pagename)[0],'/>','>')
