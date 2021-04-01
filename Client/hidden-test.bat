@echo off
cd external\hidden-test
call build.bat
cd ..\..
copy external\hidden-test\hidden-test.exe tools\hidden-test.exe