import socket
from typing import Union
import status
from datetime import datetime
import re
import threading
from communications import SocketBin,SocketBinSend
from typing import Any
from traceback import print_exception
from os.path import getsize,join
from urllib.request import unquote
from math import ceil

def lazy_read(file): #Function to lazy read
    while True:
        data = file.read(1024)
        if not data:
            break
        yield data

class FileObject:
    def __init__(self,name,data):
        self.name = name
        self.data = data

    def __str__(self):
        return self.name

    def save(self,path : str,buffersize : int) -> None:
        with open(join(path,self.name),'wb+') as file:
            for chunk in iter(self.data):
                file.writelines(chunk)

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
        print(f"Starting local {'HTTP' if isHttp is None else 'WS' if isHttp.strip().lower() != 'standar server' else 'HTTP & WS'} Server on {host}:{port}")
        self.adress : tuple = (host,port)
        self.connection : socket.socket = socket.socket()
        self.connection.bind(self.adress)
        self.urls : dict = kwargs.get("URLS")
        self.page404 : callable = page404 
        self.page500 : str = page500
        del isHttp

    def ParseFormData(self,data):
        data = data.split('------')
        data.pop(0) # empty str
        DATA : list = []
        for item in data:
            s = item.split(' ',1)[-1].split(';')
            s = [item.strip() for item in s]

            val = s.pop(0)
            tmp : dict = {}
            tmp1 = val.split(":")
            tmp[tmp1[0]] = tmp1[1]
            tmp['unknown'] : list = []

            for val in s:
                itr : list = val.split(" ")
                for j in itr:
                    try:
                        spl : list = j.split("=")
                        tmp[spl[0]] = spl[1]
                    except Exception as f:
                        tmp['unknown'].append(val)


            DATA.append(tmp)

        print(DATA,end="\n\n\n\n")
        return data

    def ParseHeaders(self,request : Union[bytes,str]):
        """For parsing the HTTP headers and giving them
           in  a Python Dictionary format
        """
        status : int = 0
        HEADERS = {}
        try:
            XS = request.decode('utf-8').split("\r\n")
        except UnicodeDecodeError as msg:
            pos : int = int(str(msg).split('position')[-1].split(':')[0].strip())
            XS = request[:pos].decode('utf-8').split("\r\n") 
            status = 1

        XS = [item for item in XS if item.strip() != '']
        HEADERS['method'] = XS.pop(0).replace("HTTP/1.1",'').strip()
        term : str
        j : int = 0
        for term in XS:
            spl : list = term.split(":",1)
            key : str = spl[0].strip()
            try:
                value : str = spl[1].strip()
                HEADERS[key] = value
            except:
                if term.startswith('---'):
                    HEADERS['DATA'] = self.ParseFormData(" ".join(XS[j:]))
                    break
                data : list = key.split('&')
                form_data = {}
                for item in data:
                    item = item.split("=")
                    form_data[item[0]] = unquote(item[1].replace("+",' '))
                HEADERS['data'] = form_data
            finally:
                j+=1

        if bool(status):
            HEADERS['files'] = request[pos:]
        return HEADERS

    def handleHTTP(self,client : socket.socket,headers : dict,URLS : dict) -> None:
        #Loop thorugh each URL searching for the TARGET
        target = headers["method"].split(" ")[1]
        for url in URLS:
            match = re.fullmatch(url,target) #full regex match
            if match: #linear search is the only way to go with regex
                try:
                    headers['IP'] = self.get_client_ip(client)
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
        request = client.recv(1024) #Await for messages
        if len(request) == 0:
            return client.close()
        headers = self.ParseHeaders(request)
        print(f'(HTTP) : {headers["method"]} | {str(datetime.now())} : {address}')
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
        kwargs.pop('http')
        super(WebsocketServer,self).__init__(host=host,port=port,http=f'{"WS" if isHttp is None else "Standar Server"}',**kwargs)
        del isHttp

    def AwaitSocket(self,add_to_clients : bool = True):
        """Wait for new connections"""
        self.connection.listen(1)
        while True:
            client,adress = self.connection.accept()
            if add_to_clients:
                self.clients.append(client)
            # threading.Thread(target=self.AwaitMessage,args=(client,adress)).start()
            threading.Thread(target=self.handleWebSocket,args=(client,adress)).start()

    def onMessage(self,**kwargs):
        """Gets called when a message is received from the client side"""
        pass

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
            data = client.recv(self.global_max_size) #TODO if wait time is more than n seconds close
            headers : dict = self.ParseHeaders(data)
        
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
                print(f"(WS) {path} : {str(datetime.now())} Connection Closed {address}")
                self.handleDisconnect(client,self.routes[path]['clients'])
                self.handleTraceback(lambda _ : CWM.onExit(client,path_info=self.routes[path],send_function=self.send),'onExit')
                break
            
            print(f"(WS) {path} : {str(datetime.now())} Received Message {address}")
            decoded = SocketBin(data)    
            self.handleTraceback(lambda _ : CWM.onMessage(data=decoded,sender_client=client,path_info=self.routes[path],send_function=self.send),"onMessage",path)

    def AwaitMessage(self,client,address):
        path : str
        send_function = self.send
        while True:
            #Await client response
            try:
                data = client.recv(self.global_max_size)
            
            #Disconnect base on Exception
            except:
                print(f"(WS) {path} : {str(datetime.now())} Connection Closed {address}")
                self.handleDisconnect(client,self.routes[path]['clients'])
                self.handleTraceback(lambda _ : CWM.onExit(client,path_info=self.routes[path],send_function=send_function),'onExit')
                break

            #Disconnect because client send empty string
            if len(data) == 0:
                print(f"(WS) {path} : {str(datetime.now())} Connection Closed {address}")
                self.handleDisconnect(client,self.routes[path]['clients'])
                self.handleTraceback(lambda _ : CWM.onExit(client,path_info=self.routes[path],send_function=send_function),'onExit')
                break

            #Connection
            try:
                headers : dict = self.ParseHeaders(data)
                path : str = headers['method'].split(" ")[1]

                #Path is not found
                if not path in self.routes:
                    print(f"(WS) : {str(datetime.now())} Connection Not Found \"{path}\" {address}")
                    client.close();break

                #Let the onConnect function handle what to do next (either send 'OK' Response to the client,do nothing or close)
                CWM = self.routes[path]["view"]
                hndl = self.handleTraceback(lambda _ : CWM.onConnect(client=client,path_info=self.routes[path],send_function=send_function,headers=headers,key=headers['Sec-WebSocket-Key']),"onConnect",path)  
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
                self.handleTraceback(lambda _ : CWM.onMessage(data=decoded,sender_client=client,path_info=self.routes[path],send_function=send_function),"onMessage",path)
        client.close()


