# < - Package Imports
from ..client_side import status
from ..Parsing.http import ParseHeaders,ParseHTTP
from ..Parsing import websocket

# < - Server Hadnling
import socket
import threading

# < - For Parsing - Hints
from datetime import datetime
import re
from typing import Any,Union
from traceback import print_exception

# < - File handling-Decoding
from os.path import getsize,join
from urllib.request import unquote
from math import ceil

SocketBin : callable;SocketBinSend : callable
SocketBin,SocketBinSend = websocket.ReceiveData,websocket.SendData

def lazy_read(file): #Function to lazy read
    while True:
        data = file.read(1024)
        if not data:
            break
        yield data

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

    def __init__(self,host : str = LOCALHOST,port : int = HTTP_PORT,page404 : callable = STANDAR_404_PAGE,page500 : str = STANDAR_500_PAGE,**kwargs):
        isHttp = kwargs.get('http')
        print(f"Initiliazing local {'HTTP' if isHttp is None else 'WS' if isHttp.strip().lower() != 'standar server' else 'HTTP & WS'} Server on {host}:{port}")
        self.adress : tuple = (host,port)
        self.connection : socket.socket = socket.socket()
        self.connection.bind(self.adress)
        self.urls : dict = kwargs.get("URLS")
        self.page404 : callable = page404 
        self.page500 : str = page500
        del isHttp

    def handleHTTP(self,client : socket.socket,headers : dict,URLS : dict) -> None:
        #Loop thorugh each URL searching for the TARGET
        target = headers[0]["method"].split(" ")[1]
        for url in URLS:
            match = re.fullmatch(url,target) #full regex match
            if match: #linear search is the only way to go with regex
                try:
                    headers[0]['IP'] = self.get_client_ip(client)
                    msg = URLS.get(url).__call__(headers)
                    if isinstance(msg,tuple): #Binary? file
                        with open(msg[1],'rb+') as file:
                            client.send(msg[0](getsize(msg[1]))) #Send the HTTP Headers with the file lenght
                            for chunk in lazy_read(file):
                                client.send(chunk) #Lazy-send the chunks
                    else:
                        client.send(msg)
                except Exception as f:
                    print_exception(type(f),f,f.__traceback__)
                    client.send(status.Http500().__call__(self.page500))
                finally:
                    return client.close()
        #Page was not found
        client.send(status.Http404().__call__(self.page404(target)))
        return client.close()

    def AwaitRequest(self):
        """Wait for requests to be made"""
        self.connection.listen(1)
        #Start thread not to block request
        while True:
            client = self.connection.accept()
            t = threading.Thread(target=self.HandleRequest,args=(client,self.urls))
            t.start()

    def HandleRequest(self,client,URLS : dict):
        """
           ** Method that handles the requests\r
           ** when they are first made,\r
           ** giving the the target route view\r
           ** and then closing the connection\r
           ** Called Only once and then thread exits\r
        """
        client,address = client 
        client.settimeout(5)
        try:
            request = client.recv(1024) #Await for messages
        except:
            return client.close()     

        if len(request) == 0:
            return client.close()

        headers = ParseHTTP(request,lambda : client.recv(1024))

        print(f'(HTTP) : {headers[0]["method"]} | {str(datetime.now())} : {address}')
        return self.handleHTTP(client,headers, URLS)

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

    def start(self):
        print(f'({str(datetime.now())}) HTTP Server has gone live.')
        return self.AwaitRequest()

