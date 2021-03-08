@echo off
cd external\Inject
call build.bat
cd ..\..
copy external\Inject\Inject.exe tools\Inject.exe