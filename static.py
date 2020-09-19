"""
FOR HANDLING PYTHON SCRIPTS IN HTMLS PAGES
TO DECLARE A SCRIPT INSIDE A PAGE USE:

SAMPLE HTML FILE:

<?python
    for num in range(20):
        html(
            <div>
                <label>This is the {num}{"th" if bool(num > 3 or num ==0) else "st" if num == 1 else "nd" if num ==2 else "rd"} Number
                <b>{ num } </b>
            </div>
        )endhtml
?>
"""
import re
import os
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
            # print(cl,end="\n\n")
            exec(cl)
            html = html.replace(statement,"\n".join(INDEX))
            STATEMENTS.append(statement)
        except Exception as f:
            if type(f) == ValueError:
                break
            raise f    
    return html