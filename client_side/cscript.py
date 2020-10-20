import re
from typing import Tuple

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
        def find_script(buff_chunk,check_buffer : bool = True):
            try:
                start = buff_chunk.index('<?python')
                try:
                    end = buff_chunk.index("?endpython>")
                    return [buff_chunk[:start],eval_script(buff_chunk[start:end]),buff_chunk[end:]]
                except:
                    return [buff_chunk[:start],buff_chunk[start:]]
            except:
                return [buff_chunk]

    
        with open(file) as f:
            state : bool = False
            _buffer : StringIO = StringIO()
            _script : StringIO = StringIO()
            for chunk in lazy_read(f,buffer_size):
                # Only start is found
                if(state):
                    try:
                        indx = chunk.index("?endpython>")
                        _script.write(chunk[:indx]);state = False
                        print(chunk[indx:])
                        eval_script(_script.getvalue())
                    except:
                        _script.write(chunk)
                        try:
                            data = _script.getvalue()
                            indx = data.index("?endpython>")
                            print(data[indx:])
                            eval_script(data)
                        except:
                            continue
                    finally:
                        continue
                pars = find_script(chunk)
                if(len(pars)==2): # only start
                    print(pars[0])
                    _buffer.write(pars[0][-10:])
                    _script.write(pars[1])
                    state = True
                elif(len(pars)==3): # all is found
                    print(pars[0])
                    print(pars[1])
                    pass
                else:
                    _buffer.write(chunk)
                    find_script(_buffer)
