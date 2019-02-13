/* -----------------------------------------------------------------------
 *   webquiz.js | javascript for controlling webquiz web pages
 * -----------------------------------------------------------------------
 *
 *   Copyright (C) Andrew Mathas and Donald Taylor, University of Sydney
 *
 *   Distributed under the terms of the GNU General Public License (GPL)
 *               http://www.gnu.org/licenses/
 *
 *   This file is part of the WebQuiz system.
 *
 *   <Andrew.Mathas@sydney.edu.au>
 *   <Donald.Taylor@sydney.edu.au>
 * ----------------------------------------------------------------------
 */

// Global variables
var correct = [];           // questions answered correctly
var buttonOrder = [];       // map from button number to question number
var questionOrder = [];     // map from question number to button number
var wrongAnswers = [];      // questions answered incorrectly


var currentB;               // current button number
var currentFeedback = null; // feedback currently being displayed
var currentQ;               // current question number
var dTotal;                 // number of discussion items
var quizindex_menu;         // handler for the drop-down menu, if it exists
var qTotal;                 // number of quiz questions
var side_closed;            // handler for displaying sidelabelclosed
var side_menu;              // handler to open and close side
var side_open;              // handler for displaying sidelabelopen
//var theme_menu              // handler for the theme_menu

// The following variables are redefined in the specifications file
var QuizSpecifications = [];
var Discussion = [];        // Headings of discussion environments
var onePage = false;

// Defined and read from in quizindex.js if it exists
var QuizTitles = [];        // Quiz titles from a quizindex environment

// Specification for the question buttons for use in updateQuestionMarker
var blank = {
    "content": "",
    "name": "blank"
};
var cross = {
    "content": "\u2718",
    "name": "cross"
};
var star = {
    "content": "\u272D",
    "name": "star"
};
var tick = {
    "content": "\u2714",
    "name": "tick"
};

function markAnswer() {
  if (typeof(Storage) !== "undefined") {
    sessionStorage.correct = JSON.stringify(correct);
    sessionStorage.wrongAnswers = JSON.stringify(wrongAnswers);
  }
}

// stop the dropdown menu from being created twice
var quizindex_menu_not_created = true;

// create the drop down menu dynamically using the QuizTitles array
function create_quizindex_menu() {
    if (quizindex_menu_not_created) {
      // add the menu icon for the quizzes menu - only called if there is at least one quiz
      document.getElementById("quizzes-menu-icon").innerHTML = " &#9776;";

      var max = 0, q, quiz_link, menu = document.createDocumentFragment();
      for (q = 0; q < QuizTitles.length; q++) {
          quiz_link = document.createElement("li");
          quiz_link.innerHTML = '<a href="' + QuizTitles[q][1] + '">' + QuizTitles[q][0] + '</a>';
          menu.appendChild(quiz_link);
          max = Math.max(max, QuizTitles[q][0].length);
      }
      quizindex_menu.style.width = Math.round(max) + "ex";
      quizindex_menu.appendChild(menu);
      quizindex_menu_not_created = false;
    }
}

// create an event listener so that we can close the drop-down menu
// whenever some one clicks outside of it
function MenuEventListener(evnt) {
    var menu_icon = document.getElementById('quzzes-menu-icon');
    if (quizindex_menu.contains(evnt.target)) {
      return; // inside the menu so just return
    } else {   // outside the menu so check the number of menu_clicks
      if (quizindex_menu.style.display === 'block' || menu_icon.contains(evnt.target)) {
        evnt.stopPropagation();
        toggle_quizindex_menu();
      }
      //if (theme_menu.style.display === 'block' || menu_icon.contains(evnt.target)) {
      //  evnt.stopPropagation();
      //  toggle_quizindex_menu();
      //}
    }
}

function toggle_quizindex_menu() {
    if (quizindex_menu.style.display === 'block') {
      quizindex_menu.style.display = 'none';
    } else {
      quizindex_menu.style.display = 'block';
      window.addEventListener('click', MenuEventListener, true);
    }
}

// function toggle_theme_menu() {// unused
//     if (theme_menu.style.display === 'block') {
//       theme_menu.style.display = 'none';
//     } else {
//       theme_menu.style.display = 'block';
//       window.addEventListener('click', MenuEventListener, true);
//     }
// }

// toggle the display of the side menu and its many associated labels
function toggle_side_menu() {
    if (side_menu.style.display === "block" || side_menu.style.display === "") {
        side_menu.style.display = "none";
        side_open.style.display = "none";
        side_closed.style.display = "block";
    } else {
        side_menu.style.display = "block";
        side_open.style.display = "block";
        side_closed.style.display = "none";
    }
}

