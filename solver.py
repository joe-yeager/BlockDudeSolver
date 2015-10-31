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
        self.state = None
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
        self.drop = [[2,0,4,0], [0,2,0,3]]
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
        self.trapFlag = False
        self.moveQuadrants = []
        self.moveList = []
    
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
            return
        if depth >= 2:
            self.trapFlag = True
        if index % self.level.width ==  0 or index < 0 or index > self.length or self.level.layout[index] == DOOR:
            return

        elif self.level.layout[index] == EMPY:
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

    def checkObstacles(self):
        self.taxiCabDistance()
        self.checkObstaclesHelper(0,0,0,self.player.index + self.modifier)

    def generateMoveQuads(self):
        i,l,w = self.player.index, self.level.layout, self.level.width
        pg = []
        pg = [ l[i-w-1], l[i-w], l[i-w+1], l[i-1], l[i], l[i+1], l[i+w-1], l[i+w],l[i+w+1] ]
        self.moveQuadrants = []
        self.moveQuadrants.append([ pg[0], pg[1], pg[3], pg[4] ])
        self.moveQuadrants.append([ pg[1], pg[2], pg[4], pg[5] ])
        self.moveQuadrants.append([ pg[3], pg[4], pg[6], pg[7] ])
        self.moveQuadrants.append([ pg[4], pg[5], pg[7], pg[8] ])

    # Fill the tree from left to right
    def addMove(self, moveNumber, move, node):
        if node.left == None:
            node.left = Tree()
            # node.left.
        elif node.middle == None:
            node.middle = Tree()
        elif node.right == None:
            node.right = Tree()

    def analyzeMoveQuads(self, move):

        if self.level.layout[self.player.index] == WEST and self.modifier == -1:
            if move in self.fall:
                self.quadMoves.append("fall")
            elif move in self.west:
                self.quadMoves.append("w")
            elif move in self.nw:
                self.quadMoves.append("nw")
            elif move in self.sw:
                self.quadMoves.append("sw")

        elif self.level.layout[self.player.index] == EAST and self.modifier == 1:
            if move in self.fall:
                self.quadMoves.append("fall")
            elif move in self.east:
                self.quadMoves.append("e")
            elif move in self.ne:
                self.quadMoves.append("ne")
            elif move in self.se:
                self.quadMoves.append("se")

    def pickMove(self):
        if not self.obstacleFlag: # no obstables, pick moves that will get you closer to goal
            if "fall" in self.quadMoves: # if fall is a valid move, it must be chosen.
                self.player.falling = True
                self.performMove(self.level, self.moveFuncs["fall"][0], self.moveFuncs["fall"][1])
                self.moveList.append("fall")
            elif self.modifier == -1:  # goal is west
                self.player.falling = False
                if "w" in self.quadMoves:
                    self.performMove(self.level, self.moveFuncs["w"][0], self.moveFuncs["w"][1])
                    self.moveList.append("w")
                elif "nw" in self.quadMoves:
                    self.performMove(self.level, self.moveFuncs["nw"][0], self.moveFuncs["nw"][1])
                    self.moveList.append("nw")
                elif "sw" in self.quadMoves:
                    self.performMove(self.level, self.moveFuncs["sw"][0], self.moveFuncs["sw"][1])
                    self.moveList.append("sw")

            else:
                self.player.falling = False
                if "e" in self.quadMoves:
                    self.performMove(self.level, self.moveFuncs["e"][0], self.moveFuncs["e"][1])
                    self.moveList.append("e")
                elif "ne" in self.quadMoves:
                    self.performMove(self.level, self.moveFuncs["ne"][0], self.moveFuncs["ne"][1])
                    self.moveList.append("ne")
                elif "se" in self.quadMoves:
                    self.performMove(self.level, self.moveFuncs["se"][0], self.moveFuncs["se"][1])
                    self.moveList.append("se")

        self.quadMoves = []

    def solve(self):
        self.quadMoves = []
        self.locateStartAndGoalState()
        if self.goalPos.x == -1 or self.player.pos.x == -1:
            print("Level is unsolvable, player or door do not exist")
            return

        self.checkObstacles()
        decisionTree = Tree()
        while not self.victory:
            self.generateMoveQuads()
            for move in self.moveQuadrants:
                self.checkVictory(move)
                self.analyzeMoveQuads(move)
            self.pickMove()
        print("Solved!!!")

    def translateMove(self, move):
        self.performMove(self.currentLevel, self.moveFuncs[move][0], self.moveFuncs[move][1])

    def resetState(self):
        self.player.index = self.player.index2

    def stepThroughSolution(self):
        print(self.moveList)
        currentMove = self.moveList.pop(0)
        self.translateMove(currentMove)

#####################################################################
#####################################################################
####################         Program Loop        ####################
#####################################################################
#####################################################################

if __name__=='__main__':
    root = Tk()
    app = App(root)
    path = "./testLevels/"
    testFiles = ["level1.csv", "level2.csv","level3.csv","level4.csv","level5.csv","level6.csv","level7.csv","level8.csv"]
    app.loadLevels(path, testFiles)
    solver = Solver()

    numLevels = len(app.levels)

    solver.setLevel(app.levels[1])
    app.displayLevel(solver.level)

    # This code will begin to run after the gui is rendered
    def startFunction():
        app.displayLevel(solver.level)
        solver.solve()
        solver.resetState()
                
        while(len(solver.moveList) > 0):
            root.update()
            solver.stepThroughSolution()
            app.displayLevel(solver.currentLevel)
            time.sleep(0.2)

    root.after(2000, startFunction)
    app.run()
