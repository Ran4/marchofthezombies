import random

import pygame
from pygame.locals import *

from bullet import *
from pointfunctions import pointDist

def getBuilding(x):
    """Gets which building a certain x position is in/close to"""
    if x < 1650: #house1
        return 1
    elif x < 2100: #house2
        return 2
    else: #house3
        return 3
        
def getFloor(building, y):
    """Gets the floor number of a certain height in a certain building"""
    if building == 1:
        if y < 166: #fourth floor
            return 4
        elif y < 255: #third floor
            return 3
        elif y < 340: #second floor
            return 2
        elif y < 422: #first floor
            return 1
        elif y < 460: #ground
            return 0
        else: #cellar
            return -1
    elif building == 2: #house2
        if y < 80: #fifth floor
            return 5
        if y < 166: #fourth floor
            return 4
        elif y < 255: #third floor
            return 3
        elif y < 340: #second floor
            return 2
        elif y < 422: #first floor
            return 1
        elif y < 460: #ground
            return 0
        else: #cellar
            return -1
    elif building == 3: #house3
        if y < 203: #third floor
            return 3
        elif y < 289: #second floor
            return 2
        elif y < 377: #first floor
            return 1
        else: #0th floor/ground
            return 0
    else:
        print "ERROR! Can't get floor information from house",house
        exit()

def getBuildingAndFloor(pos):
    """Returns a tuple consisting of building number (1-3) and
    floor number (-1 to 5) of object
    """
    x, y = pos
    
    building = getBuilding(x)
    floor = getFloor(building, y)
    
    return (building, floor)