class Server(RoutedWebsocketServer):
    
    def __init__(self,socket_paths : dict, http_paths : dict ,host : str = LOCALHOST,port : int = 8000,global_max_size : int = 4096,**kwargs) -> None:
        super(Server, self).__init__(socket_paths,host,port,global_max_size,http='',URLS=http_paths)
    
    def HandleRequest(self,client : socket.socket , URLS : dict) -> None:
        client,address = client 
        request = client.recv(1024) #Wait for a request
        
        #Client Exit        
        if len(request) == 0:
            return client.close()
        
        headers = self.ParseHeaders(request)
        if 'Content-Length' in headers:
            crem : int = int(headers['Content-Length']) - 1024
            if (crem  > 0):
                if not 'files' in headers:
                    headers['files'] = b''
                for _ in range(ceil(crem / 1024)):
                    bindata = client.recv(1024)
                    headers['files'] += bindata
                headers['files'] = FileObject('file.pnm',headers['files'])
        
        #WebSocket Connection
        if 'Upgrade' in headers:
            if headers['Upgrade'].lower()=='websocket':
                print(f'(WS) : {headers["method"]} | {str(datetime.now())} : {address}')
                return threading.Thread(target=self.handleWebSocket,args=(client,address), kwargs={'headers' : headers}).start()
        
        
        print(f'(HTTP) : {unquote(headers["method"])} | {str(datetime.now())} : {address}')
        return threading.Thread(target=self.handleHTTP,args=(client,headers,URLS)).start()


if __name__ == '__main__':
    msg = b'POST /post HTTP/1.1\r\nHost: localhost\r\nConnection: keep-alive\r\nContent-Length: 56900\r\nCache-Control: max-age=0\r\nUpgrade-Insecure-Requests: 1\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36 OPR/71.0.3770.138\r\nOrigin: http://localhost\r\nContent-Type: multipart/form-data; boundary=----WebKitFormBoundarykgXlHXcDFfR8pdxB\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\nSec-Fetch-Site: same-origin\r\nSec-Fetch-Mode: navigate\r\nSec-Fetch-User: ?1\r\nSec-Fetch-Dest: document\r\nReferer: http://localhost/post\r\nAccept-Encoding: gzip, deflate, br\r\nAccept-Language: en-US,en;q=0.9\r\n\r\n------WebKitFormBoundarykgXlHXcDFfR8pdxB\r\nContent-Disposition: form-data; name="username"\r\n\r\ndsa\r\n------WebKitFormBoundarykgXlHXcDFfR8pdxB\r\nContent-Disposition: form-data; name="file"; filename="xaxa.PNG"\r\nContent-Type: image/png\r\n\r\n\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x03^\x00\x00\x03l\x08\x06\x00\x00\x00KjyT\x00\x00\x00\x01sRGB\x00\xae\xce\x1c'
    x = Server('','')
    print(x.ParseHeaders(msg))