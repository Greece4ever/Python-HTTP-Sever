import socket
from typing import Union
import status
from datetime import datetime
import re
import threading
import base64 
from communications import SocketBin,SocketBinSend

LOCALHOST : str = "127.0.0.1"
HTTP_PORT : int = 80

class HttpServer:
    def __init__(self,host : str = LOCALHOST,port : int = HTTP_PORT,http : bool = True,**kwargs):
        print(f"Starting local {'HTTP' if http else 'WS'} Server on {host}:{port}")
        self.adress = (host,port)
        self.connection = socket.socket()
        self.connection.bind(self.adress)
        self.urls = kwargs.get("URLS")
    
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
        self.connection.listen(1)
        #Start thread not to block request
        while True:
            client = self.connection.accept()
            t = threading.Thread(target=self.HandleRequest,args=(client,self.urls))
            t.start()

    def HandleRequest(self,client,URLS : dict):
        client,address = client 
        request = client.recv(1024) #Await for messages
        if len(request) == 0:
            return ...
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

class WebsocketServer(HttpServer):
    def __init__(self,host : str = LOCALHOST,port : int = 8000):
        self.clients : list = [] #Store all the clients
        super(WebsocketServer,self).__init__(host=host,port=port,http=False)

    def AwaitSocket(self):
        self.connection.listen(1)
        while True:
            client,adress = self.connection.accept()
            t = threading.Thread(target=self.AwaitMessage,args=(client,adress))
            t.start()

    def onMessage(self,**kwargs):
        data = kwargs.get('data')
        for client in self.clients:
            self.send(client,data)

    def onExit(self,client):
        """Called when a client exits
          the 'client' paramter is part
          of the socket library 
        """
        pass
    
    def onConnect(self,client):
        """Called when a client establishes
          a connection to the server,
          the 'client' paramter is part
          of the socket library 
        """
        pass

    def send(self,client,data : str) -> None:
        """Sends data to a client"""
        client.send(SocketBinSend(data))

    def AwaitMessage(self,client,address):
        while True:
            data = client.recv(1024)
            if len(data) == 0:
                if client in self.clients:
                    indx = self.clients.index(client)
                    self.clients.pop(indx)
                self.onExit((client,address))
                break
            try: #Headers Can Be Parsed, New connection
                headers = self.ParseHeaders(data)
                self.clients.append(client)
                HTTP_MSG = status.Http101().__call__("da",headers['Sec-WebSocket-Key'])
                client.send(HTTP_MSG)
                self.onConnect((client,address))
                print(f"(WS) : {str(datetime.now())} Connection Established {address}")
            except: #Out of range error, client send a bytes object
                print(f"(WS) : {str(datetime.now())} Received Message {address}")
                decoded = SocketBin(data)
                self.onMessage(data=decoded,sender_client=client)
        client.close()