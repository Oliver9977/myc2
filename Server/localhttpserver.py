"""
for payload transfer with invoke-webrequest, and namepipe

"""

import http.server
import socketserver
import threading
import uuid


def hack_httpd(directory):
    def _init(self, *args, **kwargs):
        return http.server.SimpleHTTPRequestHandler.__init__(self, *args, directory=self.directory, **kwargs)
    return type(f'HandlerFrom<{directory}>',
                (http.server.SimpleHTTPRequestHandler,),
                {'__init__': _init, 'directory': directory})

class localhttpserver():

    def __init__(self):
        self.__local_http_server_ip = "192.168.182.131"
        self.__local_http_server_port = 80
        self.__local_http_server_path = "HSDB"

        self.__local_http_server_uuid_list = list()
        self.__local_http_server_info_list = dict()
        self.__local_http_server_httpd_list = dict()


    def __t_start_resource_handler_http_server(self,myuuid):

        httpd = socketserver.TCPServer((self.__local_http_server_ip, self.__local_http_server_port), hack_httpd(self.__local_http_server_path))
        self.__local_http_server_httpd_list[myuuid] = httpd

        print("serving at port {} ..." .format(self.__local_http_server_port))
        httpd.serve_forever()


    def start_resource_handler_http_server(self):
        myuuid = uuid.uuid4().hex[:6].upper()
        self.__local_http_server_uuid_list.append(myuuid)
        self.__local_http_server_info_list[myuuid] = (self.__local_http_server_ip,self.__local_http_server_port,self.__local_http_server_path)

        threading.Thread(target=self.__t_start_resource_handler_http_server,args=(myuuid,)).start()

    def set_server_config(self,ip,port,path):
        self.__local_http_server_ip = ip
        self.__local_http_server_port = int(port)
        self.__local_http_server_path = path

    def print_server_config(self):
        print("+++++++++++++++++++++Local Http Server Info++++++++++++++++++++++")
        print("Server ip: {}".format(self.__local_http_server_ip))
        print("Server port: {}".format(self.__local_http_server_port))
        print("Server path: {}".format(self.__local_http_server_path))

    def print_running_server_info(self,myuuid):
        print("+++++++++++++++++++++Local Http Server Info++++++++++++++++++++++")
        print("Server UUID: {}".format(myuuid))
        t_infolist = self.__local_http_server_info_list[myuuid]
        print("Server ip: {}".format(t_infolist[0]))
        print("Server port: {}".format(t_infolist[1]))
        print("Server path: {}".format(t_infolist[2]))

    def get_running_list(self):
        return self.__local_http_server_uuid_list
    
    def print_running_list(self):
        print("List of running local server: {}".format(self.__local_http_server_uuid_list))
    
    def stop_resource_handler_http_server(self,myuuid):
        if myuuid in self.__local_http_server_uuid_list:
            self.__local_http_server_httpd_list[myuuid].shutdown()
            self.__local_http_server_httpd_list[myuuid].socket.close()
            self.__local_http_server_httpd_list.pop(myuuid, None)
            self.__local_http_server_info_list.pop(myuuid,None)
            self.__local_http_server_uuid_list.remove(myuuid)

        else:
            print("[HTTPD] not running")




