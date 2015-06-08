import sys, os, time, random, math

import pygame
from pygame.locals import *

from actors import *
from game import *
from bullet import *
from stairs import *
from items import *
from spawnpoint import *
import constants as con

def zombieCount(zl):
    print "There are",len(zl),"Zombies in game:",
    d = {"Zombie":0,"Fat":0,"Dog":0}
    for z in zl:
        d[z.type] += 1
    for key in d.keys():
        print d[key],key+"s,",
    print

def setScreen(game, toggle=False):
    if toggle:
        game.fullscreen = not game.fullscreen
    
    if game.fullscreen:
        return pygame.display.set_mode(game.screensize,FULLSCREEN)
    else:
        return pygame.display.set_mode(game.screensize)

def main():
    pygame.init()
    clock = pygame.time.Clock()
    pygame.display.set_caption("March of the Zombies")
    
    game = Game()
    game.screensize = game.screenw,game.screenh = (800,600)
    game.fullscreen = False
    screen = setScreen(game)
    pygame.mixer.init() #for sound
    exit = False
    fps = 0
    
    try:
        fnt = pygame.font.Font(None,22) #font of size (=height) 22
    except: #couldn't load default font, tries to load manually
        fnt = pygame.font.SysFont("arial", 22)

    #load images, sounds and classes
    img = loadImages()
    so = loadSounds()
    bl = [] #bullet list
    
    #p = Player((1190,234)) #third floor, left, house1
    p = Player((1374,408)) #first floor, middle, house1
    zl = [ #zombie list
        Zombie((1530,234)), #third floor, right
        Zombie((1530,321)), #second floor, right
        Zombie((1190,408)), #first floor, left
        Zombie((1530,408)) #first floor, right
        ]
        
    st = [ #stairs list
        Stair((1291,234),8,-87), #to fourth floor, ladder, house1
        Stair((1369,321),113,-87), #to third floor, house1
        Stair((1220,321),113,87), #to second floor, house1
        Stair((1125,444),47,-36), #to first floor (left), house1
        Stair((1557,408),47,36), #to first floor (right), house1
        Stair((1357,510),33,-66), #to ground level (middle, cellar), house1
        
        Stair((1949,60),8,87), #to fifth floor, ladder, house2
        Stair((1917,234),8,-87), #to fourth floor, ladder, house2
        Stair((1818,234),113,87), #to third floor, house2
        Stair((1855,408),113,-87), #to second floor, house2
        Stair((1713,444),47,-36), #to first floor (left), house2
        Stair((2037,408),47,36), #to first floor (right), house2
        
        Stair((2037,147),107,36), #to fourth floor, line, house2>house3 #num. 12
        
        Stair((2302,270),8,-87), #to fourth floor, ladder, house3
        Stair((2203,270),113,87), #to third floor, house3
        Stair((2240,444),113,-87) #to second floor, house3
        ]
        
    il = [ #item spawn list
        Item((1337,160)), #fourth floor, left, house1
        Item((1403,160)), #fourth floor, middle, house1
        Item((1461,160), "randomammo"), #fourth floor, right, house1
        Item((1230,247), "random"), #third floor, left, house1
        Item((1195,334), "random"), #second floor, left, house1
        Item((1500,334), "random"), #second floor, right, house1
        Item((1265,522), "random"), #cellar, left, house1
        Item((1323,522), "random"), #cellar, right, house1
        
        Item((1810,73), "bandaid"), #fifth floor, left1, house2
        Item((1875,73), "ammo"), #fifth floor, left2, house2
        Item((1800,160), "random"), #fourth floor, left, house2
        Item((1945,247), "random"), #third floor, right, house2
        
        Item((2186,197), "random"), #third floor, left, house3
        Item((2370,197), "random"), #third floor, right, house3
        Item((2390,370), "random"), #first floor, right, house3
        
        Item((1024,457)), #ground, left of house1
        Item((1659,457)), #ground, between house1 and house2
        Item((2553,457)) #ground, right of house3
        ]
    zs = [#zombie spawns list
        #near/in house1
        SpawnPoint((580,444),"commonrandom"), #ground, left, near wall
        SpawnPoint((1190,408),"commonrandom"), #first floor, left
        SpawnPoint((1530,408),"commonrandom"), #first floor, right
        
        #near/in house2
        SpawnPoint((1970,444),"commonrandom"), #ground, right
        SpawnPoint((1790,234),"onlycommonrandom"), #third floor, left
        
        #near/in house3
        SpawnPoint((2374,270),"onlycommonrandom"), #second floor, right, in house3
        SpawnPoint((2185,357),"onlycommonrandom"), #first floor, left, in house3
        SpawnPoint((2360,444),"commonrandom"), #ground, right, in house3
        
        SpawnPoint((2810,444),"random") #ground, right, near right wall
    ]
    
    """Cursor, small cross:
    00011000
    00011000
    00011000
    11100111
    11100111
    00011000
    00011000"""
    pygame.mouse.set_cursor((8, 8),
    (4, 4),
    (24, 24, 24, 231, 231, 24, 24, 24),
    (0, 0, 0, 0, 0, 0, 0, 0))
    
    #############################
    ##Start of main loop        #
    while not exit:
        for event in pygame.event.get():
            if event.type == QUIT:
                exit = True
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    exit = True
                elif event.key == K_RETURN:
                    setScreen(game,toggle=True)
                elif event.key == K_f:
                    print "fps: %s" % round(fps, 1)
                elif event.key == K_c: #count zombies
                    zombieCount(zl)
                elif event.key == K_m: #add random zombie from random spawn
                    spawnAnotherZombie(zs, zl)
                elif event.key == K_k: #kill all zombies that aren't roaming
                    i = 0
                    while i < len(zl):
                        if not zl[i].roam:
                            zl.pop(i)
                        else:
                            i += 1
                elif event.key == K_n: #spawn MAX_ZOMBIES random zombies
                    numSpawned = 0
                    while handleAddingNewZombies(game, zs, zl,True):
                            numSpawned += 1
                    print "Spawned",numSpawned,"zombies!"

        handleLogic(img, so, game, p, zs, zl, bl, st, il)
        #print "logic handled once"
        drawGame(screen, img, fnt, game, p, zl, bl, il)
        clock.tick(60) #max 60 fps
        fps = clock.get_fps()
    #############################
    pygame.quit(); sys.exit()
    
