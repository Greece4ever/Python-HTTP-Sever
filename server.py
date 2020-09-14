import socket
from typing import Union
import status
from datetime import datetime
from pythematics.random import choice
from routes import URLS

LOCALHOST : str = "127.0.0.1"
HTTP_PORT : int = 80

class Server:
    def __init__(self,host : str = LOCALHOST,port : int = HTTP_PORT):
        print(f"Starting local  Server on {host}:{port}")
        self.adress = (host,port)
        self.connection = socket.socket()
        self.connection.bind(self.adress)
    
    def ParseHeaders(self,request : Union[bytes,str]):
            HEADERS = {}
            XS = request.decode('utf-8').split("\r\n")
            XS = [item for item in XS if item.strip() != '']
            HEADERS['method'] = XS.pop(0).replace("HTTP/1.1",'').strip()
            term : str
            for term in XS:
                spl : list = term.split(":")
                HEADERS[spl[0].strip()] = spl[1].strip()
            return HEADERS

    def AwaitRequest(self):
        while True:
            self.connection.listen(1)
            address : tuple
            client,address = self.connection.accept()
            request = client.recv(1024)
            if len(request) == 0:
                client.send(choice(status.EXCEPTIONS).__call__("<b>No Data Was Provided</b>"))
                print(f' Unknown | {str(datetime.now())} : {address}')
                continue
            headers = self.ParseHeaders(request)
            print(f'{headers["method"]} | {str(datetime.now())} : {address}')
            URL = headers["method"]
            target = URL.split(" ")[1]
            if not target in URLS:
                client.send(status.Http404.__call__("<b>Page {} Was not Found (404 Status Code)</b>".format(target)))
            else:
                client.send(URLS.get(target).__call__(headers))
            client.close()

HTTP = Server()
HTTP.AwaitRequest() 
                

