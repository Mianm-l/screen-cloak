@echo off
cd /d "%~dp0"
start "" wscript.exe "%~dp0start_silent.vbs"
exit
