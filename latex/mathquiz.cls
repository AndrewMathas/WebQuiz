%*****************************************************************************
%       Copyright (C) 2004-2010 Andrew Mathas and Donald Taylor
%                          University of Sydney
%
%  Distributed under the terms of the GNU General Public License (GPL)
%                  http://www.gnu.org/licenses/
%
% This file is part of the MathQuiz system.
% 
% Copyright (C) 2004-2010 by the School of Mathematics and Statistics
% <Andrew.Mathas@sydney.edu.au>
% <Donald.Taylor@sydney.edu.au>
%*****************************************************************************

\NeedsTeXFormat{LaTeX2e}[1996/12/01]
\ProvidesClass{mathquiz}
  [2004/12/02 v4.1
  MathQuiz LaTeX document class (based on article.cls)]
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\PassOptionsToClass{a4paper}{article}
\ProcessOptions\relax
\LoadClass{article}
\RequirePackage{amsfonts,amsmath}
\RequirePackage{bbding}
\setlength{\parindent}{0pt}
\setlength{\parskip}{10pt}
\newcommand*{\University}[1]{\def\MQ@university{#1}}
\newcommand*{\Department}[1]{\def\MQ@department{#1}}
\newcommand*{\CopyrightNotice}[1]{\def\MQ@copyright{#1}}
\University{The University of Sydney}
\Department{School of Mathematics and Statistics}
\CopyrightNotice{\the\year{} \MQ@university}
\newcommand*{\UnitCode}[1]{\def\MQ@unitCode{#1}}
\newcommand*{\UnitName}[1]{\def\MQ@unitName{#1}}
\newcommand*{\UnitURL}[1]{\def\MQ@unitUrl{#1}}
\newcommand*{\QuizzesURL}[1]{\def\MQ@quizzesUrl{#1}}
\newcommand*{\BreadCrumb}[1]{\def\MQ@breadCrumb{#1}}
\def\MQ@SetBreadCrumb#1:#2!{\def\MQ@breadCrumb{#1}}
\def\title#1{\def\@title{#1}\MQ@SetBreadCrumb#1:!}
\UnitCode{}
\UnitName{MathQuiz file}
\UnitURL{}
\QuizzesURL{}
\def\@title{No title}
\def\ps@quiz{\ps@empty
  \def\@oddhead{\hbox to\textwidth{%
      \MQ@unitCode\hss\textsc{\@title}\hss Page \thepage}}%
  \let\@evenhead=\@oddhead
}
\def\ps@firstpage{\ps@empty
  \def\@oddhead{{\hbox to\textwidth{\tiny
        \begin{tabular}{rl}
          Course code &\MQ@unitCode \\
          Course URL  &\MQ@unitUrl
        \end{tabular}
        \hfill
        \begin{tabular}{rl}
          Course name &\MQ@unitName \\
          Quiz URL    &\MQ@quizzesUrl
        \end{tabular}
      }}
  }
}
\AtBeginDocument{\thispagestyle{firstpage}}
\pagestyle{quiz}
\def\MQ@error{\PackageError{mathquiz}}
\def\maketitle{\vspace*{10mm}\begin{center}
    {\large\textsc{\@title}}%
  \end{center}
\def\title{%
  \MQ@error{\@backslashchar title can only be used in the preamble}%
  \@ehc}
}
\ifx\MQ@quizzesUrl\@empty\QuizzesURL{\MQ@unitUrl Quizzes/}\else\relax\fi%
\AtBeginDocument{\maketitle}
\newcounter{quiz}
\newcommand{\quiz}[2][\relax]{\refstepcounter{quiz}%
  \ifx#1\relax\def\MQ@url{./quiz\thequiz.html}%
  \else\def\MQ@url{#1}\fi%
  \leavevmode\medskip\newline%
  \textbf{Quiz~\arabic{quiz}}.\space #2. \newline
  \phantom{XXX}\textit{URL}:\quad \MQ@url}
\newenvironment{quizlist}{\bigskip}{}
\newenvironment{discussion}[1][Discussion]{\textbf{#1}\newline}{\par\bigskip}
\def\MQ@complain#1#2{%
  \MQ@error{\noexpand#1 required in Question \number#2}\@ehc
}
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