class LivingThing(object):
    """Abstract class used by Player and Zombie. Won't function on it's own"""
    def __init__(self, pos=(1190,234)):
        self.x, self.y = pos

        self.maxHp = 100
        self.hp = self.maxHp
        self.tod = -1 #time of death
        
        self.maxMs = 1.0
        self.ms = self.maxMs
        self.minMs = 0.5
        self.msSlow = 0 #for slowdown: lower ms by n and set this to n
        self.maxMsRegen = 0.01 #100 frames = 1 self.ms
        self.msRegen = self.maxMsRegen #time to regen ms when hurt. 
        self.minMsRegen = 0.0005 #500 frames = 0.25 self.ms
        
        self.wantToMoveLeft = False
        self.wantToMoveRight = False
        self.dir = 1 #looks to the right
        self.onStair = -1
        self.steps = 0
        self.minClimbSpeed = 0.001
        self.isInfected = False
        self.isImmune = False #can get infected
        self.canUseStairs = True
        
        self.nextAttack = 0
        
        #radii of body parts (head, body, feet)
        self.headCollisionR = 4
        self.bodyCollisionR = 4
        self.feetCollisionR = 5
        
        self.pickupR = 16 #max distance for picking up items (not inc. item radius)
        
        self.remove = False
        
    def pos(self):
        return (self.x, self.y)
        
    def setPos(self, position):
        self.x, self.y = position
        
    def hurt(self, amount): #hurts self with amount, negative values means heal
        self.hp -= amount
        if self.hp > self.maxHp:
            self.hp = self.maxHp
        if self.hp < 0:
            self.remove = True
        
    def hurtFeet(self, amount):
        """Slows regen and ms
        Negative values of amount heals feet
        Feet will continue to be hurt, you'll need to reset them manually
        (impossible for zombies, but players can pick up bandage)
        """
        self.msRegen -= amount
        if self.msRegen < self.minMsRegen:
            self.msRegen = self.minMsRegen
        elif self.msRegen > self.maxMsRegen:
            self.msRegen = self.maxMsRegen
            
        self.ms -= amount
        if self.ms < self.minMs:
            self.ms = self.minMs
        elif self.ms > self.maxMs:
            self.ms = self.maxMs
            
    def slowDown(self, amount): #slows player down for a short period
        if amount > self.ms:
            amount = self.ms
        self.ms -= amount
        self.msSlow += amount
        
        #print self.ms,"",self.msSlow,"",self.maxMs
        if self.ms + self.msSlow > self.maxMs:
            self.msSlow = self.maxMs - self.ms
        
    def regenerateMovementSpeed(self):
        if self.msSlow > 0:
            #min() to prevent from adding more ms than msSlow is slowing
            self.ms += self.msRegen
            self.msSlow -= self.msRegen
            
    def getStairSpeed(self, stair):
        """Returns speed to walk/climb up a stair/ladder"""
        stairW,stairH = stair.w*1.0, stair.h*1.0
        if stairH == 0: #prevent dividebyzero error
            return self.minClimbSpeed
        else:
            ratio = min((stairW/abs(stairH)),1.0) #prevent going over 1.0 (eg. speeding up)
            speed = max(self.minClimbSpeed, ratio*self.ms)
            #~ if self.type == "Player":
                #~ print "w/h/=",stairW,stairH,stairW/abs(stairH)
                #~ print "stairclimb speed:",speed
            return speed
            
    def cantMoveHere(self, baf, dir):
        """Checks if current position is allowed, return True if not
        Only checks one dir (-1 or 1), always returns False if dir == 0
        Position is taken as a tuple containing building number (1-3) and floor (-1-5)
        (can be found by calling getBuildingAndFloor(pos))
        """
        
        building, floor = baf
        
        if dir < 0:
            if building == 1: #house1
                if floor == 4: #fourth floor
                    return self.x < 1176+30+self.hw
                elif floor == 2 or floor == 3: #second/third floor
                    return self.x < 1176+self.hw
                elif floor == 1: #first floor
                    return self.x < 1171
                elif floor == 0: #ground
                    return self.x < 446+self.hw
                else: #cellar
                    return self.x < 1238+self.hw
            elif building == 2: #house2
                if floor == 5: #fifth floor
                    return self.x < 1765+30+self.hw
                elif floor >= 2 and floor <= 4: #second/third/fourth floor
                    return self.x < 1765+self.hw
                elif floor == 1: #first floor
                    return self.x < 1759
                else: #ground
                    return False
            else: #house3
                if floor == 3: #third floor
                    return self.x < 2144
                elif floor == 1 or floor == 2: #first/second floor
                    return self.x < 2150+self.hw
                else: #0th floor/ground
                    return False
        elif dir > 0:
            if self.x < 1650: #house1
                if self.y < 166: #fourth floor
                    return self.x > 1551-30-self.hw
                elif self.y < 340: #second/third floor
                    return self.x > 1551-self.hw
                elif self.y < 422: #first floor
                    return self.x > 1557
                elif self.y < 460: #ground
                    return False
                else: #cellar
                    return self.x > 1357
            elif self.x < 2100: #house2
                if self.y < 80: #fifth floor
                    return self.x > 2031-30-self.hw
                elif self.y < 168: #fourth floor
                    return self.x > 2037
                elif self.y < 340: #second/third floor
                    return self.x > 2031-self.hw
                elif self.y < 422: #first floor
                    return self.x > 2037
                else: #ground
                    return False
            else: #house3
                if floor >= 1: #first/second/third floor
                    return self.x > 2416-self.hw
                else: #first floor/ground
                    return self.x > 2893-self.hw
        else:
            return False
        
    def move(self, game, st):
        if self.wantToMoveLeft: #moving left
            if self.onStair == -1: #not on a stair, so moves normally
                oldx = self.x
                self.x -= self.ms
                baf = getBuildingAndFloor((self.x, self.y))
                if self.cantMoveHere(baf, -1): self.x = oldx
                
                #~ if self.type == "Player":
                    #~ print "player is in building",str(building)+", floor",floor
                    #~ print "x: %s, oldx: %s" % (self.x, oldx)
                
            else: #on a stair
                speed = self.getStairSpeed(st[self.onStair])
                self.steps -= speed
                if self.steps < 0: #walked past stair, is at start
                    #print self.type,"stepped off a stairway start"
                    self.setPos(st[self.onStair].getStart())
                    self.onStair = -1
                else: #didn't walk past stair, updates position
                    self.setPos(st[self.onStair].getPosFromSteps(self.steps))
                
            self.dir = 0
        elif self.wantToMoveRight: #moving right
            if self.onStair == -1: #not on a stair, so moves normally
                oldx = self.x
                self.x += self.ms
                baf = getBuildingAndFloor((self.x, self.y))
                if self.cantMoveHere(baf, 1): self.x = oldx
                    
                #~ if self.type == "Player":
                    #~ print "player is in building",str(building)+", floor",floor
                    #~ print "x: %s, oldx: %s" % (self.x, oldx)
                
            else: #on a stair
                speed = self.getStairSpeed(st[self.onStair])
                self.steps += speed
                if self.steps > st[self.onStair].w: #walked past stair, is at end
                    #print self.type,"stepped off a stairway end"
                    self.setPos(st[self.onStair].getStop())
                    self.onStair = -1
                else: #didn't walk past stair, updates position
                    self.setPos(st[self.onStair].getPosFromSteps(self.steps))
            self.dir = 1
            
        if self.type != "Player": #chance to slow down ("to fall")
            if self.slowdownChance > random.random():
                self.slowDown(0.1)
        
    def headCollision(self): #returns position of head collision in world
        return (self.x, self.y-11)
        
    def bodyCollision(self): #returns position of body collision in world
        return (self.x, self.y-2)
        
    def feetCollision(self): #returns position of feet collision in world
        return (self.x, self.y+8)
        
    def collideWithBullet(self, bullet):
        """Sees if a bullet collides with self
        If it does, do damage to self and see if self dies
        Returns True on collision
        """
        #first checks collision with head
        distanceToBodyPart = pointDist(self.headCollision(), bullet.pos())
        if distanceToBodyPart <= bullet.r + self.headCollisionR:
            #collision with head detected, does extra damage but doesn't slow
            self.hurt(bullet.highDamage)
            return True
        
        #checks collision with body
        distanceToBodyPart = pointDist(self.bodyCollision(), bullet.pos())
        if distanceToBodyPart <= bullet.r + self.bodyCollisionR:
            #collision with body detected
            self.hurt(bullet.midDamage)
            self.slowDown(0.05)
            return True
        
        #checks collision with feet
        distanceToBodyPart = pointDist(self.feetCollision(), bullet.pos())
        if distanceToBodyPart <= bullet.r + self.feetCollisionR:
            #collision with feet detected, does less damage but hurts feet
            self.hurt(bullet.lowDamage)
            self.slowDown(0.1)
            self.hurtFeet(0.015)
            return True
            
        return False #no collision was found

