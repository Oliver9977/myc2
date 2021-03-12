@echo off
cd external\GadgetToJScript
call build32.bat
cd ..\..
copy external\GadgetToJScript\test32.hta payload\GadgetToJScript\test32.hta
