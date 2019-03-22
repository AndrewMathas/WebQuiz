r'''
-----------------------------------------------------------------------
    webquiz_templates | html template file
-----------------------------------------------------------------------

    Copyright (C) Andrew Mathas, University of Sydney

    Distributed under the terms of the GNU General Public License (GPL)
              http://www.gnu.org/licenses/

    This file is part of the WebQuiz system.

    <Andrew.Mathas@sydney.edu.au>
----------------------------------------------------------------------
'''

# -*- encoding: utf-8 -*-

## The quiz web pages are built using the following "template" strings

# html meta statements
html_meta = r'''<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <meta name="generator" content="WebQuiz {version} (http://www.maths.usyd.edu.au/u/mathas/WebQuiz/webquiz-online-manual.html)">
  <meta name="description" content="{description}">
  <meta name="authors" content="WebQuiz: {authors}">
  <meta name="organization" content="{department}, {institution}">
  <meta name="Copyright" content="WebQuiz: {copyright}">
  <meta name="keywords" content="WebQuiz, TeX4ht, make4ht, latex, python, quiz, mathematics">
  <link href="{webquiz_url}/css/webquiz-{theme}.css" type="text/css" rel="stylesheet">
  <link href="{quiz_file}/{quiz_file}.css" type="text/css" rel="stylesheet">
'''

# javascript for setting up the questions
questions_javascript = r'''  <script src="{webquiz_url}/js/webquiz.js"></script>
  <script defer src="{mathjax}?config=MML_CHTML"></script>'''

mathjs=r'  <script defer src="https://cdnjs.cloudflare.com/ajax/libs/mathjs/5.4.0/math.min.js"></script>'

webquiz_init = r'''<div style="display: none;">
    <script src="quizindex.js"></script>
    <script>WebQuizInit({number_questions}, {number_discussions}, '{quiz_file}');</script>
  </div>'''

# Bread crumbs including a drop down menu for all of the quizzes for the unit.
# The drop-down-menu is added by create_quizindex_menu() in webquiz.js
breadcrumb_line_text = '            <li>{text}</li>\n'
breadcrumb_line_url  = '            <li><a href="{url}">{text}</a></li>\n'
breadcrumb_quizindex  = r'''              <li><a href="{quizzes_url}">{quizzes}</a>
                  <span onclick="toggle_quizindex_menu();" id="quizzes-menu-icon"></span>
                  <ul id="quizindex-menu" onclick="toggle_quizindex_menu();"></ul>
              </li>
'''
create_quizindex_menu = r'''// construct the drop down menu if QuizTitles has some entries
if (QuizTitles.length > 0 && quizindex_menu) {
    create_quizindex_menu();
}
'''
breadcrumbs = r'''<div class="breadcrumbs">
    <nav>
        <div class="navleft">
            <ul>{crumbs}            </ul>
        </div>
    </nav>
  </div>
'''

# Should we add a menu to change the theme dynamically? If so then the code
# below should be added to the breadcrumbs and then fixed a little. Perhaps the
# trickiest bit is finding the current list of supported themes.
theme_menu=r'''
        <div class="navright" >
            <span onclick="toggle_theme_menu();">Theme &#9881;</span>
            <ul><li>
                <ul id="theme-menu" onclick="toggle_theme_menu();">
                  <li>one</li><li>two</li>
                </ul>
              </li>
            </ul>
        </div>
'''

# Add a drop-down menu to the navigation to dynamically change the theme?

# question buttons
button = r'        <div id="button{b}" class="button {cls}" content=" " onClick="gotoQuestion({b})">{b}</div>'
discuss = r'        <li id="button-{b}" class="discussion" onClick="gotoQuestion(-{b})">{title}</li>'
side_menu = r'''<div id="menu-icon">
      <span id="sidelabelclosed" class="question-label" onclick="toggle_side_menu();">&#10070;</span>
      <span id="sidelabelopen" class="question-label" onclick="toggle_side_menu();">&#10006;&nbsp;{side_questions}
      </span>
    </div>
    <div id="sidemenu" class="side-menu">{discussion_list}{question_buttons}
      <div class="school">
        {department}<p>
        {institution}
      </div>
      <div class="copyright">
        <a href="http://www.maths.usyd.edu.au/u/mathas/WebQuiz/credits.html">
           <span class="webquizlogo">WebQuiz</span><span class="TEX">T<span class="E">E</span>X</span>
        </a>
        <br>&copy; Copyright<br><span style="overflow: visible;">{copyright_years}</span>
      </div>
    </div>'''

question_buttons = r'''
      <div class="buttons">
        <br>{buttons}
      </div>
      <table class="marking-key">
         <tr><td class="star">&starf;</td><td style="width: 14ex;">{side_menu_star}</td></tr>
         <tr><td class="tick">&check;</td><td>{side_menu_tick}</td></tr>
         <tr><td class="cross">&cross;</td><td>{side_menu_cross}</td></tr>
      </table>'''

