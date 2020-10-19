from ..server.server import WebsocketServer,HttpServer,RoutedWebsocketServer,Server
from ..server.routes import View,SocketView
from ..client_side import status
# from cache import Cache
import pprint,os,threading;import os

BASE_DIR = os.getcwd()
j : callable = lambda *path : os.path.join(BASE_DIR,*path)
b_f : callable = lambda file : j(*r'/Server/tests/{}'.format(file).split("/"))

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

class BinaryFile(View):
    def GET(self, request, **kwargs):
        return status.FileResponse(b_f("peos.PNG"),200)

class FormSubmit(View):
    def GET(self, request, **kwargs):
        return status.Response(200,status.Template(b_f("test.html")))

    def POST(self, request, **kwargs):
        pprint.pprint(request)
        return status.Response(200,"<div>200 OK</div>")

class Form(View):
    def GET(self, request : tuple, **kwargs) -> status.Response:
        return status.Response(200,status.Template(b_f('json.html')))

    def POST(self, request : tuple, **kwargs) -> status.Response:
        pprint.pprint(request)
        return status.JSONResponse(status_code=69,msg="gamiese",tempalte={"status" : "ok"})


class LargeVideo(View):
    def GET(self, request, **kwargs):
        r =  status.FileResponse(r"C:\Users\progr\Videos\Captures\Blender 2020-10-19 17-15-58.mp4",status_code=206)
        r.headers['Accept-Ranges'] = 'bytes'
        r.headers['Connection'] = 'keep-alive'
        return r

PATHS = {
    r'/json/?' : JsonView(),
    r'/cookie/?' : CookieSetter(),
    r'/redirect/?' : Redirecter(),
    r'/static/?' : BinaryFile(),
    r'/post/?' : FormSubmit(),
    r'/video/?' : LargeVideo(),
    r'/send_data/?' : Form()
}

CORS_DOMAINS=['http://127.0.0.1:5500','http://127.0.0.1:8000','http://google.com']
server = Server(host='127.0.0.1',socket_paths={},http_paths=PATHS,CORS_DOMAINS=[])
server.start()