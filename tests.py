from server import WebsocketServer,HttpServer,RoutedWebsocketServer
from routes import View,template,static,ApiView,SocketView
import status
import threading

class Home(View):
    def GET(self,request):
        return status.Http200().__call__(template("index.html")) 

class StaticBinary(View):
    def GET(self,request):
        return status.HttpBinary().__call__(static('ATETOKOUMPOS.m4v'),"ATETOKOUMPOS.m4v")

class ShitJson(ApiView):
    def GET(self,request):
        return status.HttpJson().__call__({"hello" : 1},200)

class Chat(View):
    def GET(self,request):
        return status.Http200().__call__(template("Examples/index.html"))

class Chat2(View):
    def GET(self,request):
        return status.Http200().__call__(template("Examples/socket.html"))

URLS : dict = {
    "/" : Home(),
    "/static" : StaticBinary(),
    "/peos" : ApiView(),
    '/another' : ShitJson(),
    '/chat' : Chat(),
    '/chat2' : Chat2()
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
