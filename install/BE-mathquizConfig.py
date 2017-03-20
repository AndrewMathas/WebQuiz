#!/usr/bin/python
"""  mathquizConfig.py | 2005 Version 4.2 | Andrew Mathas

     Python configuration file for the mathquiz system. This
     file controls the local components of the quiz page.
"""

# -----------------------------------------------------

# A relative URL which specifies the location of mathquizzes
# system files on the web server.
URL="/u/MOW/MathQuiz/"

# Local css for layout of quiz pages.
QuizCss="""<link rel="stylesheet" href="%s/css/usyd_internal.css" type="text/css">
<link rel="stylesheet" href="/u/UG/styles/menustyle.css" type="text/css">""" % URL

# Local javascript to be included on every quiz page.
QuizScripts="""<script type="text/javascript" src="/u/UG/newstyle/domMenu_alt.js"></script>
<script type="text/javascript" src="/u/UG/newstyle/QuizSubmenu.js"></script>""" 

# Local css to be included on the index page.
IndexCss=""

# Local javascript to be included on the index page.
IndexScripts="""<script type="text/javascript" src="/u/UG/newstyle/ResearchSubmenu.js"></script>
<script type="text/javascript" src="/u/UG/newstyle/JMSubmenu.js"></script>
<script type="text/javascript" src="/u/UG/newstyle/IMSubmenu.js"></script>
<script type="text/javascript" src="/u/UG/newstyle/SMSubmenu.js"></script>"""

# -----------------------------------------------------

