from server import Server,ThreadedServer
from routes import View,template,static,ApiView
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
        return status.Http200().__call__(template("socket.html"))

home = Home()
sta = StaticBinary()
rest = ApiView()
gg = ShitJson()
chat = Chat()

URLS : dict = {
    "/" : home,
    "/static" : sta,
    "/peos" : rest,
    '/another' : gg,
    '/chat' : chat 
}

HTTP_SERVER = Server()
t = threading.Thread(target=HTTP_SERVER.AwaitRequest,kwargs={"URLS" : URLS}) 
t.start()
WEBSOCKET_SERVER = ThreadedServer(port=8000)
t = threading.Thread(target=WEBSOCKET_SERVER.AwaitSocket)
t.start()