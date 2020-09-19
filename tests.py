from server import WebsocketServer,HttpServer,RoutedWebsocketServer
from routes import View,template,static,ApiView,SocketView
import status
import threading
import datetime
from cache import Cache

cache = Cache("cache.sqlite3","Cache",(1,datetime.timedelta(seconds=10)))

class Home(View):

    @cache.CacheDecorator
    def GET(self,request,**kwargs):
        isperm = kwargs.get('isPermitted')
        if isperm:
            return status.Http200().__call__("Home Page") 
        return status.Http429().__call__("Too many requests 429")

class StaticBinary(View):
    def GET(self,request):
        return status.HttpBinary().__call__(static('readme.md'),"readme.md")

class ShitJson(ApiView):
    def GET(self,request):
        return status.HttpJson().__call__({"hello" : 1},200)

class Chat(View):
    def GET(self,request):
        return status.Http200().__call__(template("Examples/index.html"))

class Chat2(View):
    def GET(self,request):
        return status.Http200().__call__(template("Examples/test.html",usePythonScript=True))

class RView(View):
    def GET(self,request):
        context = {
            'words' :["a",
                    "abandon",
                    "ability",
                    "able",
                    "abortion",
                    "about",
                    "above",
                    "abroad",
                    "absence",
                    "absolute",
                    "absolutely",
                    "absorb"]
        }
        # page_num = request['method'].split('/')[-1]
        # return status.Http200().__call__("<h2>You've visited page number {}!</h2>".format(page_num))
        return status.Http200().__call__(template("Examples/test.html",usePythonScript=True,context=context))


URLS : dict = {
    "/" : Home(),
    "/static" : StaticBinary(),
    "/peos" : ApiView(),
    '/another' : ShitJson(),
    '/chat' : Chat(),
    '/chat2' : Chat2(),
    r'\/profiles\/(\w+)(\/)?' : RView(),
}

class CustomRoute(SocketView):

    def onMessage(self,**kwargs):
        """Gets called when a message is received from the client side"""
        data = kwargs.get('data')
        path_info = kwargs.get("path_info")
        send = kwargs.get('send_function')
        for client in path_info['clients']:
            send(client,data)

class ChatRoute(CustomRoute):
    pass

PATHS = {
    '/peos' : CustomRoute(),
    '/chat' : ChatRoute(ChatRoute)
}


HTTP_SERVER = HttpServer(URLS=URLS)
WEBSOCKET_SERVER = RoutedWebsocketServer(PATHS)

t = threading.Thread(target=HTTP_SERVER.AwaitRequest) 
t.start()

t = threading.Thread(target=WEBSOCKET_SERVER.AwaitSocket)
t.start()