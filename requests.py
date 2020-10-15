import socket,ssl,pprint
from re import match
from math import ceil
import darius.Parsing.http as parseql


non_encoding : list = [
  ";", 
  ",",
  "/",
  "?", 
  ":",
  "@",
  "&",
  "=",
  "+",
  "$",
  "-",
  "_",
  ".",
  "!",
  "~",
  "*",
  "'", 
  "(", 
  ")", 
  "#",
]

with open("dsa") as f:
    XXS = f.read().encode().replace(b"\n",b"\r\n") + b"\r\n"

http_msg : callable  = lambda method,path,cookies : f'HTTP/1.1 {method.upper()} {path}\r\nAccept: */*\r\nConnection: close\r\nContent-length : 13\r\nCookie :  {";".join([f"{c}={cookies.get(c)}" for c in cookies]) + ";"}\r\nUser-Agent : Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36 OPR/71.0.3770.198\r\nAccept-Language: en-us\r\nAccept-Encoding: gzip, deflate\r\n\r\n\r\n'.encode()

class Header:
    def __init__(self,path_config : dict,headers : dict):
        self.method = path_config.get("method")
        self.url = path_config.get("url")
        self.headers : dict = headers
    
    def append(self,values : dict):
        for value in values:
            self.headers[value] = values.get(value)

    def c(self):
        value = ''
        for item in self.headers:
            value+= f'{item} : {self.headers.get(item)}\r\n'
        return value

    def pop(self,value):
        return self.headers.pop(value)

    def get_headers(self):
        return self.headers

    def get_url(self):
        return self.url

    def __call__(self):
        return f'{self.method} {self.url} HTTP/1.1\r\n' + self.c() + "\r\n"
    
class Response:
    def __init__(self,*args,**kwargs) -> None:
        self.status_code = kwargs.get('status_code')
        self.request_url = args[0]

    def __str__(self):
        return f'[{self.status_code}] XMLHttpRequest at {self.request_url}'


def gsp(x):
    chrs = ''
    for item in x:
        arr = [i for i in x.encode()]
        chrs +="%" + "%".join([hex(d).split("x",1)[-1].upper() for d in arr])
    return chrs

def encodeURIComponent(uri):
  y = ''
  for item in uri:
    if(not match("A-zZ-a",item) and not item in non_encoding):
        y += "%" + hex(ord(item)).split("x",1)[-1].upper()
        continue
    print("not encoded {}".format(item))
    y += item
  return y


def get_host(url : str):
    # try:
    protocol,dns = url.split("://",1)
    spl_dns = dns.split("/",1)
    if(":" in spl_dns[0]):
        try:
            base_url,port = spl_dns[0].split(":")
            port = int(port)
        except:
            raise ValueError("Invalid Port in URI \"{}\"".format(url))
    else:
        base_url = spl_dns[0]
        if protocol.lower() == 'http':
            port = 80

        else:
            port = 443
    if(spl_dns.__len__() > 1):
        spath = spl_dns[1]
        if(spath.strip() == ''):
            path = '/'
        else:
            path = f'/{spath}'
    else:
        path = "/"
    return [(base_url,port),path]

def XMLHttpRequest(headers : Header):
    (host,port),path = get_host(headers.get_url())
    headers.url = path
    headers.headers = {'Host' : host,**headers.headers}
    with socket.create_connection((host,port)) as connection:
        if(port!=443):
            connection.send(headers().encode())
            response = connection.recv(1024)
            print(response.decode(errors='ignore'))
            return  #parseql.ParseHeaders(response,lambda : connection.recv(1024))
        with ssl.create_default_context().wrap_socket(connection,server_hostname=host) as secure_connection:
            print("<---------- MESSAGE ------------>")
            print(headers())
            secure_connection.send(headers().encode())
            response = secure_connection.recv(1024)
            print("<------- Response ------->")
            print(response.decode(errors='ignore'))
            # return parseql.ParseHTTP(request,lambda : secure_connection.recv(1024))

request = Header({
    'method' : 'GET',
    'url' : 'https://github.com/Greece4ever'
    },{
    "Accept": "*/*",
    "Content-Length" : '0',
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Darius",
})

if __name__ == "__main__":
    pprint.pprint(
        XMLHttpRequest(request)
    )
    # print(
    #     request()
    # )