r'''
-----------------------------------------------------------------------
    mathquiz_templates | html template file
-----------------------------------------------------------------------

    Copyright (C) Andrew Mathas, University of Sydney

    Distributed under the terms of the GNU General Public License (GPL)
              http://www.gnu.org/licenses/

    This file is part of the MathQuiz system.

    <Andrew.Mathas@sydney.edu.au>
    <Donald.Taylor@sydney.edu.au>
----------------------------------------------------------------------
'''

# -*- encoding: utf-8 -*-

## The quiz web pages are built using the following "template" strings

# html meta statements
html_meta = r'''<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <meta name="viewport" content="width=device-width">
  <meta name="generator" content="MathQuiz {version} (http://www.maths.usyd.edu.au/u/MOW/MathQuiz/doc/mathquiz-manual.html)">
  <meta name="description" content="{description}">
  <meta name="authors" content="MathQuiz: {authors}">
  <meta name="organization" content="{department}, {institution}">
  <meta name="Copyright" content="MathQuiz: {copyright}">
  <meta name="keywords" content="mathquiz, TeX4ht, make4ht, latex, python, quiz, mathematics">
  <link href="{mathquiz_url}/mathquiz.css" type="text/css" rel="stylesheet">
  <link href="{quiz_file}/{quiz_file}.css" type="text/css" rel="stylesheet">
'''

# javascript for setting up the questions
questions_javascript = r'''  <script type="text/javascript" src="{mathquiz_url}/mathquiz.js"></script>
  script type="text/javascript" src="quiztitles.js"></script>
  <script type="text/javascript" src="{mathjax}?config=MML_CHTML"></script>
'''

mathquiz_init=r'''<div style="display: none;">
    <script type="text/javascript">MathQuizInit({qTotal}, {dTotal}, '{quiz_file}', {hide_side_menu});</script>
  </div>'''

# Bread crumbs including a drop down menu for all of the quizzes for the unit.
# The drop-down-menu is added by create_drop_down_menu() in maghquiz.js
breadcrumb_line_text='          <li>{text}</li>\n'
breadcrumb_line_url ='          <li><a href="{url}">{text}</a></li>\n'
breadcrumb_quizlist = '''          <li><a href="{quizzes_url}">Quizzes</a>
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
button  = r'        <div id="button{b}" class="button{cls}" content=" " onClick="gotoQuestion({b})">{b}</div>'
discuss = r'        <li id="button-{b}" class="discussion" onClick="gotoQuestion(-{b})">{title}</li>'
side_menu = r'''<div class="menu-icon">
      <span class="sidelabelclosed question-label" onclick="toggle_side_menu();">&#10070;</span>
      <span class="sidelabelopen question-label" onclick="toggle_side_menu();">&#10006;&nbsp;Questions</span>
    </div>
    <div id="sidemenu" class="side-menu">{discussion_list}
      <div class="buttons">
        <br>{buttons}
      </div>
      <table class="marking-key">
         <tr><td></td><td></td></tr>
         <tr><td style="color: #FFCC00; font-size:small;">&starf;</td><td>right first<br>attempt</td></tr>
         <tr><td style="color: green; font-size:medium;">&check;</td><td>right</td></tr>
         <tr><td style="color: red; font-size:medium;">&cross;</td><td>wrong</td></tr>
      </table>
      <div class="school">
        {department}<p>
        {institution}
      </div>
      <div class="copyright">
        <a href="http://www.maths.usyd.edu.au/u/MOW/MathQuiz/doc/credits.html">
           MathQuiz {version}
        </a>
        <br>&copy; Copyright<br><span style="overflow: visible;">2004-2017</span>
      </div>
    </div>'''

# quiz title and navigation arrows
quiz_header='''<div class="quiz-header">
        <div class="quiz-title">{title}</div><div></div>
        <span id="question-number" class="question-label">{question_number}</span>
        {arrows}
      </div>'''
navigation_arrows='''<span class="arrows">
          <a onClick="nextQuestion(-1);" title="Previous unanswered question">&#x25c4;</a>
          <span class="question-label">Questions</span>
          <a onClick="nextQuestion(1);"  title="Next unanswered question">&#x25ba;</a>
        </span>'''

# discussion item
discussion='''<div id="question-{dnum}" class="question" {display}>
        <p>{discussion.discussion}</p>{input_button}
      </div>
'''
input_button='<input type="button" name="next" value="Start quiz" onClick="return gotoQuestion(1);"/>\n'

#quiz index
quiz_list='''     <div class="quiz-list">
        <h2>{unit} Quizzes</h2>
        <ul>
          {quiz_index}
        </ul>
      </div>'''
quiz_list_item='''<li><a href={url}>{title}</a></li>'''

# now we come to the question wrappers
question_wrapper='''<div id="question{qnum}" class="question" {display}>
      {question}
      {response}
      </div>
'''
question_text='''  {question}
      <form id="Q{qnum}Form" onSubmit="return false;" class="question">
        {question_options}
        <p>
          <input type="button" value="Check Answer" name="answer" class="input-button" onClick="checkAnswer();"/>
          <input type="button" value="Next Question" class="input-button" title="Next unanswered question" name="next" onClick="nextQuestion(1);"/>
        </p>
      </form>
