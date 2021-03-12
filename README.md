# myc2
This is my version of c2, intended for penetration testing, but also useful for validation automation. 

* reverse/bind socket/pipe shell
* exe/ps1 payload
* hta/js/vba/vbs payload using GadgetToJScript
* buildin ps command lists to get av,clm,al
* command history for each stager
* tab completion
* AMSI/AV bypass

# dependence
* python3.7 + pywin32
* Microsoft Visual Studio 2019


# psload + maketoken
* psload can be used to load any ps script in the database to the stager runspace
* maketoken from sharpsploit is integrated

![alt text](img/psexec.png)

# psexec
* psexec can be chained with maketoken

![alt text](img/psexec2.png)
![alt text](img/psexec3.png)

# process injection

![alt text](img/inject.png)

# local httpserver
![alt text](img/localserver.png)
![alt text](img/localserver2.png)

# extra payload types
![alt text](img/gtojs.png)

# disclaimer
* for education and reseach only
* some of the imbedded tools are from online repo and training course, and improved/av-bypessed by me. let me know if licensing issue, will remove immediately.

# reference
* https://www.offensive-security.com/pen300-osep/
* https://www.pentesteracademy.com/redlabs
* https://github.com/xpn
* https://github.com/S3cur3Th1sSh1t
* https://github.com/0x00-0x00/NamedPipes
* https://github.com/med0x2e/GadgetToJScript 

