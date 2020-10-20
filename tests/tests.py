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
        f = request[-1].get('file')
        with open(b_f(f['filename']),'wb+') as file:
            file.write(f['data'].getvalue())
        return status.FileResponse(b_f(f['filename']),status_code=200)

class VideoStream(View):
    def GET(self, request, **kwargs):
        return status.StreamingFileResponse(r'C:\Users\progr\Videos\Captures\Blender 2020-10-19 17-15-58.mp4')

class WebSocketHandler(View):
    def GET(self, request, **kwargs):
        return status.Response(200,status.Template(b_f('socket.html')))

class ChatView(SocketView):
    def onMessage(self,data,*args,**kwargs):
        for client in self.clients:
            self.send(client,data)
    
    def onExit(self,client_that_left,**kwargs):
        ip = kwargs.get("state")
        msg = f'{ip} has left!'
        for client in self.clients:
            self.send(client,msg)

    def onConnect(self,client,**kwargs):
        sock_name = self.get_client_ip(client)
        msg = f'{sock_name} has joined!'
        self.accept(client)
        self.send(client,msg)
        for client in self.clients:
            self.send(client,msg)
        return sock_name

socket_paths = {r'/ws/chat' : ChatView()}
PATHS = {
    r'/json/?' : JsonView(),
    r'/cookie/?' : CookieSetter(),
    r'/redirect/?' : Redirecter(),
    r'/static/?' : BinaryFile(),
    r'/post/?' : FormSubmit(),
    r'/video/?' : VideoStream(),
    r'/send_data/?' : Form(),
    r'/websocket/?' : WebSocketHandler()}
server = Server(host='127.0.0.1',socket_paths=socket_paths,http_paths=PATHS,CORS_DOMAINS=['http://localhost:8000','http://localhost:3000'])
server.start()