'''

# Questions and responses:
input_answer='<input type="text"  onChange="checkAnswer();" size="5"/> {tag}'
choice_answer='<table class="question-choices">{choices}</table>'
input_single='\n<input type="hidden" name="Q{qnum}hidden"/>'

single_item='<td><input type="radio" name="Q{qnum}option"/></td><td class="brown" >{choice})</td><td><div class="question-choices">{answer}</div></td>\n'
multiple_item='<td><input type="checkbox" name="Q{qnum}option{optnum}"/></td><td class="brown" >{choice})</td><td><div class="question-choices">{answer}</div></td>\n'

tf_response_text='''        <div id="q{choice}{response}" class="response"><em class="dazzle">{answer}</em> <em>{answer2}</em>
           <div>{text}</div>
        </div>'''
single_response='''        <div id="q{qnum}response{part}" class="response">
          <em>Choice ({alpha}) is <span class="dazzle">{answer}</span></em><div>{response}</div>
        </div>'''
smiley='&#9786;'
frowny='&#9785;'

multiple_response='''        <div id="q{qnum}response{part}" class="response">
            <em>There is at least one mistake.</em><br>For example, choice <span class="brown">({alpha})</span> should be <span class="dazzle">{answer}</span>.
            <div>{response}</div>
        </div>'''
multiple_response_correct='''
        <div id="q{qnum}response0" class="response"><em class="dazzle">Correct!</em>
            <ol>
{responses}
            </ol>
        </div>'''
multiple_response_answer='              <li><em>{answer}</em> {reason}</li>'

# the remaining templates are used to prompt the user when initialising mathquiz
initialise_introduction='''
In order to work the on-line quizzes that MathQuiz constructs need to load some
javascript and CSS files that, for efficiency reasons, should be kept on your
webserver. It does not matter whether these files are in "system" directory
on your web server or in your own web directories.

In order to copy these files to the right place and access them MathQuiz needs:

  o A "web directory" on your file system that is visible from your web server
    This is the name of a dorectory or folder on your web server where the MathQuiz
    files can be copied to
  o The relative URL for accessing these files from the web
    This is the part of the URL that you have to add to your "root" URL to
    access the files. For example, if the URL for your department is
        http://www.maths.usyd.edu.au/
    and the MathQuiz files can be accessed as
        http://www.maths.usyd.edu.au/u/MOW/MathQuiz
    then the relative URL for the MathQuiz files is /u/MOW/MathQuiz
'''

web_directory_message='''The location of the files on your web server will depend on your operating system.
It is recommended that you have a separate directory for the MathQuiz files.
Common locations for the MathQuiz web directory are:
     /Library/WebServer/Documents/MathQuiz     (for mac os x)
     /usr/local/httpd/MathQuiz                 (SuSE unix)
     /usr/local/apache2/MathQuiz               (some apache configurations)
     c:\inetpub\wwwroot\MathQuiz               (windows?)

WARNING: any files of the form mathquiz.* in these directories will be deleted.
'''

mathquiz_url_message='''Please give the relative URL for the MathQuiz web directory.
In all of the examples above the relative URL for MathQuiz would be /MathQuiz

MathQuiz relative URL [{}]: '''

initialise_ending ='''
You should now be able to build web pages using mathquiz! As an initial test
you can try to build the on-line version of the mathquiz manual pages by going
to the directory
    {web_dir}/doc
and typing
    mathquiz mathquiz-online-manual
'''

mathquiz_url_warning = '''
MathQuiz has not been initialised. To remove the warning message from the web
page please use
    mathquiz --initialise
to install the MathQuiz javascript and css files.
'''

text_initialise_warning='''
MathQuiz has not yet been initialised. To remove this warning please use
      mathquiz --initialise
to install the MathQuiz web files onto your system.
'''

web_initialise_warning='''
      <div id="initialisewarning" class="warning">
        MathQuiz has not yet been initialised. To remove this warning box please use
        <blockquote>
          mathquiz --initialise
        </blockquote>
        to install the MathQuiz web files on your system.
        <button style="float: right" onclick="document.getElementById('initialisewarning').style.display='none'">OK</button>
      </div>
'''

rc_permission_error='''
Attempting to write the rc-file to {rc_file}
resulted in the error:
  {error}

To write the MathQuiz rc-file into this directory you may need to quit and run
matghquiz either using an administrator account, or using sudo on linux/macosx.

Press (and then r3eturn):
    1. To try to save to {rc_file} again
    2. To save to {alt_rc_file}
    3. To give a different filename for the rc-file
    *. Any other key to exit
'''

permission_error='''
You do not have permission to write to {}.

To install MathQuiz files into this directory you may need to quit and run
mathquiz using either an administrator account, or using sudo on linux/macosx.

Alternatively, please give a different directory.
'''

mathquiz_url_warning='''
WARNING: most of the time, but not always, the relative URL will be a suffix of
the web directory name, which is not the case with your settings. Your URL may
well be correct, however, if you have made a mistake then you can change this
at any time using the command: mathquiz --edit-settings
'''

edit_settings='''
In the mathquizrc file you can set global defaults for the following:
    department
    department_url
    institution
    institution
Leave these blank if you do not want to set defaults for them. In addition,
there are three "advanced user options":
    mathquiz_mk4
    mathjax
    mathquiz_format
Incorrect values for these settings will break MathQuiZ so you would not
normally change them.

If in doubt about any of these options then just accept the default value by
pressing return. You can change any of these settings later using the command
    mathquiz --edit-settings
'''

# no script error when javascript is not enabled
no_script='''<noscript>
    <div class="warning">
      If you are reading this message either your browser does not support
      JavaScript or because JavaScript is not enabled. You will need to enable
      JavaScript and then reload this page in order to use this quiz.
     </div>
  </noscript>'''

# and now for the mathquiz help message
mathquiz_help_message=r'''
MathQuiz allows you to write writing on-line quizzes starting from a latex file.
'''
