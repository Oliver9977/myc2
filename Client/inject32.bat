@echo off
cd external\Inject
call build32.bat
cd ..\..
copy external\Inject\Inject32.exe tools\Inject32.exe