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
\ProvidesClass{webquiz}
  [2017/03/21 v5.0
  WebQuiz LaTeX document class (based on article.cls)]


% initialise and then process document class options usng pgfopts
\RequirePackage{etoolbox}
\RequirePackage{pgfopts}
\def\unknown@options{}%          unknown options are passed to article.cls
\def\MQ@HideSideMenu{deFAULT}%     side menu visible by default
\newif\ifTikz\Tikzfalse%         true if tikz a document class option
\newif\ifpsttopdf\psttopdffalse% true if pst2pdf a document class option

% Process the documentclass options using pgfkeys and \ProcessPgfOptions
\pgfkeys{/latexquizoptions/.is family,
  /latexquizoptions,
      pst2pdf/.code      = {\global\psttopdftrue},
      tikz/.code         = {\global\Tikztrue},
      sidemenu/.style     = {hidesidemenuvalue=false},
      hidesidemenu/.style     = {hidesidemenuvalue=true},
      hidesidemenuvalue/.initial = deFAULT,
      language/.initial  = deFAULT,
      theme/.initial     = deFAULT,
      .unknown/.code={\edef\unknown@options{\unknown@options,\pgfkeyscurrentname}}
}
\newcommand\latexquizOption[1]{\pgfkeysvalueof{/latexquizoptions/#1}}

% use pgfkeys to check for valid options for the choice environment and the
% answer comparisons. As \ERROR is not define this generates an error message
% if the option is not defined.
\pgfkeys{/webquiz checker/.is family, /webquiz checker,
  choice/.is choice,
  choice/single/.code = {\textit{Exactly one option must be correct}},
  choice/multiple/.code = {\textit{Zero or more options can be correct}},
  choice/.unknown/.code = {\ERROR: invalid choice type: use single or multiple}
  comparison/.is choice,
  comparison/integer/.code = \relax,
  comparison/number/.code = \relax,
  comparison/string/.code = \relax,
  comparison/lowercase string/.code = \relax,
  comparison/eval/.code=\relax,
  comparison/.unknown/.code = {\ERROR: invalid input type: use integer, string or eval}
}

% now process the options
\ProcessPgfOptions{/latexquizoptions}% process options
\LoadClass[\unknown@options]{article}% load article class with options

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\RequirePackage{xparse}
\RequirePackage{pgffor}

% hack to fix two pgf bugs - apply only when when using tex4ht
\ifdefined\HCode
 \def\pgfsysdriver{pgfsys-tex4ht-mq-fixed.def}
\fi

\ifTikz
   \RequirePackage{tikz}
   % from https://tex.stackexchange.com/questions/390592/
   %   \ifdefined\HCode
   %     \tikzset{every node/.style={/pgf/tex4ht node/escape=true}}
   %   \fi
\fi

\def\MQ@error{\PackageError{webquiz}}
\def\MQ@complain#1#2{%
  \MQ@error{\noexpand#1 required in Question \number#2}\@ehc
}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\RequirePackage{amsfonts,amsmath}
\RequirePackage{bbding}
\setlength{\parindent}{0pt}
\setlength{\parskip}{10pt}

% Set the quiz filename for use in webquiz -- can be set directly by webquiz when
% doing pst2pdf preprocessing
\ifdefined\MQ@quizfile\relax\else\xdef\MQ@quizfile{\jobname.tex}\fi

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
\newcommand*{\UniversityURL}[1]{\def\MQ@institutionURL{#1}}
\newcommand*{\Institution}[1]{\def\MQ@institution{#1}}
\newcommand*{\University}[1]{\def\MQ@institution{#1}}

% Macros for defining the quiz web breadcrumbs using the unit code, name and
% URL. The names of these macros are chosen so as to be compatible with the
% in-house SMS package sms-uos.sty that specifies these for all units.
\newcommand*{\UnitCode}[1]{\def\uos@code{#1}}
\newcommand*{\UnitName}[1]{\def\uos@name{#1}}
\newcommand*{\UnitURL}[1]{\def\uos@url{#1}}
\newcommand*{\QuizzesURL}[1]{\def\MQ@quizzesUrl{#1}}
\newcommand*{\BreadCrumb}[1]{\def\MQ@breadcrumb{#1}}
\newcommand*{\BreadCrumbs}[1]{\def\MQ@breadcrumbs{#1}}

% Trickery to set the breadcrumb equal to the portion of the title before
% a colon in the title...I can't remember but presumably this is used in
% some of the SMS quizzes.
\def\MQ@SetBreadCrumb#1:#2!{\def\MQ@breadcrumb{#1}}
\def\title#1{\def\@title{#1}\MQ@SetBreadCrumb#1:!}

% Default values - the university and department defaults can also be
% set in the webquizrc file. The main purpose of these defaults is
% to remind the user to set them.
\UnitCode{Unit code?}
\UnitName{Unit name?}
\UnitURL{}
\QuizzesURL{deFAULT}
\BreadCrumb{deFAULT}
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
\def\ps@firstpage{\ps@empty
%   \def\@oddhead{{\hbox to\textwidth{\tiny
%         \begin{tabular}{rl}
%           Institution     & \MQ@institution \\
%           Unit name       & \uos@name \\
%           Unit code       & \uos@code \\
%           Bread crumbs    & \expandafter\string\expandafter{\MQ@breadcrumbs}
%         \end{tabular}
%         \hfill
%         \begin{tabular}{rl}
%           Institution URL & \MQ@institutionURL\\
%           Unit URL        & \uos@url \\
%           Quizzes URL     & \MQ@quizzesUrl
%         \end{tabular}
%       }}
%  }
}
\pagestyle{quiz}


%
\def\@title{No title}
\def\maketitle{\vspace*{10mm}
  \begin{center}
    {\large\textsc{\@title}}%
  \end{center}
  \def\title{%
    \MQ@error{\@backslashchar title can only be used in the preamble}%
  \@ehc}
}

\AtBeginDocument{%
  \thispagestyle{firstpage}%
  \maketitle%
  \ifx\MQ@quizzesUrl\@empty\QuizzesURL{\uos@url/Quizzes/}\else\relax\fi%
  \ifpsttopdf
   \ifdefined\HCode\else
     \textsc{WebQuiz} will process this quiz using \textbf{pst2pdf}.
   \fi
  \fi
}

% define a quiz counter for keeping track of the question numbers
\newcounter{quiz}
\newcommand{\quiz}[2][\relax]{\refstepcounter{quiz}%
  \ifx#1\relax\def\MQ@url{./quiz\thequiz.html}%
  \else\def\MQ@url{#1}\fi%
  \leavevmode\medskip\newline%
  \textbf{Quiz~\arabic{quiz}}.\space #2. \newline
  \phantom{XXX}\textit{URL}:\quad \MQ@url}
\newenvironment{quizlist}{\bigskip}{}
% \begin{dicussion}[short title][title -default-> Discussion]
\NewDocumentEnvironment{discussion}{O{Discussion}o}{%
\IfNoValueTF{#2}{\textbf{#1}}{\texbf{#2} (#1)}\newline}{\par\bigskip}
\newenvironment{banner}{\centerline{Web page banner}}{}

% As
\newif\ifInQuestion
\newif\ifInChoice
\newif\ifInItem
\newif\ifInAnswer
\newif\ifHaveResponse

\newcounter{question}
\newenvironment{question}{\bigskip%
  \refstepcounter{question}
  \global\answerfalse
  \global\InQuestiontrue
  \global\InChoicefalse
  \global\InItemfalse
  \global\InAnswerfalse
  \textbf{Question \arabic{question}.\newline}}
{\InQuestionfalse
  \ifanswer
  \ifWhenRight\else\MQ@complain\whenRight\thequestion\fi
  \ifWhenWrong\else\MQ@complain\whenWrong\thequestion\fi
  \fi
  \par\bigskip}

% \begin{choice}[choice type, number of columns] ... \end{choice} The
% allowed choice types are "single" or "multiple". The type and number
% of columns is allowed to appear in either order, so most of the fun
% and games below is sanity checking of the argunments.
\NewDocumentEnvironment{choice}{O{}}{%
  \ifInQuestion\relax% Give a warning if we aer not inside a question
  \else\MQ@error{Choice environments must be contained in a question}%
  \fi%
  \def\MQ@choicetype{single}% default choice type is single
  \def\MQ@choicecols{2}     % default of 2 columns
  \foreach \opt in {#1} {%    loop throug the options and check for strings and numbers
    \ifnum0<0\opt1\relax% \opt is a positive integer%
       \xdef\MQ@choicecols{\opt}%
    \else%
       \pgfkeys{/webquiz checker/choice/\opt}%
       \xdef\MQ@choicetype{\opt}%
    \fi%
  }%
  \leavevmode\newline
  (\textit{The choices will be printed in \MQ@choicecols\ columns in the HTML version of the quiz})
  \global\InChoicetrue%
  \par%
  \setcounter{choice}{0}%
}{\InChoicefalse}

% booleans for keeping track of where we are in an answer
\newif\ifanswer
\newif\ifWhenRight
\newif\ifWhenWrong
% supported answer comparisons
\newcommand\answer[2][integer]{%
  \answertrue%
  \ifInQuestion\relax%
  \else\MQ@error{\noexpand\answer\ must be contained in a question}%
  \fi%
  \ifInChoice%
  \MQ@error{You cannot have \noexpand\answer\ inside multiple choice}%
  \fi%
  \pgfkeys{/webquiz checker/comparison/#1}%
  \InAnswertrue%
  \leavevmode\bigskip\newline%
  \fbox{\textit{Answer (comparison #1):}\qquad#2}%
  \WhenRightfalse\WhenWrongfalse}
\newcounter{choice}
\def\MQ@option#1{%
  \ifInChoice\relax%
  \else\MQ@error{\noexpand\(in)correct must be inside a choice environment}
  \fi
  \InItemtrue\global\HaveResponsefalse
  \refstepcounter{choice}\par
  \bigskip #1\quad\textit{Option} \thequestion(\alph{choice}):\qquad}
\def\correct{\MQ@option\CheckmarkBold}
\def\incorrect{\MQ@option\XSolidBrush}
\def\response{%
  \ifInItem\relax
  \else\MQ@error{Missing \noexpand\(in)correct}
  \fi
  \ifHaveResponse\MQ@error{Only one response per option is allowed!}
  \fi
  \HaveResponsetrue
  \leavevmode\medskip\newline\textit{Response:}\space
}
\def\MQ@rightwrong#1{
  \ifInAnswer\relax
  \else\MQ@error{missing \noexpand\answer }
  \fi
  \leavevmode\medskip\newline\textit{Response when #1:}\space
}
\def\whenRight{\WhenRighttrue\MQ@rightwrong{right}}
\def\whenWrong{\WhenWrongtrue\MQ@rightwrong{wrong}}
\endinput
%%
%% End of file `webquiz.cls'.