class WebsocketServer(HttpServer):
    """An extension of the HTTP Server for handling WebSocket Protocols\n
       Only one WebSocket server 'route' can be maintained at the same time\n
       on the exact same ADDRESS and PORT using this class.

       param: host : str = LOCALHOST (127.0.0.1)  
       param: port : int = 8000
       param max_size : int = 4096 (The Maximun number of data that can be transmitted in one Message)
    """

    def __init__(self,host : str = LOCALHOST,port : int = 8000,max_size : int = 4096,**kwargs):
        self.clients : list = [] #Store all the clients
        self.max_size = max_size
        isHttp = kwargs.get('http')
        super(WebsocketServer,self).__init__(host=host,port=port,http=f'{"WS" if isHttp is None else "Standar Server"}',**kwargs)
        del isHttp,self.page404,self.page500,self.urls

    def AwaitSocket(self,add_to_clients : bool = True):
        """Wait for new connections"""
        self.connection.listen(1)
        while True:
            client,adress = self.connection.accept()
            threading.Thread(target=self.handleWebSocket,args=(client,adress)).start()

    def onMessage(self,**kwargs):
        """Gets called when a message is received from the client side"""
        pass

    def onExit(self,client,**kwargs):
        """Called when a client exits
          the 'client' paramter is part
          of the socket library 
        """
        pass
    
    def onConnect(self,client,**kwargs):
        """Called when a client establishes
          a connection to the server,
          the 'client' paramter is part
          of the socket library 
        """
        pass

    def send(self,client : socket.socket,data : str) -> None:
        """Sends data to a client"""
        client.send(SocketBinSend(data))

    def handleDisconnect(self,client : socket.socket ,list_of_clients : Any = None):
        if list_of_clients is None:
            CLS = self.clients
            indx = CLS.index(client)
            self.clients.pop(indx)
            client.close()
            return self.handleTraceback(lambda _ : self.onExit(client,send_function=self.send),'onExit')
        else:
            CLS = list_of_clients
            print(CLS,len(CLS))
            indx = CLS.index(client)
            CLS.pop(indx)
            print(CLS,len(CLS))
            client.close()
            return self.handleTraceback(lambda _ : self.onExit(client,send_function=self.send),'onExit')

    def AwaitMessage(self,client,address):
        """While a client is connected,
           this method is executing
           in an infinite loop checking
           if they are sending messages
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
                headers = ParseHeaders(data)
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

    def accept(self,client : socket.socket,**kwargs) -> None:
        key = kwargs.get('key')
        return client.send(status.Http101().__call__(key))

    def handleWebSocket(self,client,address,**kwargs):
        # client.settimeout(5) # Wait 5 seconds for connection to be established
        data = client.recv(1024)
        data = data.split(b'\r\n\r\n',1)
        headers = ParseHeaders(data[0])

        if 'Upgrade' in headers:
            if headers['Upgrade'].lower()=='websocket':
                print(f'(WS) : {headers["method"]} | {str(datetime.now())} : {address}')
            else:
                print(f'(WS) : {headers["method"]} | {str(datetime.now())} : Invalid WS Response {address}')
                return client.close()
        else:
            print(f'(WS) : {headers["method"]} | {str(datetime.now())} : Invalid WS Response {address}')
            return client.close()

        hndl = self.handleTraceback(lambda x : self.onConnect(client,adress=address,send_function=self.send,key=headers['Sec-WebSocket-Key']),"onConnect")                

        if not hndl:
            print(f"(WS) : {str(datetime.now())} Connection Closed because bool(onConnect) return False {address}")
            return client.close() #Close if there was an Exception or return None

        
        #Increment the number of clients and print 
        num_client : int = self.clients.__len__()+1
        print(f"(WS) : {str(datetime.now())} Connection Established ({num_client} Client{'s' if num_client > 1 else ''}) {address}")

        #Add them to the clients-list (current route)
        self.clients.append(client)

        while True:
            data = client.recv(self.max_size)

            if len(data) == 0:
                print(f"(WS) : {str(datetime.now())} Connection Closed {address}")
                self.handleDisconnect(client);return ...

            print(f"(WS) : {str(datetime.now())} Received Message {address}")
            decoded = SocketBin(data)   
            self.handleTraceback(lambda x : self.onMessage(data=decoded,sender_client=client),"onMessage")                                

    def start(self):
        print(f'({str(datetime.now())}) WS Server has gone live.')
        return self.AwaitSocket()

class RoutedWebsocketServer(WebsocketServer):
    """
    A Websocket Server that can have multiple routes,
    each one having it's own seperate clients,
    all running on the same ADDRESS and PORT

    Additional Parameters to WebsocketServer:
        param: global_max_size : int = 4096 (This is the message that is transmitted before establishing a connection during the WebSocket HANDSHAKE)

    """

    def __init__(self,paths : dict,host : str = LOCALHOST,port : int = 8000,global_max_size : int = 4096,**kwargs):
        self.global_max_size = global_max_size
        self.routes : dict = {}
        for item in paths:
            self.routes[item] =  {"clients" : [],"view" : paths[item]}
        super(RoutedWebsocketServer,self).__init__(host,port,**kwargs)
        del self.clients;del self.max_size

    def AwaitSocket(self):
        super(RoutedWebsocketServer,self).AwaitSocket(add_to_clients=False)

    def handleWebSocket(self,client,address,**kwargs):
        """
        A slightly more performant version of self.await message
        that first waits for the WebSocket handshake and then
        if it is sucessfull it establishes the connection
        """
        headers = kwargs.get('headers')

        if not headers: #On Plain WebSocket server here the request is sent 
            data = client.recv(self.global_max_size)
            headers : dict = ParseHeaders(data)
        
        #Check if the path is found
        path : str = headers['method'].split(" ")[1]
        if not path in self.routes:
            print(f"(WS) : {str(datetime.now())} Connection Not Found \"{path}\" {address}")
            return client.close()

        #Get The View and call the onConnect function
        CWM = self.routes[path]["view"]
        hndl = self.handleTraceback(lambda _ : CWM.onConnect(client=client,path_info=self.routes[path],send_function=self.send,headers=headers,key=headers['Sec-WebSocket-Key']),"onConnect",path)  
        
        if not hndl:
            print(f"(WS) {path} : {str(datetime.now())} Connection Closed because bool(onConnect) return False {address}")
            return client.close() #Close if there was an Exception or return None
        
        #Increment the number of clients and print 
        num_client : int = self.routes[path]['clients'].__len__()+1
        print(f"(WS) {path} : {str(datetime.now())} Connection Established ({num_client} Client{'s' if num_client > 1 else ''}) {address}")

        #Add them to the clients-list (current route)
        self.routes[path]['clients'].append(client)
        while True:
            try:
                data = client.recv(CWM.MaxSize())
            except:
                self.handleDisconnect(client,self.routes[path]['clients'])
                self.handleTraceback(lambda _ : CWM.onExit(client,path_info=self.routes[path],send_function=self.send),'onExit')
                break

            if len(data) == 0:
                print("Data is 0")
                print(f"(WS) {path} : {str(datetime.now())} Connection Closed {address}")
                self.handleDisconnect(client,self.routes[path]['clients'])
                self.handleTraceback(lambda _ : CWM.onExit(client,path_info=self.routes[path],send_function=self.send),'onExit')
                break
            
            print(f"(WS) {path} : {str(datetime.now())} Received Message {address}")
            decoded = SocketBin(data)    
            self.handleTraceback(lambda _ : CWM.onMessage(data=decoded,sender_client=client,path_info=self.routes[path],send_function=self.send),"onMessage",path)

class Server(RoutedWebsocketServer):
    
    def __init__(self,socket_paths : dict, http_paths : dict ,host : str = LOCALHOST,port : int = 8000,global_max_size : int = 4096,**kwargs) -> None:
        super(Server, self).__init__(socket_paths,host,port,global_max_size,http='',URLS=http_paths)
    
    def HandleRequest(self,client : socket.socket , URLS : dict) -> None:
        client,address = client 
        client.settimeout(5) 
        try:
            request = client.recv(1024) 
        except:
            print(f'(Server) | {str(datetime.now())} : Timed out {address}')
            return -1

        if len(request) == 0:
            return client.close()
        
        if 'Content-Length' in headers:
            crem : int = int(headers['Content-Length']) - 1024
            if (crem  > 0):
                boundrary = headers['Content-Type'].split(';') # Where new data is sent

                #Find the Form-data spliiter
                for q in boundrary:
                    if 'boundary' in q:
                        boundrary = q.split('=')[-1];break

                if type(boundrary) != list:
                    boundrary = boundrary.encode()
                    f_p = request[request.index(boundrary + b'\r\nContent-Disposition'):]
                    target = f_p.split(b"\r\n",4)

                    if not 'files' in headers:
                        headers['files'] = [*target[4:]]

                    #Await for new Responses
                    l : int = 0
                    loop_times = iter(range(ceil(crem / 1024)))
                    BIN_DATA : list = [self.parseHTMLDATA(f_p.split(b"\r\n",3))]
                    for _ in loop_times:
                        print('WAITING : {}'.format(l))
                        # client.settimeout(5)
                        bindata = client.recv(1024) #Await for file transfer
                        if boundrary in bindata:
                            print("BOUNDARY")
                            res = self.parseFile(boundrary,bindata,BIN_DATA)
                            # print(res)
                            headers['files'][l] += res[0] #before
                            l+=1
                            headers['files'].insert(l,res[1]) #after 
                            continue
                        headers['files'][l] += bindata

                    j : int
                    for j in range(len(headers['files'])):
                        headers['files'][j] = FileObject('',headers['files'][j])
                        j+=1

                    j : int = 0
                    for j in range(len(BIN_DATA)):
                        BIN_DATA[j]['data'] = headers['files'][j]

                    headers['files'] = BIN_DATA 
                else:
                    DATA = ''
                    loop_times = iter(range(ceil(crem / 1024)))
                    for _ in loop_times:
                        msg = client.recv(1024)
                        request += msg
                    parsed : str = decodeURI(request.decode(errors='ignore'))
                    
                    # print(parsed)
                    # headers = self.parse(bytes(parsed,encoding='utf-8'))
                    # print(headers,"\tThis is parsed")

        #WebSocket Connection
        if 'Upgrade' in headers:
            if headers['Upgrade'].lower()=='websocket':
                print(f'(WS) : {headers["method"]} | {str(datetime.now())} : {address}')
                return threading.Thread(target=self.handleWebSocket,args=(client,address), kwargs={'headers' : headers}).start()
        
    
        print(f'(HTTP) : {unquote(headers["method"])} | {str(datetime.now())} : {address}')
        return threading.Thread(target=self.handleHTTP,args=(client,headers,URLS)).start()

if __name__ == '__main__':
    pass