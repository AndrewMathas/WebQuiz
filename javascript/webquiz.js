/*
 * -----------------------------------------------------------------------
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
var Discussion = [];
var QuizTitles = [];
var correct = [];
var currentQ;
var currentQuiz;
var currentResponse = null;
var dTotal;
var qTotal;
var questionOrder = [];
var drop_down, side_closed, side_menu, side_open;
var wrongAnswers = [];

// The following variables are redefined in the specifications file
var QuizSpecifications = [];
var onePage = false;

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

// create the drop down menu dynamically using the QuizTitles array
function create_drop_down_menu() {
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
}

// create an event listener so that we can close the drop-down menu
// whenever some one clicks outside of it
function MenuEventListener(evnt) {
    var menu_icon = document.getElementsByClassName('menu-icon')[0];
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

// toggle the display of the side menu and its labels
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
function showQuestion(newQ) { // newQ is an integer which is always in the correct range
    var realQ;
    var button;
    if (!onePage && newQ !== currentQ) {
        if (currentQ>0) {
            realQ = questionOrder[currentQ-1];
        } else {
            realQ = currentQ
        }
        if (currentQ !== 0) { // hide the current question and responses
            hideResponse();
            document.getElementById("question" + realQ).style.display = "none";
            button = document.getElementById("button" + currentQ);
            button.classList.remove("nolink");
            if (currentQ > 0) { // question and not discussion
                button.classList.remove("button-selected");
            }
        }

        // now set currentQ = newQ and display it
        currentQ = newQ;
        if (currentQ>0) {
            realQ = questionOrder[currentQ-1];
        } else {
            realQ = currentQ
        }
        document.getElementById("question" + realQ).style.display = "table";
        button = document.getElementById("button" + currentQ);
        button.classList.add("nolink");
        if (currentQ > 0) {
            button.classList.add("button-selected");
            document.getElementById("question-number").innerHTML = currentQ;
        } else if (Discussion[-1 - currentQ]) {
            document.getElementById("question-number").innerHTML = Discussion[-1 - currentQ];
        }
    }
}

// Code to hide/show responses

function hideResponse() {
    if (currentResponse) {
        currentResponse.style.display = "none";
    }
}

function showResponse(tag) {
    hideResponse(); // hide current response
    currentResponse = document.getElementById(tag);
    currentResponse.style.display = "block";
}

// if increment==1 we find the next questions which has not
// been answered incorrectly and if increment==-1 we find the last
// such question
function nextQuestion(increment) {
    if (currentQ < 0) { // a discussion item
        if (increment === 1) {
            gotoQuestion(1);
        } else {
            gotoQuestion(qTotal);
        }
    } else {
        var q = currentQ;
        do {
            q += increment;
            if (q === 0) {
                q = qTotal;
            } else if (q > qTotal) {
                q = 1;
            }
        } while (q !== currentQ && correct[ q - 1]);
        if (q === currentQ) {
            alert("There are no more unanswered questions");
        } else {
            gotoQuestion(q);
        }
    }
}


var buttons = ['blank', 'cross', 'star', 'tick'];
function updateQuestionMarker(qnum) {
    var q = qnum - 1;
    if (currentQ > 0) {
        var marker;
        var button = document.getElementById("button" + currentQ);
        if (correct[q]) {
            if (wrongAnswers[q] === 0) {
                marker = star;
            } else {
                marker = tick;
            }
        } else {
            if (wrongAnswers[q] > 0) {
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

function gotoQuestion(qnum) {
    updateQuestionMarker(qnum);
    showQuestion(qnum);
}

// check to see whether the answer is correct and update the markers accordingly
function checkAnswer(qnum) {
    var q = qnum - 1;
    var realQ = questionOrder[q];
    var question = QuizSpecifications[realQ-1];
    var formObject = document.forms["Q" + realQ + "Form"];
    var i;
    if (question.type == "input") {
        var answer = formObject.elements[0].value;
        switch(question.comparison) {
          case 'complex':
            var a = math.complex(answer)
            var b = math.complex(question.value)
            correct[q] = (a.re==b.re && a.im==b.im)
            break;
          case 'integer':
            correct[q] = (parseInt(answer)==parseInt(question.value));
            break;
          case 'number':
            correct[q] = (math.eval(answer)==math.eval(question.value));
            break;
          case 'string':
            correct[q] = (String(question.value)==answer);
            break;
          case 'lowercase':
            correct[q] = (String(question.value).toLowerCase()==answer);
            break;
        }
        if (correct[q]) {
            showResponse("q" + realQ + "true");
        } else {
            showResponse("q" + realQ + "false");
        }
    } else if (question.type == "single") {
        var checkedAnswer = 0;
        for (i = 0; i < question.length; i++) {
            if (formObject.elements[i].checked) {
                correct[q] = question[i];
                checkedAnswer = i + 1;
                break;
            }
        }
        showResponse("q" + realQ + "response" + checkedAnswer);
    } else { // type is "multiple"
        var badAnswers = [];
        for (i = 0; i < question.length; i++) {
            if (formObject.elements[i].checked !== question[i]) {
                badAnswers.push(i + 1);
                break;
            }
        }
        // fully correct only if badAnswers == []
        if (badAnswers.length === 0) {
            correct[q] = true;
            showResponse("q" + realQ + "response0");
        } else {
            // randomly display a response for one of incorrect choices
            correct[q] = false;
            showResponse("q" + realQ + "response" + badAnswers[Math.floor(Math.random() * badAnswers.length)]);
        }
    }
    //
    if (!correct[q]) {
        wrongAnswers[q] += 1;
    }
    updateQuestionMarker(qnum);
}

/**
 * Shuffles array in place. ES6 version
 * @param {Array} a items An array containing the items.
 * https://stackoverflow.com/questions/6274339/how-can-i-shuffle-an-array
 */
