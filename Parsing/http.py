from urllib.request import unquote;from typing import Union
from math import ceil

def decodeURI(expression : Union[str,bytes]) -> str:
    if type(expression) == bytes:
        expression = expression.decode()
    # expression = expression.replace('"','').replace("'",'')
    return unquote(expression.replace("+",' ')).strip()


def ParseHeaders(headers : bytes) -> dict:
    y = headers.split(b'\r\n')
    TMP_DICT = {}
    TMP_DICT['method'] = unquote(y.pop(0).replace(b"HTTP/1.1",b'').strip().decode())
    for header in y:
        spl : str = header.split(b':',1)
        key = spl[0].strip().decode()
        value = spl[1].strip().decode()
        if ';' in value:
            TMP_DICT[key] = [unquote(item.strip()) for item in value.split(';')]
            continue
        TMP_DICT[key] = value
    return TMP_DICT


def ParseBody(body : bytes,code : int,**kwargs):
    FORM_DATA : dict = {}
    if code == 0:
        data = body.split(b'&')
        for bit in data:
            key,value = bit.split(b'=')
            key : str = decodeURI(key.decode())
            value : str = decodeURI(value.decode())
            FORM_DATA[key] = value
    else:
        split = kwargs.get('boundary')
        f_data = body.split(b'--' + split)
        for item in f_data:
            print(item.split(b'\r\n\r\n',1))
            # print(item.decode(errors='ignore'))

        # print(body,end='\n\n')
        # print(body.decode(errors='ignore'))

    return FORM_DATA

def ParseHTTP(data : bytes,await_data : callable):
    headers : bytes
    body : bytes
    # print(data.split(b'\r\n\r\n'))
    headers,body = data.split(b'\r\n\r\n',1) # Headers and body
    headers = ParseHeaders(headers)

    if __name__ != "__main__":
        if 'Content-Length' in headers:
            lenght : int = headers['Content-Length']
            if lenght > 1024:
                for _ in range(ceil(crem / 1024)):
                    response = await_data()
                    body += response

    if 'Content-Type' in headers:
        c_type = headers['Content-Type']
        if type(c_type) == list:
            for value in c_type:
                if 'boundary' in value:
                    boundary =  value.split('=')[-1]
                    body = ParseBody(body,1,boundary=boundary.encode())
        elif 'application/x-www-form-urlencoded':
            body = ParseBody(body,0)
            print(body)

    return headers


if __name__ == "__main__":
    import pprint
    s1 = b'GET /images/1 HTTP/1.1\r\nHost: localhost\r\nConnection: keep-alive\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 OPR/71.0.3770.175\r\nAccept-Encoding: identity;q=1, *;q=0\r\nAccept: */*\r\nSec-Fetch-Site: same-origin\r\nSec-Fetch-Mode: no-cors\r\nSec-Fetch-Dest: video\r\nReferer: http://localhost/post\r\nAccept-Language: en-US,en;q=0.9\r\nRange: bytes=0-\r\n\r\n'    
    s2 = b'POST /post HTTP/1.1\r\nHost: localhost\r\nConnection: keep-alive\r\nContent-Length: 235\r\nCache-Control: max-age=0\r\nUpgrade-Insecure-Requests: 1\r\nOrigin: http://localhost\r\nContent-Type: multipart/form-data; boundary=----WebKitFormBoundary0o8bArs2PkoBamqj\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 OPR/71.0.3770.175\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\nSec-Fetch-Site: same-origin\r\nSec-Fetch-Mode: navigate\r\nSec-Fetch-User: ?1\r\nSec-Fetch-Dest: document\r\nReferer: http://localhost/post\r\nAccept-Encoding: gzip, deflate, br\r\nAccept-Language: en-US,en;q=0.9\r\n\r\n------WebKitFormBoundary0o8bArs2PkoBamqj\r\nContent-Disposition: form-data; name="ena"\r\n\r\n321321\r\n------WebKitFormBoundary0o8bArs2PkoBamqj\r\nContent-Disposition: form-data; name="dio"\r\n\r\n321\r\n\r\n------WebKitFormBoundary0o8bArs2PkoBamqj--\r\n'
    s3 = b'POST /post HTTP/1.1\r\nHost: localhost\r\nConnection: keep-alive\r\nContent-Length: 304\r\nCache-Control: max-age=0\r\nUpgrade-Insecure-Requests: 1\r\nOrigin: http://localhost\r\nContent-Type: multipart/form-data; boundary=----WebKitFormBoundaryh3DxaqIJ7GjcSgPY\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 OPR/71.0.3770.175\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\nSec-Fetch-Site: same-origin\r\nSec-Fetch-Mode: navigate\r\nSec-Fetch-User: ?1\r\nSec-Fetch-Dest: document\r\nReferer: http://localhost/post\r\nAccept-Encoding: gzip, deflate, br\r\nAccept-Language: en-US,en;q=0.9\r\n\r\n------WebKitFormBoundaryh3DxaqIJ7GjcSgPY\r\nContent-Disposition: form-data; name="ena"\r\n\r\n<script>hello_world</script>\r\n------WebKitFormBoundaryh3DxaqIJ7GjcSgPY\r\nContent-Disposition: form-data; name="dio"\r\n\r\n>>> a = "hi"\r\n>>> bytes(a, encoding=\'utf8\')\r\nb\'hi\'\r\n\r\n------WebKitFormBoundary0o8bArs2PkoBamqj--'
    pprint.pprint(ParseHTTP(s2,''))