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
    print(XXS)

http_msg : callable  = lambda method,path,cookies : f'HTTP/1.1 {method.upper()} {path}\r\nAccept: */*\r\nConnection: close\r\nContent-length : 13\r\nCookie :  {";".join([f"{c}={cookies.get(c)}" for c in cookies]) + ";"}\r\nUser-Agent : Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36 OPR/71.0.3770.198\r\nAccept-Language: en-us\r\nAccept-Encoding: gzip, deflate\r\n\r\n\r\n'.encode()


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

def GET(URI : str):
    s = get_host(URI)
    path = s[1]
    if(s[0][1]!=443):
        with socket.create_connection(s[0]) as sock:
            sock.send(XXS)  
            data = sock.recv(1024)
            print(data.decode('utf-8',errors='ignore'))
            return
    with socket.create_connection(s[0]) as sock:
        print("Sending data...")
        with ssl.create_default_context().wrap_socket(sock,server_hostname=s[0][0].encode()) as wrapper:
            wrapper.send(XXS)
            print(XXS.decode('utf-8'))
            print("Data Sent...")
            response = wrapper.recv(1024)
            print(response.decode(errors='ignore'))

if __name__ == "__main__":
    path = "http://example.com/sys"
    print(f'Sending request {path}')
    GET(path)