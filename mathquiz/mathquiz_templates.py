r'''  MathQuiz.py | 2017 Version 5.0 | html template file

#*****************************************************************************
# Copyright (C) 2017 Andrew Mathas, University of Sydney
#
# Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#
# This file is part of the MathQuiz system.
#
# Copyright (C) 2004-2017 by the School of Mathematics and Statistics
# <Andrew.Mathas@sydney.edu.au>
#*****************************************************************************
'''

# -*- encoding: utf-8 -*-

## The quiz web pages are built using the following "template" strings

# Questions and responses:
#   question_css.format(<question number>, <display mode>)
#   answer_css.format(<answer number>)
#   response_css.format(<qnswer number>, <response number>)
question_css = '    #question{}{{z-index: 0; margin: 2ex 0ex 0ex 0ex; padding: 0ex 0ex 0ex 0ex; display: {};}}\n'
answer_css   = '    #answer{}{{position: relative; display: block;}}\n'
response_css = '    #q{}response{}{{padding: 0ex; border: solid black 2px; display: none;}}\n'

# question buttons
button  = r'       <div id="button{b}" class="button{cls}" content="" onClick="gotoQuestion({b})">{b}</div>'
discuss = r'       <li class="discussion" onClick="gotoQuestion(-{b})">{title}</li>'
side_menu = r''' <div>MathQuiz</div>{discussion_list}
       <div class="buttons">
         <div class="question_label">&nbsp;Questions&nbsp;</div>
         <br>{buttons}
       </div>
       <div style="clear:left; height: 1em;"></div>
       <table class="marking_key">
          <tr><td style="color: #FFCC00; font-size:small;">&starf;</td><td>right first<br>attempt</td></tr>
          <tr><td style="color: green; font-size:medium;">&check;</td><td>right</td></tr>
          <tr><td style="color: red; font-size:medium;">&cross;</td><td>wrong</td></tr>
       </table>
       <div class="copyright">
          <a href="http://www.maths.usyd.edu.au/u/MOW/MathQuiz/doc/credits.html">
             <b>MathQuiz {version}</b>
          </a>
          <p><a href="http://www.maths.usyd.edu.au">
                 School of Mathematics<br> and Statistics</a>
          <br><a href="http://www.usyd.edu.au">University of Sydney</a>
          <br>&copy; Copyright 2004-2017
          </p>
       </div>'''

# quiz title and navigation arrows
quiz_header='''{initialise_warning}<div class="quiz_header">
        <div class="quiz_title">{title}</div>
        <div style="clear:both;"></div>
        <div id="question_number" class="question_label">{question_number}</div>
        {arrows}
      </div>
'''
navigation_arrows='''<div class="arrows">
          <div onClick="nextQuestion(-1);"><div class="tooltip">Previous unanswered question</div>&#x25c4;</div>
          <div class="question_label">Questions</div>
          <div onClick="nextQuestion(1);"><div class="tooltip">Next unanswered question</div>&#x25ba;</div>
        </div>
'''

# discussion item
discussion='''     <div id="question-{dnum}" class="question" {display}><h2>{discussion.heading}</h2>
        <p>{discussion.discussion}</p>{input_button}
      </div>
'''
input_button='<input type="button" name="next" value="Start quiz" onClick="return gotoQuestion(1);"/>\n'

#quiz index
quiz_list='''     <div class="quiz_list"><h2>{course} Quizzes</h2>
        <ul>
          {quiz_index}
        </ul>
      </div>'''
quiz_list_item='''<li><a href={url}>{title}</a></li>'''

# now we come to the question wrappers
question_wrapper='''      <div id="question{qnum}" class="question" {display}>
      {question}
      {response}
      </div>
'''
question_text='''  <div class="question_text">
        {question}
      </div>
      <form id="Q{qnum}Form" onSubmit="return false;" class="question">
        {questionOptions}
        <p>
          <input type="button" value="Check Answer" name="answer" class="input_button" onClick="checkAnswer();"/>
          <input type="button" value="Next Question" class="input_button" title="Next unanswered question" name="next" onClick="nextQuestion(1);"/>
        </p>
      </form>
'''
input_answer='<input type="text"  onChange="checkanswer();" size="5"/> {tag}'
choice_answer='<table class="question_choices">{choices}</table>{hidden}'
input_single='\n<input type="hidden" name="Q{qnum}hidden"/>'