# quiz title and navigation arrows
quiz_header = r'''<div class="quiz-header">
       <div class="quiz-title">{title}</div><div></div>{arrows}
      </div>'''
navigation_arrows = r'''
       <span id="question-label" class="question-label">{question}</span>
       <span id="question-number" class="question-label">{question_number}</span>
       <span class="arrows">
          <a onClick="nextQuestion(-1);" title="{previous_question}">&#x25c4;</a>
          <span class="question-label">{questions}</span>
          <a onClick="nextQuestion(1);"  title="{next_question}">&#x25ba;</a>
       </span>'''

# discussion item
discussion = r'''<div id="question-{dnum}" class="question" style="display:{display};">
        {heading}{discussion.text}
      </div>
'''
discussion_heading = r'''<div class="question-label">{}</div>
        '''

#quiz index
quiz_index_div = r'''     <div class="quiz-index">
        <ul>
          {quiz_index}
        </ul>
      </div>'''
index_item = r'''<li><a href={url}>{title}</a></li>'''

# now we come to the question wrappers
question_wrapper = r'''<div id="question{qnum}" class="question" style="display:{display};">
      <span class="question-label">{question_number}</span>{question}
      {feedback}
      </div>
'''

question_text = r'''  {question_text}
      <form id="Q{qnum}Form" onSubmit="return false;">
        {question_options}
        <p>
          <input type="button" value="{check_answer}" name="answer" class="input-button" onClick="checkAnswer({qnum});"/>
          {nextquestion}
        </p>
      </form>
'''
nextquestion='<input type="button" value="{next_question}" class="input-button" title="{next_question}" name="next" onClick="nextQuestion(1);"/>'

# Questions and feedback:
input_answer = '{answer}&nbsp;<input type="text"  onChange="checkAnswer({qnum});" size="{size}"/>{after_text}'
choice_answer = '<table class="question-choices">{choices}</table>{after_text}'
input_single = '\n<input type="hidden" name="Q{qnum}hidden"/>'

single_item = '''<td><input type="radio" name="Q{qnum}option"/></td>
<td class="brown" >{choice}</td><td><div class="question-choices">{text}</div></td>
'''
multiple_item = '''<td><input type="checkbox" name="Q{qnum}option{optnum}"/></td>
<td class="brown" >{choice}</td><td><div class="question-choices">{text}</div></td>
'''

tf_feedback_text = r'''
        <div id="q{choice}{feedback}" class="feedback"><em class="dazzle">{correct_answer}</em> <em>{answer2}</em>
           <div>{text}</div>
        </div>'''
single_feedback = r'''
        <div id="q{qnum}feedback{part}" class="feedback">
              <em>{alpha_choice} <span class="dazzle">{correct_answer}</span></em>
              <div>{feedback}</div>
        </div>'''

multiple_feedback = r'''
        <div id="q{qnum}feedback{part}" class="feedback">
            <em>{one_mistake}</em><br>{multiple_choice_opener} <span class="dazzle">{correct_answer}</span>.
            <div>{feedback}</div>
        </div>'''
multiple_feedback_correct = r'''
        <div id="q{qnum}feedback0" class="feedback"><em class="dazzle">{correct}</em>
            <ol>
{feedback}
            </ol>
        </div>'''
multiple_feedback_answer = '              <li><em>{correct_answer}</em> {reason}</li>'

# no script error when javascript is not enabled
no_script = r'''<noscript>
    <div class="warning">
      If you are reading this message either your browser does not support
      JavaScript or because JavaScript is not enabled. You will need to enable
      JavaScript and then reload this page in order to use this quiz.
     </div>
  </noscript>'''

######################################################################
# missing webquiz.ini file
######################################################################

missing_webquiz_ini = r'''
webquiz installation error: unable to find webquiz.ini -> {}

If you believe that WebQuiz has been installed correctly then please try
rebuilding the TeX filename database. On TeXLive systems this can be done
using the command mktexlsl, or using the TeXLive gui. On MiKTEX you can
rebuild the database from the Tasks menu on the MiKTeX console. You may
need to run this command using an administrator account or sudo, on unix
systems.

'''

######################################################################
# the remaining templates prompt the user when initialising webquiz
######################################################################

initialise_invite = r'''WebQuiz needs to be initialised.

Before WebQuiz can display quiz web pages on your system it first needs to
copy some css and javascript files into a directory that is accessible from
your webserver.

Do you want to initialise WebQuiz now [Y/n]? '''

initialise_before_settings = r'''
Before you can view the webquiz settings you need to initialise WebQuiz
using the command:
    webquiz --initialise
'''

initialise_introduction = r'''
WebQuiz Initialisation
======================
If you want to install the web components of WebQuiz files into a "system"
directory then you should quit this program (use control-C on unix-like
systems) and then run
    webquiz --initialise
from an administrators account or, on unix-like systems, use:
    sudo webquiz --initialise

If you want to continue then WebQuiz will guide you through the
initialisation process.  For more information about the steps involved
see Section 3.2 of the WebQuiz manual On many systems, you can open
the webquiz manual using the command: texdoc webquiz
'''

