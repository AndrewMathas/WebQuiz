#!/usr/bin/python
"""  mathquizConfig.py | 2005 Version 4.3 | Andrew Mathas

     Python configuration file for the mathquiz system. This
     file controls the local components of the quiz page.
"""

# -----------------------------------------------------

# A relative URL which specifies the location of mathquizzes
# system files on the web server.
MathQuizURL="/u/MOW/MathQuiz/"
Images=MathQuizURL+'Images/'

# -----------------------------------------------------
def printInitialization(quiz,course,currentQ,qTotal,level):
  if course['code']=="MATH1001":
    content="MATH1001/1901<br>Quizzes"
  elif course['code']=="MATH1002":
    content="MATH1002/1902<br>Quizzes"
  elif course['code']=="MATH1005":
    content="MATH1005/1905<br>Quizzes"
  else:
    content="%s Quizzes" % course['code']

  print """<link rel="stylesheet" href="/u/UG/styles/SMS_internal1.css" type="text/css">
<link rel="stylesheet" href="/u/UG/styles/SMS_style1.css" type="text/css">
<link rel="stylesheet" href="/u/UG/styles/menustyle1.css" type="text/css">"""

  print """<script src="%sjavascript/mathquiz.js" type="text/javascript"></script>
<script language="javascript" type="text/javascript">
<!--
    var thisPage='%sQuizzes/%s.html'
    var QuizURI='%sQuizzes'
    var QuizContents='%s'
    var currentQ=%s
    var menulevel = '%s'
    var tablevel = 'current'""" % (MathQuizURL,course['url'],quiz,course['url'],content,currentQ,level)
  if qTotal>0:
    print "    MathQuizInit(%d);" % qTotal
  print """-->
</script>
<script src="quiztitles.js" type="text/javascript"></script>
<script type="text/javascript" language="javascript" src="/u/UG/newstyle/domLib.js"></script>
<script type="text/javascript" language="javascript" src="/u/UG/newstyle/domMenu_var.js"></script>
<script type="text/javascript" language="javascript" src="/u/UG/newstyle/TabsMenu.js"></script>"""
  if quiz=="index":
    print """<script type="text/javascript" language="javascript" src="/u/UG/newstyle/ResearchSubmenu.js"></script>
<script type="text/javascript" language="javascript" src="/u/UG/newstyle/JMSubmenu.js"></script>
<script type="text/javascript" language="javascript" src="/u/UG/newstyle/IMSubmenu.js"></script>
<script type="text/javascript" language="javascript" src="/u/UG/newstyle/SMSubmenu.js"></script>
<script type="text/javascript" src="/u/UG/newstyle/QSubmenu.js"></script>"""
  elif quiz=="mathquiz-manual":
    print """<script type="text/javascript" src="/u/UG/newstyle/QSubmenu.js"></script>"""
  else:
    print """<script type="text/javascript" src="/u/UG/newstyle/CourseQSubmenu.js"></script>"""

# the top of the quiz pages
def printTableTop(doc, level, year, course):
  print """<a name="top"></a>
  <div class="role">

  <div class="title">School of Mathematics and Statistics</div>
  <div class="title" style="clear: both; margin-top: 2px;">Junior</div>
  <div> <a href="http://www.usyd.edu.au/"><img src="/u/UG/Images/logo_blue_01.gif" alt="The University of Sydney" style="border: 0px none ;" height="52" width="227"></a></div>
</div>
<div class="nav_bar">
  <div class="breadcrumb"><a href="/">Maths &amp; Stats Home</a> /"""
  if doc.src=="mathquiz-manual":
    print """<a href="/u/MOW/">GEM</a> / MathQuiz"""
  elif doc.src=="credits":
    print """<a href="/u/MOW/">GEM</a> / 
             <a href="/u/MOW/MathQuiz/doc/mathquiz-manual.html">MathQuiz</a> / 
	     Credits"""
  else:
    print """<a href="/u/UG/">Teaching program</a> /
             <a href="/u/%s/">%s</a> /
             <a href="%s">%s</a> /""" % ( level, year, course['url'] , course['code'])
    if doc.src=="index":
      print "Quizzes"
    else:
      print """ <a href="%s">Quizzes</a> / %s """ % (course['quizzes'],doc.breadCrumb)
  print "</div>"
  print """ <div class="global">
    <div style="padding: 7px 0px 0px;"><a href="http://www.usyd.edu.au/"><img src="/u/UG/Images/small_crest.gif" style="border: 0px none ;" alt="The University of Sydney" height="16" width="18"></a></div>
    <div style="padding: 8px 5px 0px 2px;"><a href="http://www.usyd.edu.au/">Usyd Home</a></div>
    <div style="padding: 7px 0px 0px;"><a href="http://www.usyd.edu.au/"><img src="/u/UG/Images/lion_sml.gif" style="border: 0px none ;" alt="MyUni" height="18" width="18"></a></div>
    <div style="padding: 8px 5px 0px 2px;"><a href="http://db.auth.usyd.edu.au/myuni/myuni.stm">MyUni</a></div>
    <div><a href="http://www.library.usyd.edu.au/">Library</a></div>
    <div><a href="/u/SiteMap/">Sitemap</a></div>

    <div style="padding: 0pt 3px 0pt 0pt;">
      <form style="margin: 0pt; padding: 0pt; display: inline;" 
      action="http://search.usyd.edu.au/search/search.cgi" method="get" name="form1" id="form1">
      <input class="qlinks" name="query" size="16" value="usyd search " 
             onclick="this.value=''" type="text">
      <input name="collection" value="Usyd" type="hidden">
      <input name="num_ranks" value="10" type="hidden">
      <input src="/u/UG/Images/search_go.gif" style="border: 0px none ; width: 20px; height: 18px;" alt="Enter search string to activate 'Go' button" name="g_search" id="g_search" value="Go" align="middle" type="image">
      </form></div>
  </div>
</div>
<div class="lmspcr"><img src="/u/UG/Images/pix.gif" class="decor" alt="spcr"></div>
<div id="TabsMenu" class="dropdownroot" style="padding-top:4px; padding-left:5px; border-bottom: solid 1px #39628B; background-image:none"></div>

<script type="text/javascript"> domMenu_activate('TabsMenu'); </script>

<table width="100%" border="0" cellspacing="0" cellpadding="0">
<tr>
  <td width="160" valign="top" class="nav">
<!-- start of side menu -->"""

