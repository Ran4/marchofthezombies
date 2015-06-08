

class Game:
    """Class that stores data such as scrolling
    and variables that is needed in both the logic and the graphic function"""
    def __init__(self):
        self.sx, self.sy = 0, 0 #x and y scrolling
        self.waitingToSpawnItems = 0
        self.oldRecord = 0
        self.newRecord = False
        self.frame = 0
        
    def calculate(self): #should be called every frame
        self.frame += 1
        
    def visible(self, point):
        """Takes a point and sees if that is visible on screen"""
        px, py = point[0], point[1]
        if (px >= self.sx + self.screenw or px < self.sx
            or py < self.sy or py >= self.sy + self.screenh):
            return False
        return True
        
    def posScr(self, point):
        """Takes a point and returns it after adding sx/sy,
        iee. point relative to screen
        """
        return (point[0]-self.sx,point[1]-self.sy)