import re
from routes import template

def popAll(item):
    item.pop(0)
    item.pop(1)
    item.pop(-1)
    item.pop(-2)

def insert(string : str,index : str,ins_val : str) -> str:
    return string[:index] + ins_val + string[index:]

def parseVariables(html,content):
    objs = re.findall(r'\$\$(\w+)\$\$',html)
    for item in objs:
        html = html.replace(f"$${item}$$",str(content.get(item)))
    return html

def parseHTML(html):
    res = html.replace('html(',r'code = f"""').replace(")endhtml",'"""\n\tINDEX.append(code)')
    return res

def parseCode(html,context):
    PV = parseVariables(html,context)
    PH = parseHTML(PV)
    return PH.replace("<?python",'').replace("?>",'')
    
def findScript(html):
    STATEMENTS : list = []
    while True:
        try:
            indx1 = html.index("<?python")
            indx2 = html.index("?>")
            statement = html[indx1:indx2+2]
            html = html.replace(statement,'')
            insert(html,indx1,"HELLO!!!")
            STATEMENTS.append(statement)
        except Exception as e:
            break
    
    return STATEMENTS

context = {'context' : {"name" : 'pakis','tags' : 'peos'}}

tem = template("Examples/index.html")
x = (parseCode("""
<?python
    for item in $$context$$:
        html(<div id='msg_box' style="width: 500px;height: 500px;">
            <textarea id='text' placeholder="Type Message">
                <button id='btn'>{item}</button>
            </textarea>
        </div>)endhtml
?>      
""",context))

# statement = "if True:" + x
# print(statement)
with open("Examples/test.html") as f:
    data = f.read()

dt = findScript(data)
for item in dt:
    print(item)
# exec(statement)
# print(code)