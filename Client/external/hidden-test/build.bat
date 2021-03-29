@echo off
"C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\MSBuild\Current\Bin\MSBuild.exe" /p:Configuration=Release /p:Platform=x64
copy bin\x64\Release\hidden-test.exe
"C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\MSBuild\Current\Bin\MSBuild.exe" /p:Configuration=Release /p:Platform=x64 /t:clean
rmdir bin /s /q
rmdir obj /s /q