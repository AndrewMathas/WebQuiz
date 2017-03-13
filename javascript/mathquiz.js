//*****************************************************************************
//       Copyright (C) 2004-2016 Andrew Mathas and Donald Taylor
//                          University of Sydney
//
//  Distributed under the terms of the GNU General Public License (GPL)
//                  http://www.gnu.org/licenses/
//
// This file is part of the MathQuiz system.
//
// Copyright (C) 2004-2010 by the School of Mathematics and Statistics
// <Andrew.Mathas@sydney.edu.au>
// <Donald.Taylor@sydney.edu.au>
//*****************************************************************************

// March 2017:
//   - removed legacy code for pre-2010 browsers
//   - removed images for the question buttons and replaced with css

var currentQ, totalQ, currentQuiz;
var currentResponse;
var wrongAnswers = new Array();
var correct  = new Array();

// QuizSpecifications will be an array of the expected responses for each question
var QuizSpecifications = new Array();

// image arrays
var Images      = "/MathQuiz/Images/";
var currentImage = new Array();
var untouched    = new Array();
var ticked       = new Array();
var starred      = new Array();
var crossed      = new Array();

// specification for the question buttons
blank = {'marker': '',       'color': 'black',  'bg': '#FFF8DC' }
cross = {'marker': '\u2718', 'color': 'red',    'bg': 'linear-gradient(to bottom right, white,  grey)' }
star  = {'marker': '\u272D', 'color': 'yellow', 'bg': 'linear-gradient(to bottom right, yellow, green)' }
tick  = {'marker': '\u2714', 'color': 'green',  'bg': 'linear-gradient(to bottom right, red, yellow)' }

function MathQuizInit(num, quiz) {
  if (navigator.appName=="Netscape" && parseFloat(navigator.appVersion)<5) {
    alert("Your browser version is " + navigator.appVersion + ".\n" +
          "This quiz is unlikely to work unless your browser version is at least 5.");
  }

  // totalQ is the nunber of questions in the quiz
  totalQ = num;
  currentQ = 1
  currentQuiz = quiz
  currentResponse = null; // Points to the current response layer

  // read in the question specifications
  var read_ql = document.createElement('script');
  var head = document.getElementsByTagName('head')[0];
  read_ql.type = "text/javascript";
  read_ql.src = currentQuiz+'/quiz_list';
  head.appendChild(read_ql);

  var i;
  for ( i = 0; i < num; i++ ) {
      wrongAnswers[i] = 0; // the number of times the question has been attempted
      correct[i] = false;  // whether or not the supplied answer is correct
  }

  window.status="Finished loading";
}

// Code to hide/show questions

function showQuestion(newQ) { // newQ is an integer
  hideResponse();
  document.getElementById('question'+currentQ).style.display = 'none';
  document.getElementById('button'+currentQ).classList.remove('button-selected');
  document.getElementById('question'+newQ).style.display = 'block';
  document.getElementById('button'+newQ).classList.add('button-selected');
  currentQ=newQ;
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
function nextQuestion (increment) {
  if ( currentQ<0 ) {
    if ( increment==1 ) gotoQuestion(1);
    else gotoQuestion(totalQ);
  }
  var q = currentQ ;
  do {
    q=q+increment;
    if (q==0) q=totalQ;
    else if (q>totalQ) q=1;
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
    //    correct[qnum] = (badAnswer == 0)
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
