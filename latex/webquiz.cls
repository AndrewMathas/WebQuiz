% -----------------------------------------------------------------------
%   webquiz.cls | webquiz latex class file
% -----------------------------------------------------------------------
%
%   Copyright (C) Andrew Mathas, University of Sydney
%
%   Distributed under the terms of the GNU General Public License (GPL)
%               http://www.gnu.org/licenses/
%
%   This file is part of the Math_quiz system.
%
%   <Andrew.Mathas@sydney.edu.au>
% ----------------------------------------------------------------------

\NeedsTeXFormat{LaTeX2e}[1996/12/01]

% load webquiz-doc style
\usepackage{webquiz-ini}

% ----------------------------------------------------------------------
\ProvidesClass{webquiz}[\webquiz{release date} Version \webquiz{version}]

% initialise and then process document class options usng pgfopts
\RequirePackage{etoolbox}
\RequirePackage{pgfopts}
\def\unknown@options{}%          unknown options are passed to article.cls
\def\MQ@HideSideMenu{deFAULT}%   side menu visible by default
\newif\ifTikz\Tikzfalse%         true if tikz a document class option

\newif\ifMQ@Debugging  % for the debugging class option
% Process the documentclass options using pgfkeys and \ProcessPgfOptions
\pgfkeys{/latexquizoptions/.is family,
  /latexquizoptions,
    % turn debugging on
    debugging/.code           = {\MQ@Debuggingtrue},
    % pst2pdf
    pst2pdf/.style            = {pst2pdf value=true},
    pst2pdf value/.initial    = false,
    % languaage
    language/.initial         = deFAULT,
    % one page
    onepage/.style            = {onepage value=true},
    separatepages/.style      = {onepage value=false},
    onepage value/.initial    = deFAULT,
    % side menu
    showsidemenu/.style       = {hidesidemenu value=false},
    hidesidemenu/.style       = {hidesidemenu value=true},
    hidesidemenu value/.initial= deFAULT,
    % random order of quiz questions
    randomorder/.style        = {randomorder value=true},
    fixedorder/.style         = {randomorder value=false},
    randomorder value/.initial = deFAULT,
    % theme
    theme/.initial             = deFAULT,
    % tikz
    tikz/.code                 = {\global\Tikztrue},
    % unknown options => passed to article class
    .unknown/.code={\edef\unknown@options{\unknown@options,\pgfkeyscurrentname}}
}
\newcommand\latexquizOption[1]{\pgfkeysvalueof{/latexquizoptions/#1}}

% Use pgfkeys to check for valid options for the choice environment and the
% answer comparisons. As \ERROR is not defined an error message is
% generated when the option is not defined.
\pgfkeys{/webquiz checker/.is family, /webquiz checker,
  mode/.initial          = single,
  columns value/.initial = 1,
  columns/.style         = {columns value=#1},
  single/.style          = {mode=single},
  multiple/.style        = {mode=multiple},
  .unknown/.code         = {\ERROR: invalid choice type: use single or multiple}
  comparison/.is choice,
  comparison/complex/.code      = \relax,
  comparison/integer/.code      = \relax,
  comparison/lowercase/.code    = \relax,
  comparison/number/.code       = \relax,
  comparison/string/.code       = \relax,
  comparison/.unknown/.code     = {\ERROR: invalid input type: use integer, string or eval}
}

% now process the options
\ProcessPgfOptions{/latexquizoptions}% process options
\LoadClass[\unknown@options]{article}% load article class with options

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\RequirePackage{xparse}
\RequirePackage{pgffor}

% hack to fix two pgf bugs - apply only when when using tex4ht

\ifTikz
  \ifdefined\HCode
   \def\pgfsysdriver{pgfsys-tex4ht-mq-fixed.def}
  \fi
  \RequirePackage{tikz}
\fi

\def\MQ@Error{\PackageError{webquiz}}
\def\MQ@Debugging#1{\ifMQ@Debugging\typeout{Debugging: #1}\fi}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\RequirePackage{amsfonts,amsmath}
\RequirePackage{bbding}
\setlength{\parindent}{0pt}
\setlength{\parskip}{10pt}

% Macro to define a picture variant of \<command>. The latex version does
% nothing but the cfg version converts \<command> into an image

\newcommand\DisplayAsImage[2][]{\relax}

% Need to declare possible graphics extensions: see https://tex.stackexchange.com/questions/213461
% This is just placeholder - the real definition is used in the cfg file
%\newcommand\DeclareGraphicsExtensions[1]{}

% Macros for defining the university and department
\newcommand*{\DepartmentURL}[1]{\def\MQ@departmentURL{#1}}
\newcommand*{\Department}[1]{\def\MQ@department{#1}}

% University/instution - university included for backwards compatibility
\newcommand*{\InstitutionURL}[1]{\def\MQ@institutionURL{#1}}
\newcommand*{\Institution}[1]{\def\MQ@institution{#1}}
\newcommand*{\UniversityURL}[1]{\def\MQ@institutionURL{#1}}
\newcommand*{\University}[1]{\def\MQ@institution{#1}}

% Macros for defining the quiz web breadcrumbs using the unit code, name and
% URL. The names of these macros are chosen so as to be compatible with the
% in-house SMS package sms-uos.sty that specifies these for all units.
\newcommand*\UnitCode[1]{\def\uos@code{#1}}
\newcommand*\UnitName[1]{\def\uos@name{#1}}
\newcommand*\UnitURL[1]{\def\uos@url{#1}}
\newcommand*\QuizzesURL[1]{\def\MQ@quizzesUrl{#1}}
\newcommand*\BreadCrumb[1]{\def\MQ@breadcrumb{#1}}
\newcommand*\BreadCrumbs[1]{\def\MQ@breadcrumbs{#1}}

% Default values - the university and department defaults can also be
% set in the webquizrc file. The main purpose of these defaults is
% to remind the user to set them.
\UnitCode{Unit code?}
\UnitName{Unit name?}
\UnitURL{}
\QuizzesURL{deFAULT}
\BreadCrumb{}
\BreadCrumbs{deFAULT}
\Department{deFAULT}
\DepartmentURL{deFAULT}
\University{deFAULT}
\UniversityURL{deFAULT}

% Define page header and footer for the printable version of the quiz
% to show the unit code information.
\def\ps@quiz{\ps@empty
  \def\@oddhead{\hbox to\textwidth{%
      \uos@code\hss\textsc{\@title}\hss Page \thepage}}%
  \let\@evenhead=\@oddhead
}
\def\ps@firstpage{\ps@empty}
\pagestyle{quiz}


\def\@title{}
\def\maketitle{\vspace*{10mm}
  \begin{center}
    {\large\textsc{\@title}}%
  \end{center}
}
\AtBeginDocument{
  \maketitle%
  \def\title{\MQ@Error{\noexpand\title can only be used in the preamble}\@ehc}
  \thispagestyle{firstpage}%
  \ifdefined\HCode\else
     \textsc{WebQuiz} will process this quiz using \textbf{pst2pdf}.
  \fi
}

% -----------------------------------------------------------------------
% WebQuiz macros
% Define \MQ@XXXStart and \MQ@XXXEnd macros to avouid code duplication with
% webquiz.cfg. The following switches are used for error checking.
% -----------------------------------------------------------------------

% These are all for error checking...
\newif\ifInResponse
\newif\ifInAnswer
\newif\ifInChoice
\newif\ifInDiscussion
\newif\ifInItem
\newif\ifInQuestion
\newif\ifInQuizIndex
\newif\ifInWhenright
\newif\ifInWhenwrong

% -----------------------------------------------------------------------
% the quizindex environment and \quiz macro
% -----------------------------------------------------------------------

% the quiz counter keeps track of the question numbers in a quizindex environement
\newcounter{quiz}
\renewcommand\thequiz{\arabic{quiz}}
\def\MQ@QuizStart{%
  \MQ@Debugging{Starting \noexpand\quiz...}%
  \ifInQuizIndex\else\MQ@Error{\noexpand\quiz must appear inside a quizindex environment}\fi%
  \refstepcounter{quiz}% increment the quiz counter for the URLs
}
\NewDocumentCommand\quiz{som}{%
  \MQ@QuizStart%
  \IfBooleanTF{#1}{\def\MQ@Quiz{}}{\def\MQ@Quiz{Quiz~\thequiz.\space}}%
  \IfNoValueTF{#2}{\def\MQ@url{quiz\thequiz.html}}{\def\MQ@url{#2}}%
  \leavevmode\medskip\newline%
  \MQ@Quiz #3\newline%
  \phantom{Quiz 10}\textit{URL}:\quad \MQ@url%
}

\def\MQ@QuizIndexStart{%
  \MQ@Debugging{Starting quizindex...}%
  \ifInQuestion\MQ@Error{quizindex cannot appear in a question environment}\fi%
  \ifInDiscussion\MQ@Error{quizindex environments cannot be inside a discussion environment}\fi
  \ifInQuizIndex\MQ@Error{quizindex environments cannot be nested}\fi%
  \global\InQuizIndextrue%
}
\def\MQ@QuizIndexEnd{\global\InQuizIndexfalse\MQ@Debugging{Ending quizindex...}}
\newenvironment{quizindex}{\MQ@QuizIndexStart\bigskip}{\MQ@QuizIndexEnd}

% -----------------------------------------------------------------------
% discussion environment
% -----------------------------------------------------------------------

% \begin{dicussion}[short title][title -default-> Discussion]
\def\MQ@DiscussionStart{%
  \MQ@Debugging{Starting discussion...}%
  \ifInDiscussion\MQ@Error{discussion environments cannot be nested}\fi%
  \ifInQuestion\MQ@Error{discussion environments cannot be inside a question environment}\fi%
  \ifInQuizIndex\MQ@Error{discussion environments cannot be inside a quizindex environment}\fi%
  \global\InDiscussiontrue%
}
\def\MQ@DiscussionEnd{\global\InDiscussionfalse\MQ@Debugging{Ending discussion...}}
\NewDocumentEnvironment{discussion}{O{Discussion}O{#1}}
    {\MQ@DiscussionStart\textbf{#1} (#2)}{\MQ@DiscussionEnd\par\bigskip}

% -----------------------------------------------------------------------
% question environment
% -----------------------------------------------------------------------

% the question counter keeps track of the quiz question numbers
\newcounter{question}

\def\MQ@QuestionStart{%
  \MQ@Debugging{Starting question...}%
  \ifInDiscussion\MQ@Error{question environments cannot be inside a discussion environment}\fi%
  \ifInQuizIndex\MQ@Error{question environments cannot be inside a quizindex environment}\fi%
  \ifInQuestion\MQ@Error{question environments cannot be nested!}\fi%%
  \global\InAnswerfalse
  \global\InChoicefalse
  \global\InChoicefalse%
  \global\InItemfalse%
  \global\InQuestiontrue%
  \global\InResponsefalse
  \global\InWhenrightfalse
  \global\InWhenwrongfalse
  \refstepcounter{question}%
}

\def\MQ@QuestionEnd{
  \ifInChoice\else\ifInAnswer\else%
    \MQ@Error{Each question must contain a choice environment or an \noexpand\answer!}%
  \fi\fi%
  \global\InQuestionfalse%
  \MQ@Debugging{Ending question...}%
}

\newenvironment{question}{\MQ@QuestionStart\bigskip\textbf{Question \arabic{question}.\newline}}
                         {\par\bigskip\MQ@QuestionEnd}

% -----------------------------------------------------------------------
% choice environment, \correct and \incorrect choices and \response
% -----------------------------------------------------------------------

% the choice counter keeps track of the choices in a choice environment
\newcounter{choice}
\renewcommand\thechoice{(\alph{choice})}

\def\MQ@ChoiceStart#1{%
  \MQ@Debugging{Starting choice...}%
  \ifInQuestion\relax% Give a warning if we are not inside a question
  \else\MQ@Error{Choice environments must be contained in a question}%
  \fi%
  \ifInAnswer\MQ@Error{choice environments cannot contain an \noexpand\answer!}\fi%
  \ifInChoice\MQ@Error{choice environments cannot be nested}\fi%
  \global\InChoicetrue%
  \global\InItemfalse%
  \pgfkeys{/webquiz checker, #1}%
  \setcounter{choice}{0}% reset choice counter
}

\def\MQ@ChoiceEnd{%
  \ifInItem\else\MQ@Error{Choice environment with no choices!}\fi%
  \InChoicefalse%
  \MQ@Debugging{Ending choice...}%
}

% \begin{choice}[choice type, number of columns] ... \end{choice} The
% allowed choice types are "single" or "multiple". The type and number
% of columns is allowed to appear in either order, so most of the fun
% and games below is sanity checking of the argunments.
\NewDocumentEnvironment{choice}{O{single}}{%
  \MQ@ChoiceStart{#1}%
  \leavevmode\newline%
  (\textit{The choices will be printed in \pgfkeys{/webquiz checker/columns value} columns in the HTML version of the quiz})%
  \par%
  \setcounter{choice}{0}%
}{\MQ@ChoiceEnd}

\def\MQ@ItemStart{%
  \MQ@Debugging{Starting item...}%
  \ifInChoice\relax%
  \else\MQ@Error{\noexpand\correct and \noexpand\incorrect must be inside a choice environment}%
  \fi%
  \global\InItemtrue\global%
  \InResponsefalse%
  \refstepcounter{choice}%
}

\def\MQ@Item#1{\MQ@ItemStart\par\bigskip #1\quad\textit{Option} \thequestion\thechoice:\qquad}
\def\correct{\MQ@Item\CheckmarkBold}
\def\incorrect{\MQ@Item\XSolidBrush}

\def\MQ@ResponseStart{%
  \MQ@Debugging{Starting response...}%
  \ifInItem\relax%
  \else\MQ@Error{Missing \noexpand\correct or \noexpand\incorrect}%
  \fi%
  \ifInResponse\MQ@Error{Only one response per option is allowed!}\fi%
  \InResponsetrue%
}

\def\response{\MQ@ResponseStart\leavevmode\medskip\newline\textit{Response:}\space}

% -----------------------------------------------------------------------
% The \answer macro and \whenRight, \whenWrong
% -----------------------------------------------------------------------

% supported answer comparisons
\def\MQ@AnswerStart#1{%
  \MQ@Debugging{Starting answer...}%
  \ifInQuestion\relax%
  \else\MQ@Error{\noexpand\answer\ must be contained in a question}%
  \fi%
  \ifInChoice\MQ@Error{You cannot have \noexpand\answer inside a choice environment}\fi%
  \ifInAnswer\MQ@Error{Each question can contain only one \noexpand\answer command}\fi%
  \pgfkeys{/webquiz checker/comparison/#1}%
  \global\InAnswertrue%
  \global\InWhenrightfalse%
  \global\InWhenwrongfalse%
}

\NewDocumentCommand\answer{s O{string} m}{%
  \MQ@AnswerStart{#2}%
  \leavevmode\bigskip\newline%
  \IfBooleanTF{#1}{\fbox{\textit{(#2 comparison):}\quad#3}}%
                  {\fbox{\textit{Answer (#2 comparison):}\quad#3}}%
}

\def\MQ@WhenStart#1{%
  \MQ@Debugging{Starting when#1...}%
  \ifInAnswer\relax\else\MQ@Error{missing \noexpand\answer}\fi%
  \ifbool{InWhen#1}{%
    \MQ@Error{Only one \noexpand\when#1 per question is allowed!}%
  }{}%
  \global\booltrue{InWhen#1}%
}

\def\MQ@When#1{\MQ@WhenStart{#1}\leavevmode\medskip\newline\textit{Response when #1:}\space}
\def\whenRight{\MQ@When{right}}
\def\whenWrong{\MQ@When{wrong}}

\endinput
%% End of file `webquiz.cls'.
