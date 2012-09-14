import trames
import cons

class User:
    def __init__(self, protocol, uid, nickname, red, green, blue, x0, y0, direction, speed):
        self.protocol = protocol
        self.uid = uid
        self.nickname = nickname
        self.red = red
        self.green = green
        self.blue = blue
        self.x0 = x0
        self.y0 = y0
        self.direction = direction
        self.speed = speed
        self.alive = True

    def send(self, frame):
        self.protocol.transport.write(cons.constructFrame(frame))
    
    def getId(self):
        return self.uid

    def getProtocol(self):
        return self.protocol

    def getNickname(self):
        return self.nickname

    def getColor(self):
        return (self.red, self.green, self.blue)
    
    def getPosition(self):
        return (self.x0, self.y0)

    def getDirection(self):
        return self.direction

    def getSpeed(self):
        return self.speed
    
    def setDirection(self, i):
        self.direction = i
    
    def updatePosition(self):
        if self.direction == 1:
            dx = -self.speed
            dy = 0

        if self.direction == 2:
            dx = self.speed
            dy = 0

        if self.direction == 3:
            dx = 0 
            dy = -self.speed
    
        if self.direction == 4:
            dx = 0
            dy = self.speed
        positionx, positiony = self.getPosition()
        return (positionx+dx, positiony+dy)
    
    def setPosition(self, x, y):
        self.x0=x
        self.y0=y
        
    def die(self):
        self.alive = False

    def isAlive(self):
        return self.alive
