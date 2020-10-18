#For regular HTTP 
import json 
from typing import Union
from datetime import datetime,timezone
from io import BytesIO,StringIO
from .c_types import content_types

#For Handling Websockets
from base64 import b64encode 
from hashlib import sha1
from copy import deepcopy

common : dict = {100: 'Continue', 101: 'Switching Protocols', 200: 'OK', 201: 'Created', 202: 'Accepted', 203: 'Non-Authoritative Information', 204: 'No Content', 205: 'Reset Content', 206: 'Partial Content', 300: 'Multiple Choices', 301: 'Moved Permanently', 302: 'Found', 303: 'See Other', 304: 'Not Modified', 305: 'Use Proxy', 307: 'Temporary Redirect', 400: 'Bad Request', 401: 'Unauthorized', 402: 'Payment Required', 403: 'Forbidden', 404: 'Not Found', 405: 'Method Not Allowed', 406: 'Not Acceptable', 407: 'Proxy Authentication Required', 408: 'Request Timeout', 409: 'Conflict', 410: 'Gone', 411: 'Length Required', 412: 'Precondition Failed', 413: 'Payload Too Large', 414: 'URI Too Long', 415: 'Unsupported Media Type', 416: 'Range Not Satisfiable', 417: 'Expectation Failed', 418: "I'm a teapot", 426: 'Upgrade Required', 500: 'Internal Server Error', 501: 'Not Implemented', 502: 'Bad Gateway', 503: 'Service Unavailable', 504: 'Gateway Time-out', 505: 'HTTP Version Not Supported', 102: 'Processing', 207: 'Multi-Status', 226: 'IM Used', 308: 'Permanent Redirect', 422: 'Unprocessable Entity', 423: 'Locked', 424: 'Failed Dependency', 428: 'Precondition Required', 429: 'Too Many Requests', 431: 'Request Header Fields Too Large', 451: 'Unavailable For Legal Reasons', 506: 'Variant Also Negotiates', 507: 'Insufficient Storage', 511: 'Network Authentication Required'}
GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

class Http101(Exception):
    """For handling WS Protocol requests"""
    @classmethod
    def __call__(self,key):
        assert isinstance(key,str), "Key passed in (HTTP 101) must be {} not {}!".format(str,key)
        key = key.strip()
        key = b64encode(sha1((key + GUID).encode()).digest())
        return (b"HTTP/1.1 101 Switching Protocols\r\n"
                +b"Content-Type: text/html\r\n"
                +b"Connection: Upgrade\r\n"
                +b"Upgrade: websocket\r\n"
                +b"Sec-WebSocket-Accept: " + key + b"\r\n"
                +b"\r\n")    
    
def CookieExpirationDate(datetime_obj):
    return datetime_obj.strftime('%a, %d %b %Y %H:%M:%S %z')

class InvalidHTTPResponse(BaseException):
    pass

class Cookie:
    def __init__(self, name : str, value : str, Expires : datetime = None, Domain : str = None, HttpOnly : bool = False,Secure : bool = False, SameSite : str = None,**kwargs):
        pos_arg = locals()
        pos_arg = {**pos_arg,**pos_arg.pop('kwargs')}
        self.name : str = name #TODO NOTE BUG
        self.value : str = value

        if Expires is not None:
            try:
                pos_arg['Expires'] = CookieExpirationDate(Expires)
            except:
                raise InvalidHTTPResponse(f"Cookie expiration date must be of type {datetime} not {type(Expires)}")
        

        pos_arg.pop('name');pos_arg.pop('value');pos_arg.pop('self')
        self.positional = StringIO()

        only,secure = pos_arg.pop('HttpOnly'),pos_arg.pop('Secure')

        for arg in pos_arg:
            value = pos_arg.get(arg)
            if(value is None): continue
            self.positional.write(f'{arg}={value}; ')
        
        if(only):
            self.positional.write('HttpOnly; ')
        if(secure):
            self.positional.write('Secure; ')


    def __str__(self):
        return f'{self.name}={self.value}; {self.positional.getvalue()}'

class Template:
    def __init__(self, path : str) -> None:
        self.path = path

class Response:
    default_headers = {'Content-Type' : 'text/html'}

    def __init__(self,status_code : int, body : Union[Template,str], **kwargs):
        msg = common.get(status_code)
        if msg is None:
            msg = kwargs.get("msg")
            if(msg is None):
                raise InvalidHTTPResponse("Passed custom status code as a positional argument \"{}\" but did not supply a description.".format(status_code))
        self.status_code = status_code
        self.response_code : str = f'HTTP/1.1 {status_code} {msg}\r\n'
        self.headers : dict = deepcopy(Response.default_headers)
        self.cookies = []

        self.body = body

    def __str__(self):
        return f'<Response [{self.status_code}] cookies="{len(self.cookies)}" respond_headers="{len(self.headers)}" body="{"raw_text" if type(self.body) != Template else Template}" />'

    def __call__(self):
        # print("BEING  CALLED")
        buffer = BytesIO()
        buffer.write(self.response_code.encode())
        for item in self.headers:
            buffer.write(f'{item}: {self.headers.get(item)}\r\n'.encode())
        for item in self.cookies:
            buffer.write(f'Set-Cookie: {item}\r\n'.encode())
        buffer.write("\r\n".encode())
        buffer.write(self.body.encode())
        return buffer.getvalue()

    def set_cookie(self,*cookies):
        self.cookies += [str(item) for item in cookies]
        
class JSONResponse(Response):
    def __init__(self,template,*args,**kwargs):
        super(JSONResponse,self).__init__(body=template,*args, **kwargs)
        self.headers['Content-Type'] = 'application/json'
        self.body = json.dumps(template)

class FileResponse(Response):
    def __init__(self,path : str,*args,**kwargs):
        super(FileResponse,self).__init__(body=Template(path),*args, **kwargs)
        filename = path.split("\\")[-1] #get the filename
        ctype = content_types.get('.' + filename.split(".")[-1].lower()) #get the mime for the file type (.FILETYPE)
        if ctype is not None:
            self.headers['Content-Type'] = ctype
        else:
            self.headers.pop('Content-Type')
        self.headers['Content-Disposition'] = 'inline; attachment; filename={}'.format(filename)
        
    
    def __call__(self):
        return super(FileResponse,self).__call__()
        
def Redirect(path : str,redirect_status_code : int = 302):
    r = Response(status_code=redirect_status_code,body='')
    r.headers['Location'] = path
    return r    

if __name__ == "__main__":
    pass