webroot_request = r'''----
To make files accessible from your web server WebQuiz needs:
  o A directory, or folder, on your server that is visible from your
    web server. This directory MUST be accessible from the web. It can
    either be a "system" directory or in your personal web directories.
  o The relative URL for accessing these files from the web. This is
    the part of the URL that you have to add to your "root" URL to
    access the files. For example, if the URL for your department is
        http://www.maths.usyd.edu.au/
    and the WebQuiz files can be accessed as
        http://www.maths.usyd.edu.au/teaching/WebQuiz
    then the relative URL for the WebQuiz files is /teaching/WebQuiz

It is recommended that you create a separate directory for WebQuiz on your
web server. The location of the files on your web server will depend on
your operating system and system configuration. A common sysem location
for the WebQuiz web directory on a {platform} system is
     {webquiz_dir}
'''

not_installed = r'''
According to kpsewhich, the TeX components of WebQuiz are not installed
on your system. If you have downloaded the WebQuiz zip file from ctan
then try using:
    > webquiz --tex-install
If the TeX components are already installed then something has gone
horribly wrong. If you think this is a bug please report it by creating
an issue at {}
'''

oserror_copying = r'''There was a problem copying files to {web_dir}
Error: {err}

Please give a different directory
'''

webquiz_url_message = r'''
Please give the relative URL for the WebQuiz web directory. For example,
if the base of your web server's directory is /var/www/html/ and the
WebQuiz web directory is /var/www/html/courses/WebQuiz then the
relative URL for the WebQuiz directory would be /courses/WebQuiz.

WebQuiz relative URL [{}]: '''

initialise_ending = r'''
You should now be able to build web pages using webquiz! As an initial
test you can try to build the example files from the webquiz manual
by going to the directory
    {web_dir}/doc/examples
If pstricks and dvisgvm are properly configured (see Section 3.3 of
the manual), then you can also try building the online manual, by
going to the directory
    {web_dir}/doc/examples
and typing:
    webquiz webquiz-online-manual

If you want to change the default webquiz settings please use:
    webquiz --edit-settings
'''

text_initialise_warning = r'''
WebQuiz has not yet been initialised. To remove this warning please use
      webquiz --initialise
to install the WebQuiz web files onto your system.
'''

web_initialise_warning = r'''
      <div id="initialisewarning" class="warning">
        WebQuiz has not yet been initialised. To remove this warning box please use
        <blockquote>
          webquiz --initialise
        </blockquote>
        to install the WebQuiz web files on your system.
        <button style="float: right" onclick="document.getElementById('initialisewarning').style.display='none'">OK</button>
      </div>
'''

rc_permission_error = r'''
Attempting to write the rcfile to {rcfile}
resulted in the error:
  {error}

To write the WebQuiz rcfile into this directory you may need to quit
and run webquiz again, either using an administrator account, or using
sudo on linux/macosx.

Press the key 1-3, followed by RETURN, to:
    1. Try to save to {rcfile} again
    2. Save to the user rcfile {alt_rcfile}
    3. Give a different location for the rcfile
Press any other key to exit without saving.
'''

permission_error = r'''
You do not have permission to write to {}.

To install WebQuiz files into this directory you may need to quit and
run webquiz using either an administrator account, or using sudo on
linux/macosx.

Alternatively, please give a different directory.
'''

insufficient_permissions = r'''
Insufficient permissions. Try using sudo or using an admisitrator account.
{}
'''

webquiz_url_warning = r'''
WARNING: most of the time, but not always, the relative URL will be a
suffix of the web directory name, which is not the case with your
settings. Your URL may well be correct, however, if you have made a
mistake then you can change this at any time using the command:
    webquiz --initialise
'''

edit_settings = r'''----
In the webquizrc file you can set global defaults for the following:
    breadrumbs
    colour theme
    department
    department_url
    engine
    institution
    institution
    language
Leave these blank if you do not want default values. There are three
additional "advanced: options:
    mathjax
    webquiz_layout
    webquiz_mk4
Please only change these settings if you know what you are doing
because incorrect values for these settings will break WebQuiz.

With each setting the default value is printed inside square brackets.
For example, as [default]. Press RETURN to accept the default value.
Except for the location of the WebQuiz web directory all of these
settings are easy to change at any time using the command:
    webquiz --edit-settings
'''

advanced_settings = r'''
** The remaining settings are advanced settings that you probably **
** do not want to change at this time. Incorrect values for these **
** settings will break WebQuiz so accept the defaults unless you  **
** know what you are doing.                                       **
'''

# and now for the webquiz help message
webquiz_help_message = r'''
WebQuiz allows you to write interactive online quizzes using latex
'''
