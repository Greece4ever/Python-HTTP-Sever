from ..server.server import WebsocketServer,HttpServer,RoutedWebsocketServer,Server
from ..server.routes import View,SocketView
from ..client_side import status
# from cache import Cache
import pprint,os,threading;import os

BASE_DIR = os.getcwd()
j : callable = lambda *path : os.path.join(BASE_DIR,*path)

class Hello(View):
    def GET(self, request, **kwargs):
        response = status.Response(200,status.Template(j(*r'/Server/tests/test.html'.split("/"))))
        return response

class JsonView(View):
    def GET(self, request, **kwargs):
        response =  status.JSONResponse(template={"status" : "ok"},status_code=200)
        return response

class Redirecter(View):
    def GET(self, request, **kwargs):
        return status.Redirect('/json')

class CookieSetter(View):
    def GET(self, request, **kwargs):
        response = status.Response(200,'<b>Hello World</b>')
        response.set_cookie(status.Cookie("id","3"))
        return response

PATHS = {
    r'/hello/?' : Hello(),
    r'/json/?' : JsonView(),
    r'/cookie/?' : CookieSetter(),
    r'/redirect/?' : Redirecter()
}

CORS_DOMAINS=['http://127.0.0.1:5500','http://127.0.0.1:8000','http://google.com']
server = Server(host='127.0.0.1',socket_paths={},http_paths=PATHS,CORS_DOMAINS=[])
server.start()