class Player(LivingThing):
    def __init__(self, *args,**kw):
        super(Player, self).__init__(*args,**kw)
        
        self.maxHp = 100
        self.hp = self.maxHp
        
        self.type = "Player"
        self.pistolAmmo = 12
        self.records = 4
        
        self.maxMs = 1.0
        self.ms = self.maxMs
        self.minMs = 0.3
        self.maxMsRegen = 0.01 #100 frames = 1 self.ms
        self.msRegen = self.maxMsRegen #time to regen ms when hurt. 
        self.minMsRegen = 0.0025 #400 frames = 1 self.ms
        
        self.shootDelay = 34 #time between pistol shots
        self.throwDelay = 38 #time between record throws
        self.hw = 8 #half width
        self.hh = 15 #half height
        
    def calculate(self, game, so, zl, bl, st, il):
        key = pygame.key.get_pressed()
        
        self.regenerateMovementSpeed()
        
        self.wantToMoveLeft = False
        self.wantToMoveRight = False
        
        if key[K_w] or key[K_s]: #trying to move up/down stair
            if self.onStair == -1: #isn't already on a stair
                #finds nearby stair
                if self.dir == 1: #moving right, iee. finding a start
                    for i in range(len(st)):
                        if st[i].isCloseEnoughStart(self.pos()):
                            self.onStair = i
                            self.steps = 0
                            self.setPos(st[i].getStart())
                            break
                else: #moving left, iee. finding a stop
                    for i in range(len(st)):
                        if st[i].isCloseEnoughStop(self.pos()):
                            self.onStair = i
                            self.steps = st[i].w
                            self.setPos(st[i].getStop())
                            break
            else: #already on a stair
                pass
                """
                if key[K_w]: #trying to go up stair
                    if st[self.onStair].h > 0: #stair going down = left
                        self.wantToMoveLeft = True
                    else:
                        self.wantToMoveRight = True
                elif key[K_s]: #trying to go down stair
                    if st[self.onStair].h > 0: #stair going down = right
                        self.wantToMoveRight = True
                    else:
                        self.wantToMoveLeft = True
                """
        
        if key[K_a]:
            self.wantToMoveLeft = True
        elif key[K_d]:
            self.wantToMoveRight = True
                
        self.move(game, st)
        self.pickupNearbyItems(so, il)
        self.calculateShooting(game, so, bl)
        
    def pickupNearbyItems(self, so, il):
        for i in range(len(il)):
            if not il[i].type: #doesn't have a type, iee. item not spawned
                continue
                
            distanceToItem = pointDist(self.pos(), il[i].pos())
            if distanceToItem < il[i].r + self.pickupR:
                #was close enough to pick up item, so does that
                self.giveItem(so, il[i].type)
                il[i].type = None #"removes" item
            
    def giveItem(self, so, type):
        """Gives self something depending on type
        Example: giveItem(so,"records") gives player a records item, eg. 2 records
        """
        if type == "ammo":
            self.pistolAmmo += 12
            so["ammo"].play()
        elif type == "records":
            self.records += 2
            so["ammo"].play()
        elif type == "bandaid":
            self.hurt(-20) #heals with 20 hp
            self.hurtFeet(-0.3)
            so["healthkit"].play()
        elif type == "healthkit":
            self.hurt(-45) #heals with 45 hp
            self.hurtFeet(-0.4)
            so["healthkit"].play()
        elif type == "beartrap":
            self.hurt(23)
            self.hurtFeet(0.35)
            so["beartrap"].play()
            
    def calculateShooting(self, game, so, bl):
        game.mpos = pygame.mouse.get_pos()
        game.mbut = pygame.mouse.get_pressed()
        game.aimpos = (game.mpos[0]+game.sx, game.mpos[1]+game.sy)
        game.relaimpos = (game.aimpos[0]-self.x,
            game.aimpos[1]-self.y) #aim relative to player
        
        if game.mbut[0]: #pressing left button, iee. want to shoot pistol
            if self.nextAttack == 0:
                if self.pistolAmmo > 0:
                    bl.append(Bullet(self.pos(), game.relaimpos))
                    self.pistolAmmo -= 1
                    so["pistolfire"].play()
                else:
                    pass #clik! sound, no ammo
                self.nextAttack = self.shootDelay
        elif game.mbut[2]: #pressing right button, iee. want to throw records
            if self.nextAttack == 0:
                if self.records > 0:
                    bl.append(Bullet(self.pos(), game.relaimpos, "record"))
                    self.records -= 1
                    so["throw"].play()
                else:
                    pass #no records to throw
                self.nextAttack = self.throwDelay
        
        if self.nextAttack > 0:
            self.nextAttack -= 1
        
