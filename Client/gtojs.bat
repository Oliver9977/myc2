@echo off
cd external\GadgetToJScript
call build.bat
cd ..\..
copy external\GadgetToJScript\test.hta payload\GadgetToJScript\test.hta
copy external\GadgetToJScript\test.js payload\GadgetToJScript\test.js
copy external\GadgetToJScript\test.vba payload\GadgetToJScript\test.vba
copy external\GadgetToJScript\test.vbs payload\GadgetToJScript\test.vbs
