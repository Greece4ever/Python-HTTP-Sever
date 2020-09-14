from server import Server
from routes import View,template,static,ApiView
import status

class Home(View):
    def GET(self,request):
        return status.Http200().__call__(template("index.html")) 

class StaticBinary(View):
    def GET(self,request):
        return status.HttpBinary().__call__(static('ATETOKOUMPOS.m4v'),"ATETOKOUMPOS.m4v")

class ShitJson(ApiView):
    def GET(self,request):
        return status.HttpJson().__call__({"hello" : 1},200)

home = Home()
sta = StaticBinary()
rest = ApiView()
gg = ShitJson()

URLS : dict = {
    "/" : home,
    "/static" : sta,
    "/peos" : rest,
    '/another' : gg
}

HTTP_SERVER = Server()
HTTP_SERVER.AwaitRequest(URLS)