class Zombie(LivingThing): #standard zombie
    """Can be used on its own (as a standard zombie)
    or be used as a superclass by overriding variables/methods
    """
    def __init__(self, *args,**kw):
        super(Zombie, self).__init__(*args,**kw)
        self.building = getBuilding(self.x)
        self.maxHp = 100
        self.hp = self.maxHp
        
        self.maxMs = 0.25
        self.ms = self.maxMs    
        self.minMs = 0.07
        self.maxMsRegen = 0.002 #125 frames = 0.25 self.ms
        self.msRegen = self.maxMsRegen #time to regen ms when hurt. 
        self.minMsRegen = 0.0005 #500 frames = 0.25 self.ms
        
        self.attackRangeW = 16
        self.attackRangeH = 49
        self.attackDamage = 15
        self.infectionChance = 0.1 #10 %
        self.meleeAttackDelay = 60 #1 time per second
        self.wantToGotoStairway = -1 #none
        self.wantToGotoStairwayType = 0
        self.wait = 0
        self.type = "Zombie"
        self.spr = "zombie"
        self.hw = 8 #half width
        self.hh = 15 #half height
        
        self.isInfected = True
        self.isImmune = True #Zombies are immune to infection (duh)
        self.roam = 0 #if >0, zombie will move roamDir. <0 is permanent roam mode
        self.roamDir = 0
        self.startRoamChance = 0.001 #chance to start roaming (not always used)
        self.slowdownChance = 0.001 #chance to slow down when moving
        
    def calculateAttack(self):
        """Should be called upon every think. Time until zombie can attack again"""
        if self.nextAttack > 0:
            self.nextAttack -= 1
            
    def attack(self, so, p):
        """Tries attacking player, returns True if attack was tried"""
        closeEnough = (p.x >= self.x - self.attackRangeW and
            p.x <= self.x + self.attackRangeW and
            p.y >= self.y - (self.attackRangeH/2) and
            p.y <= self.y + (self.attackRangeH/2))
                
        if closeEnough:
            #zombie is in range of attacking the player
            if self.nextAttack == 0:
                #zombie can attack, so zombie attacks:
                print self.type,"attacked player for",
                print self.attackDamage,"damage"
                p.hurt(self.attackDamage)
                p.hurtFeet(0.05)
                
                #chance to infect player
                #~ if not p.isImmune:
                    #~ if self.infectionChance > random.random():
                        #~ #was infected
                        #~ print self.type,
                        #~ #print "infected player with the Zombie virus"
                        #~ p.isInfected = True
                
                so["zombieattack"].play()
                self.nextAttack = self.meleeAttackDelay
            return True
        return False
            
    def thinkOnSameHouseAndFloor(self, so, game, st, p):
        """Should be called when zombie and player is in the same house
        and on the same floor
        """
        #print "Zombie is on the same level"
        self.wantToGotoStairway = -1 #no need to use a stairway
        #move towards player
        #print "Wants to move towards player"
        if self.x > p.x: #go left
            self.wantToMoveLeft = True
        elif self.x < p.x: #go right
            self.wantToMoveRight = True
        self.move(game, st)
        
    def thinkFindStairway(self, game, st, p, verticalDirectionWant, building=-1):
        """Called to find a stairway going in specified direction
        verticalDirectionWant can have values -1 (up) or 1 (down)
        building can be -1 (any building) or >= 0 (only stairs of a certain building)"""
        #print self.type,"trying to find stairway"
        stairDistX = [-1]*len(st) #list of distances to stairways
        stairType = [-1]*len(st) #list of start (0) or stop (1) of stairways
        for i in range(len(st)): #creates a list of distances
            if self.y > st[i].y - 2 and self.y < st[i].y + 2: #start
                #print "Zombie is in correct y-axis for",
                #print "start of stairway",i
                stairType[i] = 0
            elif (self.y > st[i].y+st[i].h - 2 and
                self.y < st[i].y+st[i].h + 2): #stop
                stairType[i] = 1
                #print "Zombie is in correct y-axis for",
                #print "end of stairway",i
            else: #neither start nor stop could be reached in y-axis
                #print "Zombie can't reach stairway (y-axis)",i
                continue
                
            if st[i].h < 0:
                if stairType[i] == 0: #start
                    stairDir = -1
                else: #stop
                    stairDir = 1
            else:
                if stairType[i] == 0: #start
                    stairDir = 1
                else: #stop
                    stairDir = -1
                
            #will now see if it goes in the right direction
            if (verticalDirectionWant == stairDir):
                if stairType[i] == 0: #distance to start
                    stairDistX[i] = abs(st[i].x - self.x)
                elif stairType[i] == 1: #distance to stop
                    stairDistX[i] = abs((st[i].x + st[i].w) - self.x)
                else:
                    print "Error!"
                #print "Zombie found stair",i,"at x distance",stairDistX[i]
            else:
                pass
                #~ print "Stairway",i,"goes in the wrong direction!"
                #~ print "Zombie vertwant:",verticalDirectionWant
                #~ print "Stair dir:", stairDir
        #now have a list of distances in stairDistX
        #will find the lowest distance and set that as a goal
        lowest = 100000000 #100m, huge start value
        index = -1
        for i in range(len(st)):
            if stairType[i] == -1 or stairDistX[i] == -1:
                #stairway can't be reached
                continue
                
            if building >= 0: #stair point must be in a certain building
                if stairType[i] == 0: #start
                    stairBuilding = getBuilding(st[i].x)
                else: #stop
                    stairBuilding = getBuilding(st[i].x+st[i].w)
                if building != stairBuilding: #not the same building
                    #stairway can't be reached
                    continue
            
            if abs(stairDistX[i]) < lowest:
                lowest = stairDistX[i]
                index = i
                
        #start order to move towards stairway[index]
        #(if index is -1, nothing will be followed since no stairway was found)
        self.wantToGotoStairway = index
        if index == -1:
            print "Zombie wants to climb a stairway, but none can be found!"
            self.wait += 60 #do nothing for a while
        else:
            #print "Zombie now wants to climb stairway",index
            self.wantToGotoStairwayType = stairType[index]
        self.move(game, st)
        
    def thinkGoToStairway(self, game, st, p):
        #print "Zombie wants to go to stairway",self.wantToGotoStairway,
        #if self.wantToGotoStairwayType == 0: print "start"
        #else: print "stop"
        #now decides which direction to move in
        if self.wantToGotoStairwayType == 0: #start
            if (self.canUseStairs and
                st[self.wantToGotoStairway].isCloseEnoughStart(self.pos())):
                #print self.type,"started walking on stairway",
                #print self.wantToGotoStairway,"start"
                self.onStair = self.wantToGotoStairway
                self.steps = 0
                self.setPos(st[self.wantToGotoStairway].getStart())
                self.wantToGotoStairway = -1
                return
            
            if self.x < st[self.wantToGotoStairway].x-1:
                self.wantToMoveRight = True
            elif self.x > st[self.wantToGotoStairway].x+1:
                self.wantToMoveLeft = True
        elif self.wantToGotoStairwayType == 1: #end
            if (self.canUseStairs and
                st[self.wantToGotoStairway].isCloseEnoughStop(self.pos())):
                #print self.type,"started walking on stairway",
                #print self.wantToGotoStairway,"end"
                self.onStair = self.wantToGotoStairway
                self.steps = st[self.wantToGotoStairway].w
                self.setPos(st[self.wantToGotoStairway].getStop())
                self.wantToGotoStairway = -1
                return
            
            if self.canUseStairs:
                if self.x < (st[self.wantToGotoStairway].x +
                    st[self.wantToGotoStairway].w - 1):
                    self.wantToMoveRight = True
                elif self.x > (st[self.wantToGotoStairway].x +
                    st[self.wantToGotoStairway].w + 1):
                    self.wantToMoveLeft = True
            else: #is a dog, will move around instead of stay at the stairs
                if self.startRoamChance > random.random():
                    self.roam += random.randint(240,1200) #4 to 20 seconds
                    self.roamDir = (random.randint(0,1)*2)-1
                    #~ print self.type,"started to roam, will roam for",
                    #~ print round(self.roam/60,1),"more seconds",
                    if self.roamDir == -1:
                        print "(moving left)"
                    elif self.roamDir == 1:
                        print "(moving right)"
                    else:
                        print "(not moving)"
                    return
                
                if self.x < (st[self.wantToGotoStairway].x +
                    self.stairValue(game) +
                    st[self.wantToGotoStairway].w - 1):
                    self.wantToMoveRight = True
                elif self.x > (st[self.wantToGotoStairway].x +
                    self.stairValue(game) +
                    st[self.wantToGotoStairway].w + 1):
                    self.wantToMoveLeft = True
        else:
            print "ERROR:",self.type,"wants to go to",self.wantToGotoStairway,
            print "but stairwaytype is not 0 or 1 (start/end)"
        
        self.move(game, st)
        
    def getVerticalDirectionWant(self, y):
        """Returns -1 or 0 or 1, depending on where y is (under=1,over=1,same=0
        The distance when something is over or under is decided by self.attackRangeH/2"""
        if self.y < y - self.attackRangeH/2: #zombie is above player: go lower (down)
            return 1
        elif self.y > y + self.attackRangeH/2: #zombie is under player: go higher (up)
            return -1
        else: #zombie is at the same height as player
            return 0
    
    def thinkOnSameHouse(self, so, game, st, p):
        """Should be called from self.think() when zombie and
        player is in the same house
        """
        #sees if zombie is over/under player
        #the zombie is over/under if within attackRangeH/2 pixels height of player
        verticalDirectionWant = self.getVerticalDirectionWant(p.y)
        
        if verticalDirectionWant == 0: #zombie is on the same level
            self.thinkOnSameHouseAndFloor(so, game, st, p)
            return
            
        #zombie isn't on the same level, sees if it has orders to go to a certain stairway
        if self.wantToGotoStairway >= 0: #wants to go to a certain stairway
            self.thinkGoToStairway(game, st, p)
        else: #don't have any order
            #finds closest stairway that goes in wanted direction and is in the same building
            self.thinkFindStairway(game, st, p, verticalDirectionWant, self.building)
            
    def thinkOnNotSameHouse(self, game, st, p, housenow, housegoal):
        """Should be called from self.think() when zombie and player is in the same house
        housenow is the house that self is in right now,
        housgoal is where self wants to go
        """
        if self.wantToGotoStairway >= 0: #wants to go to a certain stairway
            self.thinkGoToStairway(game, st, p)
        else: #don't have any stairway to go to
            zbaf = getBuildingAndFloor(self.pos())
            if zbaf[1] == 0: #is on ground floor, so just move toward building
                if housenow < housegoal: #is left of goal, so go right
                    self.wantToMoveRight = True
                elif housenow > housegoal: #is right of goal, so go left
                    self.wantToMoveLeft = True
                self.move(game, st)
                    
            elif zbaf[1] == -1: #is below ground floor (ie. in cellar), so go up
                #finds stairway going up
                self.thinkFindStairway(game, st, p, -1, self.building)
                    
            else: #is above ground floor, so goes down in same building
                #unless on building 2, floor 4: walk the line
                #but only if player is in building 3, floor 1-3
                if (zbaf[0] == 2 and zbaf[1] == 4 and
                    housegoal == 3 and getFloor(housegoal, p.y) >= 1):
                    #gives order to walk to line
                    self.wantToGotoStairway = 12 #line index
                    self.wantToGotoStairwayType = 0 #start of line
                #or unless on building 3 floor 2-3: walk up
                elif zbaf[0] == 3 and zbaf[1] >= 2:
                    #finds stairway going up
                    self.thinkFindStairway(game, st, p, -1)
                else:
                    #finds stairway going down
                    self.thinkFindStairway(game, st, p, 1, self.building)
            
    def thinkRoam(self, game, st):
        """"Called when roaming (self.roam)"""
        if self.roam > 0: #decreases roam time if not permanent roam
            self.roam -= 1
            if self.roam == 0:
                print self.type,"stopped roaming"
        if self.roamDir == 1:
            self.wantToMoveRight = True
        elif self.roamDir == -1:
            self.wantToMoveLeft = True
        self.move(game, st)
        return
        
    def thinkOnStair(self, game, st):
        """Called when self is on a stair (self.onStair >= 0)"""
        if self.wantToGotoStairwayType == 0: #start
            #started at start, so should move right
            self.wantToMoveRight = True
        elif self.wantToGotoStairwayType == 1: #end
            #started at end, so should move left
            self.wantToMoveLeft = True
        self.move(game, st)
        
    def think(self, so, game, st, p):
        """Makes the zombie think. A simple AI routine
        Calls other think-functions"""
        self.regenerateMovementSpeed()
        self.calculateAttack() #attack timers
        
        if self.wait > 0: #is ordered to wait, so do nothing
            self.wait -= 1
            return
        
        #temp variables that are reset every frame, used when calling self.move()
        self.wantToMoveLeft = False
        self.wantToMoveRight = False
        
        if self.attack(so, p): #attacks if close enough
            return
        
        if self.onStair >= 0: #is on a stair, so continues moving
            self.thinkOnStair(game, st)
            return
        
        if self.roam: #in roam mode
            self.thinkRoam(game, st)
            return
            
        #sees if the Zombie is in the same house as the Player
        zbaf = getBuildingAndFloor(self.pos())
        pbaf = getBuildingAndFloor(p.pos())
        self.building = zbaf[0]
        
        houseWant = self.building - pbaf[0]
        
        if houseWant: #isn't 0, thus isn't in same house
            self.thinkOnNotSameHouse(game, st, p, zbaf[0], pbaf[0])
        else: #housewant is 0, thus in the same house
            self.thinkOnSameHouse(so, game, st, p)
            
