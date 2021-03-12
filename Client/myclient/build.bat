@echo off
"C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\MSBuild\Current\Bin\MSBuild.exe" /p:Configuration=Release /p:Platform="Any CPU"
copy bin\Release\myclient.exe
"C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\MSBuild\Current\Bin\MSBuild.exe" /p:Configuration=Release /p:Platform="Any CPU" /t:clean
rmdir bin /s /q
rmdir obj /s /q