@echo off
copy payload\myclient32.exe external\donut\target32.exe
cd external\donut
call toshellcode32.bat
cd ..\..
copy external\donut\loader.bin payload\loader32.bin
copy external\donut\loader.bin external\Inject\Resources\loader.bin
