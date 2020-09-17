import re
from routes import template

def parseStatic(file):
    objs = re.findall(r'$$(\w+)$$',file)
    return objs

tem = template("Examples/index.html")
print(parseStatic(tem))


