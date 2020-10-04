A vary simple, yet **convinient** module with no external dependencies that can be used to hande **HTTP** requests as well as more complex connections such as **Websockets**.

The way to define **http** methods is by inheriting from the base class `View` and redefining the method that are going to be used.

```python
class Home(View):
    def GET(self,request,**kwargs):
        return status.Http200().__call__("<h1>Home Page</h1>") #200 Response
    
    def POST(self,request,**kwargs):
        return status.HttpJson().__call__({"error" : "not found"},404) #JSON 404
    
    def HEAD(self,request,**kwargs):
        path_to_img : str = os.path.join(os.getcwd(),'my_img.png')
        #If it can, the browser will display the file there
        return status.HttpBinary().__call__(path_to_img,200,display_in_browser=True) 
    
    def PUT(self,request,**kwargs):
        return status.Redirect().__call__('https://github.com') #Redirect

    def __init__(self,**kwargs):
        #You can add any HTTP method that may not be called
        #By overriding the __init__ method and 
        #Inserting the HTTP method name and the function
        #that should be called when a request is made
        super(Home,self).__init__(**kwargs)
        self.cases['PUT'] = self.PUT
```

and then to register the view you must put the valid **URL**s into a dictionary using  **Regex** to describe the **URL path** and for the value the View that was defined earlier

```
URLS = {
    r"/home(\/)?" : Home(),
}

CORS_DOMAINS=['http://127.0.0.1:5500','http://127.0.0.1:8000','http://google.com']
HttpServer(URLS=URLS,CORS_DOMAINS=CORS_DOMAINS,port=80).start() #
```

This will start the **HTTP** Server on port 80 with the values in `CORS_DOMAINS` being suitable for Cross Origin requests (**X-FRAMES** not included).

