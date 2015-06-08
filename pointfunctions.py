from math import sqrt

def pointDist(pos1, pos2): #returns the distance between two points
    dx = pos2[0] - pos1[0]
    dy = pos2[1] - pos1[1]
    return sqrt(dx**2 + dy**2)