def handleLogic(img, so, game, p, zs, zl, bl, st, il):
    #call classes here
    p.calculate(game, so, zl, bl, st, il)
    
    for zombie in zl:
        zombie.think(so, game, st, p)
        
    #moves all bullets
    moveBullets(game, bl)
    
    #checks collision of all bullets
    collideBullets(img, so, bl, zl)
    
    #might add new zombies or items
    handleAddingNewZombies(game, zs, zl)
    handleAddingNewItems(game, il)
    
    if p.remove and p.tod == -1: #sets time of death for player
        p.tod = game.frame
        savedTod = 0
        try:
            filename = os.path.join("data", "todrecord.txt")
            f = open(filename)
            savedTod = int(f.readline().strip())
            f.close()
        except:
            print "Error loading todrecord.save"
        if p.tod > savedTod:
            f = open(filename,"w")
            f.write(str(p.tod))
            f.close()
            game.newRecord = True
        else:
            game.oldRecord = savedTod
        
    
    game.sx = p.x-400
    game.playerRel = (p.x-game.sx,p.y-game.sy) #player position relative screen
    game.calculate() #updates things such as game.frame
    
    
def spawnAnotherZombie(zs, zl):
    """Spawns a zombie from random zombie spawn
    Returns True if possible, otherwise False (only when above con.MAX_ZOMBIES)
    """
    if len(zl) >= con.MAX_ZOMBIES:
        return False #can't add more zombies
    zombie = random.choice(zs).getZombie()
    if not zombie:
        print "ERROR ZOMG zombie is None!"
        exit()
    zl.append(zombie)
    return True
    
def getUnvisibleZombieSpawns(game, zs):
    """takes a list of zombie spawns and returns all those that aren't visible"""
    nonvisibleSpawns = []
    for spawn in zs:
        if not game.visible(spawn.pos()):
            nonvisibleSpawns.append(spawn)
    return nonvisibleSpawns
    
def handleAddingNewZombies(game, zs, zl,forceSpawn=False):
    addZombie = forceSpawn
    if not addZombie:
        #first, sees if we should add a zombie this frame
        if game.frame < con.TIME_TIL_FASTER_ZOMBIE_SPAWN: #before 2 (default) minutes
            addZombie = game.frame % con.FAST_ZOMBIE_SPAWN == 0 #every 3 seconds
        else: #after 2 (default) minutes
            addZombie = game.frame % con.SLOW_ZOMBIE_SPAWN == 0 #every 5 seconds
        
    if addZombie:
        if len(zl) >= con.MAX_ZOMBIES:
            return False #can't add more zombies
        
        #zombie should be added, now needs to find a zombie spawn not on screen
        spawns = getUnvisibleZombieSpawns(game, zs)
        if len(spawns) == 0: #no unvisible spawn found, so selects all spawns
            spawns = zs
        #gets a zombie from random spawn and append that to the zombie list
        zombie = random.choice(spawns).getZombie()
        zl.append(zombie)
        return True
    return False

