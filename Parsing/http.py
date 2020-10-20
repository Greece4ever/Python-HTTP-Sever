from urllib.request import unquote
from typing import Union
from math import ceil
import io,json

def lazy_read(file,chunk_size : int = 1024): #Function to lazy read
    while True:
        data = file.read(chunk_size)
        if not data:
            break
        yield data

def decodeURI(expression : Union[str,bytes]) -> str:
    if type(expression) == bytes:
        expression = expression.decode()
    return unquote(expression.replace("+",' ')).strip()

def ParseHeaders(headers : bytes) -> dict:
    y = headers.split(b'\r\n')
    TMP_DICT = {}
    TMP_DICT['method'] = unquote(y.pop(0).replace(b"HTTP/1.1",b'').strip().decode())
    method,uri = TMP_DICT['method'].split(" ",1)
    TMP_DICT['type'] = method
    TMP_DICT['uri'] = uri
    for header in y:
        if(not b':' in header): continue
        spl : str = header.split(b':',1)
        key = spl[0].strip().decode()
        value = spl[1].strip().decode()
        if ';' in value:
            TMP_DICT[key] = [unquote(item.strip()) for item in value.split(';')]
            continue
        TMP_DICT[key] = value
    return TMP_DICT

def ParseFileContent(i):
    if b':' in i:
        spl : list = i.split(b':')
        return spl[0].strip(),spl[1].strip()

    elif b'=' in i:
        spl : list = i.split(b'=')
        return  spl[0].strip(),spl[1].strip()

def ParseBody(body : bytes,code : int,**kwargs):
    if code == 0:
        FORM_DATA : dict = {}
        data = body.split(b'&')
        for bit in data:
            key,value = bit.split(b'=')
            key : str = decodeURI(key.decode())
            value : str = decodeURI(value.decode())
            FORM_DATA[key] = value
    elif code == 1:
        FORM_DATA : list = {}
        split = kwargs.get('boundary')
        f_data = body.split(b'--' + split)
        f_data.pop(-1)
        for item in f_data:
            if len(item) < 2:
                continue
            attrs = {}
            itm_prs : list = item.split(b'\r\n\r\n',1)
            bl = itm_prs[0].split(b';')
            for i in bl:
                if b'\r\n' in i:
                    i = i.split(b'\r\n')
                    for i_s in i:
                        _ =  ParseFileContent(i_s)
                        if _ is None:
                            continue
                        k,v = [decodeURI(attr.replace(b'"',b'').replace(b"'",b'')) for attr in _]
                        attrs[k] = v
                    continue
                
                _ = ParseFileContent(i)
                if _ is None:
                    continue
                k,v = [decodeURI(attr.replace(b'"',b'').replace(b"'",b'')) for attr in _]
                attrs[k] = v
            
            if 'filename' in attrs:
                attrs['data'] = io.BytesIO(itm_prs[-1])
            else:

                attrs['data'] = io.StringIO(itm_prs[-1][0:len(itm_prs[-1])-2].decode())
            
             
            if 'name' in attrs:
                FORM_DATA[attrs.pop('name')] = attrs
            else:
                if not 'default' in FORM_DATA:
                    FORM_DATA['default'] = []
                FORM_DATA['default'].append(attrs)

    elif code == 2:
        data = json.loads(body)
        return data

    return FORM_DATA

def ParseHTTP(data : bytes,await_data : callable,**kwargs):
    headers : bytes
    body : bytes
    headers,body = data.split(b'\r\n\r\n',1) # Headers and body
    headers = ParseHeaders(headers)

    if 'Content-Length' in headers:
        lenght : int = int(headers['Content-Length']) # TODO <IS IT REALLY WORTH CATCHING THE EXCEPTION>
        
        if(lenght > kwargs.get("max_size")): # THE CLIENT WANTS TO SEND A SHIT LOAD OF DATA BLOCK HIM
            return 666

        if len(body) < lenght:
            for _ in range(ceil(lenght / 1024)):
                response = await_data()
                body += response

    if 'Content-Type' in headers:
        c_type = headers['Content-Type']
        if type(c_type) == list:
            if('json' in c_type[0]):
                return headers,ParseBody(body,2)
            for value in c_type:
                if 'boundary' in value:
                    boundary : list =  value.split('=')[-1]
                    response : tuple =  headers,ParseBody(body,1,boundary=boundary.encode())
                    return response
        elif c_type == 'application/x-www-form-urlencoded':
            return headers

    return headers,()

def AwaitFullBody(headers : dict,initial_body : bytes,await_data : callable,**kwargs) -> dict:
    ctype,length = [headers.get('Content-Type'),headers.get('Content-Length')] #if they do not provide content-length they may go fuck themselves
    if None in (ctype,length):
        return ''
    code : int
    
    length : int = int(length)
    if(length > kwargs.get("max_size")):
        return 666

    boundary = None    
    if ctype == 'application/x-www-form-urlencoded':
        code = 0
    else:
        if type(ctype) == list:
            if 'json' in  ctype[0]:
                code = 2
            elif 'x-www-form-urlencoded' in ctype[0]:
                code = 0
            else:
                code = 1
                for value in ctype:
                    boundary : Exception = KeyError
                    for value in ctype:
                        if 'boundary' in value:
                            boundary : bytes =  value.split('=')[-1].encode()

    in_body_len = len(initial_body)
    if (in_body_len - length) < 0:
        wait_times = ceil((length - in_body_len) / 1024) # TODO
        for _ in range(wait_times):
            response = await_data()
            initial_body += response
    return ParseBody(initial_body,code=code,boundary=boundary)

if __name__ == "__main__":
    pass