function shuffle(a) {
    var i, j;
    for (i = a.length - 1; i > 0; i--) {
        j = Math.floor(Math.random() * (i + 1));
        [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
}

// initialise the quiz, loading specifications and setting up the first question
function WebQuizInit(questions, discussions, quizfile) {
    // process init options
    qTotal = questions;
    dTotal = discussions;
    currentQuiz = quizfile;

    // display the first question or discussion item
    currentQ = 0;
    var newQ = (dTotal > 0) ? -1 : 1;

    // set up arrays for tracking how many times the questions have been attempted
    var i;
    for (i = 0; i < qTotal; i++) {
        wrongAnswers[i] = 0;    // the number of times the question has been attempted
        correct[i] = false;     // whether or not the supplied answer is correct
        questionOrder[i] = i+1; // determine the order of the question
    }

    // read the question specifications for the quiz
    // and then wait for the QuizSpecifications to load
    var script = document.createElement('script');
    script.src =  currentQuiz + "/wq-" + currentQuiz + ".js";
    script.type = "text/javascript";
    document.head.appendChild(script);

    // compute these only once
    side_menu = document.getElementById('sidemenu');
    side_open = document.getElementsByClassName('sidelabelopen')[0];
    side_closed = document.getElementsByClassName('sidelabelclosed')[0];
    drop_down = document.getElementById("drop-down-menu");

    // make the drop down menu if QuizTitles has some entries
    if (QuizTitles.length > 0 && drop_down) {
        create_drop_down_menu();
    }

    if (qTotal==0) {
        // ugly hack to position copyright message when there are no questions
        side_menu.style.height='60ex';
        var school = side_menu.getElementsByClassName('school')[0];
        school.style.position = 'relative'
        school.style.bottom = '-40ex'
        var copyright = side_menu.getElementsByClassName('copyright')[0];
        copyright.style.position = 'relative'
        copyright.style.bottom = '-40ex'
    }
}


