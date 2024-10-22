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
* If you prefer kali, use networking trick
  ```
  sudo sysctl -w net.ipv4.ip_forward=1
  sudo iptables -t nat -A POSTROUTING -o [VPN INTERFACE] -j MASQUERADE
  [Add Kali ip to Windows route table]
  sudo iptables -t nat -A PREROUTING -d [VPN IP] -j DNAT --to-destination [LOCAL WINDOWS]
  sudo iptables -t nat -A POSTROUTING -s [LOCAL WINDOWS] -j SNAT --to-source [VPN IP]
  ```

* If want to share connection
  ```
  sudo iptables -t nat -A PREROUTING -d [VPN IP] -p tcp --dport [DPORT] -j DNAT --to-destination [LOCAL WINDOWS]:[LOCAL PORT]
  ```


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

# extra hta template
* hta -> powershell
 
![alt text](img/hta.png)

# file download
![alt text](img/download1.png)
![alt text](img/download2.png)
![alt text](img/download3.png)

# change directory (ps + .net)
* `cd` in `tool` will change both ps directory and .net directory the same time. 

![alt text](img/cd.png)

# psremote
* enter remote ps session, use `psreset` to reset back to local session. 

![alt text](img/psremote1.png)
![alt text](img/psremote2.png)

# spawnps
* start a new stager using powershell. 

![alt text](img/spawnps.png)

# psjump
* jump using remote powershell. 

![alt text](img/psjump1.png)

# kerberoast
* kerberoast and asreproast

![alt text](img/kerbo.png)

# port forward

![alt text](img/pfw1.png)
![alt text](img/pfw2.png)
![alt text](img/pfw3.png)

# forward connect
* this will allow connecting to the target from a running stager

![alt text](img/fwc.png)

# Interesting findings
* With .Net 4.8 on 17763 (ie. KB4486153), process injection using the technique available in GadgetToJSscript template will fail to load `System.Management.Automation.dll` on the targeted process. It only happens with 32bit and possible workaround with inject to `powershell.exe` instead. 

![alt text](img/pierror.png)

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

