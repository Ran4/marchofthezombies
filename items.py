import random

allItemNames = [ #list of all types of items
    "ammo",
    "records",
    "bandaid",
    "healthkit",
    "beartrap"
]

commonItemList = [ #list of common items
    "ammo",
    "records"
]

class Item:
    """If self.type is None (which is default arg),
    item won't be printed to screen
    """
    def __init__(self, pos, type=None):
        self.x, self.y = pos
        self.r = 1
        self.type = type
        if type:
            self.setType(type)
        
    def setType(self, type):
        if type == "random": #only random items
            type = random.choice(allItemNames + commonItemList)
        elif type == "commonrandom": #only common items
            type = random.choice(commonItemList)
        elif type == "randomammo":
            type = random.choice(["ammo","records"])
            
        self.sprname = type
        #hw = half width, h = height
        if type == "ammo":
            self.hw = 4
            self.h = 9
        elif type == "records":
            self.hw = 7
            self.h = 9
        elif type == "bandaid":
            self.hw = 7
            self.h = 6
        elif type == "beartrap":
            self.hw = 11
            self.h = 6
        elif type == "healthkit":
            self.hw = 5
            self.h = 11
        else:
            print "ERROR: Couldn't find item type",type
            exit()
            
        self.type = type
        
    def pos(self):
        return (self.x, self.y)
        
    def drawPos(self):
        """Returns position of item adjusted for drawing
        All items are drawn so that self.y is the lowest part of the image
        """
        return (self.x-self.hw, self.y-self.h+2)