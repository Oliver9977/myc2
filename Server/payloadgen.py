import os
import subprocess

class mypayloadgen():
    def __init__(self):
        self.__to_client = "Client\\"
        self.__to_pstemplate = "Client\\payload\\template\\"
        self.__pstemplate = "Invoke-myclient.ps1"
        self.__parentdir = os.path.dirname(os.getcwd())
        self.__payload_tag = r"%%PAYLOAD%%"
        self.__to_payload = "Client\\payload\\"
        self.__outputname = "Invoke-myclient.ps1"

    def gen_exe(self):
        
        mycwd = os.path.join(self.__parentdir,self.__to_client)

        output = subprocess.run(["psgen.bat"], capture_output=True, shell=True, cwd=mycwd)
        myb64 = output.stdout.decode("utf-8")[:-2] #remove new line and EOF

        with open(os.path.join(self.__parentdir,self.__to_pstemplate,self.__pstemplate),mode='r') as f:
            all_of_it = f.read()
        
        #print(all_of_it.replace(self.__payload_tag,myb64))
        with open(os.path.join(self.__parentdir,self.__to_payload,self.__outputname),mode='w') as f:
            f.write(all_of_it.replace(self.__payload_tag,myb64))




if __name__ == "__main__":
    t_mypayloadgen = mypayloadgen()
    t_mypayloadgen.gen_exe()

