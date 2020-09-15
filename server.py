import socket
from typing import Union
import status
from datetime import datetime
import re
import threading

LOCALHOST : str = "127.0.0.1"
HTTP_PORT : int = 80

class Server:
    def __init__(self,host : str = LOCALHOST,port : int = HTTP_PORT,http : bool = True):
        print(f"Starting local {'HTTP' if http else 'WS'} Server on {host}:{port}")
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

    def AwaitRequest(self,URLS : dict):
        while True:
            self.connection.listen(1)
            address : tuple
            client,address = self.connection.accept()
            request = client.recv(1024)
            if len(request) == 0:
                continue
            headers = self.ParseHeaders(request)
            print(f'(HTTP) : {headers["method"]} | {str(datetime.now())} : {address}')
            URL = headers["method"]
            target = URL.split(" ")[1]
            if not target in URLS:
                client.send(status.Http404.__call__("<b>Page {} Was not Found (404 Status Code)</b>".format(target)))
            else:
                try:
                    client.send(URLS.get(target).__call__(headers))
                except Exception as error:
                    print(f'[ERROR] : {error}')
                    client.send(status.Http500().__call__("<h1>Internal Server Error</h1>"))

            client.close()

class ThreadedServer(Server):
    def __init__(self,host : str = LOCALHOST,port : int = 8000):
        super(ThreadedServer,self).__init__(host=host,port=port,http=False)

    def AwaitSocket(self):
        self.connection.listen(1)
        while True:
            client,adress = self.connection.accept()
            t = threading.Thread(target=self.AwaitMessage,args=(client,adress))
            t.start()

    def AwaitMessage(self,client,address):
        while True:
            data = client.recv(1024)
            print(data)
            try:
                if str(data.strip()) != '':
                    headers = self.ParseHeaders(data)
                    HTTP_MSG = status.Http101().__call__("da",headers['Sec-WebSocket-Key'])
                    client.send(HTTP_MSG)
            except Exception as f:
                continue
        client.close()

