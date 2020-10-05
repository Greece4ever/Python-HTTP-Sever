from ..client_side import status
from ..client_side import cscript as st

def UI405(method : str) -> str:
    return "<h1> Method {} not Allowed </h1>".format(method)

class View:
    """
    The basis of handling HTTP Connections and requests\r\n
    such as POST or GET and responding back to the client.\r\n
    
    You can redefine any request method to your liking,\n
    and by passing request as a positional arguemnt\n
    so as to receive the parsed request data\n

    every response must be an HTTP status code,\n
    with either a template render or string text\n
    """
    def __init__(self,**kwargs):
        self.cases = {
            'GET' : self.GET,
            'POST' : self.POST,
            "HEAD" : self.HEAD,
            "PUT" : self.PUT,
            "DELETE" : self.DELETE,
            "CONNECT" : self.CONNECT,
            "OPTIONS" : self.OPTIONS,
            "TRACE" : self.TRACE,
            "PATCH" : self.PATCH
        }
        self.PAGE_405_FUNCTION = kwargs.get('PAGE_405_FUNCTION')
        self.PAGE_405_FUNCTION = self.PAGE_405_FUNCTION if self.PAGE_405_FUNCTION is not None else UI405

    def GET(self,request):
        return status.Http405().__call__(UI405("GET"))

    def POST(self,request):
        return status.Http405().__call__(UI405("POST"))

    def HEAD(self,request):
        return status.Http405().__call__(UI405("HEAD"))

    def PUT(self,request):
        return status.Http405().__call__(UI405("PUT"))

    def DELETE(self,request):
        return status.Http405().__call__(UI405("DELETE"))

    def CONNECT(self,request):
        return status.Http405().__call__(UI405("CONNECT"))

    def OPTIONS(self,request):
        return status.Http405().__call__(UI405("OPTIONS"))

    def TRACE(self,request):
        return status.Http405().__call__(UI405("TRACE"))

    def PATCH(self,request):
        return status.Http405().__call__(UI405("PATCH"))

    def __call__(self,request):
        method = request[0]['method'].split(" ")[0].upper()
        view = self.cases.get(method)
        if(view is None):
            print("[ERROR] Request method not found : {}".format(method))
            return status.Http405().__call__("Method {} not allowed.".format(method))
        return self.cases.get(method)(request)

class SocketView:
    """
    A view for handling WebSocket connections and keeping the connection alive\n
    used in the URLS passed in to the RoutedWebsocketServer __init__ method.\n

    Parameters:
        param: max_size = The maximum amount of data to be transfered at a time
        DEFAULT = 4096

    Methods:
        (NOT TO BE OVERRIDDEN)
        method: send (Send message to a client) 
        method: accept (Accept a client connection)
        (TO BE OVERRIDDEN)
        method: onMessage (What to do on a client message)
        method: onExit (What to do on client exit)
        method: onConnect (What to do on client connect)
        method: get_client_ip (get the client's socketname)

    """
    def __init__(self,max_size : int = 4096):
        self.max_size = max_size

    def onMessage(self,**kwargs):
        pass

    def onExit(self,client,**kwargs):
        pass
    
    def onConnect(self,client,**kwargs) -> bool:
        pass

    def send(self,client,socketfunction):
        pass

    def get_client_ip(self,client) -> str:
        return client.getsockname()[0]

    def accept(self,client,key : str) -> None:
        """Accept client WebSocket Connection"""
        HTTP_MSG = status.Http101().__call__(key)
        client.send(HTTP_MSG)

    def MaxSize(self):
        return self.max_size

def template(path : str,usePythonScript : bool = False,context : dict =  {}):
    with open(path,'r',encoding='utf-8') as f:
        data = f.read()
    if usePythonScript:
        data = st.findScript(data,context)
    return data

if __name__ == "__main__":
    pass