def getUnvisibleItemSpawns(game, il):
    """returns a list of indexes of itemspawners that aren't visible"""
    indexlist = []
    for i in range(len(il)):
        if not game.visible(il[i].pos()):
            indexlist.append(i)
            #print "Found non-visible item",i,"at x/y:",il[i].x,il[i].y
    #print "Indexlist of unvisible items:",indexlist
    return indexlist

def spawnAnotherItem(game, il):
    """Picks a random item spawn and spawns an item
    Returns true if item was spawned, otherwise false
    """
    unvisibleindexlist = getUnvisibleItemSpawns(game, il)
    if len(unvisibleindexlist) == 0:
        print "No invisible items found!"
        unvisibleindexlist = []
        for i in range(len(il)):
            unvisibleindexlist.append(i)
    
    for i in range(4): #tries up to 4 times if there is already an item there
        #selects random item spawner
        index = random.choice(unvisibleindexlist)
        
        if il[index].type == None: #no item in item spawn, so spawns one
            il[index].setType("random")
            return True #placed item
    
    return False #couldn't place item
    
def handleAddingNewItems(game, il):
    if game.frame % con.ITEM_RESPAWNTIME == 0: #spawn item every 7 (default) seconds
        game.waitingToSpawnItems += 1
        
    if game.waitingToSpawnItems > 0: #wants to create items
        if game.waitingToSpawnItems > con.MAX_ITEM_QUEUE:
            game.waitingToSpawnItems = con.MAX_ITEM_QUEUE
        
        if spawnAnotherItem(game, il): #returns True if item was placed
            print "Item added!"
            game.waitingToSpawnItems -= 1
            
def moveBullets(game, bl):
    for bullet in bl:
        bullet.x += bullet.vec[0]
        bullet.y += bullet.vec[1]
        
        if bullet.type == "record": #record is effected by gravity
            bullet.vec = (bullet.vec[0]*con.AIR_FRICTIION,
                bullet.vec[1] + con.GRAVITY)
        
        #flags un-visible bullets for removal
        if not game.visible(bullet.pos()):
            bullet.remove = True
            
    removeBullets(bl)
        
def removeBullets(bl): #removes bullets from bullet list
    i = 0
    while i < len(bl):
        if bl[i].remove:
            bl.pop(i)
        i += 1
        
def removeZombies(zl): #removes zombies from zombie list
    i = 0
    while i < len(zl):
        if zl[i].remove:
            zl.pop(i)
        i += 1
        
def collideBullets(img, so, bl, zl): #collides bullets with zombies
    #first collides with zombies
    for bullet in bl:
        for zombie in zl:
            if zombie.remove:
                continue #won't check zombies that are already dead
                
            if zombie.collideWithBullet(bullet): #returns true on collision
                bullet.remove = True
                so["hit"].play()
                break #won't check collision with this bullet anymore
    removeZombies(zl)
    
    #then collides with house/environment
    for bullet in bl:
        if bullet.remove: #some bullets might have collided with a zombie
            continue
        if img["bcoll"].get_at((int(bullet.x),int(bullet.y)))[0] == 0:
            bullet.remove = True
            
    removeBullets(bl)
    
