/*
 * -----------------------------------------------------------------------
 *   mathquiz.js | javascript for controlling mathquiz web pages
 * -----------------------------------------------------------------------
 *
 *   Copyright (C) Andrew Mathas and Donald Taylor, University of Sydney
 *
 *   Distributed under the terms of the GNU General Public License (GPL)
 *               http://www.gnu.org/licenses/
 *
 *   This file is part of the Math_quiz system.
 *
 *   <Andrew.Mathas@sydney.edu.au>
 *   <Donald.Taylor@sydney.edu.au>
 * ----------------------------------------------------------------------
 */

// Global variables
var currentQ, qTotal, dTotal, currentQuiz, currentResponse=null;
var Discussion = new Array();
var QuizSpecifications = new Array();
var QuizTitles = new Array();
var correct  = new Array();
var wrongAnswers = new Array();

// QuizSpecifications will be an array of the expected responses for each question
var QuizSpecifications = new Array();

// Specification for the question buttons for use in updateQuestionMarker
blank = {'marker': '',       'color': 'black',  'bg': '#FFF8DC' }
cross = {'marker': '\u2718', 'color': 'red',    'bg': 'linear-gradient(to bottom right, white,  slateblue)' }
star  = {'marker': '\u272D', 'color': 'yellow', 'bg': 'linear-gradient(to bottom right, yellow, green)' }
tick  = {'marker': '\u2714', 'color': 'green',  'bg': 'linear-gradient(to bottom right, red, yellow)' }

// Add a small delay for loading the quiz specifications. Not sure that this
// actually does anything. We can't use a while-loop because with this the
// page never loads
var WaitForQuizSpecifications = function(qTotal){
  if (QuizSpecifications.length<qTotal) {
    setTimeout(WaitForQuizSpecifications, 15)
  }
}

// initialise the quiz, loading specifcations and setting up the first question
function MathQuizInit(questions, discussions, quizfile) {
  if (navigator.appName=="Netscape" && parseFloat(navigator.appVersion)<5) {
    alert("Your browser version is " + navigator.appVersion + ".\n" +
          "This quiz is unlikely to work unless your browser version is at least 5.");
  }

  qTotal = questions
  dTotal = discussions
  currentQuiz = quizfile

  // read the question specifications for the quiz from <currentQuiz>/quiz_list.js
  document.head.appendChild(document.createElement("script")).src=currentQuiz+'/quiz_list.js';
  WaitForQuizSpecifications(qTotal);

  // make the drop down menu if QuizTitles has some entries
  if (QuizTitles.length>0 && document.getElementById('drop_down_menu')) {
      create_drop_down_menu()
  }

  currentQ=0
  newQ =(dTotal>0) ? -1 : 1
  showQuestion(newQ)

  // set up arrays for tracking how many times that questions have been attempted
  var i;
  for (i = 0; i < qTotal; i++ ) {
      wrongAnswers[i] = 0; // the number of times the question has been attempted
      correct[i] = false;  // whether or not the supplied answer is correct
  }
}

// Code to hide/show questions

function showQuestion(newQ) { // newQ is an integer which is always in the correct range
    if ( newQ != currentQ ) {
        if ( currentQ != 0 ) { // hide the current question and responses
            hideResponse();
            document.getElementById('question'+currentQ).style.display = 'none';
            var button = document.getElementById('button'+currentQ);
            button.classList.remove('nolink');
            if (currentQ>0) {
                button.classList.remove('button-selected');
            }
        }

        // now set curtentQ = newQ and display it
        currentQ = newQ;
        document.getElementById('question'+currentQ).style.display = 'table';
        var button = document.getElementById('button'+currentQ);
        button.classList.add('nolink');
        if (currentQ>0) {
              button.classList.add('button-selected');
              document.getElementById('question_number').innerHTML = 'Question '+currentQ;
        } else if ( Discussion[-1-currentQ] ) {
              document.getElementById('question_number').innerHTML = Discussion[-1-currentQ]
        }
    }
}

// Code to hide/show responses

function hideResponse() {
  if (currentResponse != null) {
      currentResponse.style.display = 'none';
  }
}

function showResponse(tag) {
  hideResponse()
  currentResponse = document.getElementById(tag);
  currentResponse.style.display = 'block';
}

