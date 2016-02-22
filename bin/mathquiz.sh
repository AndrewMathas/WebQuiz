#!/bin/sh -f

#*****************************************************************************
#       Copyright (C) 2010 Andrew Mathas and Donald Taylor
#                          University of Sydney
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#*****************************************************************************

# This is a shell wrapper for the MathQuiz conversion programs. We
# first run htlatex on $quizfile=$x, and then use mathquiz.py to
# convert the xml produced into html. Finally, we move all images
# files into a subdirectory, called $quizfile, and remove all
# extraneous files.
#                                         Andrew Mathas, 20/1/2004

# Directory containing the local mathquiz files. This is the top level
# directory which contains the python files etc for MathQuiz
MathQuizSRC="/usr/local/src/MathQuiz/"
# The relative URL for MathQuiz on your web server. This is the top level URL
# for MathQuiz which is needed for links for the images
MathQuizURL="/MathQuiz/"
# Location of python
Python="/usr/bin/python"

#############################################################################
# option defaults -- you shouldn't need to change anything after this line.
runhtlatex=1
debug=0
deletexmlfile=1
htoptions=""
MathQuizOptions=""
SRC=""
Version="4.4"

usage() {
  cat <<EndOfUsage 
MATHQUIZ(1)               SMS Manual Page

  mathquiz - convert latex file which uses mathquiz.cls into an 
             HTML based quiz 

SYNOPSIS
  mathquiz [-f] [-x] file

DESCRIPTION
  MathQuiz is a system for writing interactive web quizzes. It
  uses tex4ht together with some python scripts to convert a
  latex file, which uses the mathquiz.cls class file, into an
  interactive web based quiz.
  
  For documentation on using the mathquiz.cls class file see:
    http://rome/u/MOW/MathQuiz/doc/mathquiz-manual.html

  MathQuiz is maintained by Andrew Mathas so any queries should
  be directed to him at an.drewmathas@sydney.edu.au. Please contact
  him with any queries about mathquiz.

OPTIONS
  Both options are for debugging and are not intended for general
  use.
      -f    Process only the xml file (and does not run htlatex).
            This option. This is only useful if mathquiz was last
            run using the -x option (otherwise, there is no xml
            file to process).
      -x    Do not delete the xml file.
      -v #V Use version #V
      -d    Debug mode: no intermediate files are deleted.

AUTHOR
  Andrew Mathas

Version $Version                                      April 2010

EndOfUsage
exit 
}

# parse arguments
set -- `getopt --quiet --unquoted l:v:dfx $*`
test $? -ne 0 && ( usage; exit )

while [ $1 != -- ]
do
  case $1 in
    -f) runhtlatex=0 
        deletexmlfile=0 ;;
    -v) SRC="$2"
        shift;;
    -d) debug=1 
        deletexmlfile=0 ;;
    -l) MathQuizOptions="--local $2"
        shift ;;
    -x) deletexmlfile=0 ;;
    -*) usage && exit   ;;
  esac
  shift
done
shift # move past the "--" returned by getopt

MathQuizSRC="${MathQuizSRC}${SRC}/src"
echo "Using ${MathQuizSRC} version ${Version}"

# check numbr of arguments and exit if necessary
test $# -ne 1 && usage 

# remove extension from $1
quizfile="`echo $1 | sed 's@\..*@@'`"

# check that quiz file exists
test ! -r "$quizfile.tex" \
  && echo "  MathQuiz: File $quizfile.tex not found" && exit 1

# set file permissions for any files that we create
umask 022

# Test that tex file exists and create quizfile subdirectory if needed
test ! -r $quizfile.tex && echo "$quizfile.tex not found !!" && exit 1

# remove old html file
/bin/rm -f $quizfile.html

if test $runhtlatex -eq 0 ; then

  # skip htlatex
  echo "Converting to html"
  $Python  $MathQuizSRC/mathquiz.py --url "$MathQuizURL" $MathQuizOptions $quizfile.xml > $quizfile.html

else
  # remove old image files
  test -e $quizfile && /bin/rm -Rf $quizfile
  test ! -e $quizfile && mkdir $quizfile

  echo "Running htlatex: htlatex $quizfile $MathQuizSRC/mathquiz $htoptions"
  htlatex $quizfile $MathQuizSRC/mathquiz.cfg $htoptions

  echo "Converting to html"
  mv $quizfile.html $quizfile.xml
  $Python  $MathQuizSRC/mathquiz.py $MathQuizOptions $quizfile.xml > $quizfile.html

  test $? -ne 0 && echo "ERROR: MathQuiz returned an error?!" && exit $?

  # Now move all of the image files into the directory $quizfile -
  # This should be done by tex4ht??? The bonus is that we remove the
  # $quizfile directory if there are no images.
  if test $runhtlatex -eq 1; then 
    echo "moving images files"
    gawk -F\/ -v quizfile="$quizfile" \
         'BEGIN{str="src=\"" quizfile; moved["fred"]=0 ; images=0 } 
          ($1 == str) { file=substr($2,1, index($2,"\"")-1) 
                        if ( ! (file in moved) ) {
                          images+=1
                          moved[ file ]=1
                          cmd="/bin/mv " file " " quizfile "/" file 
  		        system( cmd ) 
  		        close ( cmd 
  		    } 
          }
          END{ if (images==0) system("/bin/rmdir " quizfile ) 
          }' $quizfile.xml
  fi
fi

# Remove everything but the original tex file, and the html and css files
if test $debug -eq 0 ; then
  /bin/rm -f $quizfile.{aux,4ct,dvi,idv,log,4tc,lg,tmp,xref}
fi

test $deletexmlfile -eq 1 && /bin/rm $quizfile.xml

#echo "Please contact Andrew Mathas with any queries about mathquiz."

