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
def headData(quiz,course,currentQ,qTotal):
  if course['code']=="MATH1001":
    content="MATH1001/1901<br>Quizzes"
  elif course['code']=="MATH1002":
    content="MATH1002/1902<br>Quizzes"
  elif course['code']=="MATH1005":
    content="MATH1005/1905<br>Quizzes"
  else:
    content="%s Quizzes" % course['code']
  hd = """<script src="%sjavascript/mathquiz.js" type="text/javascript"></script>
<script language="javascript" type="text/javascript">
<!--
    var QuizURI='%sQuizzes'
    var QuizContents='%s'
    var currentQ=%s
    """ % (MathQuizURL,course['url'],content,currentQ)
  if qTotal>0:
    hd += "    MathQuizInit(%d);\n" % qTotal
  hd += """-->
</script>
<script src="quiztitles.js" type="text/javascript"></script>
"""
  if quiz=="index":
    hd += """<script type="text/javascript" language="javascript" src="/u/SMS/web2010/js/ResearchSubmenu.js"></script>
<script type="text/javascript" language="javascript" src="/u/SMS/web2010/js/JMSubmenu.js"></script>
<script type="text/javascript" language="javascript" src="/u/SMS/web2010/js/IMSubmenu.js"></script>
<script type="text/javascript" language="javascript" src="/u/SMS/web2010/js/SMSubmenu.js"></script>
<script type="text/javascript" src="/u/SMS/web2010/js/QSubmenu.js"></script>
"""
  elif quiz in [ 'mathquiz-manual','credits']:
    hd += '<script type="text/javascript" src="/u/SMS/web2010/js/QSubmenu.js"></script>\n'
  else:
    hd += '<script type="text/javascript" src="/u/SMS/web2010/js/CourseQSubmenu.js"></script>\n'
  return hd

# breadcrumbs line
def breadcrumbs(doc, course):
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
def menu(doc, course):
  menuname = 'MATHQUIZ'
  m = ''
  if len(course['name'])>0:
    if len(doc.quizList)==0:  # not on a quiz index page
      if  doc.src in ["mathquiz-manual","credits"]: menu="QSubmenu"
      else: menu="CourseQSubmenu"
      m += """<ul class="navmenu">
    <li>
      <div class="dropdownroot" id="%s"></div>
      <script type="text/javascript"> domMenu_activate('%s'); </script>
    </li>
""" % ( menu,menu)
      if doc.src == "mathquiz-manual":
        m+="""<li class="heading">
       Manual Contents:
    </li>
"""
      elif len(doc.discussionList)>0:
	  m += """<li class="heading">
       Discussion:
    </li>
"""
    else:
      menuname = "Current Students"
      m += '[@@ URLplus=[^^~currentmenu^^] @@]\n'
  return menuname, m

def printQuizPage(doc,meta,headData,menuname,menu,course,pagebody):
  page={}
  page['UNIT_OF_STUDY,CODE']='QUIZ'
  pagename=doc.src+'.html'
  courseurl=course['url']+'Quizzes'
  if pagename in [ 'mathquiz-manual.html','credits.html']:
    page['UNIT_OF_STUDY,tablevel']='internal'
  else:
    page['UNIT_OF_STUDY,tablevel']='current'
  page['UNIT_OF_STUDY,menuname']= menuname
  page['UNIT_OF_STUDY,pagetitle']=doc.title
  page['UNIT_OF_STUDY,title']= ''
  page['meta_string']=meta
  page['head_data_string']=headData
  page['breadcrumbs_string']=breadcrumbs(doc, course)
  page['menu_string']=menu
  page['page_body_string']=pagebody
  page['nopreview'] = ''
  print string.replace(writepagenew.processtemplate(page,{},courseurl[3:],pagename)[0],'/>','>')