// if increment==+1 we find the next questions which has not
// been wrongAnswers correctly; if increment==-1 we find the last
// such question
function nextQuestion(increment) {
  if ( currentQ<0 ) {
    if ( increment==1 ) gotoQuestion(1);
    else gotoQuestion(qTotal);
  } else {
    var q = currentQ ;
    do {
      q=q+increment;
      if (q==0) q=qTotal;
      else if (q>qTotal) q=1;
    } while (q!=currentQ && correct[q-1] );
    if (q==currentQ)
      alert("There are no more unanswered questions");
    else {
      if ( increment==1 ) {
        self.status = 'Question '+q+' is the next unanswered question';
      } else {
        self.status = 'Question '+q+' was the last unanswered question';
      }
      gotoQuestion( q );
    }
  }
}

function updateQuestionMarker() {
  var qnum = currentQ - 1 ;
  if (currentQ<0) return true; // nothing to change in this case
  var button = document.getElementById('button' + currentQ);
  if (correct[qnum]) {
    if (wrongAnswers[qnum] == 0) {
        marker = star;
    } else {
        marker = tick;
    }
  } else {
    if (wrongAnswers[qnum] > 0) {
        marker = cross
    } else {
        marker = blank
    }
  }
  button.style.background = marker.bg;
  button.style.color      = marker.color
  button.setAttribute('content', marker.marker)
}

function gotoQuestion(qnum) {
  updateQuestionMarker();
  showQuestion(qnum);
}

// check to see whether the answer is correct and update the markers accordingly
function checkAnswer() {
  var qnum = currentQ - 1;
  var question = QuizSpecifications[qnum];
  var formObject = document.forms["Q"+currentQ+"Form"];

  if (question.type == "input") {
    if (question.value == parseFloat(formObject.elements[0].value)) {
      correct[qnum] = true;
      showResponse('q'+currentQ+'true');
    }
    else {
      correct[qnum] = false;
      showResponse('q'+currentQ+'false');
    }
  }
  else if (question.type == "single") {
    var checkedAnswer = 0;
    for  (var i = 0; i < question.length; i++ ) {
      if (formObject.elements[i].checked) {
        correct[qnum] = question[i];
        checkedAnswer = i+1;
        break;
      }
    }
    showResponse('q'+currentQ+'response'+checkedAnswer);
  }
  else { // type is "multiple"
    var badAnswer = 0;
    for  (var i = 0; i < question.length; i++ ) {
      if (formObject.elements[i].checked != question[i]) {
        badAnswer = i+1;
        break;
      }
    }
    // fully correct only if badAnswer === 0
    if (badAnswer > 0) {
      correct[qnum] = false;
      showResponse('q'+currentQ+'response'+badAnswer);
    }
    else {
      correct[qnum] = true;
      showResponse('q'+currentQ+'response0');
    }
  }
  //
  if ( !correct[qnum] ) { wrongAnswers[qnum] += 1; }
  updateQuestionMarker();
}

// create the drop down menu dynamically using the QuizTitles array
function create_drop_down_menu() {
   // add the menu icon for the quizzes menu if there is at least one quiz
   if (QuizTitles.length>0) {
     document.getElementById('quizzes_menu_icon').innerHTML=' &#9776;'
   }

   var drop_down = document.getElementById('drop_down_menu');
   var max = 0;
   for (q=0; q < QuizTitles.length; q++) {
       var quiz_link = document.createElement('li')
       quiz_link.innerHTML = '<a href="'+QuizTitles[q][1]+'">'+QuizTitles[q][0]+'</a>';
       drop_down.appendChild(quiz_link);
       max = Math.max(max, QuizTitles[q][0].length)
    }
    drop_down.style.width = Math.round(max)+'ex'
}

function toggle_side_menu_display() {
    var side_menu = document.getElementsByClassName('side_menu')[0]
    if (side_menu.style.display=='block' || side_menu.style.display=='') {
        side_menu.style.display='none'
    } else {
        side_menu.style.display='block'
    }
}

function toggle_quiz_menu() {
    var quiz_menu = document.getElementById('drop_down_menu')
    if (quiz_menu.style.display=='block') {
        quiz_menu.style.display='none'
    } else {
        quiz_menu.style.display='block'
    }
}
