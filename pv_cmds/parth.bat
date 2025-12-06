@echo off
REM if the user gave only a filename, add the examples folder
IF EXIST "%~1" (
    python "D:\Parth\PV_lang\main.py" "%~1"
) ELSE (
    python "D:\Parth\PV_lang\main.py" "D:\Parth\PV_lang\examples\%~1"
)
