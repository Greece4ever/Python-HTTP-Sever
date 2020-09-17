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
    """A simple HTTP Server for handling requests"""

    def __init__(self,host : str = LOCALHOST,port : int = HTTP_PORT,http : bool = True,**kwargs):
        print(f"Starting local {'HTTP' if http else 'WS'} Server on {host}:{port}")
        self.adress = (host,port)
        self.connection = socket.socket()
        self.connection.bind(self.adress)
        self.urls = kwargs.get("URLS")
    
    def ParseHeaders(self,request : Union[bytes,str]):
        """For parsing the HTTP headers and giving them
           in  a Python Dictionary format
        """
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
        """Wait for requests to be made"""
        self.connection.listen(1)
        #Start thread not to block request
        while True:
            client = self.connection.accept()
            t = threading.Thread(target=self.HandleRequest,args=(client,self.urls))
            t.start()

    def HandleRequest(self,client,URLS : dict):
        """Handle the requests
           giving the the target route view
           and then closing the connection
        """
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
    """An extension of the HTTP Server for handling WebSocket Protocols"""

    def __init__(self,host : str = LOCALHOST,port : int = 8000,max_size : int = 4096):
        self.clients : list = [] #Store all the clients
        self.max_size = max_size
        super(WebsocketServer,self).__init__(host=host,port=port,http=False)

    def AwaitSocket(self,add_to_clients : bool = True):
        """Wait for new connections"""
        self.connection.listen(1)
        while True:
            client,adress = self.connection.accept()
            if add_to_clients:
                self.clients.append(client)
            t = threading.Thread(target=self.AwaitMessage,args=(client,adress))
            t.start()

    def onMessage(self,**kwargs):
        """Gets called when a message is received from the client side"""
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


    def handleDisconnect(self,client):
        CLS = self.clients
        indx = CLS.index(client)
        self.clients.pop(indx)
        client.close()
        self.onExit(client)


    def AwaitMessage(self,client,address):
        """While a client is connected,
           this method is executing
           in an infinite loop checking
           if they are sending messagess
        """
        while True:
            try:
                data = client.recv(self.max_size)
            except:
                print(f"(WS) : {str(datetime.now())} Connection Closed {address}")
                self.handleDisconnect(client)
                break
            try: #Headers Can Be Parsed, New connection
                headers = self.ParseHeaders(data)
                HTTP_MSG = status.Http101().__call__(headers['Sec-WebSocket-Key'])
                client.send(HTTP_MSG)
                self.onConnect((client,address))
                print(f"(WS) : {str(datetime.now())} Connection Established {address}")
            except: #Out of range error, client send a bytes object
                print(f"(WS) : {str(datetime.now())} Received Message {address}")
                decoded = SocketBin(data)                               
                self.onMessage(data=decoded,sender_client=client)
        client.close()

class RoutedWebsocketServer(WebsocketServer):
    def __init__(self,paths : dict,host : str = LOCALHOST,port : int = 8000,global_max_size : int = 4096):
        self.global_max_size = global_max_size
        self.routes : dict = {}
        for item in paths:
            self.routes[item] =  {"clients" : [],"view" : paths[item]}
        super(RoutedWebsocketServer,self).__init__(host,port)
        del self.clients;del self.max_size

    def AwaitSocket(self):
        super(RoutedWebsocketServer,self).AwaitSocket(add_to_clients=False)

    def AwaitMessage(self,client,address):
        path : str
        while True:
            try:
                data = client.recv(self.global_max_size)
            except:
                print(f"(WS) : {str(datetime.now())} Connection Closed {address}")
                self.handleDisconnect(client)
                break
            
            try:
                headers = self.ParseHeaders(data)
                path = headers['method'].split(" ")[1]

                #Path is not found
                if not path in self.routes:
                    print(f"(WS) : {str(datetime.now())} Connection Not Found \"{path}\" {address}")
                    client.close();break

                #Send the 'OK' Response to the client
                HTTP_MSG = status.Http101().__call__(headers['Sec-WebSocket-Key'])
                client.send(HTTP_MSG)
                print(f"(WS) {path} : {str(datetime.now())} Connection Established on \"{path}\"  {address}")
                
                #Add him to the clients-list
                self.routes[path]['clients'].append(client)
                CWM = self.routes[path]["view"]
            except: #Out of range error, client send a bytes object
                print(f"(WS) {path} : {str(datetime.now())} Received Message {address}")
                decoded = SocketBin(data)                               
                CWM.onMessage(data=decoded,sender_client=client,path_info=self.routes[path])

        client.close()
