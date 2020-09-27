""""
    All HTTP Response codes that will be received on the client-side,\r\n
    To use one of them you can call them inside the method\r\n
    using the .__call__ method and the html you want to render\r\n
"""

import json #For json
from typing import Tuple
import os

#For Handling Websockets
from base64 import b64encode 
from hashlib import sha1

from .c_types import content_types

GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

class Http100(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 100 Continue\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


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
                +b"\r\n"
                )    


class Http2xx(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 2xx **Successful**\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n"    
                +template.encode())    


class Http200(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 200 OK\r\n"
                +b"Content-Type: text/html\r\n"
                +b"Connection: close\r\n"
                +b"\r\n" 
                +template.encode())    

class HttpBinary(Exception):
    """For transfering binaries-files (or any file really) through HTTP 
    """
    @classmethod
    def __call__(self,path,code,display_in_browser : bool = False) -> Tuple[callable,str]:
        status = NUM_STATUS.get(str(code)) #Get the status code message
        assert (status is not None), "Invalid Status code \"{}\"".format(code) #raise exception if it does not exist
        filename = path.split("\\")[-1] #get the filename
        ctype = content_types.get('.' + filename.split(".")[-1].lower()) #get the mime for the file type (.FILETYPE)
        ctype = b'' if ctype is None else "Content-Type: {}\r\n".format(ctype).encode()

        #Return callabe
        if not display_in_browser:
            return (lambda size : (
                    f"HTTP/1.1 {code} {status}\r\n".encode()
                    + ctype
                    +"Content-Length : {}\r\n".format(size).encode()
                    # +"Content-Disposition: inline" if display_in_browser else "Content-Disposition : attachment; filename=\"{}\"\r\n".format(filename).encode()
                    +"Content-Disposition : attachment; filename=\"{}\"\r\n".format(filename).encode()
                    +b"\r\n"
            ),path)
        return (lambda size : (
                f"HTTP/1.1 {code} {status}\r\n".encode()
                + ctype
                +"Content-Length : {}\r\n".format(size).encode()
                +"Content-Disposition: inline; filename=\"{}\"\r\n".format(filename).encode()
                +b"\r\n"
        ),path)


class HttpJson(Exception):
    """
    For correctly transfering JSON
    data through HTTP that do not
    need to be parsed by JavaScript
    """
    @classmethod
    def __call__(self,template,status):
        try:
            status = NUM_STATUS.get(str(status))
        except:
            raise TypeError("Invalid HTTP Status code {}".format(status))
        data = json.dumps(template)
        return (f"HTTP/1.1 {status}\r\n".encode()
                +b"Content-Type: application/json\r\n"
                +b"\r\n" 
                +data.encode())    


class Http201(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 201 Created\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http202(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 202 Accepted\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http203(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 203 Non-Authoritative Information\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http204(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 204 No Content\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http205(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 205 Reset Content\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http206(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 206 Partial Content\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http3xx(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 3xx **Redirection**\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http300(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 300 Multiple Choices\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http301(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 301 Moved Permanently\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http302(Exception):
    @classmethod
    def __call__(self,template,location):
        return (b"HTTP/1.1 302 Found\r\n"
                +b"Content-Type: text/html\r\n"
                +b"Location : " + f'{location}'.encode()
                +b"\r\n" 
                +template.encode())    

class Redirect(Exception):
    @classmethod
    def __call__(self,location):
        return Http302().__call__('',location)

class Http303(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 303 See Other\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http304(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 304 Not Modified\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http305(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 305 Use Proxy\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http307(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 307 Temporary Redirect\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http4xx(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 4xx **Client Error**\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http400(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 400 Bad Request\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http401(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 401 Unauthorized\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http402(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 402 Payment Required\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http403(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 403 Forbidden\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http404(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 404 Not Found\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http405(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 405 Method Not Allowed\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http406(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 406 Not Acceptable\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http407(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 407 Proxy Authentication Required\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http408(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 408 Request Timeout\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http409(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 409 Conflict\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http410(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 410 Gone\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http411(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 411 Length Required\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http412(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 412 Precondition Failed\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http413(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 413 Payload Too Large\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http414(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 414 URI Too Long\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http415(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 415 Unsupported Media Type\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http416(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 416 Range Not Satisfiable\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http417(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 417 Expectation Failed\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http418(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 418 I'm a teapot\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http426(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 426 Upgrade Required\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http5xx(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 5xx **Server Error**\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http500(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 500 Internal Server Error\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http501(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 501 Not Implemented\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http502(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 502 Bad Gateway\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http503(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 503 Service Unavailable\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http504(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 504 Gateway Time-out\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http505(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 505 HTTP Version Not Supported\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http102(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 102 Processing\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http207(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 207 Multi-Status\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http226(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 226 IM Used\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http308(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 308 Permanent Redirect\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http422(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 422 Unprocessable Entity\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http423(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 423 Locked\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http424(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 424 Failed Dependency\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http428(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 428 Precondition Required\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http429(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 429 Too Many Requests\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http431(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 431 Request Header Fields Too Large\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http451(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 451 Unavailable For Legal Reasons\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http506(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 506 Variant Also Negotiates\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http507(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 507 Insufficient Storage\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    


class Http511(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 511 Network Authentication Required\r\n"
                +b"Content-Type: text/html\r\n"
                +b"\r\n" 
                +template.encode())    

NUM_STATUS = {'1xx': '**Informational**', '100': 'Continue', '101': 'Switching Protocols', '2xx': '**Successful**', '200': 'OK', '201': 'Created', '202': 'Accepted', '203': 'Non-Authoritative Information', '204': 'No Content', '205': 'Reset Content', '206': 'Partial Content', '3xx': '**Redirection**', '300': 'Multiple Choices', '301': 'Moved Permanently', '302': 'Found', '303': 'See Other', '304': 'Not Modified', '305': 'Use Proxy', '307': 'Temporary Redirect', '4xx': '**Client Error**', '400': 'Bad Request', '401': 'Unauthorized', '402': 'Payment Required', '403': 'Forbidden', '404': 'Not Found', '405': 'Method Not Allowed', '406': 'Not Acceptable', '407': 'Proxy Authentication Required', '408': 'Request Timeout', '409': 'Conflict', '410': 'Gone', '411': 'Length Required', '412': 'Precondition Failed', '413': 'Payload Too Large', '414': 'URI Too Long', '415': 'Unsupported Media Type', '416': 'Range Not Satisfiable', '417': 'Expectation Failed', '418': "I'm a teapot", '426': 'Upgrade Required', '5xx': '**Server Error**', '500': 'Internal Server Error', '501': 'Not Implemented', '502': 'Bad Gateway', '503': 'Service Unavailable', '504': 'Gateway Time-out', '505': 'HTTP Version Not Supported', '102': 'Processing', '207': 'Multi-Status', '226': 'IM Used', '308': 'Permanent Redirect', '422': 'Unprocessable Entity', '423': 'Locked', '424': 'Failed Dependency', '428': 'Precondition Required', '429': 'Too Many Requests', '431': 'Request Header Fields Too Large', '451': 'Unavailable For Legal Reasons', '506': 'Variant Also Negotiates', '507': 'Insufficient Storage', '511': 'Network Authentication Required', '7xx': '**Developer Error**'}

if __name__ == "__main__":
    pass