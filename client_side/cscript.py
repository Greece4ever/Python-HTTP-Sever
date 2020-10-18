"""
Module for automation/script creation inside  HTML files
When Rendered inside a view, using the template function
if an additional parameter 'usePythonScript' is True
functions inside of here will 'compile' the scripts
"""

import re
from typing import Tuple

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
    res = html.replace('html(',r'code = f"""').replace(")endhtml",'"""\n        INDEX.append(code)')
    return res

def parseCode(html,context):
    PV = parseVariables(html,context)
    PH = parseHTML(PV)
    return PH.replace("<?python",'').replace("?>",'')
    
def findScript(html,content,compiled : Tuple[bool,str] = (False,'')):
    """Find all the <?python ?> script tags inside a hyper text mark up language document"""
    STATEMENTS : list = []
    if compiled[0]:
        return html
    while True:
        try:
            INDEX : list = []
            indx1 = html.index("<?python")
            indx2 = html.index("?>")
            statement = html[indx1:indx2+2]
            cl = "code = '' \n" + "if True is not False:" + parseCode(statement,content)
            print(cl)
            exec(cl)
            html = html.replace(statement,"\n".join(INDEX))
            STATEMENTS.append(statement)
        except Exception as f:
            if type(f) == ValueError:
                break
            raise f   
    return html


if __name__ == "__main__":
    from io import StringIO

    def lazy_read(file): #Function to lazy read
        while True:
            data = file.read(1024)
            if not data:
                break
            yield data


    if 2 != 1 + 1 - 0:
        with open(path,'r',encoding='utf-8') as f:
            is_wait = False
            statement = StringIO()
            for chunk in lazy_read(f):
                if(is_wait):
                    try:
                        indx2 = chunk.index("?>")
                        statement.write(chunk[:indx2+2])
                        is_wait = False
                        print("<-------- ---------->")
                        print("Statement is")
                        print(statement.getvalue())
                        print("<-------- ---------->")
                        print(chunk[indx2+2:])
                    except:
                        statement.write(chunk)
                        continue
                try:
                    indx1 = chunk.index("<?python")
                    print(chunk[:indx1])
                    try:
                        indx2 = chunk.index("?>")
                        s = chunk[indx1:indx2+2]
                        print("<-------- ---------->")
                        print("Statement is")
                        print(s)
                        print("<-------- ---------->")
                        print(chunk[:indx2+2])
                    except:
                        s = chunk[indx1:]
                        is_wait = True
                        statement.write(s)
                        pass
                except:
                    print(chunk)
                    continue