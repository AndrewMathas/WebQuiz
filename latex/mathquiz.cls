% -----------------------------------------------------------------------
%   mathquiz.cls | mathquiz latex class file
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
%   <Donald.Taylor@sydney.edu.au>
% ----------------------------------------------------------------------

\NeedsTeXFormat{LaTeX2e}[1996/12/01]
\ProvidesClass{mathquiz}
  [2017/03/21 v5.0
  MathQuiz LaTeX document class (based on article.cls)]

\DeclareOption{pst2pdf}{
   % this option tells mathquiz to use pst2pdf
   \ifdefined\HCode\else
     \AtBeginDocument{\textsc{MathQuiz} will process this quiz using \textbf{pst2pdf}.}
   \fi
}


\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\PassOptionsToClass{a4paper}{article}
\ProcessOptions\relax
\LoadClass{article}

\def\MQ@error{\PackageError{mathquiz}}
\def\MQ@complain#1#2{%
  \MQ@error{\noexpand#1 required in Question \number#2}\@ehc
}

\RequirePackage{amsfonts,amsmath}
\RequirePackage{bbding}
\setlength{\parindent}{0pt}
\setlength{\parskip}{10pt}

% Set the quiz filename for use in mathquiz -- can be set directly by mathquiz when
% doing pst2pdf preprocessing
\ifdefined\MQ@quizfile\relax\else\xdef\MQ@quizfile{\jobname.tex}\fi

% Macros for defining the university and department
\newcommand*{\DepartmentURL}[1]{\def\MQ@depturl{#1}}
\newcommand*{\Department}[1]{\def\MQ@department{#1}}
\newcommand*{\UniversityURL}[1]{\def\MQ@uniurl{#1}}
\newcommand*{\University}[1]{\def\MQ@university{#1}}

% Macros for defining the quiz web breadcrumbs using the unit code, name and
% URL. The names of these macros are chosen so as to be compatible with the
% in-house SMS package sms-uos.sty that specifies these for all units.
\newcommand*{\UnitCode}[1]{\def\uos@code{#1}}
\newcommand*{\UnitName}[1]{\def\uos@name{#1}}
\newcommand*{\UnitURL}[1]{\def\uos@url{#1}}
\newcommand*{\QuizzesURL}[1]{\def\MQ@quizzesUrl{#1}}
\newcommand*{\BreadCrumb}[1]{\def\MQ@breadCrumb{#1}}

% Trickery to set the breadcrumb equal to the portion of the title before
% a colon in the title...I can't remember but [resumably this is used in
% some of the SMS quizzes.
\def\MQ@SetBreadCrumb#1:#2!{\def\MQ@breadCrumb{#1}}
\def\title#1{\def\@title{#1}\MQ@SetBreadCrumb#1:!}

% Default values - the university and department defaults can also be
% set in the mathquizrc file. The main purpose of these defaults is
% to remind the user to set them.
\UnitCode{Unit code???}
\UnitName{Unit name???}
\UnitURL{Unit URL???}
\QuizzesURL{}
\BreadCrumb{Crumbs???}
\Department{School of Mathematics and Statistics}
\DepartmentURL{/}
\University{University of Sydney}
\UniversityURL{https://www.sydney.edu.au}

% Define page header and footer for the printable version of the quiz
% to show the course code information.
\def\ps@quiz{\ps@empty
  \def\@oddhead{\hbox to\textwidth{%
      \uos@code\hss\textsc{\@title}\hss Page \thepage}}%
  \let\@evenhead=\@oddhead
}
\def\ps@firstpage{\ps@empty
  \def\@oddhead{{\hbox to\textwidth{\tiny
        \begin{tabular}{rl}
          Course code &\uos@code \\
          Course URL  &\uos@url
        \end{tabular}
        \hfill
        \begin{tabular}{rl}
          Course name &\uos@name \\
          Quizzes URL    &\MQ@quizzesUrl
        \end{tabular}
      }}
  }
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
  \thispagestyle{firstpage}
  \maketitle%
  \ifx\MQ@quizzesUrl\@empty\QuizzesURL{\uos@url/Quizzes/}\else\relax\fi%
}

% deifne a quiz counter for keeping track of the question numbers
\newcounter{quiz}
\newcommand{\quiz}[2][\relax]{\refstepcounter{quiz}%
  \ifx#1\relax\def\MQ@url{./quiz\thequiz.html}%
  \else\def\MQ@url{#1}\fi%
  \leavevmode\medskip\newline%
  \textbf{Quiz~\arabic{quiz}}.\space #2. \newline
  \phantom{XXX}\textit{URL}:\quad \MQ@url}
\newenvironment{quizlist}{\bigskip}{}
\newenvironment{discussion}[1][Discussion]{\textbf{#1}\newline}{\par\bigskip}

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
\newenvironment{Choice}[2][\relax]{%
  \if2#2\else%
  (\textit{The choices will be listed in #2 columns in
    the HTML version of the quiz})
  \fi
  \ifInQuestion\relax
  \else\MQ@error{Choice environments must be contained in a question}
  \fi
  \global\InChoicetrue
  \par\ifx #1\relax(\textit{Exactly one option must be correct})%
  \else(\textit{Zero or more options can be correct})
  \fi%
  \setcounter{choice}{0}%
}{\InChoicefalse}

\newenvironment{choice}[1][\relax]
{\begin{Choice}[#1]{2}}%
  {\end{Choice}}
\newif\ifanswer
\newif\ifWhenRight
\newif\ifWhenWrong
\newcommand\answer[2][\relax]{%
  \answertrue%
  \ifInQuestion\relax%
  \else\MQ@error{\noexpand\answer\ must be contained in a question}%
  \fi%
  \ifInChoice%
  \MQ@error{You cannot have \noexpand\answer\ inside multiple choice}%
  \fi%
  \InAnswertrue%
  \leavevmode\bigskip\newline%
  \fbox{\textit{Answer:}\qquad#2}\qquad#1%
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
%% End of file `mathquiz.cls'.
