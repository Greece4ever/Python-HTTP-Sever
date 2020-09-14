import status

class View:
    def __init__(self):
        pass

    def GET(self):
        return status.Forbbiden

    def POST(self):
        return status.Forbbiden 

class Route:
    def __init__(self,path : str,view : View,**kwargs : bool):
        self.path = path
        self.view = view
        self.cases = {
            'GET' : self.view.GET,
            'POST' : self.view.POST
        }
        useRegex = kwargs.get('useRegex')
    
    def callView(self,request):
        return self.cases.get(request['method'].upper())(request)

