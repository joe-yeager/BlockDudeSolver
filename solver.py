import sys
from Tkinter import Tk, Frame, Canvas
from PIL import ImageTk
import csv
import time

EMPY, BRCK, BLCK, WEST, EAST, DOOR = 0,1,2,3,4,5
width, height = 0,0
HEADING = {3:"w",4:"e"}

####################        Data Types        ####################
class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Level:
    def __init__(self, width,height,layout):
        self.width = width
        self.height = height
        self.layout = layout

####################        App Class        ####################
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Block Dude Solver")
        self.frame = Frame(self.root)
        self.frame.pack()
        self.canvas = Canvas(self.frame, bg="white", width=(width*24)+100, height=(height*24)+100)
        self.canvas.pack()
        self.levels = []

        filedir = "./assets/"
        filenames = ["brick.png","block.png","dudeLeft.png","dudeRight.png","door.png"]
        
        self.imageArray = []        
        self.imageArray.append("")
        for i in range(0,len(filenames)):
            self.imageArray.append(ImageTk.PhotoImage(file=filedir + filenames[i]))

    def displayLevel(self,level):
        length = len(level.layout)
        row = 0
        for i in range(0,length):
            if i % (level.width) == 0:
                row += 1
            if level.layout[i] != EMPY:
                x = ((i%(level.width))*24) + 65
                y = (row*24) + 40
                self.canvas.create_image(x,y, image=self.imageArray[level.layout[i]])

    def loadLevels(self,fileArray):
        length = len(fileArray)
        for i in range(0,length):
            with open(fileArray[i], 'rb') as f:
                reader = csv.reader(f)
                reader = list(reader).pop(0)
                level = map(int,reader)
                width = level.pop(0)
                height = level.pop(0)
                newLevel = Level(width,height,level)
                self.levels.append(newLevel)

    def updateCanvasDems(self,width, height):
        newWidth = (width*24)+100
        newHeight = (height*24)+100
        self.canvas.config(width=newWidth,height=newHeight)

    def clearCanvas(self):
        self.canvas.delete("all")

    def run(self):
        self.root.mainloop()

class Player:
    def __init__(self):
        self.pos = Coordinate(0,0)
        self.dir = 0
        self.isHoldingBlock = False
    
    def setPos(self,x,y):
        self.pos.x = x
        self.pos.y = y

    def setDirection(self, playerIndex):
        self.dir = HEADING[playerIndex]

    def moveEast(self):
        self.pos.x += 1

    def moveWest(self):
        self.pos.x -= 1

    def moveNEast(self):
        self.moveEast()
        self.pos.y += 1

    def moveNWest(self):
        self.moveWest()
        self.pos.y += 1

    def moveSEast(self):
        self.moveEast()
        self.pos.y -= 1

    def moveSWest(self):
        self.moveWest()
        self.pos.y -= 1

    def pickupBlock(self):
        self.isHoldingBlock = True

    def dropBlock(self):
        self.isHoldingBlock = False

    def fall(self):
        self.post.y -= 1;

####################        Solver Class        ####################
class Solver:
    def __init__(self):
        
        self.player = Player()
        self.victory = False;
        self.east = [[0,0,4,0],[0,0,3,0],[0,0,3,1],[0,0,3,2]]
        self.west = [[0,0,0,3],[0,0,0,4],[0,0,1,4],[0,0,2,4]]
        self.nw = [[0,0,1,3],[0,0,2,3]]
        self.ne = [[0,0,4,1],[0,0,4,2]]
        self.pickUp = [[0,0,4,2],[0,0,2,3]]
        self.drop = [[0,0,4,0], [0,0,0,3]]
        self.sw = [[0,3,0,1],[0,3,0,2]]
        self.se = [[4,0,1,0],[4,0,2,0]]
        self.fall = [[3,1,0,1],[3,1,0,0],[3,0,0,0],[3,2,0,1],[3,2,0,0],[3,1,0,2],[3,2,0,2],[3,0,0,1],[3,0,0,2],
                        [1,4,1,0],[1,4,0,0],[0,4,0,0],[2,4,1,0],[2,4,0,0],[1,4,2,0],[2,4,2,0],[0,4,1,0],[0,4,2,0]]

        print(self.fall[1])

    def setLevel(self,level):
        self.level = level
        self.length = len(self.level.layout)

    def locateStartAndGoalState(self):
        self.goalPos, self.playerPos, self.playerDir = -1,-1,""
        for i in range(0,self.length):
            if self.level.layout[i] == DOOR:
                x, y = i % self.level.width, (i - (i%self.level.width))/self.level.width
                self.goalPos = Coordinate(x,y)
            elif self.level.layout[i] == WEST or self.level.layout[i] == EAST:
                x, y = i % self.level.width, (i - (i%self.level.width))/self.level.width
                self.player.setPos(x,y)
                self.player.setDirection(self.level.layout[i])

    def shallowSolvabilityCheck(self):
        if self.goalPos == -1 or self.playerPos == -1 or self.playerDir == "":
            return False
        return True

    def taxiCabDistance(self):
        self.taxiCab = Coordinate(self.goalPos.x-self.player.x, self.goalPos.y-self.player.y)

    def declareVictory(self):
        self.victory = True

    def checkVictory(self):
        taxiCabDistance()
        # Player is directly east of door, same elevation
        if self.taxiCab.y == 0 && self.taxiCab.x == 1:
            self.player.moveWest()
            declareVictory()
        # Player is directly west of door, same elevation
        elif self.taxiCab.y == 0 && self.taxiCab.x == -1:
            self.player.moveEast()
            declareVictory()
            
        # Player is directly above door, fall
        elif self.taxiCab.x == 0 && self.taxiCab.y == 1:
            self.player.fall()
            declareVictory()

        # player is ne, nw, sw, or se from door
        elif abs(self.taxiCab.x) == 1 && abs(self.taxiCab.y) == 1 
            if self.taxiCab.x == 1 && self.taxiCab.y == 1:
                self.player.moveNWest()
            elif self.taxiCab.x == -1 && self.taxiCab.y == 1:
                self.player.moveNEast()
            elif self.taxiCab.x == 1 && self.taxiCab.y == -1:
                self.player.moveSWest()
            elif self.taxiCab.x == -1 && self.taxiCab.y == -1:
                self.player.moveSEast()
            declareVictory()



####################         Program Loop        ####################
if __name__=='__main__':
    root = Tk()
    app = App(root)
    testFiles = ["./testLevels/level1.csv"]
    app.loadLevels(testFiles)
    solver = Solver()

    numLevels = len(app.levels)
    for i in range(0, numLevels):
        solver.setLevel(app.levels[i])
        app.updateCanvasDems(solver.level.width,solver.level.height)
        app.displayLevel(solver.level)
        solver.locateStartAndGoalState()
        solver.shallowSolvabilityCheck()

    app.run()
