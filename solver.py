import sys
from Tkinter import Tk, Frame, Canvas
from PIL import ImageTk
import csv
import time

EMPY, BRCK, BLCK, WEST, EAST, DOOR = 0,1,2,3,4,5
width, height = 0,0

#####################################################################
#####################################################################
######################        Data Types        #####################
#####################################################################
#####################################################################

class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Level:
    def __init__(self, width,height,layout):
        self.width = width
        self.height = height
        self.layout = layout

class Tree:
    def __init__(self):
        self.move = None
        self.level = None
        self.index = None
        self.left = None
        self.middle = None
        self.right = None

#####################################################################
#####################################################################
######################        App Class        ######################
#####################################################################
#####################################################################

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
        self.canvas.delete("all")
        self.updateCanvasDems(level.width,level.height)
        length = len(level.layout)
        row = 0
        for i in range(0,length):
            if i % (level.width) == 0:
                row += 1
            if level.layout[i] != EMPY:
                x = ((i%(level.width))*24) + 65
                y = (row*24) + 40
                self.canvas.create_image(x,y, image=self.imageArray[level.layout[i]])

    def loadLevels(self,path, fileArray):
        length = len(fileArray)
        for i in range(0,length):
            with open(path + fileArray[i], 'rb') as f:
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

    def run(self):
        self.root.mainloop()

#####################################################################
#####################################################################
######################      Player Class       ######################
#####################################################################
#####################################################################

class Player:
    def __init__(self):
        self.pos = Coordinate(0,0)
        self.dir = 0
        self.isHoldingBlock = False
        self.index = 0
        self.falling = False

    def setPos(self,x,y):
        self.pos.x = x
        self.pos.y = y

    def setDirection(self, playerValue):
        self.dir = playerValue

    def moveEast(self):
        self.pos.x += 1
        self.index += 1

    def moveWest(self):
        self.pos.x -= 1
        self.index -= 1

    def moveNEast(self, width):
        self.moveEast()
        self.pos.y += 1
        self.index -= (width)

    def moveNWest(self,width):
        self.moveWest()
        self.pos.y += 1
        self.index -= (width)

    def fall(self, width):
        self.pos.y -= 1;
        self.index += (width)

    def moveSEast(self, width):
        self.moveEast()
        self.fall()

    def moveSWest(self,width):
        self.moveWest()
        self.fall()

    def pickupBlock(self):
        self.isHoldingBlock = True

    def dropBlock(self):
        self.isHoldingBlock = False

#####################################################################
#####################################################################
####################        Solver Class        #####################
#####################################################################
#####################################################################