class FatZombie(Zombie):
    """Subclass of Zombie. Like Zombie but slower and tougher"""
    def __init__(self, *args,**kw):
        super(FatZombie, self).__init__(*args,**kw)
        
        self.maxHp = 150 #50 % more hp
        self.hp = self.maxHp
        
        self.maxMs = 0.2 #.5 slower than Zombie
        self.ms = self.maxMs    
        self.minMs = 0.05
        self.maxMsRegen = 0.002 #125 frames = 0.25 self.ms
        self.msRegen = self.maxMsRegen #time to regen ms when hurt. 
        self.minMsRegen = 0.0005 #500 frames = 0.25 self.ms
        
        self.attackDamage = 21 #slightly higher dps than Zombie
        self.infectionChance = 0.2 #20 %
        self.meleeAttackDelay = 80 #0.75 times per second
        self.type = "Fat"
        self.spr = "fatzombie"
        self.hw = 10 #half width
        self.hh = 17 #half height
        
class ZombieDog(Zombie): #faster than Zombie, but can't climb stairways
    """Subclass of Zombie. Like Zombie but faster and with more damage.
    Can't climb stairways, will roam near them instead"""
    def __init__(self, *args,**kw):
        super(ZombieDog, self).__init__(*args,**kw)
        
        self.maxHp = 80 #20 hp less than Zombie
        self.hp = self.maxHp
        
        self.maxMs = 0.75 #three times faster than Zombie: 3/4 of unharmed Player
        self.ms = self.maxMs    
        self.minMs = 0.3
        self.maxMsRegen = 0.004 #125 frames = 0.5 self.ms
        self.msRegen = self.maxMsRegen #time to regen ms when hurt. 
        self.minMsRegen = 0.001 #500 frames = 0.5 self.ms
        
        self.attackRangeW = 21
        self.attackRangeH = 25
        self.attackDamage = 8 #much higher dps than Zombie
        self.infectionChance = 0.3 #30 %
        self.meleeAttackDelay = 20 #3 times per second
        self.type = "Dog"
        self.spr = "zombiedog"
        self.hw = 19 #half width
        self.hh = 12 #half height
        
        self.canUseStairs = False
        self.stairVal = 0
        
    def stairValue(self, game):
        """Returns a value that is changed every 4 seconds
        The dog will think that the stair's position is adjusted by this value
        which means that it'll go there instead of just waiting by the
        stairway (since it can't use it)
        """
        if self.stairVal == 0 or game.frame % 240 == 0:
            #finds a new value from 25 to 150 or -25 to -150
            val = random.randint(25,150)
            val *= (random.randint(0,1)*2)-1 #multiplies by 1 or -1
            self.stairVal = val
        return self.stairVal