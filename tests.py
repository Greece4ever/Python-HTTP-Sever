from server import Server
from routes import View,template,static
import status
import magic

class Home(View):
    def GET(self,request):
        return status.Http200().__call__(template("index.html")) 

class StaticDog(View):
    def GET(self,request):
        return status.HttpBinary().__call__(static('last_Words.PNG'))

home = Home()
dog = StaticDog()

print(magic.from_file("last_Words.png"))

URLS : dict = {
    "/" : home,
    "/dog" : dog
}

HTTP_SERVER = Server()
HTTP_SERVER.AwaitRequest(URLS)