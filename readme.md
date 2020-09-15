## Python Web Server

A very simple and easy to use **HTTP** Server that can also handle **Websocket** Protocols with no external server dependenices (such as **Redis** or anything of that kind) written entirely in **Python**

You can use it by cloning the repository and creating your own **.py** file in the same directory

```sql
git clone https://github.com/Greece4ever/Python-HTTP-Sever.git
```
The only external dependency is on the `magic` module for guessing the **HTTP** Header "**Content-Type**" when provided a file so that the browser will render the correct thing.


### Http Server

Starting an **HTTP** Server is very easy, all you have to  do is **pass in** a dictionary with the **URLS PATHS** and their corresponding `View` class, (for handling the request)

All you do is inherit from `View` and then redefine the methods you want to accept **while** at the same time passing the **HTTP** status code that will be displayed.

```python
#Relative Imports
from server import HttpServer
from routes import View,ApiView
import status
#Built-in
import threading

class Dog(View):
    def GET(self,request):
        return status.Http200().__call__("<div>This is A <b>dog</b> Page</div>") #HTML or Loaded File

class Cat(ApiView):
    def GET(self,request):
        return status.HttpJson().__call__({'animal' : 'cat'},403) #JSON Response and CODE

dog = Dog()
cat = Cat()

#The Valid URLS
URLS = {
    '/dog' : dog,
    '/cat' : cat,
}

HTTP_SERVER = HttpServer(URLS=URLS) #Initliazie the Server
t = threading.Thread(target=HTTP_SERVER.AwaitRequest) #Start the thread listening for connections
t.start()
```
if you want to return **binary** data or data of a specific `Content-Type` attribute like **JavaScript**, **.PNG**, .**MP3** or whatever else, you can you the `status.HttpBinary().__call__(static("Path/To/File"),"Path/To/File")` and if you want to load an **HTML** page from inside a directory you put the **relative** or **absolute** path to the `template` function

```
from routes import View,static,template
from server import HttpServer
import status

#Rendering a custom Binary or external file
class Image(View):
    def GET(self,request):
        template_name = "last_Words.PNG" #Relative Path
        return status.HttpBinary().__call__(static(template_name),template_name)

#Loading an html page instead of hard coding it.
class HTML(View):
    def GET(self,request):
        return status.Http200().__call__(template("index.html")) #Relative path
```

### Websocket Server

Because when you run a **Websocket** server you're most likely going to have an **HTTP** Server running in Parallel, so one way to deal with this is to launch both servers but on a different port at a different thread but of course on the **Same Adress** to prevent **Cross-Origin-Request** problems

Each **Websocket** server must inherit from the base `WebsocketServer` class and there you can redefine the following methods `onConnect` on client connection , `onExit` on client exit , `onMessage` when a message is received

```
from server import WebsocketServer

class MyCustomSocket(WebsocketServer):

    def onConnect(self,client):
        print("Client {} connected to Websocket.".format(client[-1])) #Adress of client

    def onExit(self,client):
        print("Client {} Exited Websocket.".format(client[-1])) #Adress of client

    def onMessage(self,**kwargs):
        data = kwargs.get('data') #Retive the data
        #For Everyone Connected to the socket echo the mssage back
        for client in self.clients:
            self.send(client,data)
```

and because create a **Websocket** server is useless if you do not already have an **HTTP** server running 

```
class Chat(View):
    def GET(self,request):
        return status.Http200().__call__(template("index.html")) #Render index.html

chat = Chat()

URLS = {
    '/chat' : chat,
}
```

#### Client Side

The `index.html` could just be any html file but the following **JavaScript** must be put inside to handle **WS**

```js
const host = window.location.host
const PORT = 8000;
const socket = new WebSocket(`ws://${host}:${PORT}/ws/connection`) //Path does not matter

socket.onmessage = (response) => {
    document.body.innerHTML += `<p>${response.data}</p>` //Never Put user-typed HTML like this
}
```

and finally to **Initialize** the servers 

```python
HTTP_SERVER = HttpServer(URLS=URLS)
Socket_Server = MyCustomSocket(port=8000) #For Each different path a new Socket Server is required

#Start the HTTP and Websocket on different threads
t1 = threading.Thread(target=HTTP_SERVER.AwaitRequest) 
t2 = threading.Thread(target=Socket_Server.AwaitSocket)

t1.start()
t2.start()
```

To run the server all you need to do is **execute** the above script 

```
python demo.py
```

And if you go and visit your `/chat` path and while having it open on 2 **Browser-Windows** you can verify that the sockets are indeed working