def drawGame(surface, img, fnt, game, p, zl, bl, il):
    surface.fill((20,148,255)) #bg
    
    #grassline
    #~ surface.fill((0,128,0),(0,458, 800,600))
    
    #draw houses
    surface.blit(img["houses"],(-game.sx,-game.sy))
    
    #draw items
    for item in il:
        if not item.type: #doesn't have a type, iee. item not spawned
            continue
            
        if game.visible(item.pos()):
            surface.blit(img[item.sprname],
                game.posScr(item.drawPos()))
    
    #draw zombies
    for zombie in zl:
        if game.visible(zombie.pos()): #only draw zombies that are visible
            sprname = zombie.spr
            
            if zombie.dir == 0: sprname += "_l"#is looking left
            else: sprname += "_r" #is looking right
                
            surface.blit(img[sprname],
                game.posScr((zombie.x-zombie.hw, zombie.y-zombie.hh)))
    
    #draws player
    if p.dir == 0: #is looking left
        surface.blit(img["player_l"], (game.playerRel[0]-8, game.playerRel[1]-15))
    else: #is right
        surface.blit(img["player_r"], (game.playerRel[0]-8, game.playerRel[1]-15))
                
    #draws bullets
    for bullet in bl:
        if game.visible(bullet.pos()):
            surface.blit(img[bullet.sprname],
                game.posScr(bullet.drawPos()))
        
    #GUI
    #draws ammo info
    ammoInfoText = "Ammo: %s" % p.pistolAmmo
    ammoInfoSurface = fnt.render(ammoInfoText, False, (0,0,0))
    surface.blit(ammoInfoSurface, (5,556))
    
    recordsInfoText = "Records: %s" % p.records
    recordsInfoSurface = fnt.render(recordsInfoText, False, (0,0,0))
    surface.blit(recordsInfoSurface, (5,578))
    
    #draws lifemeter
    #text
    hpInfoSurface = fnt.render("HP:", False, (0,0,0))
    surface.blit(hpInfoSurface, (5,512))
    #colored box of width 0 to 100
    width = p.hp*100 / p.maxHp #0 to 100
    surface.fill((224,0,0), (50+1,512+1, width,17))
    #meter overlay
    surface.blit(img["meter"], (50,512))
    
    #draws feetmeter
    #text
    hpInfoSurface = fnt.render("Feet:", False, (0,0,0))
    surface.blit(hpInfoSurface, (5,534))
    #colored box of width 0 to 100
    width = (p.ms-p.minMs)*100 / (p.maxMs-p.minMs)
    #print p.ms,"",p.msSlow,"",p.maxMs
    surface.fill((64,224,32), (50+1,534+1, width,17))
    #meter overlay
    surface.blit(img["meter"], (50,534))
    
    #draws time info
    if p.tod == -1: #hasn't died yet
        timeAliveInfo = "Time alive: %s seconds" % (game.frame / 60)
    else: #is dead
        timeAliveInfo = ("You survived %s seconds!" %
            round(p.tod / 60.0, 1))
            
        if game.newRecord:
            recordSurface = fnt.render("New record!", False,(0,0,0))
        else:
            recordText = ("The record is %s seconds" %
                (round(game.oldRecord / 60.0,1)))
            recordSurface = fnt.render(recordText, False,(0,0,0))
        surface.blit(recordSurface, (5,27))
    timeAliveSurface = fnt.render(timeAliveInfo, False, (0,0,0))
    surface.blit(timeAliveSurface, (5,5))

    pygame.display.update()
    
def loadImages():
    opj = os.path.join
    imagenames = [
    ["player_l", opj("data","player_l.png")],
    ["player_r", opj("data","player_r.png")],
    
    ["zombie_l", opj("data","zombie_l.png")],
    ["zombie_r", opj("data","zombie_r.png")],
    ["fatzombie_l", opj("data","fatzombie_l.png")],
    ["fatzombie_r", opj("data","fatzombie_r.png")],
    ["zombiedog_l", opj("data","zombiedog_l.png")],
    ["zombiedog_r", opj("data","zombiedog_r.png")],
    
    ["houses", opj("data","houses.png")],
    ["bcoll", opj("data","houses_bulletcollision.png")],
    
    ["standardbullet", opj("data", "standardbullet.png")],
    ["recordbullet", opj("data", "recordbullet.png")],
    
    ["meter", opj("data","meter.png")],
    
    ["ammo", opj("data","items", "ammo.png")],
    ["records", opj("data","items", "records.png")],
    ["bandaid", opj("data","items", "bandaid.png")],
    ["healthkit", opj("data","items", "healthkit.png")],
    ["beartrap", opj("data","items", "beartrap.png")]
    ]
    img = {}
    for name in imagenames:
        try:
            img[name[0]] = pygame.image.load(name[1]).convert()
            img[name[0]].set_colorkey((255,0,255)) #pink
        except:
            print "Couldn't load",name[1],"\nExiting"
            sys.exit()
    return img
    
def loadSounds():
    opj = os.path.join
    soundnames = [
    ["pistolfire", opj("data","sounds", "pistolfire.wav")],
    ["throw", opj("data","sounds", "throw.wav")],
    ["zombieattack", opj("data","sounds", "zombieattack.wav")],
    ["hit", opj("data","sounds", "hit.wav")],
    ["beartrap", opj("data","sounds", "beartrap.wav")],
    ["healthkit", opj("data","sounds", "healthkit.wav")],
    ["ammo", opj("data","sounds", "ammo.wav")]
    ]
    so = {}
    for name in soundnames:
        try:
            so[name[0]] = pygame.mixer.Sound(name[1])
        except:
            print "Couldn't load",name[1],"\nExiting"
            sys.exit()
    return so

if __name__ == "__main__":
	main()