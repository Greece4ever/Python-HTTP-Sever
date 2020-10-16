import socket,ssl,pprint
from re import match
from math import ceil
# import ..parsing.http as parseql
from ..parsing.http import ParseHeaders
import zlib

def parse_headers(data : bytes,):
    parsed : dict = ParseHeaders(data)
    parsed['status'] = parsed.pop('type')
    parsed['alias'] = parsed.pop('uri')
    parsed.pop('method')
    return parsed


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
            value+= f'{item}: {self.headers.get(item)}\r\n' # GAMO TO XRISTO SAS NGINX KAI APACHE MALAKES 
        return value                                        # DEN MPOREITE NA KANATE PARSE TA HEADERS
                                                            # AN IPARXEI GAMIMENO KENO PRIN TO :


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

def get_host(url : str):
    try:
        protocol,dns = url.split("://",1)
    except:
        raise ValueError(f"Invalid URL : \"{url}\"")
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


base_request = lambda **kwargs: Header(
    {
        'method' : kwargs.get("method"),
        'url' : kwargs.get("url")
    },
    {
        "Host" : kwargs.get("host"),
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
})


def XMLHttpRequest(headers : Header,recv_size : int = 1024,
    header_wait_time : int = 1,
    header_recv_size : int = 1024,
    max_wait_time : int = 1,
    allow_redirect : bool = True,
    allow_recursive_redirect : bool = False):
    kwargs = locals()
    (host,port),path = get_host(headers.get_url())
    headers.url = path
    headers.headers['Host'] = host
    try:
        with socket.create_connection((host,port)) as connection:
            if(port!=443):
                connection.send(headers().encode())
                response = connection.recv(1024)
                print(response.decode(errors='ignore'))
                h_b = response.split(2*b'\r\n',1)
                return parseHRS(h_b,headers,host,recv= lambda : connection.recv(1024))

            with ssl.create_default_context().wrap_socket(connection,server_hostname=host) as secure_connection:
                secure_connection.send(headers().encode())
                secure_connection.settimeout(max_wait_time)
                hedrs : bytes = b''
                body : bytes = b''
                while True:  # Parse Headers
                    try:
                        response = secure_connection.recv(header_recv_size)
                    except:
                        return hedrs

                    spl = response.split(b"\r\n\r\n")
                    if(len(spl) > 1):
                        hedrs += spl[0]
                        hedrs = parse_headers(hedrs)
                        break

                    hedrs += response
                
                if(hedrs.get('status').startswith('30')): # 3xx Redirection
                    location = hedrs.get("Location")
                    if(not allow_redirect or not location):
                        return "TELOS " # TODO BUG NOTE
                    kwargs["headers"].url = location
                    if(not allow_recursive_redirect):
                        kwargs['allow_redirect'] = False
                    pprint.pprint(hedrs)
                    return XMLHttpRequest(**kwargs)

                while True: # Parse Body
                    try:
                        data = secure_connection.recv(recv_size)
                        body += data
                    except:
                        break

    except socket.gaierror:
        raise RuntimeError(f"No results on DNS lookup for '{host}' on port {port}.")

    return hedrs,body
    # return parseHRS(h_b,headers,host,recv= lambda : secure_connection.recv(1024))
            
def GET(target,**kwargs):
    return XMLHttpRequest(base_request(url=target,method='GET'),**kwargs)

if __name__ == "__main__":
    pprint.pprint(
        GET('https://en.wikipedia.org/wiki/User_agent',max_wait_time=3,allow_redirect=False,allow_recursive_redirect=False)[0]
    )
    # req = XMLHttpRequest(request)
    # print(req)
    # pprint.pprint(req.headers)
    