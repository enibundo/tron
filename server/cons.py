import struct
    

def constructInt8(data):
    d = "\x01"
    d += struct.pack('!b', data)
    return d

def constructInt16(data):
    d = "\x02"
    d += struct.pack('!h', data)
    return d

def constructInt32(data):
    d = "\x04"
    d += struct.pack('!i', data)
    return d

def constructUInt8(data):
    d = "\x11"
    d += struct.pack('!B', data)
    return d

def constructUInt16(data):
    d = "\x12"
    d += struct.pack('!H', data)
    return d

def constructUInt32(data):
    d = "\x14"
    d += struct.pack('!I', data)
    return d

def constructString(data):
    d = "\x20"
    d += struct.pack('!H', len(data))
    d += struct.pack('!'+str(len(data))+'s', data)
    return d

def constructDouble(data):
    d = "\x30"
    d += struct.pack('!d', data)
    return d

dispatch = {
    'int8'   : constructInt8,
    'int16'  : constructInt16,
    'int32'  : constructInt32,
    'uint8'  : constructUInt8,
    'uint16' : constructUInt16,
    'uint32' : constructUInt32,
    'string' : constructString,
    'double' : constructDouble
    }

def constructFrame(frame):
    d = '\xFF'
    d += struct.pack('!B', frame[0]) # id
    d += struct.pack('!B', (len(frame[1]))) # n
    datas = frame[1]

    for data in datas:
        theType = data[0]
        theVal = data[1]
        d += dispatch[theType](theVal)
    return d