// Code to hide/show questions
function showQuestion(newB, newQ) { // newQ is an integer which is always in the correct range
    // alert('showing newB='+newB+', newQ='+newQ+', currentQ='+currentQ+'.');
    if (!onePage) {
      // hide the current question and feedback
      if (newQ!=currentQ && currentQ!=0) {
            hideFeedback();
            document.getElementById("question" + currentQ).style.display = "none";
            // "de-select" the current button
            currentB.classList.remove("button-selected");
      }
      // display the new question
      document.getElementById("question" + newQ).style.display = "table";

      // update the question/discussion header and select question button
      if (newQ > 0) {
          document.getElementById("question-label").style.display = 'contents';
          document.getElementById("question-number").innerHTML = String(newB);
      } else {
          document.getElementById("question-label").style.display = 'none';
          document.getElementById("question-number").innerHTML = Discussion[-newQ];
      }
      // set currentB = the current button and "select" the current button
      currentB = document.getElementById("button" + newB);
      currentB.classList.add("button-selected");
    }

    // finally set currentQ = current question
    currentQ = newQ;
}

// Code to hide/show feedback

function hideFeedback() {
    if (currentFeedback) {
        currentFeedback.style.display = "none";
    }
}

function showFeedback(tag) {
    // alert('Showing feedback for '+tag+'.');
    hideFeedback(); // hide current feedback
    currentFeedback = document.getElementById(tag);
    currentFeedback.style.display = "block";
}

// if increment==1 we find the next questions which has not
// been answered incorrectly and if increment==-1 we find the last
// such question
function nextQuestion(increment) {
    if (currentQ < 0) { // a discussion item => go to either first or last question
        if (increment === 1) {
            gotoQuestion(1);
        } else {
            gotoQuestion(qTotal);
        }
    } else {
        var b = buttonOrder[currentQ], q;
        do {
            b += increment;
            if (b === 0) {
                b = qTotal;
            } else if (b > qTotal) {
                b = 1;
            }
            q = questionOrder[b];
        } while (q !== currentQ && correct[q]);
        if (b === currentB) {
            alert("There are no more unanswered questions");
        } else {
            gotoQuestion(b);
        }
    }
}


var buttons = ['blank', 'cross', 'star', 'tick'];
function updateQuestionMarker(bnum, qnum) {
    // alert('updating bnum='+bnum+', qnum='+qnum+', currentQ='+currentQ+'.');
    // here qnum is assumed to be the question number in the web form
    if (qnum > 0) {
        var marker;
        var button = document.getElementById('button'+bnum);
        if (correct[qnum]) {
            if (wrongAnswers[qnum] === 0) {
                marker = star;
            } else {
                marker = tick;
            }
        } else {
            if (wrongAnswers[qnum] > 0) {
                marker = cross;
            } else {
                marker = blank;
            }
        }
        for (var b = 0; b < buttons.length; b++) {
           button.classList.remove(buttons[b]);
        }
        button.classList.add(marker.name);
        button.setAttribute("content", marker.content);
    }
}

// jumps to a chosen question and pushes the number of this question to the browser history
function gotoQuestion(bnum) {
    // bnum is a button number so we need to convert to a question number

    var qnum = (bnum>0) ? questionOrder[bnum] : bnum;
    gotoQuestionHelper(qnum);
    history.pushState(qnum, null, null);
}

// jumps to the specified question (without pushing it to the browser history)
function gotoQuestionHelper(qnum) {
    var bnum = (qnum>0) ? buttonOrder[qnum] : qnum;
    updateQuestionMarker(bnum, qnum);
    showQuestion(bnum, qnum);
}

// dictionary of comparison methods for when question.type=='input'
// each function in the dictionary returns true or false
var compare = {
  'complex': function(ans, val) {// check real and imaginary parts
               var a = math.complex(ans);
               var b = math.complex(val);
               return a.re==b.re && a.im==b.im;
             },
  'integer': function(ans, val) {// compare as integers
               return parseInt(val)==parseInt(ans);
             },
  'lowercase':  function(ans, val) {//convert to lowercase string and compare
               return val==String(ans).toLowerCase();
             },
  'number':  function(ans, val) {// compare as numbers
               return math.eval(val)==math.eval(ans);
             },
  'string':  function(ans, val) {// compare as strings
               return val==String(ans);
             }
};

