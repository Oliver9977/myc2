@echo off
cd external\shellcode-encoder
call build.bat
cd ..\..
copy external\shellcode-encoder\shellcode-encoder.exe tools\shellcode-encoder.exe
tools\shellcode-encoder.exe