import socket,ssl,pprint
from time import time as current_time
from ..parsing.http import ParseHeaders
from io import BytesIO

def parse_headers(data : bytes,):
    parsed : dict = ParseHeaders(data)
    parsed['status'] = parsed.pop('type')
    parsed['alias'] = parsed.pop('uri')
    parsed.pop('method')
    return parsed

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
            value+= f'{item}: {self.headers.get(item)}\r\n' 
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
        self.response_headers = headers
        self.request_headers = kwargs.get("request_headers")
        self.status_code = status_code
        self.request_url = request_url
        self.host = kwargs.get('host') 
        self.detail_resp = kwargs.get("detail_response")
        self.body = kwargs.get('body')
        self.is_ssl = kwargs.get("ssl")
        self.time_taken = kwargs.get('time_taken')
        self.is_really_secure = kwargs.get("is_really_secure")

    def __str__(self) -> str:
        return f'<XMLHttpRequest [{self.status_code}] alias="{self.detail_resp}" host="{self.host}" timing="{round(self.time_taken*1000,2)}ms" SSL_ENCRYPTED={self.is_ssl} is_really_secure={self.is_really_secure} />'

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
    return [(base_url,port),(path,protocol)]


base_request = lambda **kwargs: Header(
    {
        'method' : kwargs.get("method"),
        'url' : kwargs.get("url")
    },
    {
        "Host" : kwargs.get("host"),
        "Accept-Encoding": "identity",
        "Accept-Language": "en-US,en;q=0.9",
})


async def XMLHttpRequest(headers : Header,recv_size : int = 1024,
    header_wait_time : int = 1,
    header_recv_size : int = 1024,
    max_wait_time : int = 1,
    allow_redirect : bool = True,allow_incorrect_ssl : bool = False,
    allow_recursive_redirect : bool = False,**history):
    kwargs : dict = locals()
    (host,port),(path,protocol) = get_host(headers.get_url())
    headers.url : str = path
    headers.headers['Host'] : str = host
    try:
        if(port == 443): # Handle SSL
            if(allow_incorrect_ssl):
                context = ssl._create_unverified_context()
                is_really_secure = False
            else:
                is_really_secure = True
                context = ssl.create_default_context()
            ssl_enc = True
            secure_connection = context.wrap_socket(socket.create_connection((host,port)),server_hostname=host)
        else:
            secure_connection = socket.create_connection((host,port))
            is_really_secure = False
            ssl_enc = False

        t0 = current_time()
        with secure_connection:
            secure_connection.send(headers().encode())
            secure_connection.settimeout(max_wait_time)
            hedrs : bytes = b''
            body : BytesIO = BytesIO()
            while True:  # Parse Headers
                response = secure_connection.recv(header_recv_size)
                if(not response):
                    hedrs = parse_headers(hedrs)
                    break

                spl = response.split(b"\r\n\r\n")
                if(len(spl) > 1):
                    body.write(spl[1])
                    hedrs += spl[0]
                    hedrs = parse_headers(hedrs)
                    break

                hedrs += response

            if(hedrs.get('status').startswith('30')): # 3xx Redirection - No Request Body
                location = hedrs.get("Location")
                if(allow_redirect and location):
                    if(location.startswith('/')):
                        location = f'{protocol}://{host}{location}'
                        print("firstr")

                    elif(True not in (location.startswith('https://'),location.startswith('http://'))):
                        location = f'{protocol}://{host}{path}/{location}'

                    kwargs["headers"].url = location
                    if(not allow_recursive_redirect):
                        kwargs['allow_redirect'] = False
                    return XMLHttpRequest(**kwargs)
            else:  
                _len = hedrs.get("Content-Length")  
                if(_len):
                    for _ in range(int(int(_len) / recv_size)):
                        data = secure_connection.recv(recv_size)
                        body.write(data)
                else:
                    secure_connection.settimeout(1)
                    while True: # Body
                        try:
                            data = secure_connection.recv(recv_size)
                            body.write(data)
                            if(data.strip() == b'0' or not data):
                                break
                        except:
                            break
        t1 = current_time()
    except socket.gaierror:
        raise RuntimeError(f"No results on DNS lookup for '{host}' on port {port}.")

    return Response(headers=hedrs,status_code=hedrs.pop('status'),host=host,request_url=path,is_really_secure=is_really_secure,
    detail_response=hedrs.pop("alias"),body=body,ssl=ssl_enc,time_taken=(t1-t0),request_headers=headers.headers)
    # return hedrs,body
            
def GET(target,**kwargs):
    return XMLHttpRequest(base_request(url=target,method='GET'),**kwargs)

async def hack():
    response = await GET('http://localhost:8000/redirect',max_wait_time=1,allow_redirect=False)
    return response

if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()

    async def fetch(uri):
        print("FETCHING {}".format(uri))
        return await GET(uri,max_wait_time=1,allow_redirect=False)

    asyncio.ensure_future(fetch(f'http://localhost:8000/6'))
    asyncio.ensure_future(fetch(f'http://localhost:8000/5'))
    asyncio.ensure_future(fetch(f'http://localhost:8000/4'))
    asyncio.ensure_future(fetch(f'http://localhost:8000/2'))
    asyncio.ensure_future(fetch(f'http://localhost:8000/3'))

    loop.run_forever()