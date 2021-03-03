@echo off
"C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\MSBuild\Current\Bin\MSBuild.exe" /p:Configuration=Debug /p:Platform=x64 /t:csexec-net45
copy csexec\bin\x64\Debug\csexec.exe
"C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\MSBuild\Current\Bin\MSBuild.exe" /p:Configuration=Debug /p:Platform=x64 /t:clean
rmdir csexec\bin /s /q
rmdir csexec\obj /s /q
rmdir csexecsvc\bin /s /q
rmdir csexecsvc\obj /s /q