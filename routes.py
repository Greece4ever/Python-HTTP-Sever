import status

class View:
    def __init__(self):
        self.cases = {
            'GET' : self.GET,
            'POST' : self.POST
        }

    def GET(self,request):
        msg = status.Http200.__call__("<h1>Welcome to the <b>Blog</b> homepage!<h1>")
        return msg

    def POST(self,request):
        return status.Http403.__call__("<h3>I DON'T LIKE POST REQUESTS</h3>")

    def __call__(self,request):
        return self.cases.get(request['method'].split(" ")[0].upper())(request)


class MyView(View):
    def GET(self,request):
        return status.Http200.__call__("<h1>Welcome to my custom made path</h1>")

class MySecondView(View):
    def GET(self,request):
        return status.Http403.__call__("<h2>No One is allowed to come here</h2>")

x = View()
y = MyView()
z = MySecondView()

URLS : dict = {
        "/" : x,
        "/PATH" : y,
        "/pakis" : z 
    }
