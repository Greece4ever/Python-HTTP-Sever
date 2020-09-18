import re
from routes import template

def popAll(item):
    item.pop(0)
    item.pop(1)
    item.pop(-1)
    item.pop(-2)

def parseVariables(file):
    objs = re.findall(r'\$\$(\w+)\$\$',file)
    return objs

def parseCode(file,context):
    objs = re.findall(r'@@(.*)@@',file)
    for item in objs:
        item = item.strip()
        if item.startswith('for'):
            variables = parseVariables(item)
            for var in variables:
                item = item.replace(var,str(context.get(var)))
            print(item)

context = {'static' : [1,2,3,4,5]}

tem = template("Examples/index.html")
print(parseCode(tem,context))


