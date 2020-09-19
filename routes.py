import status
import json
import static as st

def UI405(method : str) -> str:
    return "<h1> Method {} not Allowed </h1>".format(method)

class View:
    def __init__(self):
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
        return self.cases.get(request['method'].split(" ")[0].upper())(request)

class ApiView(View):
    def __init__(self):
        self.not_allowed = {"error" : "Not Allowed"}
        super(ApiView,self).__init__()

    status.HttpJson(json)
    def GET(self,request):
        return status.HttpJson().__call__(self.not_allowed,405)

    def POST(self,request):
        return status.HttpJson().__call__(self.not_allowed,405)

    def HEAD(self,request):
        return status.HttpJson().__call__(self.not_allowed,405)

    def PUT(self,request):
        return status.HttpJson().__call__(self.not_allowed,405)


    def DELETE(self,request):
        return status.HttpJson().__call__(self.not_allowed,405)

    def CONNECT(self,request):
        return status.HttpJson().__call__(self.not_allowed,405)

    def OPTIONS(self,request):
        return status.HttpJson().__call__(self.not_allowed,405)

    def TRACE(self,request):
        return status.HttpJson().__call__(self.not_allowed,405)

    def PATCH(self,request):
        return status.HttpJson().__call__(self.not_allowed,405)

class SocketView:
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

def template(path : str,usePythonScript : bool = False,context : dict =  {}):
    with open(path,'r') as f:
        data = f.read()
    if usePythonScript:
        data = st.findScript(data,context)
    return data

def static(path : str):
    with open(path,'rb+') as f:
        data = f.read()
    return data