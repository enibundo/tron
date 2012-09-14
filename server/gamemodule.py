import os, sys
import user
import time
import trames
cmd_folder = os.path.dirname(os.path.abspath(__file__))+"/lib"
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)
from twisted.internet import protocol, reactor # TCP etc.


def make_list(size):
    mylist=[]
    for i in range(size):
        mylist.append(0)
    return mylist

def make_matrix(rows, cols):
    matrix = []
    for i in range(rows):
        matrix.append(make_list(cols))
    return matrix

class Game:
    def __init__(self, maxPlayers):
        self.maxPlayers=maxPlayers
        self.players = []
        self.stillPlaying=True
        self.playersInGame = maxPlayers
        self.matrix = make_matrix(1000, 1000)

        
    def registerNewPlayer(self, protocol, frame):
        red = trames.getData(frame, 0)
        green = trames.getData(frame, 1)
        blue = trames.getData(frame, 2)
        nickname = trames.getData(frame, 3)
        
        myid = self.nextId()

        if myid==0:
            posx, posy, d = (100, 100, 4) # a droite
        if myid==1:
            posx, posy, d = (900, 100, 1)
        if myid==2:
            posx, posy, d = (100, 900, 2)
        if myid==3:
            posx, posy, d = (900, 900, 3)
        newPlayer= user.User(protocol, myid, nickname, red, green, blue, posx, posy, d, 1) 
        self.addPlayer(newPlayer)
        return newPlayer
    
    def addPlayer(self, player):
        self.players.append(player)
        
    def placeLeft(self):
        return (len(self.players) < self.maxPlayers)

    def nextId(self):
        return len(self.players)

    def getUsers(self):
        return self.players
    
    def getUser(self, i):
        return self.players[i]

    def prepare(self):
        for user_r in self.players:
            for userp in self.players:
                uid = userp.getId()
                nickname = userp.getNickname()
                red, green, blue = userp.getColor()
                posx, posy = userp.getPosition()
                d = userp.getDirection()
                s = userp.getSpeed()
                print "sending Information to "+str(uid)
                frame=[0x55, [("uint16", uid),
                              ("string", nickname),
                              ("uint8", red), # R
                              ("uint8", green), # G
                              ("uint8", blue), # B
                              ("uint16", posx), # x0
                              ("uint16", posy),
                              ("uint8", d),
                              ("uint8", s)]]
                user_r.send(frame)
            user_r.send(trames.TRAME_END)
    
    
    def countDown(self, i):
        if i > 0:
            for player in self.players:
                player.send([0x50, [("string", str(i))]])
            reactor.callLater(1, self.countDown, i-1)

    def start(self):
         for player in self.players:
            player.send([0x53, [("string", "START")]])
         cnt=0
         self.gameLoop()
             
    def gameLoop(self):
        if self.stillPlaying:
            self.instant()
            reactor.callLater(0.035, self.gameLoop)
        else:
            self.sendWinner()
            
    def sendWinner(self):
        winId = None

        for p in self.players:
            if p.isAlive():
                winId = p.getId()

        if winId <> None:
            for p in self.players:
                p.send([0x57, [("uint16", winId)]])

    def getUser(self, protocol):
        for player in self.players:
            if player.getProtocol()==protocol:
                return player
        return None
    
    def instant(self):
        for player in self.players:

            posx, posy = player.updatePosition()

            if posx>=0 and posx<1000 and posy>=0 and posy<1000 and self.matrix[posx][posy]==0:
                player.setPosition(posx, posy)
                self.matrix[posx][posy]=1
            else:
                if player.isAlive():
                    player.die()
                    self.playersInGame = self.playersInGame -1
                    
                if self.playersInGame == 1:
                    self.stillPlaying=False

                # death frame
                pid = player.getId()
                f = [0x44, [("uint16", pid)]]
                
                for p1 in self.players:
                    p1.send(f)

        for p1 in self.players:
            k=[("uint32", 2)]
            for p2 in self.players:
                i = p2.getId()
                x, y = p2.getPosition()
                d = p2.getDirection()
                #print "id:"+str(i)+" pos:"+str(x)+", "+str(y)
                k.append( ("uint16", i))
                k.append( ("uint16", x))
                k.append( ("uint16", y))
                k.append( ("uint16", d))
            p1.send([0x54, k])
                

            