# the top of the quiz pages
def printTableTop(level, year, course):
  Images=URL+'Images/'
  top="""<a name="top"></a>
<table width="100%%" border="0" cellspacing="0" cellpadding="0" class="role">
  <tr>
      <td colspan="2"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" 
        hspace="375" vspace="0" class="decor"></td>
  </tr>
  <tr>
      <td width="227"><a href="http://www.usyd.edu.au"><img src=\""""+Images+"""logo_blue_01.gif" width="227" height="52" 
           alt="The University of Sydney" border="0"  class="decor"></a></td>
      <td width="*" style="background-image: url("""+Images+"""logo_blue_02.gif); background-position: top left; background-repeat: no-repeat" class="role">
      <div align="right">
      School&nbsp;of&nbsp;Mathematics&nbsp;and&nbsp;Statistics&nbsp;&nbsp;<br>
                         MathQuiz&nbsp;&nbsp;</div>
    </td>
  </tr>
  </table>
  <table cellpadding="0" cellspacing="0" border="0" width="100%%">
  <tr>
      <td style="background-image: url("""+Images+"""breadcrumb_blend.gif)" height="21" 
        nowrap class="breadcrumb">&nbsp;<a href="/" class="breadcrumb">Maths & Stats </a> /
          <a href="/u/UG/" class="breadcrumb">Teaching program</a> /
              <a href="/u/UG/%s/" class="breadcrumb">%s</a> /
              <a href="%s" class="breadcrumb">%s</a> /
              Quizzes&nbsp;&nbsp;</td>
      <td style="background-image: url("""+Images+"""breadcrumb_blend.gif)" height="21" 
        align="right">
      <table border="0" cellspacing="0">
        <tr>
            <td valign="middle"><a href="http://www.usyd.edu.au"><img src=\""""+Images+"""small_crest.gif" width="18" height="16" border="0" 
	         alt="The University of Sydney"></a></td>
            <td nowrap valign="middle" class="global">
	     <a href="http://www.usyd.edu.au" class="global">USyd </a>&nbsp;</td>
            <td valign="middle"><a href="http://db.auth.usyd.edu.au/myuni/myuni.stm"><img src=\""""+Images+"""lion_sml.gif" width="18" height="18" border="0" 
	        alt="MyUni"></a></td>
            <td nowrap valign="middle" class="global">
	     <a href="http://db.auth.usyd.edu.au/myuni/myuni.stm" class="global">
	        MyUni</a>&nbsp;</td>
            <td nowrap valign="middle" class="global">
	     <a href="http://www.library.usyd.edu.au/" class="global">
	        Library</a>&nbsp;</td>
            <td nowrap valign="middle" class="global">
	    <a href="/u/SiteMap/" class="global">Sitemap</a>&nbsp;</td>
            <td nowrap valign="middle" class="search">
            <form style="margin-top: 0px; margin-bottom: 0px" method="get" 
	          action="http://search.usyd.edu.au/search/search.cgi">
              <input type="text" name="query" size="9" class="search" value="Search" 
	             onClick="this.value=''">
              <input type=hidden name="collection" value="Usyd">
              <input type=hidden name="num_ranks" value="10">
              <input type=image src=\""""+Images+"""search_go.gif" 
	             alt="Start search" name="g_search" value="Go"></form></td>
        </tr>
      </table>
    </td>
  </tr>
  <tr>
      <td colspan="2" bgcolor="#CCCC66" height="1"><img
    src=\""""+Images+"""navy.gif" width="1" height="1" hspace="100%%" alt=""  class="decor"></td>
  </tr>
</table>
<table width="100%%" border="0" cellspacing="0" cellpadding="0">
  <tr>
      <td colspan="20"><img src=\""""+Images+"""navy.gif" width="1" height="1" vspace="2" alt="" 
        class="decor"></td>
  </tr>
  <tr>
      <td width="5"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" hspace="2"></td>
      <td width="4" valign="top" class="tabnames"><img src=\""""+Images+"""tabLeftCorner.gif" width="4" height="22" alt=""></td>
      <td nowrap class="tabnames">
      <div align="center">&nbsp;<a href="/u/About/" class="tabnames">About the School</a>&nbsp;</div>
    </td>
      <td width="4" valign="top" class="tabnames"><img src=\""""+Images+"""tabRightCorner.gif" width="4" height="22" alt=""></td>
      <td width="4" valign="top" class="tabnames"><img src=\""""+Images+"""tabLeftCorner.gif" width="4" height="22" alt=""></td>
      <td nowrap class="tabnames"><div align="center">&nbsp;<a href="/res/Research.html" class="tabnames">Research Activities</a>&nbsp;</div>
    </td>
      <td width="4" valign="top" class="tabnames"><img src=\""""+Images+"""tabRightCorner.gif" width="4" height="22" alt=""></td>
      <td width="4" valign="top" class="tabnames"><img src=\""""+Images+"""tabLeftCorner.gif" width="4" height="22" alt=""></td>
      <td nowrap class="tabnames"><div align="center">&nbsp;<a href="/u/PS/" class="tabnames">For prospective students</a>&nbsp;</div>
    </td>
    <td width="4" valign="top" class="tabnames"><img src=\""""+Images+"""tabRightCorner.gif" width="4" height="22" alt=""></td>
    <td width="4" valign="top" class="tabnamesin"><img src=\""""+Images+"""tabLeftCorner.gif" width="4" height="22" alt=""></td>
    <td nowrap class="tabnamesin"><div align="center">&nbsp;<a href="/u/UG/" class="tabnames">For current students</a>&nbsp;</div>
    </td>
    <td width="4" valign="top" class="tabnamesin"><img src=\""""+Images+"""tabRightCorner.gif" width="4" height="22" alt=""></td>
    <td width="4" valign="top" class="tabnames"><img src=\""""+Images+"""tabLeftCorner.gif" width="4" height="22" alt=""></td>
    <td nowrap class="tabnames"><div align="center">&nbsp;<a href="/local.html" class="tabnames">School Internal Web Site</a>&nbsp;</div>
    </td>
    <td width="4" valign="top" class="tabnames"><img src=\""""+Images+"""tabRightCorner.gif" width="4" height="22" alt=""></td>
    <td width="1000" bgcolor="#ffffff"></td>
  </tr>
  <tr >
      <td colspan="20" bgcolor="#AD2431" class="tabnames"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" hspace="250" class="decor">
    </td>
  </tr>
</table>
<table width="100%%" height="100%%" border="0" cellspacing="0" cellpadding="0">
<tr>
  <td width="160" valign="top" class="nav">
<!-- start of side menu -->
<table width="160" border="0" cellspacing="0" cellpadding="0" class="nav">
  <tr>
      <td height="2" colspan="3" class="decor">
      <img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" vspace="2"></td>
  </tr>
  <tr>
      <td height="5" colspan="3">
      <img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" vspace="5" class="decor"></td>
  </tr>"""
  print top % ( level, year, course['url'], course['code'] )

