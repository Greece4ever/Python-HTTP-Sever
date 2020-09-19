import socket
from typing import Union
import status
from datetime import datetime
import re
import threading
from communications import SocketBin,SocketBinSend
from typing import Any
from traceback import print_exception

LOCALHOST : str = "127.0.0.1"
HTTP_PORT : int = 80
STANDAR_404_PAGE : callable = lambda page : "<b>Page {} Was not Found (404 Status Code)</b>".format(page)
STANDAR_500_PAGE : str = "<h1>500 Internal Server Error</h1>"

class HttpServer:
    """
    A Standar Hyper Text Transfer Protool (HTTP) server,\n
    that given a HTTP request on a specific route,\n
    returns a specific 'View' class method depending on the method\n
    and the PATH, which if not found a 404 page is returned passed in the context of:\n
    param: page404 : callable = STANDAR_404_PAGE
        STANDAR_404_PAGE = lambda page : '<b>Page {} Was not Found (404 Status Code)</b>'.format(page)

    if an Exception is raised in one of the passed in VIEWS the standar 500 Page will be passed in
    param: page505 : str = STANDAR_500_PAGE 


    """

    def __init__(self,host : str = LOCALHOST,port : int = HTTP_PORT,http : bool = True,page404 : callable = STANDAR_404_PAGE,page500 : str = STANDAR_500_PAGE,**kwargs):
        print(f"Starting local {'HTTP' if http else 'WS'} Server on {host}:{port}")
        self.adress : tuple = (host,port)
        self.connection : socket.socket = socket.socket()
        self.connection.bind(self.adress)
        self.urls : dict = kwargs.get("URLS")
        self.page404 : callable = page404 
        self.page500 : str = page500

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
            return client.close()
        headers = self.ParseHeaders(request)
        print(f'(HTTP) : {headers["method"]} | {str(datetime.now())} : {address}')
        URL = headers["method"]
        target = URL.split(" ")[1]
        for url in URLS:
            match = re.fullmatch(url,target)
            if match: #linear search is the only way to go with regex
                try:
                    headers['IP'] = self.get_client_ip(client)
                    URLS.get(url).__call__(headers,snd=client.send)
                    # client.send(URLS.get(url).__call__(headers,snd=client.send))
                except Exception as f:
                    print_exception(type(f),f,f.__traceback__)
                    client.send(status.Http500().__call__(self.page500))
                finally:
                    return client.close()

        client.send(status.Http404().__call__(self.page404(target)))
        return client.close()

    def get_client_ip(self,client):
        return client.getsockname()[0]

    def handleTraceback(self,function,fname,path : str =  None):
        try:
            res = function(0)
            return res
        except Exception as f:
            path = path if path is not None else ''
            print(f"[ERROR] (WS) {path} : {str(datetime.now())} An Exception occurred while calling the {fname} function")
            print_exception(type(f),f,f.__traceback__)
            return False

class WebsocketServer(HttpServer):
    """An extension of the HTTP Server for handling WebSocket Protocols\n
       Only one WebSocket server 'route' can be maintained at the same time\n
       on the exact same ADDRESS and PORT using this class.

       param: host : str = LOCALHOST (127.0.0.1)  
       param: port : int = 8000
       param max_size : int = 4096 (The Maximun number of data that can be transmitted in one Message)
    """

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


    def handleDisconnect(self,client,list_of_clients : Any = None):
        if list_of_clients is None:
            CLS = self.clients
            indx = CLS.index(client)
            self.clients.pop(indx)
            client.close()
            self.onExit(client)

        else:
            CLS = list_of_clients
            indx = CLS.index(client)
            CLS.pop(indx)
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
                self.handleTraceback(lambda x : self.onExit(client),"onExit");break

            if len(data) == 0:
                print(f"(WS) : {str(datetime.now())} Connection Closed {address}")
                self.handleDisconnect(client)
                self.handleTraceback(lambda x : self.onExit(client),"onExit");break

            #First Time Connection
            try: 
                #Parse The Headers and initialize Websocket
                headers = self.ParseHeaders(data)
                HTTP_MSG = status.Http101().__call__(headers['Sec-WebSocket-Key'])
                client.send(HTTP_MSG)
                self.handleTraceback(lambda x : self.onConnect((client,address)),"onConnect")                
                print(f"(WS) : {str(datetime.now())} Connection Established {address}")

            #Typical Message
            except Exception: 
                print(f"(WS) : {str(datetime.now())} Received Message {address}")                
                decoded = SocketBin(data)
                self.handleTraceback(lambda x : self.onMessage(data=decoded,sender_client=client),"onMessage")                               
        client.close()

class RoutedWebsocketServer(WebsocketServer):
    """
    A Websocket Server that can have multiple routes,
    each one having it's own seperate clients,
    all running on the same ADDRESS and PORT

    Additional Parameters to WebsocketServer:
        param: global_max_size : int = 4096 (This is the message that is transmitted before establishing a connection during the WebSocket HANDSHAKE)

    """

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
        send_function = self.send
        while True:
            try:
                data = client.recv(self.global_max_size)
            except:
                #Disconnect base on Exception
                print(f"(WS) {path} : {str(datetime.now())} Connection Closed {address}")
                self.handleDisconnect(client,self.routes[path]['clients'])
                break

            if len(data) == 0:
                #Disconnect because client send empty string
                print(f"(WS) {path} : {str(datetime.now())} Connection Closed {address}")
                self.handleDisconnect(client,self.routes[path]['clients'])
                break

            #Connection
            try:
                headers = self.ParseHeaders(data)
                path = headers['method'].split(" ")[1]

                #Path is not found
                if not path in self.routes:
                    print(f"(WS) : {str(datetime.now())} Connection Not Found \"{path}\" {address}")
                    client.close();break

                #Let the onConnect function handle what to do next (either send 'OK' Response to the client,do nothing or close)
                CWM = self.routes[path]["view"]
                hndl = self.handleTraceback(lambda x : CWM.onConnect(client=client,path_info=self.routes[path],send_function=send_function,headers=headers,key=headers['Sec-WebSocket-Key']),"onConnect",path)  
                if not hndl:
                    print(f"(WS) {path} : {str(datetime.now())} Connection Closed because bool(onConnect) return False {address}")
                    return client.close() #Close if there was an Exception or return None
               
                num_client : int = self.routes[path]['clients'].__len__()+1
                print(f"(WS) {path} : {str(datetime.now())} Connection Established ({num_client} Client{'s' if num_client > 1 else ''}) {address}")

                #Add him to the clients-list (current route)
                self.routes[path]['clients'].append(client)

            #Websocket Message
            except: 
                print(f"(WS) {path} : {str(datetime.now())} Received Message {address}")
                decoded = SocketBin(data)    
                self.handleTraceback(lambda x : CWM.onMessage(data=decoded,sender_client=client,path_info=self.routes[path],send_function=send_function),"onMessage",path)
        client.close()
