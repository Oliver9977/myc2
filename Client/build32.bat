@echo off
cd myclient
call build32.bat
cd ..
copy myclient\myclient32.exe payload\myclient32.exe
