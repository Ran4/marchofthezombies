import math

class Bullet:
    def __init__(self, pos=(0,0), dirVect=(0,0), type="standard"):
        """Creates a bullet. Arguments are optional. Takes:
        a position tuple (default (0,0))
        a tuple representing a direction vector (magnitude is of no importance)
            (default (0,0), thus the bullet won't move)
        a type, defaults "standard" but can also be "record"
        """
        self.x, self.y = pos
        self.setType(type)
        self.vec = self.normalizeVect(dirVect, self.spd)
        self.remove = False #flag that is set true when bullet should be removed
        
    def normalizeVect(self, vec, scale=1):
        """takes a tuple representing a 2d vector and normalizes it
        Optional argument: will also scale vector to a certain length
        """
        vectorLength = math.sqrt(vec[0]**2 + vec[1]**2)
        
        if vectorLength != 0 and scale != 0: #can't divide by zero
            return (vec[0]/(vectorLength/scale), vec[1]/(vectorLength/scale))
        return (0,0)
        
    def setType(self, type):
        self.sprname = type+"bullet" #example: "standardbullet" or "recordbullet"
        self.type = type
        
        #determines bullet radius, half the image width/height, speed, damage
        if type == "standard":
            self.r = 1
            self.hw = 1
            self.hh = 1
            self.spd = 4
            self.lowDamage = 11
            self.midDamage = 18
            self.highDamage = 27
        elif type == "record":
            self.r = 9
            self.hw = 4
            self.hh = 7
            self.spd = 3.5#3
            self.lowDamage = 39
            self.midDamage = 70
            self.highDamage = 105
        else:
            print "ERROR: Couldn't find bullet type",type
            exit()
        
    def pos(self):
        return (self.x, self.y)
        
    def drawPos(self): #returns position adjusted for drawing
        return (self.x-self.hw, self.y-self.hh)
        
if __name__ == "__main__":
    b = Bullet()
    print (3,4)
    print b.normalizeVect((3,4))