class Solver:
    def __init__(self):
        
        self.player = Player()
        self.victory = False;
        self.east = [[0,0,4,0]]
        self.west = [[0,0,0,3]]
        self.faceEast = [[0,0,3,0],[0,0,3,1],[0,0,3,2]]
        self.faceWest = [[0,0,0,4],[0,0,1,4],[0,0,2,4]]
        self.nw = [[0,0,1,3],[0,0,2,3]]
        self.ne = [[0,0,4,1],[0,0,4,2]]
        self.pickUp = [[0,0,4,2],[0,0,2,3]]
        self.drop = [[0,0,4,0], [0,0,0,3]]
        self.sw = [[0,3,0,1],[0,3,0,2]]
        self.se = [[4,0,1,0],[4,0,2,0]]
        self.fall = [[3,1,0,1],[3,1,0,0],[3,0,0,0],[3,2,0,1],[3,2,0,0],[3,1,0,2],[3,2,0,2],[3,0,0,1],[3,0,0,2],
                        [1,4,1,0],[1,4,0,0],[0,4,0,0],[2,4,1,0],[2,4,0,0],[1,4,2,0],[2,4,2,0],[0,4,1,0],[0,4,2,0]]

        ## Victory Moves
        self.V = {
            "e":    [[0,0,4,5]],
            "w":    [[0,0,5,3]],
            "nw":   [[5,0,1,3],[5,0,2,3]],
            "ne":   [[0,5,4,1],[0,5,4,2]],
            "sw":   [[0,3,5,1],[0,3,5,2]],
            "se":   [[4,0,1,5],[4,0,2,5]],
            "fall": [[3,1,5,1],[3,1,5,0],[3,0,5,0],[3,2,5,1],[3,2,5,0],[3,1,5,2],[3,2,5,2],[3,0,5,1],[3,0,5,2],
                        [1,4,1,5],[1,4,0,5],[0,4,0,5],[2,4,1,5],[2,4,0,5],[1,4,2,5],[2,4,2,5],[0,4,1,5],[0,4,2,5]],
        }
        self.obstacleFlag = False
        self.obstacleHeight = 0
        self.blocksRequired = 0
        self.availableBlocks = 0
        self.blockGoals = []
        self.blockLocs = []
        self.trapFlag = False
        self.moveQuadrants = []
        self.moveList = []
    
    def prettyPrintLevel(self):
        lower = 0
        upper = 0
        temp = []
        length = len(self.level.layout)
        for i in range(0, length/self.level.width):
            upper += self.level.width
            for k in range(lower, upper):
                temp.append(self.level.layout[k])
            print(temp)
            temp = []
            lower += self.level.width

    def setLevel(self,level):
        self.level = Level(level.width,level.height,list(level.layout) )
        self.currentLevel = Level(self.level.width, self.level.height, list(self.level.layout) )
        self.length = len(self.level.layout)
        self.moveFuncs = {  #These depend on properties of the level, so define it after they are set
            "fall"  : [self.player.fall, self.level.width],
            "w"     : [self.player.moveWest, None],
            "e"     : [self.player.moveEast, None],
            "nw"    : [self.player.moveNWest, self.level.width],
            "ne"    : [self.player.moveNEast, self.level.width],
            "sw"    : [self.player.moveSWest, self.level.width],
            "se"    : [self.player.moveSEast, self.level.width],
            "fw"    : [self.player.setDirection, WEST],
            "fe"    : [self.player.setDirection, EAST],
            "pickup": [self.player.pickupBlock, None],
            "drop"  : [self.player.dropBlock, None],
        }

    def locateStartAndGoalState(self):
        self.goalPos = Coordinate(-1,-1)
        self.player.setPos(-1,-1)
        for i in range(0,self.length):
            if self.level.layout[i] == DOOR:
                x, y = i % self.level.width, (i - (i%self.level.width))/self.level.width
                self.goalPos = Coordinate(x,y)
            elif self.level.layout[i] == WEST or self.level.layout[i] == EAST:
                x, y = i % self.level.width, (i - (i%self.level.width))/self.level.width
                self.player.setPos(x,y)
                self.player.index,self.player.index2 = i,i
                self.player.setDirection(self.level.layout[i])

    def taxiCabDistance(self):
        self.taxiCab = Coordinate(self.goalPos.x-self.player.pos.x, self.goalPos.y-self.player.pos.y)
        if self.taxiCab.x < 0: # the door is west
            self.modifier = -1
        else: # the door is east
            self.modifier = 1

    def checkVictory(self, move):
        for k,v in self.V.iteritems():
            if move in v:
                self.moveList.append(k)
                self.victory = True
                break

    def performMove(self,level, move, arg=None):
        oldIndex = self.player.index
        if arg == None:
            move()
        else:
            move(arg)
        level.layout[oldIndex] = 0
        level.layout[self.player.index] = self.player.dir

    # check the block in front of player
    # if there is a brick, check the space above it
    # while you scan forward, check down to see if there is a drop off
    def checkObstaclesHelper(self, prevHeight, height, depth, index):
        if height - prevHeight > 1:
            self.obstacleFlag = True
            self.obstacleHeight = height
            self.obstableIndex = index
        if depth >= 2:
            self.trapFlag = True
        if index % self.level.width ==  0 or index < 0 or index > self.length or self.level.layout[index] == DOOR:
            return

        elif self.level.layout[index] == EMPY:
            if self.obstacleFlag:
                return
            spaceBelow = self.level.layout[index + self.level.width]
            if spaceBelow == BLCK or spaceBelow == BRCK: # If space below is brick/block go forward
                newIndex = index + self.modifier
                self.checkObstaclesHelper(0, 0, 0, newIndex)
            elif spaceBelow == EMPY: # If space below is brick/block go down
                newIndex = index  +  self.level.width
                self.checkObstaclesHelper(0, 0, depth+1, newIndex)
            elif spaceBelow == DOOR:
                return

        elif self.level.layout[index] == BRCK or self.level.layout[index] == BLCK:
            spaceAbove = self.level.layout[index - self.level.width]
            if spaceAbove == BLCK or spaceAbove == BRCK: # move up when the block above is a block
                newIndex = index -  (height * self.level.width)
                self.checkObstaclesHelper(prevHeight, height+1, 0, newIndex)
            elif spaceAbove == EMPY: # move forward when the block above is empty 
                newIndex = index  +  self.modifier
                self.checkObstaclesHelper(height+1, 0, 0, newIndex)
            elif spaceAbove == DOOR:
                return
    
    def calculateBlocksRequired(self):
        self.blocksRequired = 0
        for i in range (1, self.obstacleHeight):
            tempI = self.obstableIndex - (i * self.modifier)
            for j in range (i, self.obstacleHeight):
                tempI += self.level.width
                if self.level.layout[tempI] == EMPY:
                    self.blockGoals.append(tempI)
                    self.blocksRequired += 1
    
    def findBlocks(self, level):
        tempI = self.obstableIndex - 1
        tempX = tempI % level.width
        self.availableBlocks = 0
        for i in range (1, level.height+1):
            endRow = i * level.width
            for j in range (tempX, endRow):
                if level.layout[j] == BLCK:
                    self.blockLocs.append(j)
                    self.availableBlocks += 1
            tempX += level.width

    def findClosestBlock(self):
        self.closest = sys.maxint
        for i in range(0,len(self.blockLocs)):
            dist = self.blockLocs[i] - self.player.index
            # dist %= self.level.width
            if abs(dist) < self.closest:
                self.closest = dist

    def checkObstacles(self, level):
        self.taxiCabDistance()
        self.checkObstaclesHelper(0,0,0,self.player.index + self.modifier)
        if self.obstacleFlag:
            self.calculateBlocksRequired()
            self.findBlocks(level)
            if self.availableBlocks < self.blocksRequired:
                print "Level is unsolvable, not enough blocks"
                self.victory = True

    def generateMoveQuads(self):
        i,l,w = self.player.index, self.level.layout, self.level.width
        pg = []
        pg = [ l[i-w-1], l[i-w], l[i-w+1], l[i-1], l[i], l[i+1], l[i+w-1], l[i+w],l[i+w+1] ]
        self.moveQuadrants = []
        self.moveQuadrants.append([ pg[0], pg[1], pg[3], pg[4] ])
        self.moveQuadrants.append([ pg[1], pg[2], pg[4], pg[5] ])
        self.moveQuadrants.append([ pg[3], pg[4], pg[6], pg[7] ])
        self.moveQuadrants.append([ pg[4], pg[5], pg[7], pg[8] ])

    def analyzeMoveQuads(self, move):
        if move in self.fall:
            self.quadMoves.append("fall")
        if move in self.west:
            self.quadMoves.append("w")
        if move in self.nw:
            self.quadMoves.append("nw")
        if move in self.sw:
            self.quadMoves.append("sw")
        if move in self.east:
            self.quadMoves.append("e")
        if move in self.ne:
            self.quadMoves.append("ne")
        if move in self.se:
            self.quadMoves.append("se")
        if move in self.faceWest:
            self.quadMoves.append("fw")
        if move in self.faceEast:
            self.quadMoves.append("fe")
        if move in self.pickUp and not self.player.isHoldingBlock:
            self.quadMoves.append("pickup")
        if move in self.drop and self.player.isHoldingBlock:
            self.quadMoves.append("drop")

    def selectMove(self, moveCode):
        self.performMove(self.level, self.moveFuncs[moveCode][0], self.moveFuncs[moveCode][1])
        self.moveList.append(moveCode)

    def prioritizeWest(self):
        if "w" in self.quadMoves:
            self.selectMove("w")
        elif "nw" in self.quadMoves:
            self.selectMove("nw")
        elif "sw" in self.quadMoves:
            self.selectMove("sw")

    def prioritizeEast(self):
        if "e" in self.quadMoves:
            self.selectMove("e")
        elif "ne" in self.quadMoves:
            self.selectMove("ne")
        elif "se" in self.quadMoves:
            self.selectMove("se")

    def solveObstacle(self):
        self.findClosestBlock()
        playerWest = self.player.index - 1
        playerEast = self.player.index + 1
        if self.player.isHoldingBlock:
            if self.player.dir == WEST and playerWest in self.blockGoals:
                self.level.layout[playerWest] = BLCK
                self.selectMove("drop")
                self.blockGoals.remove(playerWest)
                self.obstacleFlag = False
                self.checkObstacles(self.level)
            if self.player.dir == EAST and playerEast in self.blockGoals:
                self.level.layout[playerEast] = BLCK
                self.selectMove("drop")
                self.blockGoals.remove(playerEast)
                self.obstacleFlag = False
                self.checkObstacles(self.level)
        if "pickup" in self.quadMoves and not self.player.isHoldingBlock and self.obstacleFlag:
            if self.player.dir == WEST:
                self.level.layout[playerWest] = EMPY
                removeValue = playerWest
            elif self.player.dir == EAST:
                self.level.layout[playerEast] = EMPY
                removeValue = playerEast
            self.selectMove("pickup")
            # self.blockLocs.remove(removeValue)
        elif self.closest < 0:  #block is to the west
            self.prioritizeWest()
        elif self.closest > 0:  #block is to the east
            self.prioritizeEast()

    def pickMove(self):
        if "fall" in self.quadMoves: # if fall is a valid move, it must be chosen.
            self.player.falling = True
            self.selectMove("fall")

        elif not self.obstacleFlag: # no obstables, pick moves that will get you closer to goal
            self.player.falling = False
            if self.modifier == -1:  # goal is west
                self.prioritizeWest()
            else:
                self.prioritizeEast()
        
        else:
            self.player.falling = False
            self.solveObstacle()



        self.quadMoves = []
    def solve(self):
        self.quadMoves = []
        self.locateStartAndGoalState()
        if self.goalPos.x == -1 or self.player.pos.x == -1:
            print("Level is unsolvable, player or door do not exist")
            return

        self.checkObstacles(self.level)

        while not self.victory:
            self.generateMoveQuads()
            for move in self.moveQuadrants:
                self.checkVictory(move)
                self.analyzeMoveQuads(move)
            self.pickMove()

        print("Solved!!!")

    def resetState(self):
        self.player.index = self.player.index2

    def stepThroughSolution(self):
        print(self.moveList)
        currentMove = self.moveList.pop(0)
        if currentMove == "drop":
            if self.player.dir == WEST:
                self.currentLevel.layout[self.player.index - 1] = BLCK
            else:
                self.currentLevel.layout[self.player.index + 1] = BLCK

        self.performMove(self.currentLevel, self.moveFuncs[currentMove][0], self.moveFuncs[currentMove][1])


#####################################################################
#####################################################################
####################         Program Loop        ####################
#####################################################################
#####################################################################

if __name__=='__main__':
    root = Tk()
    app = App(root)
    path = "./testLevels/"
    testFiles = ["level1.csv", "level2.csv","level3.csv","level4.csv",
                 "level5.csv","level6.csv","level7.csv","level8.csv"]
    gamePath = "./gameLevels/"
    gameFiles = ["level2.csv"]
    app.loadLevels(path, testFiles)
    # app.loadLevels(gamePath, gameFiles)

    numLevels = len(app.levels)

    # This code will begin to run after the gui is rendered
    def startFunction():
        for i in range(0, numLevels):
            solver = Solver()
            solver.setLevel(app.levels[i])
            app.displayLevel(solver.level)
            solver.solve()
            solver.resetState()
            
            raw_input("Press Enter to view solution...")
            while(len(solver.moveList) > 0):
                root.update()
                solver.stepThroughSolution()
                app.displayLevel(solver.currentLevel)
                time.sleep(0.2)
            raw_input("Press Enter to begin solving next level")

    root.after(2000, startFunction)
    app.run()