// check to see whether the answer is correct and update the markers accordingly
function checkAnswer(qnum) {
    // alert('checking qnum='+qnum+'.');
    var question = QuizSpecifications[qnum];
    var studentAnswer = document.forms["Q" + qnum + "Form"];
    var i;
    if (question.type == "input") {
        var answer = studentAnswer.elements[0].value;
        if (answer=='') { //must have hit checkAnswer without answering, so ignore
          alert('Please answer the question first!');
          return;
        }
        try {
          correct[qnum] = compare[question.comparison](answer, question.value);
        } catch(err) {
          correct[qnum] = False;
        }

        if (correct[qnum]) {
            showFeedback("q" + qnum + "true");
        } else {
            showFeedback("q" + qnum + "false");
        }
    } else if (question.type == "single") {
        var checkedAnswer = 0;
        for (i = 0; i < question.length; i++) {
            if (studentAnswer.elements[i].checked) {
                correct[qnum] = question[i];
                checkedAnswer = i + 1;
                break;
            }
        }
        showFeedback("q" + qnum + "feedback" + checkedAnswer);
    } else { // type is "multiple"
        var badAnswers = [];
        for (i = 0; i < question.length; i++) {
            if (studentAnswer.elements[i].checked !== question[i]) {
                badAnswers.push(i + 1);
                break;
            }
        }
        // fully correct only if badAnswers == []
        if (badAnswers.length === 0) {
            correct[qnum] = true;
            showFeedback("q" + qnum + "feedback0");
        } else {
            // randomly display a feedback for one of incorrect choices
            correct[qnum] = false;
            showFeedback("q" + qnum + "feedback" + badAnswers[Math.floor(Math.random() * badAnswers.length)]);
        }
    }
    //
    if (!correct[qnum]) {
        wrongAnswers[qnum] += 1;
    }
    updateQuestionMarker(buttonOrder[qnum], qnum);
    markAnswer();
}

/**
 * Shuffle the questionOrder array and make buttonOrder its inverse
 * Based on https://stackoverflow.com/questions/6274339/how-can-i-shuffle-an-array
 */
function shuffleQuestions() {
    var i, j, qi;
    for (i = questionOrder.length-1; i > 0; i--) {
        j = 1+Math.floor(Math.random() * i);
        qi = questionOrder[i];
        questionOrder[i]=questionOrder[j];
        questionOrder[j]=qi;
    }
    // ...and compute the inverse map
    for (i = buttonOrder.length - 1; i > 0; i--) {
        buttonOrder[questionOrder[i]] = i;
    }
}

// Restores the state of the question markers from the session storage
function initSession() {
    if (typeof(Storage) !== "undefined") {
      if (sessionStorage.correct)
        correct = JSON.parse(sessionStorage.correct);
      if (sessionStorage.wrongAnswers)
        wrongAnswers = JSON.parse(sessionStorage.wrongAnswers);
    }

    for (i = 0; i < qTotal+1; i++) {
      updateQuestionMarker(buttonOrder[i],i);
    }

    // make the browser history remember the first question
    qnum = (dTotal > 0) ? -1 : questionOrder[1];
    history.replaceState(qnum, null, null);
}

// initialise the quiz, loading specifications and setting up the first question
function WebQuizInit(questions, discussions, quizfile) {
    // process init options

    // callback for browser history events
    window.addEventListener('popstate', function(e) {
       gotoQuestionHelper(e.state);
    });

    qTotal = questions;
    dTotal = discussions;

    // remove question arrows when there are no questions
    if (qTotal==0) {
        document.getElementsByClassName('arrows')[0].style.display='none'
    }

    // display the first question or discussion item
    currentB = 0;
    currentQ = 0;
    var newQ = (dTotal > 0) ? -1 : 1;

    // set up arrays for tracking how many times the questions have been attempted
    var i;
    for (i = 0; i < qTotal+1; i++) {
        wrongAnswers[i] = 0;    // the number of times the question has been attempted
        correct[i] = false;     // whether or not the supplied answer is correct
        questionOrder[i] = i; // will determine the order of the questions
        buttonOrder[i] = i;    // will determine the order of the buttons
    }

    // read the question specifications for the quiz
    // and then wait for the QuizSpecifications to load
    var script = document.createElement('script');
    script.src =  quizfile + "/wq-" + quizfile + ".js";
    script.type = "text/javascript";
    document.head.appendChild(script);

    // compute these only once
    side_menu = document.getElementById('sidemenu');
    side_open = document.getElementById('sidelabelopen');
    side_closed = document.getElementById('sidelabelclosed');
    quizindex_menu = document.getElementById("quizindex-menu");
    //theme_menu = document.getElementById('theme-menu');

    // make the drop down menu if QuizTitles has some entries
    if (QuizTitles.length > 0 && quizindex_menu) {
        create_quizindex_menu();
    }
}


