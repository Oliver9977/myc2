@echo off
"C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\MSBuild\Current\Bin\MSBuild.exe" /p:Configuration=Release /p:Platform=x86
copy bin\x86\Release\Inject.exe Inject32.exe
"C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\MSBuild\Current\Bin\MSBuild.exe" /p:Configuration=Release /p:Platform=x86 /t:clean
rmdir bin /s /q
rmdir obj /s /q