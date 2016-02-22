// $Id: common.js,v 1.4 2003/01/28 22:57:31 don Exp $
// mathquiz.js | 2004-01-20 | Andrew Mathas | version 3.0
// common.js   | 2002-09-29 | Don Taylor    | version 2.0

// 27 Jan 03
// At the moment this is a mix of old code that works
// for NN4 and IE4+ together with new code for browsers
// such as NN6+ that support the Document Object Model.
// It may be possible to improve the code somewhat by
// removing some of the 'eval's.
// Note.  getObject() is only called when isDOM is true.
// - it should be possible to use it for other browser
// types.

var isDOM = false;
var layerRef, styleRef;
var currentQ, totalQ;
var currentRLayer;
var wrongAnswers = new Array();
var correct  = new Array();

function getObject(str) {
  retval = null;
  if (document.getElementById) {
    retval = document.getElementById(str).style;
  }
  else if (document.layers) {
    retval = document.layers[str];
  }
  else if (document.all) {
    retval = document.all(str).style;
  }
  return retval;
}

// image arrays
var Images      = "/u/MOW/MathQuiz/Images/";
var currentImage = new Array();
var untouched    = new Array();
var ticked       = new Array();
var starred      = new Array();
var crossed      = new Array();

// QList will be an array of the expected responses for each question
var QList = new Array();

function MathQuizInit(num) {
  if (navigator.appName=="Netscape" && parseFloat(navigator.appVersion)<5) {
    alert("Your browser version is " + navigator.appVersion +
     ".\nThis quiz is unlikely to work unless your browser version is at least 5.");
  }
  // distinguish between various object models
  if (document.getElementById) {
    layerRef = "";
    styleRef = ".style";
    isDOM = true;
  }
  else {
    if (document.layers) {  // e.g. NN4
      layerRef = "document.layers";
      styleRef = "";
    }
    else {
      if (document.all) { // e.g. IE4+
        layerRef = "document.all";
        styleRef = ".style";
      } 
      else {
        alert('Cannot determine object model.  Perhaps the browser version is too old');
      }
    }
  }
  totalQ = num;
  currentRLayer = null; // Points to the current response layer

  var i;
  for ( i = 0; i < num; i++ ) {
    wrongAnswers[i] = 0;     // the number of times the question has been attempted
    correct[i] = false;  // whether or not the supplied answer is correct
  }

  // preload the images
  for ( i = 1; i <= num; i++ ) {
    currentImage[i-1] = new Image(31,31);
    currentImage[i-1].src = Images+"border"+i+".gif";
    untouched[i-1] = new Image(31,31);
    untouched[i-1].src = Images+"clear"+i+".gif";
    ticked[i-1] = new Image(31,31);
    ticked[i-1].src = Images+"tick"+i+".gif";
    starred[i-1] = new Image(31,31);
    starred[i-1].src = Images+"star"+i+".gif";
    crossed[i-1] = new Image(31,31);
    crossed[i-1].src = Images+"cross"+i+".gif";
  }
  window.status="Finished loading";
}
// for hysterical reasons
function init(num) {
  MathQuizInit(num) 
}

// Code to hide/show questions

function showQLayer(newQ) { // newQ is an integer
  hideRLayer();
  if (isDOM) {
    getObject('question'+currentQ).visibility = 'hidden';
    currentQ = newQ;
    getObject('question'+currentQ).visibility = 'visible';
  }
  else {
    eval(layerRef + "['question" + currentQ + "']" + styleRef + ".visibility = 'hidden'");
    currentQ = newQ;
    eval(layerRef + "['question" + currentQ + "']" + styleRef + ".visibility = 'visible'");
  }
}

// Code to hide/show responses

function hideRLayer() {
  if (currentRLayer != null) {
    if (isDOM)
      currentRLayer.visibility = 'hidden';
    else
      eval(currentRLayer + styleRef + ".visibility = 'hidden'");
  }
}

function showRLayer(tag) {
  hideRLayer()
  if (isDOM) {
    currentRLayer = getObject(tag);
    currentRLayer.visibility = 'visible';
  } 
  else {
    currentRLayer = layerRef+"['question"+currentQ+"']."+layerRef+"['answer"+currentQ+"']."
      +layerRef+"['"+tag+"']";
    eval(currentRLayer + styleRef + ".visibility = 'visible'");
  }
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
    alert("There are no more unwrongAnswers questions");
  else {
    if ( increment==1 ) {
      self.status = 'Question '+q+' is the next unwrongAnswers question';
    } else {
      self.status = 'Question '+q+' was the last unwrongAnswers question';
    }
    gotoQuestion( q );
  }
}

