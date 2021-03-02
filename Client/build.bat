@echo off
cd myclient
call build.bat
cd ..
copy myclient\myclient.exe payload\myclient.exe
