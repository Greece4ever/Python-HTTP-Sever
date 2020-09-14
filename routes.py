import status

class View:
    def __init__(self):
        self.cases = {
            'GET' : self.GET,
            'POST' : self.POST
        }

    def GET(self,request):
        msg = status.Http404.__call__("<h1>No such route<h1>")
        return msg

    def POST(self,request):
        return status.Http403.__call__("<h3>No such method</h3>")

    def __call__(self,request):
        return self.cases.get(request['method'].split(" ")[0].upper())(request)

def template(path : str):
    with open(path,'r') as f:
        data = f.read()
    return data

def static(path : str):
    with open(path,'rb+') as f:
        data = f.read()
    return data