single_item='<td><input type="radio" name="Q{qnum}option"/></td><td><div class="question_choices">{answer}</div></td>'
multiple_item='<td><input type="checkbox" name="Q{qnum}option{optnum}"/></td><td><div class="question_choices">{answer}</div></td>'

tf_response_text='''        <div id="q{choice}{response}" class="response"><em>{answer}</em>
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


# html meta statements
html_meta = r'''<meta name="generator" content="MathQuiz {version} (http://www.maths.usyd.edu.au/u/MOW/MathQuiz/doc/mathquiz-manual.html)">
  <meta name="organization" content="School of Mathematics and Statistics, University of Sydney">
  <meta name="Copyright" content="University of Sydney 2004-2017">
  <meta name="keywords" content="mathquiz, TeX4ht, make4ht, latex, python, quiz, mathematics">
  <meta name="description" content="Interative quiz generated by MathQuiz from latex using TeX4ht">
  <meta name="authors" content="{authors}">
  <meta name="viewport" content="width=device-width"/>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <link href="{MathQuizURL}/mathquiz.css" type="text/css" rel="stylesheet">
  <link href="{quiz_file}/{quiz_file}.css" type="text/css" rel="stylesheet">
'''

# javascript for setting up the questions
questions_javascript = r'''  <script src="{MathQuizURL}/mathquiz.js" type="text/javascript"></script>
  <script src="quiztitles.js" type="text/javascript"></script>
  <script type="text/javascript" src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=MML_CHTML"></script>
  <style type="text/css"> .MathJax_MathML {{text-indent: 0;}}</style>
  <script type="text/javascript">
     document.addEventListener("DOMContentLoaded", function(event) {{
       MathQuizInit({qTotal},{dTotal},'{quiz}');
     }});
  </script>
'''

# the remaining templates are used to prompt the user when initialising mathquiz

initialise_introduction='''
The on-line quizzes that MathQuiz constructs use javascript and casading style
sheets and these files need to be placed on your webserver.

To do this mathquiz needs:
  o A directory on your local file system that is visible from your web server
  o A relative URL to the web directory above.

WARNING: any files of the form mathquiz.* in these directories will be deleted.
'''

web_directory_message='''
MathQuiz needs to install javascript and css files on the web sever. You can put these
files into your own web directory or in a system directory. Possible system directories
include:
     /Library/WebServer/Documents/MathQuiz     (for mac os x)
     /usr/local/httpd/MathQuiz                 (SuSE unix)
     /usr/local/apache2/MathQuiz               (some apache configurations)
     c:\inetpub\wwwroot\MathQuiz               (windows?)
It is recommended that you have a separate directory for MathQuiz files.

MathQuiz web directory [{}]: '''

mathquiz_url_message='''Please give the *relative* URL for the MathQuiz web directory.
In all of the examples above the root would be /MathQuiz

MathQuiz relative URL [{}]: '''

initialise_ending ='''
You should now be able to build web pages using mathquiz! As an initial test
you can try to build the on-line version of the mathquiz manual pages by going
to the directory
    {web_dir}
and typing
    mathquiz mathquiz-manual
'''

sms_http = 'http://www.maths.usyd.edu.au/u/MOW/MathQuiz/'

mathquiz_url_warning = '''
MathQuiz has not yet been initialised so the quiz pages will be slower than
they need to be. Please use
    mathquiz --initialise
to better configure MathQuiz.
'''
initialise_warning='''<div class="warning">
        MathQuiz has not yet been initialised so the quiz pages will be slower than they need to be.
        Please use <em>mathquiz --initialise</em> to better configure MathQuiz.
      </div>
'''

permission_error='''
You do not have permission to write to the directory {}.
To install MathQuiz files into this directory you probably need to run this
command using an administrator account, or sudo on linux/macosx.
'''

# no script error when javascript is not enabled
no_script='''<noscript>
      <div class="warning">
        If you are reading this message either your browser does not support
        JavaScript or because JavaScript is not enabled. You will need to enable
        JavaScript and then reload this page in order to use this quiz.
       </div>
    </noscript>'''

