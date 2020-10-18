from ..client_side import status
from ..client_side import cscript as st

err_msg = "Method not allowed"

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

    def GET(self,request):
        return status.Response(405,err_msg)

    def POST(self,request):
        return status.Response(405,err_msg)

    def HEAD(self,request):
        return status.Response(405,err_msg)

    def PUT(self,request):
        return status.Response(405,err_msg)

    def DELETE(self,request):
        return status.Response(405,err_msg)

    def CONNECT(self,request):
        return status.Response(405,err_msg)

    def OPTIONS(self,request):
        return status.Response(405,err_msg)

    def TRACE(self,request):
        return status.Response(405,err_msg)

    def PATCH(self,request):
        return status.Response(405,err_msg)

    def __call__(self,request):
        method = request[0]['method'].split(" ")[0].upper()
        view = self.cases.get(method)
        if(view is None):
            print("[ERROR] Request method not found : {}".format(method))
            return status.Response(405,err_msg)
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
        self.keys = {}
        self.clients = {}

    def onMessage(self,**kwargs):
        pass

    def onExit(self,client,**kwargs):
        pass
    
    def onConnect(self,client,**kwargs) -> bool:
        """onConnect must return an object,
           so that bool(object) is True,
           and will then be stored as state.
           if the bool(object) returns False
           the connection will be closed
        """
        pass

    def get_client_ip(self,client) -> str:
        return client.getsockname()[0]

    def accept_with_key(self,client,key : str) -> None:
        """Accept client WebSocket Connection"""
        HTTP_MSG = status.Http101().__call__(key)
        client.send(HTTP_MSG)

    def accept(self,client) -> None:
        key = self.keys.get(client)
        HTTP_MSG = status.Http101().__call__(key)
        return client.send(HTTP_MSG)

    def set_send_function(self,function : callable):
        self.send = function

    def MaxSize(self):
        return self.max_size

if __name__ == "__main__":
    pass