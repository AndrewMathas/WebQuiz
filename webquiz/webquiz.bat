@echo off
rem WebQuiz batch file to find and launch python executable

rem Set TEXMF to root TeX directory and look for webquiz.py in scripts/webquiz
setlocal enableextensions
for /F "tokens=*" %%i in ('kpsewhich -var-value TEXMFMAIN') do (SET TEXMF=%%i)

rem First look for webquiz.py in the current directory
set WebQuiz="webquiz.py"
if not exist %WebQuiz% (
    if exist "%TEXMF%/scripts/webquiz/webquiz.py" (
      set WebQuiz="%TEXMF%/scripts/webquiz/webquiz.py"
    )
)
rem
rem exit with an error if webquiz.py has not been found
if not exist %WebQuiz% (
  echo WebQuiz executable not found. Please check that WebQuiz is properly installed>&2
  exit /b 1
)

rem check for the python interpreter in the PATH
for %%I in (python.exe) do set "PYTHONEXE=%%~$PATH:I"
if not defined PYTHONEXE (
  echo %~nx0: Python interpreter not installed or not on the PATH>&2
  exit /b 1
)

rem launch webquiz
"%PYTHONEXE%" %WebQuiz% %*
