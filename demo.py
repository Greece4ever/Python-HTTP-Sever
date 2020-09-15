#Relative Imports
from server import HttpServer,WebsocketServer
from routes import View,ApiView,static,template
import status
#Built-in
import os
import threading


class MyCustomSocket(WebsocketServer):

    def onConnect(self,client):
        """Called when a client establishes
          a connection to the server,
          the 'client' paramter is part
          of the socket library 
        """
        print("Client {} connected to Websocket.".format(client[-1]))


    def onExit(self,client):
        """Called when a client exits
          the 'client' paramter is part
          of the socket library 
        """
        print("Client {} Exited Websocket.".format(client[-1]))


    def onMessage(self,**kwargs):
        """This method gets called when
           a message is received from a 
           client, and is the most useful
        """
        data = kwargs.get('data') #Retive the data
        #For Everyone Connected to the socket echo the mssage back
        for client in self.clients:
            self.send(client,data)



class Chat(View):
    def GET(self,request):
        return status.Http200().__call__(template(os.path.join(os.getcwd(),'Examples','index.html')))

chat = Chat()

#The Valid URLS
URLS = {
    '/chat' : chat,
}

HTTP_SERVER = HttpServer(URLS=URLS)
Socket_Server = MyCustomSocket(port=8000) #For Each different path a new Socket Server is required

t1 = threading.Thread(target=HTTP_SERVER.AwaitRequest) 
t2 = threading.Thread(target=Socket_Server.AwaitSocket)

t1.start()
t2.start()