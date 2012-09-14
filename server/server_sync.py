import os, sys
import struct
import cons
import trames
import gamemodule
import user

cmd_folder = os.path.dirname(os.path.abspath(__file__))+"/lib"
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

from twisted.internet import protocol, reactor # TCP etc.
from construct import * # Data parsing
from twisted.internet.protocol import Protocol, Factory
from twisted.protocols import stateful

def myhex(i):
    ret="0x"
    if i<=15:
        ret += "0"
    ret += hex(i)[2:].upper()
    return ret

def displayFrame(trame):
    strr=myhex(trame[0])
    if strr=="0x00":
        return "{ END }"

    for data in trame[1]:
        type, val = data
        strr += ", "+type+" "
        if type[0]=='i' or type[1]=='i':
            strr += str(val)
        else:
            if type=='double':
                strr += "%.13f"%val
            else:
                strr += "\""+val+"\""
    return "{ "+strr+" }"

def sendFrame(to, x):
    print "sending frame "+displayFrame(x)
    to.transport.write(cons.constructFrame(x))


class MyProto(stateful.StatefulProtocol):
    def game(self):
        return self.factory.jeux
    

    packet_kinds = {
        '\x01' : ('int8', (1, 'si8received')),
        '\x02' : ('int16',(2, 'si16Received')),
        '\x04' : ('int32',(4, 'si32Received')),
        '\x11' : ('uint8',(1, 'ui8Received')),
        '\x12' : ('uint16',(2, 'ui16Received')),
        '\x14' : ('uint32',(4, 'ui32Received')),
        '\x20' : ('string',(2, 'stringReceivedBis')),
        '\x30' : ('double', (8, 'doubleReceived'))
        }
    

    def getHex(stringname):
        for f in types.keys():
            if types[f][0]==stringname:
                return f

    def getName(hexcode):
        return types[hexcode][0]

    def isConnected(self):
       try : 
            self.factory.connectedUsers.index(self)
            return True
       except ValueError:
           return False

    #def connectionLost(self, reason):
    #    self.game().removeUser(
    # TODO : remove user From self.game().usersList
   
    def getInitialState(self):
        return self.frameStartReceived, 1

    def frameStartReceived(self, data):
        self.ffstart = struct.unpack('!B', data)[0]
        if self.ffstart==0x00:
            self.frame = [0x00]
            self.frameReceived()
        else: # 0xff
            return self.frameHeaderReceived, 2
    
    def frameHeaderReceived(self, data):
        self.frameid, self.packets = struct.unpack('!BB', data)
        self.data = ""
        self.frame = [self.frameid, []]
        return self.dataHeaderReceived, 1

    def dataHeaderReceived(self, data):
        size, method = self.packet_kinds[data][1]
        return getattr(self, method), size    
    
    # unsigned int 8
    def ui8Received(self, data):
        n = struct.unpack('!B', data)[0]
        self.frame[1].append(("uint8", n))
        return self._nextState()
    
    # unsigned int 16
    def ui16Received(self, data):
        n = struct.unpack('!H', data)[0]
        self.frame[1].append(("uint16", n))
        return self._nextState()
    
    # unsigned int 32
    def ui32Received(self, data):
        n = struct.unpack('!I', data)[0]
        self.frame[1].append(("uint32", n))
        return self._nextState()

    # signed int 8
    def si8Received(self, data):
        n = struct.unpack('!b', data)[0]
        self.frame[1].append(("int8", n))
        return self._nextState()

    # signed int 16
    def si16Received(self, data):
        n = struct.unpack('!h', data)[0]
        self.frame[1].append(("int16", n))
        return self._nextState()

    # signed int 32
    def si32Received(self, data):
        n = struct.unpack('!i', data)[0]
        self.frame[1].append(("int32", n))
        return self._nextState()


    def stringReceivedBis(self, data):
        self.strLen = struct.unpack('!H', data)[0]
        return self.stringReceived, self.strLen
    
    def stringReceived(self, data):
        receivedString = struct.unpack(str(self.strLen)+"s", data)[0]
        self.frame[1].append(("string", receivedString))
        return self._nextState()
    
    def doubleReceived(self, data):
        doubleReceived = struct.unpack('!d', data)[0]
        self.frame[1].append(("double", doubleReceived))
        return self._nextState()

    def _nextState(self):
        self.packets -= 1
        if self.packets:
            return self.dataHeaderReceived, 1
        else:
            self.frameReceived(self.ffstart, self.frameid, self.data)
            self.ffstart, self.frameid, self.data = None, None, None
            return self.frameStartReceived, 1
        # Got all the data packets. Receive another frame? drop
        # the connection? I don't know...
        # return self.frameHeaderReceived, 3
        

    def recIFrame(self, frame):
        if trames.areFramesEqual(frame, trames.TRAME_VERSION_DEMANDE):
            print "Good version"
            sendFrame(self, trames.TRAME_VERSION_POS)
        else:
            print "Not good version"
            sendFrame(self, trames.TRAME_VERSION_NEG)

    def recCFrame(self, frame):
        print "registering players"
        if not self.game().placeLeft():
            sendFrame(self, [0x43, [("string", "NO"), ("string", "No more place!")]])
        else:
            self.user = self.game().registerNewPlayer(self, frame)
            myid = self.user.getId()
            self.user.send([0x43, [("string", "OK"), ("uint16", myid)]])
            if myid == int(sys.argv[2])-1:
                self.game().prepare()
                self.game().countDown(3)
                self.game().start()
    
    def recOFrame(self, frame):
        order = trames.getData(frame, 0)
        old_direction = self.user.getDirection()
        
        if not order=="idle":
            if (old_direction==1 and order=="left") or (old_direction==2 and order=="right"):
                new_direction=3
            if (old_direction==1 and order=="right") or (old_direction==2 and order=="left"):
                new_direction=4
            if (old_direction==3 and order=="left") or (old_direction==4 and order=="right"):
                new_direction=2
            if (old_direction==3 and order=="right") or (old_direction==4 and order=="left"):
                new_direction=1
            self.user.setDirection(new_direction)

    def frameReceived(self, ffstart, frameid, data):
        print displayFrame(self.frame)
       
        ids = {
            0x43:self.recCFrame,
            0x49:self.recIFrame,
            0x4F:self.recOFrame,
            }
        try:
            ids[frameid](self.frame)
        except KeyError:
            print "Error"
            print "Received frame:"
            print self.frame
            print "id = "+str(frameid)

class MyProtoFactory(Factory):
    protocol = MyProto
    connectedUsers = []
    jeux = gamemodule.Game(int(sys.argv[2])) # maxplayers

    # TODO:
    # for each user : 
    # id : 
    # colors : [R, G, B]
    # pos, x, y, speed, etc.

factory = MyProtoFactory()
reactor.listenTCP(5555, factory)
reactor.run()