// nextQuestion + calls to navOver and navOut
function NextQuestion(increment) {
  var q=currentQ+increment;
  if (increment==1) { image='nextpage'; msg='Next unwrongAnswers question';
  } else { image ='prevpage'; msg='Last unwrongAnswers question' ;
  }
  navOut(image);
  nextQuestion(increment);
  setTimeout("navOver(image,msg);", 5);
}
    
function showProgress() {
  var qnum = currentQ - 1 ;
  if (currentQ<0) return true; // nothing to change in this case
  if (isDOM) {
    var imageref = document.images['progress'+currentQ];
    if (correct[qnum]) {
      if (wrongAnswers[qnum] == 0) {
        imageref.src = starred[currentQ-1].src;
      } else {
        imageref.src = ticked[currentQ-1].src;
      }
    } else {
      if (wrongAnswers[qnum] == 0) {
        imageref.src = untouched[currentQ-1].src;
      } else {
        imageref.src = crossed[currentQ-1].src;
      } 
    } 
  }
  else {
    var stem = layerRef+"['progress'].document.progress"+currentQ;
    if (wrongAnswers[qnum] > 0) {
      if (correct[qnum]) {
        if (wrongAnswers[qnum] == 0) {
          eval(stem+".src='"+Images+"star"+currentQ+".gif'");
        } else {
          eval(stem+".src='"+Images+"tick"+currentQ+".gif'");
        }
      }
      else {
        if (wrongAnswers[qnum] == 0) {
          eval(stem+".src='"+Images+"cross"+currentQ+".gif'");
        } else {
          eval(stem+".src='"+Images+"clear"+currentQ+".gif'");
        }
      }
    }
  }
}

function gotoQuestion(qnum) {
  var oldcurrentQ=currentQ;
  showProgress();
  showQLayer(qnum);
  if ( oldcurrentQ<0 ) return true;
  if (isDOM)
    document.images['progress'+currentQ].src = currentImage[currentQ-1].src;
  else
    eval(layerRef+"['progress'].document.progress"+currentQ+".src='"+Images+"border"+currentQ+".gif'");
}

function checkAnswer() { 
  var qnum = currentQ - 1;
  var responsePattern = QList[qnum];
  if (isDOM)
    var formObject = document.forms["Q"+currentQ+"Form"];
  else
    var formObject = eval(layerRef + "['question"+currentQ+"'].document.Q" + currentQ + "Form");

  if (responsePattern.type == "input") {
    if (responsePattern.value == parseFloat(formObject.elements[0].value)) {
      correct[qnum] = true;
      showRLayer(eval("'q'+currentQ+'true';"));
    }
    else {
      correct[qnum] = false;
      showRLayer(eval("'q'+currentQ+'false';"));
    }
  }
  else if (responsePattern.type == "single") {
    var checkedAnswer = 0;
    for  (var i = 0; i < responsePattern.length; i++ ) {
      if (formObject.elements[i].checked) {
        correct[qnum] = responsePattern[i];
        checkedAnswer = i+1;
        break;
      }
    }
    showRLayer(eval("'q'+currentQ+'response'+checkedAnswer;"));
  }
  else { // type is "multiple"
    var badAnswer = 0;
    for  (var i = 0; i < responsePattern.length; i++ ) {
      if (formObject.elements[i].checked != responsePattern[i]) {
        badAnswer = i+1;
        break;
      }
    }
    //    correct[qnum] = (badAnswer == 0)
    if (badAnswer > 0) {
      correct[qnum] = false;
      showRLayer(eval("'q'+currentQ+'response'+badAnswer;"));
    }
    else {
      correct[qnum] = true;
      showRLayer(eval("'q'+currentQ+'response0';"));
    }
  }
  // 
  if ( !correct[qnum] ) { wrongAnswers[qnum] += 1; }
  showProgress();
}

function navOver(name, descr) {
	var highlight_img = Images+"h-"+name+".gif";
	document[name].src = highlight_img;
	self.status = descr;
	return true;
}

function navOut(name) {
	var normal_img = Images+"nn-"+name+".gif";
	document[name].src = normal_img;
	self.status = "";
	return true;
}
function menuOver(quiznum, descr) {
	document['quiztitle'+quiznum].src = Images+"red_arrow.gif";
	self.status = descr;
	return true;
}

function menuOut(quiznum) {
	document['quiztitle'+quiznum].src = Images+"arrow.gif";
	self.status = "";
	return true;
}
    

