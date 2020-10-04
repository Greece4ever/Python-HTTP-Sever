from datetime import datetime

def ffs(x):
    return (x&-x).bit_length()-1

def binraw(trm : bin):
    return str(bin(trm)).replace('0b','') 

def ReceiveData(inputData):
    byteArray =  inputData
    datalength = byteArray[1] & 127
    indexFirstMask = 2
    if datalength == 126:
        indexFirstMask = 4
    elif datalength == 127:
        indexFirstMask = 10
    masks = [m for m in byteArray[indexFirstMask : indexFirstMask+4]]
    indexFirstDataByte = indexFirstMask + 4;decodedChars = []
    i : int = indexFirstDataByte;j : int = 0
    while i < len(byteArray):
        decodedChars.append( chr(byteArray[i] ^ masks[j % 4]) )
        i += 1;j += 1
    return ''.join(decodedChars)


def SendData(data):
    bytesFormatted = []
    bytesFormatted.append(129) 

    bytesRaw = data.encode()
    bytesLength = len(bytesRaw)
    if bytesLength <= 125 :
        bytesFormatted.append(bytesLength)
    elif 65535 >= bytesLength >= 126:
        bytesFormatted.append(126)
        bytesFormatted.append( ( bytesLength >> 8 ) & 255 )
        bytesFormatted.append( bytesLength & 255 )
    else :
        bytesFormatted.append( 127 )
        bytesFormatted.append( ( bytesLength >> 56 ) & 255 )
        bytesFormatted.append( ( bytesLength >> 48 ) & 255 )
        bytesFormatted.append( ( bytesLength >> 40 ) & 255 )
        bytesFormatted.append( ( bytesLength >> 32 ) & 255 )
        bytesFormatted.append( ( bytesLength >> 24 ) & 255 )
        bytesFormatted.append( ( bytesLength >> 16 ) & 255 )
        bytesFormatted.append( ( bytesLength >>  8 ) & 255 )
        bytesFormatted.append( bytesLength & 255 )

    bytesFormatted = bytes(bytesFormatted)
    bytesFormatted = bytesFormatted + bytesRaw
    return bytesFormatted

def AwaitSocketData(fin : int,data : bytearray,await_data : callable,max_size : int,**kwargs) -> str:
    prnt = kwargs.get("prnt_func")
    if fin == 126:
        payload : int = int.from_bytes([data[2],data[3]],'big')
        prnt(payload)
        loop_times : int = int(payload / max_size) # NOTE L1:
        for _ in range(loop_times):
            data += await_data()
        decoded = ReceiveData(data)

    else: #127
        payload : int = int.from_bytes(data[2:10],'big')
        prnt(payload)
        loop_times : int = int(payload / max_size) #NOTE L1:
        for _ in range(loop_times):
            data += await_data()
        decoded = ReceiveData(data)
    
    return decoded

def EnsureSocket(headers,s_data : tuple) -> None:
    client,address = s_data
    if 'Upgrade' in headers:
        if headers['Upgrade'].lower()=='websocket':
            print(f'(WS) : {headers["method"]} | {str(datetime.now())} : {address}')
        else:
            print(f'(WS) : {headers["method"]} | {str(datetime.now())} : Invalid WS Response {address}')
            return client.close()
    else:
        print(f'(WS) : {headers["method"]} | {str(datetime.now())} : Invalid WS Response {address}')
        return client.close()


if __name__ == "__main__":
    pass