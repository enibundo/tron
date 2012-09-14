"""
Une Trame = Frame (T)

le_type sera un de ces types : 
-int8
-int16
-int32
-uint8
-uint16
-uint32
-double
-string

"""

TRAME_VERSION_DEMANDE = [0x49, [('string', 'PC2RON?'), ('string', 'PC2RON2011')]]
TRAME_VERSION_POS = [0x41, [('string', 'OK'), ('string', 'PC2RON2011')]]
TRAME_VERSION_NEG = [0x41, [('string', 'NO'), ('string', 'PC2RON2011')]]
TRAME_END = [0x45, []]

def areFramesEqual(frame1, frame2):
    return frame1==frame2

def isThisFrame(frame, obj):
    """
    obj is : [id, [(type1, val1), (type2, val2)]]
    """
    theId = obj[0]
    datas = obj[1]
    length = len(datas)
    cnt = 0
    for data in datas:
        theType = data[0]
        theVal = data[1]
        return (len(frame['data'])==length 
                and frame['data'][cnt]['type'] == theType
                and frame['data'][cnt]['val'] == theVal)

def isOfTheForm(frame, obj):
    cnt=0
    for d in frame[1]:
        if (d[0] <> obj[cnt]):
            return False
        cnt += 1
    return True

def getFrameLength(frame):
    return len(frame[1])

# raises IndexError if i bigger than data-length
def getData(frame, i):
    if len(frame[1]) <= i:
        raise IndexError
    return frame[1][i][1]

def getId(frame):
    return frame[0]

# DATA FUNCTIONS
def getType(data):
    return data[0]

def getValue(data):
    return data[1]
        