# the left hand menu for the index page
def printIndexSideMenu():
  Images=URL+'Images/'
  print """<!-- start of side menu -->
<tr valign="top">
  <td nowrap>&nbsp;<img src=\""""+Images+"""right_arrow.gif" alt="" width="9" height="9">&nbsp;</td>
  <td colspan="2"><a href="/u/About/" class="nav">About the School</a></td>
</tr>
<tr valign="top">
  <td class="nav"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt=""></td>
  <td nowrap><img src=\""""+Images+"""bullet.gif" width="6" height="9" alt="" hspace="3" vspace="3"></td>
  <td width="100%%" class="nav"><a href="/u/About/Students.html" class="nav">More links for students</a></td>
</tr>
<tr>
  <td height="7" colspan="3"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" vspace="3" class="decor"></td>
</tr>
<tr valign="top" bgcolor="#FFFFFF">
  <td class="menuDivLine" colspan="3"><img src=\""""+Images+"""navy.gif" width="1" height="2" alt="" class="decor"></td>
</tr>
<tr>
  <td height="7" colspan="3"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" vspace="3" class="decor"></td>
</tr>
<tr valign="top">
  <td nowrap>&nbsp;<img src=\""""+Images+"""right_arrow.gif" alt="" width="9"
height="9">&nbsp;</td>
  <td colspan="2"><a href="/u/About/Contact.html" class="nav">Contacting us</a></td>
</tr>
<tr>
  <td height="7" colspan="3"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" vspace="3" class="decor"></td>
</tr>
<tr valign="top" bgcolor="#FFFFFF">
  <td class="menuDivLine" colspan="3"><img src=\""""+Images+"""navy.gif" width="1" height="2" alt="" class="decor"></td>
</tr>
<tr>
  <td height="7" colspan="3"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" vspace="3" class="decor"></td>
</tr>
<tr valign="top">
  <td nowrap>&nbsp;<img src=\""""+Images+"""right_arrow.gif" alt="" width="9"
height="9">&nbsp;</td>
  <td colspan="2"><a href="/u/About/people.html" class="nav">People</a></td>
</tr>
<tr>
  <td height="7" colspan="3"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" vspace="3" class="decor"></td>
</tr>
<tr valign="top" bgcolor="#FFFFFF">
  <td class="menuDivLine" colspan="3"><img src=\""""+Images+"""navy.gif" width="1" height="2" alt="" class="decor"></td>
</tr>
<tr>
  <td height="7" colspan="3"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" vspace="3" class="decor"></td>
</tr>
<tr valign="top">
  <td nowrap>&nbsp;<img src=\""""+Images+"""right_arrow.gif" alt="" width="9"
height="9">&nbsp;</td>
  <td nowrap colspan="2"><a style="visibility: hidden; line-height: 0px" class="nav" href="/res/Research.html">Research</a><div class="dropdownroot" id="ResearchSubmenu"></div>
  <script type="text/javascript">domMenu_activate('ResearchSubmenu');</script></td>
</tr>
<tr>
  <td height="7" colspan="3"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" vspace="3" class="decor"></td>
</tr>
<tr valign="top" bgcolor="#FFFFFF">
  <td class="menuDivLine" colspan="3"><img src=\""""+Images+"""navy.gif" width="1" height="2" alt="" class="decor"></td>
</tr>
<tr>
  <td height="7" colspan="3"
    class="decor"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" vspace="3"></td>
</tr>
  <tr valign="top">
  <td nowrap>&nbsp;<img src=\""""+Images+"""right_arrow.gif" alt="" width="9" height="9">&nbsp;</td>
  <td colspan="2"><a href="/u/UG/" class="nav">Undergraduate Teaching</a></td>
</tr>
<tr>
  <td valign="top" colspan="3" class="decor"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" vspace="1"></td>
</tr>
<tr valign="top">
  <td class="nav"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt=""></td>
  <td width="5" class="nav"><img src=\""""+Images+"""bullet.gif" width="6" height="9" alt="" hspace="3" vspace="3"></td>
  <td width="100%%" class="nav"><a class="nav" href="/u/UG/SpecialConsideration.html">Special Consideration</a></td>
</tr>
<tr>
  <td valign="top" colspan="3" class="decor"><img src=\""""+Images+"""navy.gif" width="1" height="5" alt="" vspace="3"></td>
</tr>
<tr valign="top" bgcolor="#FFFFFF">
  <td class="menuDivLine" colspan="3"><img src=\""""+Images+"""navy.gif" width="1" height="2" alt="" class="decor"></td>
</tr>
<tr>
  <td height="7" colspan="3" class="nav"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" vspace="3"></td>
</tr>
<tr valign="top">
  <td nowrap class="nav">&nbsp;<img src=\""""+Images+"""right_arrow.gif" alt="" width="9" height="9">&nbsp;</td>
  <td class="nav" colspan="2"><a style="visibility: hidden; line-height: 0px" class="nav" href="/u/UG/JM/">Junior</a><div class="dropdownroot" id="JuniorSubmenu"></div><script type="text/javascript"> domMenu_activate('JuniorSubmenu');</script></td>
</tr>
<tr>
  <td class="nav" colspan="3" height="6"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" vspace="3"></td>
</tr>
<tr valign="top" bgcolor="#FFFFFF">
  <td class="menuDivLine" colspan="3"><img src=\""""+Images+"""navy.gif" width="1" height="2" alt="" class="decor"></td>
</tr>
<tr>
  <td height="7" colspan="3"
    class="decor"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" vspace="3"></td>
</tr>
<tr valign="top">
  <td nowrap>&nbsp;<img src=\""""+Images+"""right_arrow.gif" alt="" width="9" height="9">&nbsp;</td>
  <td class="nav" colspan="2"><a style="visibility: hidden; line-height: 0px" class="nav" href="/u/UG/IM/">Intermediate</a><div class="dropdownroot" id="InterSubmenu"></div><script type="text/javascript"> domMenu_activate('InterSubmenu');</script></td>
</tr>
<tr>
  <td valign="top" colspan="3" class="decor"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" vspace="3"></td>
</tr>
<tr valign="top" bgcolor="#FFFFFF">
  <td class="menuDivLine" colspan="3"><img src=\""""+Images+"""navy.gif" width="1" height="2" alt="" class="decor"></td>
</tr>
<tr>
  <td height="7" colspan="3" class="decor"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" vspace="3"></td>
</tr>
<tr valign="top">
  <td nowrap>&nbsp;<img src=\""""+Images+"""right_arrow.gif" alt="" width="9" height="9">&nbsp;</td>
  <td class="nav" colspan="2"><a style="visibility: hidden; line-height: 0px" class="nav" href="/u/UG/SM/">Senior</a><div class="dropdownroot" id="SeniorSubmenu"></div><script type="text/javascript"> domMenu_activate('SeniorSubmenu'); </script></td>
</tr>
<tr>
  <td valign="top" colspan="3" class="decor"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" vspace="3"></td>
</tr>
<tr valign="top" bgcolor="#FFFFFF">
  <td class="menuDivLine" colspan="3"><img src=\""""+Images+"""navy.gif" width="1" height="2" alt="" class="decor"></td>
</tr>
<tr>
  <td height="7" colspan="3"
    class="decor"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" vspace="3"></td>
</tr>
<tr valign="top">
  <td nowrap >&nbsp;<img src=\""""+Images+"""right_arrow.gif" alt="" width="9"
height="9">&nbsp;</td>
  <td colspan="2"><a href="/u/UG/HM/" class="nav">Honours
</a></td>
</tr>
<tr>
  <td valign="top" colspan="3" class="decor"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" vspace="3"></td>
</tr>
<tr valign="top" bgcolor="#FFFFFF">
  <td class="menuDivLine" colspan="3"><img src=\""""+Images+"""navy.gif" width="1" height="2" alt="" class="decor"></td>
</tr>
<tr>
  <td height="7" colspan="3" class="decor"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" vspace="3"></td>
</tr>
<tr>
  <td valign="top" colspan="3" class="decor"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" vspace="3"></td>
</tr>
<tr valign="top" bgcolor="#FFFFFF">
  <td class="menuDivLine" colspan="3"><img src=\""""+Images+"""navy.gif" width="1" height="2" alt="" class="decor"></td>
</tr>
<tr>
  <td height="7" colspan="3" class="navselected"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" vspace="3"></td>
</tr>
<tr valign="top">
  <td nowrap class="navselected">&nbsp;<img src=\""""+Images+"""down_arrow.gif" alt="" width="9"
height="9">&nbsp;</td>
  <td colspan="2" class="navselected"><a href="/u/MOW/" class="nav">GEM
</a></td>
</tr>
<tr valign="top">
  <td class="navselected" class="navselected"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt=""></td>
  <td width="9" class="navselected"><img src=\""""+Images+"""bullet.gif" width="6" height="9" alt="" hspace="3" vspace="3"></td>
  <td width="100%%" class="navselected"><a style="visibility: hidden;
  line-height: 0px" class="navselected" href="/u/MOW/#quiz">quizzes</a><div class="dropdownroot" id="QuizSubmenu"></div><script type="text/javascript">
    domMenu_activate('QuizSubmenu');
</script></td>
</tr>
<tr>
  <td valign="top" colspan="3" class="navselected"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" vspace="3"></td>
</tr>
<tr valign="top" bgcolor="#FFFFFF">
  <td class="menuDivLine" colspan="3"><img src=\""""+Images+"""navy.gif" width="1" height="2" alt="" class="decor"></td>
</tr>
<tr>
  <td height="7" colspan="3"
    class="decor"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" vspace="3"></td>
</tr>
<tr valign="top">
  <td nowrap
>&nbsp;<img src=\""""+Images+"""right_arrow.gif" alt="" width="9"
height="9">&nbsp;</td>
  <td colspan="2"><a href="/u/BC/" class="nav">Bridging Courses
</a></td>
</tr>
<tr>
  <td valign="top" colspan="3" class="decor"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" vspace="3"></td>
</tr>
<tr valign="top" bgcolor="#FFFFFF">
  <td class="menuDivLine" colspan="3"><img src=\""""+Images+"""navy.gif" width="1" height="2" alt="" class="decor"></td>
</tr>
<tr>
  <td height="7" colspan="3"
    class="decor"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" vspace="3"></td>
</tr>
<tr valign="top">
  <td nowrap
>&nbsp;<img src=\""""+Images+"""right_arrow.gif" alt="" width="9"
height="9">&nbsp;</td>
  <td colspan="2"><a href="/u/UG/common/SS/" class="nav">Summer School
</a></td>
</tr>
<tr>
  <td valign="top" colspan="3" class="decor"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" vspace="3"></td>
</tr>
<tr valign="top" bgcolor="#FFFFFF">
  <td class="menuDivLine" colspan="3"><img src=\""""+Images+"""navy.gif" width="1" height="2" alt="" class="decor"></td>
</tr>
<tr>
  <td height="7" colspan="3"
    class="decor"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" vspace="3"></td>
</tr>
<tr valign="top">
  <td nowrap
>&nbsp;<img src=\""""+Images+"""right_arrow.gif" alt="" width="9"
height="9">&nbsp;</td>
  <td colspan="2"><a href="/u/PG/" class="nav">Postgraduate
</a></td>
</tr>
<tr>
  <td valign="top" colspan="3" class="decor"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" vspace="3"></td>
</tr>
<tr valign="top" bgcolor="#FFFFFF">
  <td class="menuDivLine" colspan="3"><img src=\""""+Images+"""navy.gif" width="1" height="2" alt="" class="decor"></td>
</tr>
<tr>
  <td height="7" colspan="3"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" vspace="3" class="decor"></td>
</tr>
<tr valign="top">
  <td nowrap>&nbsp;<img src=\""""+Images+"""right_arrow.gif" alt="" width="9"
height="9">&nbsp;</td>
  <td colspan="2"><a href="/w/tt/lecture.html" class="nav">Lecture timetable</a></td>
</tr>
<tr>
  <td height="7" colspan="3"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" vspace="3" class="decor"></td>
</tr>
<tr valign="top" bgcolor="#FFFFFF">
  <td class="menuDivLine" colspan="3"><img src=\""""+Images+"""navy.gif" width="1" height="2" alt="" class="decor"></td>
</tr>
<tr>
  <td height="7" colspan="3"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" vspace="3" class="decor"></td>
</tr>
<tr valign="top">
  <td nowrap>&nbsp;<img src=\""""+Images+"""right_arrow.gif" alt="" width="9"
height="9">&nbsp;</td>
  <td colspan="2"><a href="/w/tt/tutorial.html" class="nav">Tutorial timetable</a></td>
</tr>
<tr>
  <td height="7" colspan="3"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" vspace="3" class="decor"></td>
</tr>
<tr valign="top" bgcolor="#FFFFFF">
  <td class="menuDivLine" colspan="3"><img src=\""""+Images+"""navy.gif" width="1" height="2" alt="" class="decor"></td>
</tr>
<tr>
  <td height="7" colspan="3"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" vspace="3" class="decor"></td>
</tr>
<tr valign="top">
  <td nowrap>&nbsp;<img src=\""""+Images+"""right_arrow.gif" alt="" width="9"
height="9">&nbsp;</td>
  <td colspan="2"><a href="/u/SiteMap/" class="nav">Sitemap</a></td>
</tr>
<tr>
  <td height="7" colspan="3"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" vspace="3" class="decor"></td>
</tr>
<tr valign="top" bgcolor="#FFFFFF">
  <td class="menuDivLine" colspan="3"><img src=\""""+Images+"""navy.gif" width="1" height="2" alt="" class="decor"></td>
</tr>
<tr>
  <td height="7" colspan="3"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" vspace="3" class="decor"></td>
</tr>
<tr valign="top">
  <td nowrap>&nbsp;<img src=\""""+Images+"""right_arrow.gif" alt="" width="9"
height="9">&nbsp;</td>
  <td colspan="2"><a href="/Search.html" class="nav">School Search</a></td>
</tr>
<tr>
  <td height="7" colspan="3"><img src=\""""+Images+"""navy.gif" width="1" height="1" alt="" vspace="3" class="decor"></td>
</tr>"""
