r'''
-----------------------------------------------------------------------
    webquiz_templates | html template file
-----------------------------------------------------------------------

    Copyright (C) Andrew Mathas, University of Sydney

    Distributed under the terms of the GNU General Public License (GPL)
              http://www.gnu.org/licenses/

    This file is part of the WebQuiz system.

    <Andrew.Mathas@sydney.edu.au>
    <Donald.Taylor@sydney.edu.au>
----------------------------------------------------------------------
'''

# -*- encoding: utf-8 -*-

## The quiz web pages are built using the following "template" strings

# html meta statements
html_meta = r'''<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <meta name="viewport" content="width=device-width">
  <meta name="generator" content="WebQuiz {version} (http://www.maths.usyd.edu.au/u/mathas/WebQuiz/webquiz-online-manual.html)">
  <meta name="description" content="{description}">
  <meta name="authors" content="WebQuiz: {authors}">
  <meta name="organization" content="{department}, {institution}">
  <meta name="Copyright" content="WebQuiz: {copyright}">
  <meta name="keywords" content="webquiz, TeX4ht, make4ht, latex, python, quiz, mathematics">
  <link href="{webquiz_url}/css/webquiz-{theme}.css" type="text/css" rel="stylesheet">
  <link href="{quiz_file}/{quiz_file}.css" type="text/css" rel="stylesheet">
'''

# javascript for setting up the questions
questions_javascript = r'''  <script src="{webquiz_url}/webquiz.js"></script>
  <script src="quiztitles.js"></script>
  <script src="{mathjax}?config=MML_CHTML"></script>
'''

mathjs='  <script src="https://cdnjs.cloudflare.com/ajax/libs/mathjs/5.4.0/math.min.js"></script>'

webquiz_init = r'''<div style="display: none;">
    <script type="text/javascript">WebQuizInit({number_quizzes}, {number_discussions}, '{quiz_file}', {hide_side_menu});</script>
  </div>'''

# Bread crumbs including a drop down menu for all of the quizzes for the unit.
# The drop-down-menu is added by create_drop_down_menu() in webquiz.js
breadcrumb_line_text = '          <li>{text}</li>\n'
breadcrumb_line_url = '          <li><a href="{url}">{text}</a></li>\n'
breadcrumb_quizlist = r'''          <li><a href="{quizzes_url}">{quizzes}</a>
          <span onclick="toggle_dropdown_menu();" id="quizzes-menu-icon"></span>
          <ul id="drop-down-menu" onclick="toggle_dropdown_menu();"></ul>
        </li>
'''
breadcrumbs = r'''<div class="breadcrumbs">
    <nav>
        <ul>
{crumbs}
        </ul>
    </nav>
  </div>
'''

# question buttons
button = r'        <div id="button{b}" class="button{cls}" content=" " onClick="gotoQuestion({b})">{b}</div>'
discuss = r'        <li id="button-{b}" class="discussion" onClick="gotoQuestion(-{b})">{title}</li>'
side_menu = r'''<div class="menu-icon">
      <span class="sidelabelclosed question-label" onclick="toggle_side_menu();">&#10070;</span>
      <span class="sidelabelopen question-label" onclick="toggle_side_menu();">&#10006;&nbsp;{questions}</span>
    </div>
    <div id="sidemenu" class="side-menu">{discussion_list}
      <div class="buttons">
        <br>{buttons}
      </div>
      <table class="marking-key">
         <tr><td style="color: #FFCC00; font-size:small;">&starf;</td><td style="width: 14ex;">{side_menu_star}</td></tr>
         <tr><td style="color: green; font-size:medium;">&check;</td><td>{side_menu_tick}</td></tr>
         <tr><td style="color: red; font-size:medium;">&cross;</td><td>{side_menu_cross}</td></tr>
      </table>
      <div class="school">
        {department}<p>
        {institution}
      </div>
      <div class="copyright">
        <a href="http://www.maths.usyd.edu.au/u/mathas/WebQuiz/credits.html">
           WebQuiz {version}
        </a>
        <br>&copy; Copyright<br><span style="overflow: visible;">2004-2018</span>
      </div>
    </div>'''

# quiz title and navigation arrows
quiz_header = r'''<div class="quiz-header">
        <div class="quiz-title">{title}</div><div></div>
        <span id="question-number" class="question-label">{question_number}</span>
        {arrows}
      </div>'''
navigation_arrows = r'''<span class="arrows">
          <a onClick="nextQuestion(-1);" title="{previous_question}">&#x25c4;</a>
          <span class="question-label">{questions}</span>
          <a onClick="nextQuestion(1);"  title="{next_question}">&#x25ba;</a>
        </span>'''

# discussion item
discussion = r'''<div id="question-{dnum}" class="question" {display}>
        {discussion.text}{input_button}
      </div>
'''
input_button = '<input type="button" name="next" value="Start quiz" onClick="return gotoQuestion(1);"/>\n'

#quiz index
quiz_list_div = r'''     <div class="quiz-list">
        <h2>{unit} {quizzes}</h2>
        <ul>
          {quiz_index}
        </ul>
      </div>'''
quiz_list_item = r'''<li><a href={url}>{title}</a></li>'''

# now we come to the question wrappers
question_wrapper = r'''<div id="question{qnum}" class="question" {display}>
      {question}
      {response}
      </div>
'''
question_text = r'''  {question_text}
      <form id="Q{qnum}Form" onSubmit="return false;" class="question">
        {question_options}
        <p>
          <input type="button" value="{check_answer}" name="answer" class="input-button" onClick="checkAnswer();"/>
          <input type="button" value="{next_question}" class="input-button" title="{next_question}" name="next" onClick="nextQuestion(1);"/>
        </p>
      </form>
'''

