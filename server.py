import socket
from typing import Union
import status
from datetime import datetime

LOCALHOST : str = "127.0.0.1"

class Server:
    def __init__(self,host : str = LOCALHOST):
        self.adress = (host,80)
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
            try:
                self.connection.listen(1)
                address : tuple
                client,address = self.connection.accept()
                request = client.recv(1024)
                headers = self.ParseHeaders(request)
                print(f'{headers["method"]} | {str(datetime.now())} : {address}')
                # request = self.ParseHeaders(request.decode('utf-8'))
                # print(f'{request["method"]} - at {address}')
                # print(request)
                client.send(b"HTTP/1.1 403 Forbidden\n"
                        +b"Content-Type: text/html\n"
                        +b"\n" # Important!
                        +b"<html><body>Hello World</body></html>\n")
                client.close()
            except KeyboardInterrupt:
                break

HTTP = Server()
HTTP.AwaitRequest() 
                

