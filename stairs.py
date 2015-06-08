from pointfunctions import pointDist

class Stair:
    def __init__(self, pos, w, h):
        self.x, self.y = pos
        self.r = 2
            
        self.w = w
        self.h = h
        
    def getStart(self):
        """Returns the position of the left-most part of the stairs ("start")"""
        return (self.x, self.y)
        
    def getStop(self):
        """Returns the position of the right-most part of the stairs ("end")"""
        return (self.x+self.w, self.y+self.h)
        
    def getPosFromSteps(self, steps):
        """Takes a position and number of steps taken on stair and returns
        a new position
        """
        x = self.x + steps
        y = self.y + ((steps*1.0)/abs(self.w))*self.h
        return (x,y)
        
    def isCloseEnoughStart(self, pos):
        """Returns true if a certain position is close enough to the start
        of the stair"""
        if pointDist(self.getStart(), pos) < self.r:
            return True
        return False
        
    def isCloseEnoughStop(self, pos):
        """Returns true if a certain position is close enough to the stop
        of the stair"""
        if pointDist(self.getStop(), pos) < self.r:
            return True
        return False