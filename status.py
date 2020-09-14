class Http100(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 100 Continue\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http101(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 101 Switching Protocols\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http2xx(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 2xx **Successful**\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http200(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 200 OK\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http201(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 201 Created\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http202(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 202 Accepted\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http203(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 203 Non-Authoritative Information\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http204(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 204 No Content\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http205(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 205 Reset Content\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http206(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 206 Partial Content\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http3xx(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 3xx **Redirection**\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http300(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 300 Multiple Choices\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http301(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 301 Moved Permanently\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http302(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 302 Found\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http303(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 303 See Other\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http304(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 304 Not Modified\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http305(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 305 Use Proxy\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http307(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 307 Temporary Redirect\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http4xx(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 4xx **Client Error**\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http400(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 400 Bad Request\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http401(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 401 Unauthorized\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http402(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 402 Payment Required\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http403(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 403 Forbidden\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http404(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 404 Not Found\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http405(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 405 Method Not Allowed\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http406(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 406 Not Acceptable\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http407(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 407 Proxy Authentication Required\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http408(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 408 Request Timeout\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http409(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 409 Conflict\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http410(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 410 Gone\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http411(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 411 Length Required\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http412(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 412 Precondition Failed\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http413(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 413 Payload Too Large\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http414(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 414 URI Too Long\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http415(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 415 Unsupported Media Type\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http416(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 416 Range Not Satisfiable\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http417(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 417 Expectation Failed\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http418(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 418 I'm a teapot\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http426(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 426 Upgrade Required\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http5xx(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 5xx **Server Error**\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http500(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 500 Internal Server Error\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http501(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 501 Not Implemented\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http502(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 502 Bad Gateway\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http503(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 503 Service Unavailable\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http504(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 504 Gateway Time-out\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http505(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 505 HTTP Version Not Supported\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http102(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 102 Processing\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http207(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 207 Multi-Status\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http226(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 226 IM Used\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http308(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 308 Permanent Redirect\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http422(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 422 Unprocessable Entity\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http423(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 423 Locked\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http424(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 424 Failed Dependency\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http428(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 428 Precondition Required\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http429(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 429 Too Many Requests\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http431(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 431 Request Header Fields Too Large\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http451(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 451 Unavailable For Legal Reasons\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http506(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 506 Variant Also Negotiates\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http507(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 507 Insufficient Storage\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    


class Http511(Exception):
    @classmethod
    def __call__(self,template):
        return (b"HTTP/1.1 511 Network Authentication Required\n"
                +b"Content-Type: text/html\n"
                +b"\n" 
                +template.encode())    
