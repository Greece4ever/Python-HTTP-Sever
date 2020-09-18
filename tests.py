from server import WebsocketServer,HttpServer,RoutedWebsocketServer
from routes import View,template,static,ApiView,SocketView
import status
import threading
import datetime
from cache import Cache

cache = Cache("cache.sqlite3","Cache",(10,datetime.timedelta(minutes=1)))

class Home(View):

    @cache.CacheDecorator
    def GET(self,request,**kwargs):
        print(kwargs.get('isPermitted'))
        return status.Http200().__call__("Home Page") 

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
        return status.Http200().__call__(template("Examples/socket.html"))

class RView(View):
    def GET(self,request):
        page_num = request['method'].split('/')[-1]
        return status.Http200().__call__("<h2>You've visited page number {}!</h2>".format(page_num))

class Axios(View):
    def GET(self, request):
        s = ["a",
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
            "absorb",
                ]
        return status.Http200().__call__(template("Examples/test.html",usePythonScript=True,context={'names' : s}))

URLS : dict = {
    "/" : Home(),
    "/static" : StaticBinary(),
    "/peos" : ApiView(),
    '/another' : ShitJson(),
    '/chat' : Chat(),
    '/chat2' : Chat2(),
    r'\/profiles\/(\w+)(\/)?' : RView(),
    r'/nums\/(\d+)' : Axios()
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