# Questions and responses:
input_answer = '{answer}:&nbsp<input type="text"  onChange="checkAnswer();" size="{size}"/>{after_text}'
choice_answer = '<table class="question-choices">{choices}</table>{after_text}'
input_single = '\n<input type="hidden" name="Q{qnum}hidden"/>'

single_item = '''<td><input type="radio" name="Q{qnum}option"/></td>
<td class="brown" >{choice})</td><td><div class="question-choices">{text}</div></td>
'''
multiple_item = '''<td><input type="checkbox" name="Q{qnum}option{optnum}"/></td>
<td class="brown" >{choice})</td><td><div class="question-choices">{text}</div></td>
'''

tf_response_text = r'''        <div id="q{choice}{response}" class="response"><em class="dazzle">{correct_answer}</em> <em>{answer2}</em>
           <div>{text}</div>
        </div>'''
single_response = r'''        <div id="q{qnum}response{part}" class="response">
              <em>{alpha_choice} <span class="dazzle">{correct_answer}</span></em>
              <div>{response}</div>
        </div>'''

multiple_response = r'''        <div id="q{qnum}response{part}" class="response">
            <em>{one_mistake}</em><br>{multiple_choice_opener} <span class="dazzle">{correct_answer}</span>.
            <div>{response}</div>
        </div>'''
multiple_response_correct = r'''
        <div id="q{qnum}response0" class="response"><em class="dazzle">{correct}</em>
            <ol>
{responses}
            </ol>
        </div>'''
multiple_response_answer = '              <li><em>{correct_answer}</em> {reason}</li>'

initialise_invite = r'''WebQuiz is a tool for creating on-line quizzes. For efficiency reasons,
WebQuiz needs to be initialised and, in particular, it needs to copy some
files into a directory that is accessible from your webserver.

Do you want to initialise WebQuiz now [Y/n]? '''

# no script error when javascript is not enabled
no_script = r'''<noscript>
    <div class="warning">
      If you are reading this message either your browser does not support
      JavaScript or because JavaScript is not enabled. You will need to enable
      JavaScript and then reload this page in order to use this quiz.
     </div>
  </noscript>'''

###############################################################################
# the remaining templates are used to prompt the user when initialising webquiz
###############################################################################

initialise_introduction = r'''----
To initialise WebQuiz you will be prompted for default settings and file
locations. We try to explain what is needed at each step. If needed, more
information can be found in section 3.2 of the manual. On many systems
you open the WebQuiz manual by typing
    texdoc webquiz
from the command-line.
'''

webroot_request = r'''----
To make files accessible from your web server WebQuiz needs:
  o A directory, or folder, on your server that is visible from your
    web server. This directory must be accessible from the web. It can
    either be a "system" directory or in your own personal directories.
  o The relative URL for accessing these files from the web. This is
    the part of the URL that you have to add to your "root" URL to
    access the files. For example, if the URL for your department is
        http://www.maths.usyd.edu.au/
    and the WebQuiz files can be accessed as
        http://www.maths.usyd.edu.au/u/MOW/WebQuiz
    then the relative URL for the WebQuiz files is /u/MOW/WebQuiz

WARNING: WebQuiz will delete any files of the form webquiz.* from the
WebQuiz web directory during initialisation.

We recommended that you create a separate directory for WebQuiz on your
web server. The location of the files on your web server will depend on
your operating system and system configuration. A common location for
the WebQuiz web directory on a {platform} system is
     {webquiz_dir}
'''

oserror_copying = r'''There was a problem copying files to {web_dir}
Error: {err}

Please give a different directory
'''

webquiz_url_message = r'''Please give the relative URL for the WebQuiz web directory. For example,
if the base of your web server's directory is /var/www/html/ and the
WebQuiz web directory is /var/www/html/courses/WebQuiz then the
relative URL for the WebQuiz directory would be /courses/WebQuiz.

WebQuiz relative URL [{}]: '''

initialise_ending = r'''
You should now be able to build web pages using webquiz! As an initial
test you can try to build the on-line version of the webquiz manual
pages by going to the directory
    {web_dir}/doc
and typing
    webquiz webquiz-online-manual
'''

webquiz_url_warning = r'''
WebQuiz has not been initialised. To remove the warning message from
the web page please use
    webquiz --initialise
to install the WebQuiz javascript and css files.
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
Attempting to write the rc-file to {rc_file}
resulted in the error:
  {error}

To write the WebQuiz rc-file into this directory you may need to quit
and run webquiz again, either using an administrator account, or using
sudo on linux/macosx.

Press the following key, followed by return, to:
    1. To try to save to {rc_file} again
    2. To save to {alt_rc_file}
    3. To give a different filename for the rc-file
Press any other key to exit.
'''

permission_error = r'''
You do not have permission to write to {}.

To install WebQuiz files into this directory you may need to quit and
run webquiz using either an administrator account, or using sudo on
linux/macosx.

Alternatively, please give a different directory.
'''

webquiz_url_warning = r'''
WARNING: most of the time, but not always, the relative URL will be a
suffix of the web directory name, which is not the case with your
settings. Your URL may well be correct, however, if you have made a
mistake then you can change this at any time using the command:
    webquiz --edit-settings
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
    webquiz_format
    webquiz_mk4
Please only change these settings if you know what you are doing
because incorrect values for these settings will break WebQuiz.

With each setting the default value is printed inside square brackets.
For example, as [default]. Press return to accept the default value.
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
WebQuiz allows you to write interactive on-line quizzes using latex
'''
