import random

from actors import *

zombieTypesList = [ #list of all types of zombies
    "Zombie", #standard zombie
    "Fat", #slower but stronger dito
    "Dog"
]

commonZombiesList = (#common zombies, standalone or combine with ZombieTypesList
    ["Zombie"]*4 +
    ["Fat"]*2
    )

class SpawnPoint:
    """Mainly used for keeping track of which type of zombie should spawn,
    and where"""
    def __init__(self, pos, type="random"):
        self.x, self.y = pos
        self.setType(type)
        
    def setType(self, type):
        """sets what type of zombie this spawn produces
        "random" means that every time you call getZombie() you'll get a
        random zombie type
        "commonrandom" is random but with some zombies being more common
        "onlycommonrandom" is random but only with common zombies
        """
        if (type not in zombieTypesList and
            type.lower() != "random" and
            type.lower() != "commonrandom" and
            type.lower() != "onlycommonrandom"):
            #type is neither in zombieTypesList nor is random: error!
            print "ERROR: Couldn't find zombie type",type
            exit()
            
        self.type = type
        
    def getZombie(self):
        """Call this when you want a zombie: this will return a zombie
        of the correct type (iee. could be randomized etc.) in the correct position
        """
        type = self.type.lower()
        if type.lower() == "random":
            type = random.choice(zombieTypesList)
        elif type.lower() == "commonrandom":
            type = random.choice(zombieTypesList+commonZombiesList)
        elif type.lower() == "onlycommonrandom":
            type = random.choice(commonZombiesList)
        
        if type == "Zombie":
            return Zombie(self.pos())
        elif type == "Fat":
            return FatZombie(self.pos())
        elif type == "Dog":
            return ZombieDog(self.pos())
        
    def pos(self):
        return (self.x, self.y)
        
    def drawPos(self): #returns position adjusted for drawing
        return (self.x-self.hw, self.y-self.h)