def ReceiveData(inputData):
    byteArray =  inputData
    datalength = byteArray[1] & 127
    indexFirstMask = 2
    if datalength == 126:
        indexFirstMask = 4
    elif datalength == 127:
        indexFirstMask = 10
    masks = [m for m in byteArray[indexFirstMask : indexFirstMask+4]]
    indexFirstDataByte = indexFirstMask + 4
    decodedChars = []
    i : int = indexFirstDataByte
    j : int = 0
    while i < len(byteArray):
        decodedChars.append( chr(byteArray[i] ^ masks[j % 4]) )
        i += 1
        j += 1
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