# the left hand menu for the index page
def printIndexSideMenu():
  print """<ul class="navmenu">
<li class="navmenu"><a href="/u/About/" class="nav">About the School</a>

  <ul class="navsubmenu">
    <li class="navsubmenu"><a href="/u/About/Students.html" class="nav">Resources for students</a></li>
  </ul></li>

<li class="navmenu"><a href="/u/About/Contact.html" class="nav">Contacting us</a></li>
<li class="navmenu"><a href="/u/About/people/" class="nav">People</a></li>
<li class="navmenu" style="list-style-image: none; list-style: none;"><div class="dropdownroot" id="ResearchSubmenu" style="width: 100%"></div>
      <script type="text/javascript">domMenu_activate('ResearchSubmenu');
      </script></li>
<li class="navmenu"><a href="/u/UG/" class="nav">Teaching Program</a>
  <ul class="navsubmenu">
    <li class="navsubmenu"><a class="nav" href="/u/UG/SpecialConsideration.html">Special Consideration</a></li>
    <li class="navsubmenu"><a class="nav" href="/u/UG/pdftips.html">pdf tips</a></li>

    <li class="navsubmenu"><a class="nav" href="/u/UG/asscover.pdf">Assignment cover sheet</a></li>
    <li class="navsubmenu"><a class="nav" href="/u/UG/mathstattimetable.html">Timetables</a></li>
  </ul></li>
<li class="navselected" style="list-style-image: none; list-style: none;"><div class="selspacing"><div class="dropdownroot" id="JuniorSubmenu" style="width: 100%"></div></div>
       <script type="text/javascript">domMenu_activate('JuniorSubmenu');
       </script>
  <ul class="navselsubmenu">
    <li class="navsubmenu"><a class="nav" href="/u/UG/JM/#Units of Study">Units of study</a></li>

  </ul>
<li class="navmenu" style="list-style-image: none; list-style: none;"><div class="selspacing"><div class="dropdownroot" id="InterSubmenu" style="width: 100%"></div></div>
       <script type="text/javascript">domMenu_activate('InterSubmenu');
       </script>
<li class="navmenu" style="list-style-image: none; list-style: none;"><div class="selspacing"><div class="dropdownroot" id="SeniorSubmenu" style="width: 100%"></div></div>
       <script type="text/javascript">domMenu_activate('SeniorSubmenu');
       </script>
<li class="navmenu"><a href="/u/UG/HM" class="nav">Honours</a>
<li class="navmenu" style="list-style-image: none; list-style: none;">
  <div class="selspacing">
    <div class="dropdownroot" id="QSubmenu" style="width: 100%"></div></div>

       <script type="text/javascript">domMenu_activate('QSubmenu');
       </script></li>
<li class="navmenu"><a href="/u/BC/" class="nav">Bridging Courses</a></li>
<li class="navmenu"><a href="/u/UG/common/SS/" class="nav">Summer School</a></li>
<li class="navmenu"><a href="/u/PG/" class="nav">Postgraduate</a></li>
<li class="navmenu"><a href="/u/SiteMap/" class="nav">Sitemap</a></li>
<li class="navmenu"><a href="/u/About/search.html" class="nav">School Search</a></li>
</ul>
"""
