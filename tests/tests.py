from ..server.server import WebsocketServer,HttpServer,RoutedWebsocketServer,Server
from ..server.routes import View,template,SocketView
from ..client_side import status
# from cache import Cache
import pprint,os,threading;import os

# cache = Cache("cache.sqlite3","Cache",(1,datetime.timedelta(seconds=10)))
STATIC_FILES_DIR : str = r'C:\Users\Spartakos\Desktop\server\static'

class Home(View):
    # @cache.CacheDecorator
    def GET(self,request,**kwargs):
        return status.Http200().__call__("Home Page") 

class JsonView(View):
    def GET(self,request):
        return status.HttpBinary().__call__(r'C:\Users\Spartakos\Desktop\server\tests\json.html',200,display_in_browser=True)

    def POST(self,request):
        pprint.pprint(request[-1])
        return status.HttpJson().__call__({
            'state' : 'ok',
            'isGood' : True
        },200)

class Chat(View):
    def GET(self,request):
        return status.HttpBinary().__call__(r'C:\Users\Spartakos\Desktop\server\tests\socket.html',200,display_in_browser=True)

class Chat2(View):
    def GET(self,request):
        return status.Http200().__call__(template(os.path.join(os.getcwd(),"test.html"),usePythonScript=True))

class RView(View):
    def GET(self,request):
        context = {
            'words' :["a","abandon","ability","able","abortion","about","above","abroad","absence","absolute","absolutely","absorb"]
        }
        return status.Http200().__call__(template("test.html",usePythonScript=True,context=context))

class Imgres(View):
    def GET(self,request):
        num = [item for item in request[0]['uri'].split("/") if item.strip() != ''][-1]
        files = os.listdir(r'C:\Users\Spartakos\Desktop\server\static')
        if int(num) >= len(files):
            return status.HttpBinary().__call__(os.path.join(r'C:\Users\Spartakos\Desktop','Capture.JPG'),200,display_in_browser=True)
        return status.HttpBinary().__call__(os.path.join(STATIC_FILES_DIR,files[int(num)]),200,display_in_browser=True)
        # return status.HttpBinary().__call__(os.path.join(r'C:\Users\Spartakos\Desktop','ΑΣΘΕΝΙΔΗΣ ΛΕΩΝΙΔΑΣ.PDF'),200,display_in_browser=True)

class SampleView(View):
    def GET(self,request):
        from random import random
        context = {
            'random' : [
                [int(random() * 255) for _ in range(3)] for __ in range(10) ]
        }
        return status.Http200().__call__(template(r"C:\Users\Spartakos\Desktop\server\tests\test.html",usePythonScript=True,context=context))

    def POST(self,request):
        pprint.pprint(request)
        return status.Http200().__call__("<h1>Helo World!</h1>")

class PostView(View):
    def GET(self, request):
        return status.Http200().__call__(template(r"C:\Users\Spartakos\Desktop\server\tests\test.html",usePythonScript=True))

    def POST(self,request):
        pprint.pprint(request)
        body = request[-1]
        for item in body:
            if 'filename' in item:
                with open(os.path.join(r'C:\Users\Spartakos\Desktop\server\static',item['filename']),'wb+') as f:
                    for line in iter(item['data'].readlines()):
                        f.write(line)
            else:
                print(item,item['data'].read())

        return status.Http200().__call__("""<span style='color : red' >if</span><span>(<span>x</span>==<span style='color : blue'>1</span>)""")

class RedirectView(View):
    def GET(self,request):
        return status.Redirect().__call__('/poutsa')
    
S_PATH = r'C:\Users\Spartakos\Desktop\server\tests\socket.html'

class WSView(View):
    def GET(self,request):
        return status.Http200().__call__(template(S_PATH))

URLS : dict = {
    r"^(\/)?" : Home(),
    r"/accounts/register(\/)?" : Home(),
    r"(\/)?nova(\/)?\?(.*)" : WSView(),
    r"(\/)?peos(\/)?\?(.*)" : WSView(),
    r"(\/)?sql(\/)?\?(.*)" : WSView(),
    r"(\/)?pie(\/)?\?(.*)" : WSView(),
    r'(\/)?json(\/)?' : JsonView(),
    '/chat' : Chat(),
    '/chat2' : Chat2(),
    r'(\/)images\/(\d+)(\/)?' : Imgres(),
    r'\/profiles\/(\w+)(\/)?' : RView(),
    r'(\/)tests(\/)(\d+)(\/)?' : SampleView(),
    r'/post' : PostView(),
    r'/redirect' : RedirectView()
}

# Routed WS Server
class CustomRoute(SocketView):
    def onConnect(self,client,**kwargs):
        #Get the **kwarg arguments
        key = kwargs.get("key")
        path_info = kwargs.get("path_info")
        send = kwargs.get('send_function')
        msg_to_send = "{} has connected!".format(self.get_client_ip(client))

        #Accept the user send send him the message
        self.accept(client=client,key=key) #Accept the client request
        send(client,msg_to_send)


        #Send the message to all the clients in the same path that someone has connected
        for client in path_info['clients']:
            send(client,msg_to_send)
        return True

    def onMessage(self,**kwargs):
        """Gets called when a message is received from the client side"""
        data = kwargs.get('data')
        path_info = kwargs.get("path_info")
        send = kwargs.get('send_function')
        for client in path_info['clients']:
            send(client,data)

    def onExit(self,client,**kwargs):
        path_info = kwargs.get("path_info")
        send = kwargs.get('send_function')
        for client in path_info['clients']:
            send(client,"{} has left!".format(self.get_client_ip(client)))

class SimpleWebSocketServer(WebsocketServer):
    def onConnect(self,client,**kwargs):
        key = kwargs.get("key")
        msg_to_send = "{} has connected!".format(self.get_client_ip(client))
        self.accept(client=client,key=key) #Accept the client request
        self.send(client,msg_to_send)
        for client in self.clients:
            self.send(client,msg_to_send)
        return True

    def onMessage(self,**kwargs):
        """Gets called when a message is received from the client side"""
        data = kwargs.get('data')
        for client in self.clients:
            self.send(client,data)

    def onExit(self,client,**kwargs):
        for client in self.clients:
            self.send(client,"{} has left!".format(self.get_client_ip(client)))


PATHS = {
    '/peos' : CustomRoute(),
    '/sql' : CustomRoute(),
    '/nova' : CustomRoute(),
    '/pie' : CustomRoute()
}

CORS_DOMAINS=['http://127.0.0.1:5500','http://127.0.0.1:8000','http://google.com']
server = Server(host='127.0.0.1',socket_paths=PATHS,http_paths=URLS,CORS_DOMAINS=[None])
# full_server.start()
# server = HttpServer(URLS=URLS,port=8000,CORS_DOMAINS=['http://127.0.0.1:5500','http://127.0.0.1:8000','http://google.com'])
# ws_server = RoutedWebsocketServer(paths=PATHS,port=69)
# ws_server = SimpleWebSocketServer(port=69)
threading.Thread(target=server.start).start()
# threading.Thread(target=ws_server.start).start()