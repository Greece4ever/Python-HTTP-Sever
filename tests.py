import json

with open("statuses.json",encoding="utf-8") as f:
    data = json.loads(f.read())


for status_code in data:
    code = status_code['code']
    phrase = status_code['phrase']
    cly = rf"""
    class Http{code}(Exception):
        @classmethod
        def __call__(self,template):
            return (b"HTTP/1.1 {code} {phrase}\n"
                    +b"Content-Type: text/html\n"
                    +b"\n" 
                    +template.encode())    
    """
    with open("status.py",mode='a',encoding='utf-8') as h:
        h.write("\n" + cly)

