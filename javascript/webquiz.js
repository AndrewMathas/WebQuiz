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
var drop_down               // handler for the drop-down menu, if it exists
var qTotal;                 // number of quiz questions
var side_closed             // handler for displaying sidelabelclosed
var side_menu               // handler to open and close side
var side_open;              // handler for displaying sidelabelopen

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

// stop the dropdown menu from being created twice
var drop_down_not_created = true;

// create the drop down menu dynamically using the QuizTitles array
function create_drop_down_menu() {

    if (drop_down_not_created) {
      // add the menu icon for the quizzes menu - only called if there is at least one quiz
      document.getElementById("quizzes-menu-icon").innerHTML = " &#9776;";

      var max = 0, q, quiz_link, menu = document.createDocumentFragment();
      for (q = 0; q < QuizTitles.length; q++) {
          quiz_link = document.createElement("li");
          quiz_link.innerHTML = '<a href="' + QuizTitles[q][1] + '">' + QuizTitles[q][0] + '</a>';
          menu.appendChild(quiz_link);
          max = Math.max(max, QuizTitles[q][0].length);
      }
      drop_down.style.width = Math.round(max) + "ex";
      drop_down.appendChild(menu);

      drop_down_not_created = false;
    }
}

// create an event listener so that we can close the drop-down menu
// whenever some one clicks outside of it
function MenuEventListener(evnt) {
    var menu_icon = document.getElementsByClassId('menu-icon');
    if (drop_down.contains(evnt.target)) {
      return; // inside the menu so just return
    } else {   // outside the menu so check the number of menu_clicks
      if (drop_down.style.display === 'block' || menu_icon.contains(evnt.target)) {
        evnt.stopPropagation();
        toggle_dropdown_menu();
      }
    }
}

function toggle_dropdown_menu() {
    if (drop_down.style.display === 'block') {
      drop_down.style.display = 'none';
    } else {
      drop_down.style.display = 'block';
      window.addEventListener('click', MenuEventListener, true);
    }
}

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
    // alert('showing newB='+newB+', newQ='+newQ+'.');
    if (!onePage && newQ !== currentQ) {
        if (currentQ !== 0) { // hide the current question and feedback
            hideFeedback();
            document.getElementById("question" + currentQ).style.display = "none";
            currentB.classList.remove("nolink");
            if (currentQ > 0) { // question and not discussion
                currentB.classList.remove("button-selected");
            }
        }
        // display newQ
        document.getElementById("question" + newQ).style.display = "table";
    }
    // now set currentQ = to the question indexed by newQ in questionOrder
    // and currentB = current button
    currentQ = newQ;
    currentB = document.getElementById("button" + newB);
    currentB.classList.add("nolink");
    if (!onePage) {
      if (currentQ > 0) {
          currentB.classList.add("button-selected");
          document.getElementById("question-number").innerHTML = newB;
      } else if (Discussion[-currentQ]) {
          document.getElementById("question-number").innerHTML = Discussion[-currentQ];
      }
    }
}

// Code to hide/show feedback

function hideFeedback() {
    if (currentFeedback) {
        currentFeedback.style.display = "none";
    }
}

function showFeedback(tag) {
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

function gotoQuestion(bnum) {
    // bnum is a button number so we need to convert to a question number
    var qnum = questionOrder[bnum];
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
               return parseInt(ans)==parseInt(val);
             },
  'lowercase':  function(ans, val) {//convert to lowercase string and compare
               return ans==String(val).toLowerCase();
             },
  'number':  function(ans, val) {// compare as numbers
               return math.eval(ans)==math.eval(val);
             },
  'string':  function(ans, val) {// compare as strings
               return ans==String(val);
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
          alert('Please answer the question first!')
          return
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

// initialise the quiz, loading specifications and setting up the first question
function WebQuizInit(questions, discussions, quizfile) {
    // process init options
    qTotal = questions;
    dTotal = discussions;

    // display the first question or discussion item
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
    drop_down = document.getElementById("drop-down-menu");

    // make the drop down menu if QuizTitles has some entries
    if (QuizTitles.length > 0 && drop_down) {
        create_drop_down_menu();
    }

    if (qTotal==0) {
        // ugly hack to position copyright message when there are no questions
        side_menu.style.height='60ex';
        var school = side_menu.getElementById('school');
        school.style.position = 'relative';
        school.style.bottom = '-25ex';
        var copyright = side_menu.getElementById('copyright')
        copyright.style.position = 'relative';
        copyright.style.bottom = '-35ex';
    }
}


