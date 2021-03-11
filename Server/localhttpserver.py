"""
for payload transfer with invoke-webrequest, and namepipe

"""

import http.server
import socketserver
import threading



class localhttpserver():

    def __init__(self):
        self.__local_http_server_ip = "192.168.182.131"
        self.__local_http_server_port = 80
        self.__local_http_server_path = "HSDB\\"


    def __t_start_resource_handler_http_server(self):
        t_handler = http.server.SimpleHTTPRequestHandler

        with socketserver.TCPServer((self.__local_http_server_ip, self.__local_http_server_port), t_handler) as httpd:
            print("serving at port {} ..." .format(self.__local_http_server_port))
            httpd.serve_forever()


    def start_resource_handler_http_server(self):
        threading.Thread(target=self.__t_start_resource_handler_http_server).start()

    def set_server_config(self,ip,port,path):
        self.__local_http_server_ip = ip
        self.__local_http_server_port = port
        self.__local_http_server_path = path

    def print_server_config(self):
        print("+++++++++++++++++++++Local Http Server Info++++++++++++++++++++++")
        print("Server ip: {}".format(self.__local_http_server_ip))
        print("Server port: {}".format(self.__local_http_server_port))
        print("Server path: {}".format(self.__local_http_server_path))

        

