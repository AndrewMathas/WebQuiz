@echo off
setlocal enableextensions
rem assuming the main script is in the same directory
if not exist "%~dpn0.py" (
  echo %~nx0: main script "%~dpn0.py" not found>&2
  exit /b 1
)
rem check if interpreter is on the PATH
for %%I in (python.exe) do set "PYTHONEXE=%%~$PATH:I"
if not defined PYTHONEXE (
  echo %~nx0: Python interpreter not installed or not on the PATH>&2
  exit /b 1
)
"%PYTHONEXE%" "%~dpn0.py" %*
