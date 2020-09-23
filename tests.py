from server import WebsocketServer,HttpServer,RoutedWebsocketServer,Server
from routes import View,template,SocketView
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

class ShitJson(View):
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


class Imgres(View):
    def GET(self,request):
        return status.HttpBinary().__call__("megalos.PNG",200)

class SampleView(View):
    def GET(self,request):
        from random import random
        context = {
            'random' : [
                [int(random() * 255) for _ in range(3)] for __ in range(10) ]
        }
        return status.Http200().__call__(template("Examples/test2.html",usePythonScript=True,context=context))

class PostView(View):
    def GET(self, request):
        return status.Http200().__call__(template("Examples/test.html",usePythonScript=True))

    def POST(self,request):
        # print(request)
        return status.Http200().__call__("""<title>Hello</title>""")

URLS : dict = {
    r"^(\/)?" : Home(),
    '/another' : ShitJson(),
    '/chat' : Chat(),
    '/chat2' : Chat2(),
    r'(\/)images\/(\d+)(\/)?' : Imgres(),
    r'\/profiles\/(\w+)(\/)?' : RView(),
    r'(\/)tests(\/)(\d+)(\/)?' : SampleView(),
    r'/post' : PostView()
}

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

class ChatRoute(CustomRoute):
    pass

PATHS = {
    '/peos' : CustomRoute(),
    '/chat' : ChatRoute()
}

URLS['/SQL'] = CustomRoute()

server = Server(PATHS,URLS,port=80)
server.AwaitRequest()
# threading.Thread(target=server.AwaitRequest).start()


# HTTP_SERVER = HttpServer(URLS=URLS)
# WEBSOCKET_SERVER = RoutedWebsocketServer(PATHS)

# t = threading.Thread(target=HTTP_SERVER.AwaitRequest) 
# t.start()

# t = threading.Thread(target=WEBSOCKET_SERVER.AwaitSocket)
# t.start()