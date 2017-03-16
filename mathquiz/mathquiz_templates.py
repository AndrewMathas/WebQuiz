r"""  MathQuiz.py | 2017 Version 5.0 | html template file

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
"""

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
discuss = r'       <li class="discussion" onClick="gotoQuestion(-{b}">{title}</li>'
side_menu = r'''   <h2>MathQuiz</h2>{discussionList}
       <div class="buttons"><div class="question_label">&nbsp;Questions&nbsp;</div><br>{buttons}
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
quiz_title='''  <div id="quiz_header">
        <div class="quiz_title">{title}</div><div style="clear:both;"</div>{arrows}
      </div>
'''
navigation_arrows='''
        <div id="question_number" class="question_label">Question 1</div>
        <div class="arrows">
          <span onClick="nextQuestion(1);"><span class="tooltip">Next unanswered question</span>&#x25ba;</span>
          <div class="question_label">Questions</div>
          <span onClick="nextQuestion(-1);"><span class="tooltip">Previous unanswered question</span>&#x25c4;<span>
        </div>'''

# discussion item
discussion='''     <div id="question-{dnum}"><h2>{discussion.heading}</h2>
        <p>{discussion.discussion}</p>{input_button}
      </div>
'''
input_button='<input type="button" name="next" value="Start quiz" onClick="return gotoQuestion(1);"/>\n'

#quiz index
quiz_list='''     <div class="quiz_list"><h2>{course} Quizzes</h2>
        <ul>
          {quizindex}
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
      <form id="Q{qnum}Form" action="" onSubmit="return false;">
        {questionOptions}
        <p><input type="button" value="Check Answer" name="answer" onClick="checkAnswer();"/>
        <span style="width:40px;">&nbsp;</span>
        <input type="button" value="Next Question" title="Next unanswered question" name="next" onClick="nextQuestion(1);"/></p>
      </form>
'''
input_answer='<input type="text"  onChange="checkanswer();" size="5"/>{tag}'
choice_answer='<table class="question_choices">{choices}</table>{hidden}'
hidden_choice='\n<input type="hidden" checked="checked" name="Q{qnum}hidden"/>'

# html meta statements
html_meta = r"""<meta name="generator" content="MathQuiz {version} (http://www.maths.usyd.edu.au/u/MOW/MathQuiz/doc/mathquiz-manual.html)">
  <meta name="organization" content="School of Mathematics and Statistics, University of Sydney">
  <meta name="Copyright" content="University of Sydney 2004-2017">
  <meta name="keywords" content="mathquiz, TeX4ht, make4ht, latex, python, quiz, mathematics">
  <meta name="description" content="Interative quiz generated using MathQuiz from latex using TeX4ht ">
  <meta name="authors" content="{authors}">
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <link href="{MathQuizURL}mathquiz.css" type="text/css" rel="stylesheet">
  <link href="{quiz_file}.css" type="text/css" rel="stylesheet">
"""


# Previously used
#   <script type="text/javascript" src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>
# but this case rendering errors

# javascript for setting up the questions
questions_javascript = r"""  <script src="{MathQuizURL}mathquiz.js" type="text/javascript"></script>
  <script src="quiz_titles.js" type="text/javascript"></script>
  <script type="text/javascript" src="https://c328740.ssl.cf1.rackcdn.com/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML" ></script>
  <style type="text/css"> .MathJax_MathML {{text-indent: 0;}}</style>
  <script type="text/javascript">window.onLoad=MathQuizInit({qTotal},'{quiz}');</script>"""

# Document tree structure
#   doc.title
#      .questionList[].question
#                     .answer.type               (Choice)
#                            .itemList[].expect
#                                       .answer
#                                       .response
#                     .answer.tag                (Answer)
#                            .whenTrue
#                            .whenFalse




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
discuss = r'       <li class="discussion" onClick="gotoQuestion(-{b}">{title}</li>'
side_menu = r'''   <h2>MathQuiz</h2>{discussionList}
       <div class="buttons"><div class="question_label">&nbsp;Questions&nbsp;</div><br>{buttons}
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
quiz_title='''  <div id="quiz_header">
        <div class="quiz_title">{title}</div><div style="clear:both;"</div>{arrows}
      </div>
'''
navigation_arrows='''
        <div id="question_number" class="question_label">Question 1</div>
        <div class="arrows">
          <span onClick="nextQuestion(1);"><span class="tooltip">Next unanswered question</span>&#x25ba;</span>
          <div class="question_label">Questions</div>
          <span onClick="nextQuestion(-1);"><span class="tooltip">Previous unanswered question</span>&#x25c4;<span>
        </div>'''

# discussion item
discussion='''     <div id="question-{dnum}"><h2>{discussion.heading}</h2>
        <p>{discussion.discussion}</p>{input_button}
      </div>
'''
input_button='<input type="button" name="next" value="Start quiz" onClick="return gotoQuestion(1);"/>\n'

#quiz index
quiz_list='''     <div class="quiz_list"><h2>{course} Quizzes</h2>
        <ul>
          {quizindex}
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
      <form id="Q{qnum}Form" action="" onSubmit="return false;">
        {questionOptions}
        <p><input type="button" value="Check Answer" name="answer" onClick="checkAnswer();"/>
        <span style="width:40px;">&nbsp;</span>
        <input type="button" value="Next Question" title="Next unanswered question" name="next" onClick="nextQuestion(1);"/></p>
      </form>
'''
input_answer='<input type="text"  onChange="checkanswer();" size="5"/>{tag}'
choice_answer='<table class="question_choices">{choices}</table>{hidden}'
hidden_choice='\n<input type="hidden" checked="checked" name="Q{qnum}hidden"/>'

# html meta statements
html_meta = r"""<meta name="generator" content="MathQuiz {version} (http://www.maths.usyd.edu.au/u/MOW/MathQuiz/doc/mathquiz-manual.html)">
  <meta name="organization" content="School of Mathematics and Statistics, University of Sydney">
  <meta name="Copyright" content="University of Sydney 2004-2017">
  <meta name="keywords" content="mathquiz, TeX4ht, make4ht, latex, python, quiz, mathematics">
  <meta name="description" content="Interative quiz generated using MathQuiz from latex using TeX4ht ">
  <meta name="authors" content="{authors}">
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <link href="{MathQuizURL}mathquiz.css" type="text/css" rel="stylesheet">
  <link href="{quiz_file}.css" type="text/css" rel="stylesheet">
"""


# Previously used
#   <script type="text/javascript" src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>
# but this case rendering errors

# javascript for setting up the questions
questions_javascript = r"""  <script src="{MathQuizURL}mathquiz.js" type="text/javascript"></script>
  <script src="quiz_titles.js" type="text/javascript"></script>
  <script type="text/javascript" src="https://c328740.ssl.cf1.rackcdn.com/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML" ></script>
  <style type="text/css"> .MathJax_MathML {{text-indent: 0;}}</style>
  <script type="text/javascript">window.onLoad=MathQuizInit({qTotal},'{quiz}');</script>"""

# Document tree structure
#   doc.title
#      .questionList[].question
#                     .answer.type               (Choice)
#                            .itemList[].expect
#                                       .answer
#                                       .response
#                     .answer.tag                (Answer)
#                            .whenTrue
#                            .whenFalse

