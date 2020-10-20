"""
Module for automation/script creation inside  HTML files
When Rendered inside a view, using the template function
if an additional parameter 'usePythonScript' is True
functions inside of here will 'compile' the scripts
"""

import re
from typing import Tuple
from ..server.server import lazy_read


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

    def replace_str_index(text,index=0,replacement=''):
        return '%s%s%s'%(text[:index],replacement,text[index+1:])

    REGXP = r'\((\s+)?<\w+(.*?)>(.*?)</\w+>(\s+)?\)'

    def eval_script(data):
        html : list = []
        start = data.index('<?python')
        print(data[:start])
        end = data.index('?endpython>') + len("?endpython>")
        point_of_interest = data[start+len("<?python"):end-len("?endpython>")]
        point_of_interest = "if 1:" + point_of_interest # \(<\w+>(.*?)</\w+>\)

        for item in (re.finditer(REGXP,point_of_interest,flags=re.DOTALL)):  # r'\(<\w+>(.*?)</\w+>\)'
            match = item.group()
            point_of_interest = point_of_interest.replace(match,r'html.append(f"""' + replace_str_index(replace_str_index(match),len(match)-2) + r'""")')

        exec(point_of_interest)
        print("\n".join(html))
        print(data[end:])
    

    def script_in_chunks(file, buffer_size : int = 1024):
        prev = StringIO()

        def find_script(buff_chunk,check_buffer : bool = True):
            try:
                start = buff_chunk.index('<?python')
                try:
                    end = buff_chunk.index("?endpython>")
                    return [buff_chunk[:start],eval_script(buff_chunk[start:end]),buff_chunk[end:]]
                except:
                    return [buff_chunk[:start],buff_chunk[start:]]
            except:
                return buff_chunk

    
        with open(file) as f:
            for chunk in lazy_read(f,buffer_size):
                _buffer : StringIO = StringIO()
                pars = find_script(chunk)
                if(len(pars)==2):
                    print(pars[0])
                    _buffer.write(pars[1])
                elif(len(pars)==3):
                    print(pars[0])
                    print(pars[1])
                    pass
