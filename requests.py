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
    
    def __init__(self,request_url,status_code,headers,**kwargs) -> None:
        self.headers = headers
        self.status_code = status_code
        self.request_url = request_url
        self.host = kwargs.get('host') # detail_response
        self.detail_resp = kwargs.get("detail_response")


    def __str__(self) -> str:
        return f'<XMLHttpRequest [{self.status_code}] alias="{self.detail_resp}" target="{self.host}" header_length="{len(self.headers)}" />'

    def setBody(self, data : bytes) -> None:
        self.body = data

    def __repr__(self) -> str:
        return self.__str__()

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

def parseHRS(h_b,*args,**kwargs):
    print(args)
    hrs = parseql.ParseHeaders(h_b[0])
    code = hrs.pop('type')
    detail = hrs.pop('uri');hrs.pop('method')
    resp = Response(status_code=code,detail_response=detail,headers=hrs,request_url=args[0].url,host=args[1])
    recv = kwargs.get("recv")
    if(len(h_b) > 1):
        resp.setBody(h_b[1])
    else:
        i = 0
        while True:
            r = recv()
            if(len(r)==0):
                break
            print(r.split(b"\r\n",1))
            print(i,"<--- Iterations")
            i+=1

    return resp


def XMLHttpRequest(headers : Header):
    (host,port),path = get_host(headers.get_url())
    headers.url = path
    headers.headers = {'Host' : host,**headers.headers}
    with socket.create_connection((host,port)) as connection:
        if(port!=443):
            connection.send(headers().encode())
            response = connection.recv(1024)
            print(response.decode(errors='ignore'))
            h_b = response.split(2*b'\r\n',1)
            return parseHRS(h_b,headers,host,recv= lambda : connection.recv(1024))
        with ssl.create_default_context().wrap_socket(connection,server_hostname=host) as secure_connection:
            secure_connection.send(f'GET / HTTP/1.1\r\nHost: {host}\r\nConnection: keep-alive\r\nCache-Control: max-age=0\r\nUpgrade-Insecure-Requests: 1\r\nUser-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36 OPR/71.0.3770.198\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\nSec-Fetch-Site: none\r\nSec-Fetch-Mode: navigate\r\nSec-Fetch-User: ?1\r\nSec-Fetch-Dest: document\r\nAccept-Encoding: gzip, deflate, br\r\nAccept-Language: en-US,en;q=0.9\r\nCookie: csrftoken=J9wmXKesPqeqZ9uKpJpP5DQsK5pLQv1rB6yF7ODeKR1yKUW287exFTYBbDvCdpG0\r\n\r\n'.encode())
            response = '1321'
            response = secure_connection.recv(1024)
            print(response.decode(errors='ignore'))
            while True:
                response = secure_connection.recv(1024)
                print(response.decode(errors='ignore'))
                if(not response):
                    print("broke")
                    break
            h_b = response.split(2*b'\r\n',1)
            return parseHRS(h_b,headers,host,recv= lambda : secure_connection.recv(1024))
            
request = Header({
    'method' : 'GET',
    'url' : 'https://stackoverflow.com/questions/43925672/bad-request-your-browser-sent-a-request-that-this-server-could-not-understand'},
    {"Accept": "*/*",
    "Content-Length" : '0',
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Darius",
})

if __name__ == "__main__":
    req = XMLHttpRequest(request)
    print(req)
    pprint.pprint(req.headers)