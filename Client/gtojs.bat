@echo off
cd external\GadgetToJScript
call build.bat
cd ..\..
cp external\GadgetToJScript\test.hta payload\GadgetToJScript\test.hta
cp external\GadgetToJScript\test.js payload\GadgetToJScript\test.js
cp external\GadgetToJScript\test.vba payload\GadgetToJScript\test.vba
cp external\GadgetToJScript\test.vbs payload\GadgetToJScript\test.vbs
