@echo off
cd external\CSExec
call build.bat
cd ..\..
copy external\CSExec\csexec.exe tools\csexec.exe
