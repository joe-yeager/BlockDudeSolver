import sys
from Tkinter import Tk, Frame, Canvas
from PIL import ImageTk
import csv
import time

EMPY, BRCK, BLCK, WEST, EAST, DOOR = 0,1,2,3,4,5
width, height = 0,0

#####################################################################
######################        Data Types        #####################
#####################################################################
class Coordinate:
    def __init__(s, x, y):
        s.x, s.y = x, y

class Level:
    def __init__(s, width,height,layout):
        s.width, s.height, s.layout = width, height, layout

#####################################################################
######################        App Class        ######################
#####################################################################
class App:
    def __init__(s, root):
        s.root = root
        s.root.title("Block Dude Solver")
        s.frame = Frame(s.root)
        s.frame.pack()
        s.canvas = Canvas(s.frame, bg="white", width=(width*24)+100, height=(height*24)+100)
        s.canvas.pack()
        s.levels,s.imageArray = [],[]
        filedir = "./assets/"
        filenames = ["brick.png","block.png","dudeLeft.png","dudeRight.png","door.png"]
           
        s.imageArray.append("")
        for i in range(0,len(filenames)):
            s.imageArray.append(ImageTk.PhotoImage(file=filedir + filenames[i]))

    def displayLevel(s,level):
        s.canvas.delete("all")
        s.updateCanvasDems(level.width,level.height)
        length = len(level.layout)
        row = 0
        for i in range(0,length):
            if i % (level.width) == 0:
                row += 1
            if level.layout[i] != EMPY:
                x = ((i%(level.width))*24) + 65
                y = (row*24) + 40
                s.canvas.create_image(x,y, image=s.imageArray[level.layout[i]])

    def loadLevels(s,path, fileArray):
        length = len(fileArray)
        for i in range(0,length):
            with open(path + fileArray[i], 'rb') as f:
                reader = csv.reader(f)
                reader = list(reader).pop(0)
                level = map(int,reader)
                width = level.pop(0)
                height = level.pop(0)
                newLevel = Level(width,height,level)
                s.levels.append(newLevel)

    def updateCanvasDems(s,width, height):
        newWidth = (width*24)+100
        newHeight = (height*24)+100
        s.canvas.config(width=newWidth,height=newHeight)

    def run(s):
        s.root.mainloop()

#####################################################################
######################      Player Class       ######################
#####################################################################
class Player:
    def __init__(s):
        s.pos = Coordinate(0,0)
        s.dir, s.index = 0, 0
        s.isHoldingBlock, s.falling = False, False

    def setPos(s,x,y):
        s.pos.x, s.pos.y = x, y

    def setDirection(s, playerValue):
        s.dir = playerValue

    def moveEast(s):
        s.pos.x += 1
        s.index += 1

    def moveWest(s):
        s.pos.x -= 1
        s.index -= 1

    def moveNEast(s, width):
        s.moveEast()
        s.pos.y += 1
        s.index -= (width)

    def moveNWest(s,width):
        s.moveWest()
        s.pos.y += 1
        s.index -= (width)

    def fall(s, width):
        s.pos.y -= 1;
        s.index += (width)

    def pickupBlock(s):
        s.isHoldingBlock = True

    def dropBlock(s):
        s.isHoldingBlock = False

#####################################################################
####################        Solver Class        #####################
#####################################################################
class Solver:
    def __init__(s):
        
        s.player = Player()
        s.victory = False;
        s.validMoves = {
            "e": [[0,0,4,0]],
            "w": [[0,0,0,3]],
            "fe": [[0,0,3,0],[0,0,3,1],[0,0,3,2]],
            "fw": [[0,0,0,4],[0,0,1,4],[0,0,2,4]],
            "nw": [[0,0,1,3],[0,0,2,3]],
            "ne": [[0,0,4,1],[0,0,4,2]],
            "pu": [[0,0,4,2],[0,0,2,3]],
            "dr": [[0,0,4,0], [0,0,0,3]],
            "fa": [[3,1,0,1],[3,1,0,0],[3,0,0,0],[3,2,0,1],[3,2,0,0],[3,1,0,2],[3,2,0,2],[3,0,0,1],[3,0,0,2],
                            [1,4,1,0],[1,4,0,0],[0,4,0,0],[2,4,1,0],[2,4,0,0],[1,4,2,0],[2,4,2,0],[0,4,1,0],[0,4,2,0]]
        }
        s.V = {
            "e":    [[0,0,4,5]],
            "w":    [[0,0,5,3]],
            "nw":   [[5,0,1,3],[5,0,2,3]],
            "ne":   [[0,5,4,1],[0,5,4,2]],
            "fa": [[3,1,5,1],[3,1,5,0],[3,0,5,0],[3,2,5,1],[3,2,5,0],[3,1,5,2],[3,2,5,2],[3,0,5,1],[3,0,5,2],
                        [1,4,1,5],[1,4,0,5],[0,4,0,5],[2,4,1,5],[2,4,0,5],[1,4,2,5],[2,4,2,5],[0,4,1,5],[0,4,2,5]]
        }
        s.obstacleFlag,s.trapFlag = False, False
        s.obstacleHeight,s.blocksRequired,s.availableBlocks = 0,0,0
        s.blockGoals, s.blockLocs, s.moveQuadrants,s.moveList,s.quadMoves = [],[],[],[],[]
    
    def prettyPrintLevel(s):
        lower, uppper = 0, 0
        temp = []
        length = len(s.level.layout)
        for i in range(0, length/s.level.width):
            upper += s.level.width
            for k in range(lower, upper):
                temp.append(s.level.layout[k])
            print(temp)
            temp = []
            lower += s.level.width

    def setLevel(s,level):
        s.level = Level(level.width,level.height,list(level.layout) )
        s.currentLevel = Level(s.level.width, s.level.height, list(s.level.layout) )
        s.length = len(s.level.layout)
        s.moveFuncs = {  #These depend on properties of the level, so define it after they are set
            "fa"    : [s.player.fall, s.level.width],
            "w"     : [s.player.moveWest, None],
            "e"     : [s.player.moveEast, None],
            "nw"    : [s.player.moveNWest, s.level.width],
            "ne"    : [s.player.moveNEast, s.level.width],
            "fw"    : [s.player.setDirection, WEST],
            "fe"    : [s.player.setDirection, EAST],
            "pu"    : [s.player.pickupBlock, None],
            "dr"    : [s.player.dropBlock, None],
        }

    def locateStartAndGoalState(s):
        s.goalPos = Coordinate(-1,-1)
        s.player.setPos(-1,-1)
        for i in range(0,s.length):
            if s.level.layout[i] == DOOR:
                x, y = i % s.level.width, (i - (i%s.level.width))/s.level.width
                s.goalPos = Coordinate(x,y)
            elif s.level.layout[i] == WEST or s.level.layout[i] == EAST:
                x, y = i % s.level.width, (i - (i%s.level.width))/s.level.width
                s.player.setPos(x,y)
                s.player.index,s.player.index2 = i,i
                s.player.setDirection(s.level.layout[i])

    def taxiCabDistance(s):
        s.taxiCab = Coordinate(s.goalPos.x-s.player.pos.x, s.goalPos.y-s.player.pos.y)
        s.modifier = s.taxiCab.x / abs(s.taxiCab.x)

    def checkVictory(s, move):
        for k,v in s.V.iteritems():
            if move in v:
                s.moveList.append(k)
                s.victory = True
                break

    def performMove(s,level, move, arg=None):
        oldIndex = s.player.index
        if arg == None:
            move()
        else:
            move(arg)
        level.layout[oldIndex] = 0
        level.layout[s.player.index] = s.player.dir

    def checkObstaclesHelper(s, prevHeight, height, depth, index):
        if height - prevHeight > 1:
            s.obstacleFlag = True
            s.obstacleHeight, s.obstableIndex = height, index
            if depth >= 2:
                s.trapFlag = True
        if index % s.level.width ==  0 or index < 0 or index > s.length or s.level.layout[index] == DOOR:
            return

        elif s.level.layout[index] == EMPY:
            if s.obstacleFlag:
                return
            spaceBelow = s.level.layout[index + s.level.width]
            if spaceBelow == BLCK or spaceBelow == BRCK: # If space below is brick/block go forward
                newIndex = index + s.modifier
                s.checkObstaclesHelper(0, 0, 0, newIndex)
            elif spaceBelow == EMPY: # If space below is brick/block go down
                newIndex = index  +  s.level.width
                s.checkObstaclesHelper(0, 0, depth+1, newIndex)
            elif spaceBelow == DOOR:
                return

        elif s.level.layout[index] == BRCK or s.level.layout[index] == BLCK:
            spaceAbove = s.level.layout[index - s.level.width]
            if spaceAbove == BLCK or spaceAbove == BRCK: # move up when the block above is a block
                newIndex = index -  (height * s.level.width)
                s.checkObstaclesHelper(prevHeight, height+1, 0, newIndex)
            elif spaceAbove == EMPY: # move forward when the block above is empty 
                newIndex = index  +  s.modifier
                s.checkObstaclesHelper(height+1, 0, 0, newIndex)
            elif spaceAbove == DOOR:
                return
    
    def calculateBlocksRequired(s):
        s.blocksRequired = 0
        for i in range (1, s.obstacleHeight):
            tempI = s.obstableIndex - (i * s.modifier)
            for j in range (i, s.obstacleHeight):
                tempI += s.level.width
                if s.level.layout[tempI] == EMPY:
                    s.blockGoals.append(tempI)
                    s.blocksRequired += 1
    
    def findBlocks(s, level):
        tempI = s.obstableIndex - 1
        tempX = tempI % level.width
        s.availableBlocks = 0
        for i in range (1, level.height+1):
            endRow = i * level.width
            for j in range (tempX, endRow):
                if level.layout[j] == BLCK:
                    s.blockLocs.append(j)
                    s.availableBlocks += 1
            tempX += level.width

    def findClosestSubgoal(s, priority, restriction):
        s.closest = sys.maxint
        for i in range(0,len(priority)):
            if priority[i] not in restriction:
                dist = (priority[i] % s.level.width) - (s.player.index % s.level.width)
                if abs(dist) < s.closest:
                    s.closest = dist

    def checkObstacles(s, level):
        s.taxiCabDistance()
        s.obstacleFlag = False
        s.checkObstaclesHelper(0,0,0,s.player.index + s.modifier)
        if s.obstacleFlag:
            s.calculateBlocksRequired()
            s.findBlocks(level)
            if s.availableBlocks < s.blocksRequired:
                print "Level is unsolvable, not enough blocks"
                s.victory = True

    def generateMoveQuads(s):
        i,l,w = s.player.index, s.level.layout, s.level.width
        pg = [ l[i-w-1], l[i-w], l[i-w+1], l[i-1], l[i], l[i+1], l[i+w-1], l[i+w],l[i+w+1] ]
        s.moveQuadrants = []
        s.moveQuadrants.append([ pg[0], pg[1], pg[3], pg[4] ])
        s.moveQuadrants.append([ pg[1], pg[2], pg[4], pg[5] ])
        s.moveQuadrants.append([ pg[3], pg[4], pg[6], pg[7] ])
        s.moveQuadrants.append([ pg[4], pg[5], pg[7], pg[8] ])

    def analyzeMoveQuads(s, move):
        for k,v in s.validMoves.iteritems():
            if move in v:
                if k == "pu" and not s.player.isHoldingBlock:
                    s.quadMoves.append(k)
                elif k == "dr" and s.player.isHoldingBlock:
                    s.quadMoves.append(k)
                elif k != "dr" or k!= "pu":
                    s.quadMoves.append(k)

    def selectMove(s, moveCode):
        print moveCode
        s.performMove(s.level, s.moveFuncs[moveCode][0], s.moveFuncs[moveCode][1])
        s.moveList.append(moveCode)

    def prioritizeMoves(s, moveSet):
        for move in s.quadMoves:
            if move in moveSet:
                s.selectMove(move)

    def checkPriority(s, prioritizer):
        if prioritizer < 0:  #block is to the west
            s.prioritizeMoves(["w","nw","fw"])
        else:  #block is to the east
            s.prioritizeMoves(["e","ne","fe"])

    def solveObstacle(s):
        s.findClosestSubgoal(s.blockLocs, s.blockGoals)
        playerWest, playerEast = s.player.index - 1, s.player.index + 1
        playerAdj = playerWest if s.player.dir == WEST else playerEast
        if s.player.isHoldingBlock:
            if playerAdj in s.blockGoals:
                s.level.layout[playerAdj] = BLCK
                s.blockLocs.append(playerAdj)
                s.selectMove("dr")
                s.checkObstacles(s.level)
            else:
                s.findClosestSubgoal(s.blockGoals, s.blockLocs)
                s.checkPriority(s.closest)
        elif "pu" in s.quadMoves and playerAdj not in s.blockGoals:
            s.level.layout[playerAdj] = EMPY
            s.selectMove("pu")
            s.blockLocs.remove(playerAdj)
        else:
            s.checkPriority(s.closest) 

    def pickMove(s):
        if "fa" in s.quadMoves: # if fall is a valid move, it must be chosen.
            s.player.falling = True
            s.selectMove("fa")
        elif not s.obstacleFlag: # no obstables, pick moves that will get you closer to goal
            s.player.falling = False
            s.checkPriority(s.modifier)
        else:
            s.player.falling = False
            s.solveObstacle()
        s.quadMoves = []

    def solve(s):
        s.locateStartAndGoalState()
        if s.goalPos.x == -1 or s.player.pos.x == -1:
            return

        s.checkObstacles(s.level)
        while not s.victory:
            s.generateMoveQuads()
            for move in s.moveQuadrants:
                s.checkVictory(move)
                s.analyzeMoveQuads(move)
            s.pickMove()
        print("Solved!!!")

    def resetState(s):
        s.player.index = s.player.index2

    def stepThroughSolution(s):
        print(s.moveList)
        currentMove = s.moveList.pop(0)
        if currentMove == "dr":
            playerAdj = s.player.index - 1 if s.player.dir == WEST else s.player.index + 1
            s.currentLevel.layout[playerAdj] = BLCK
        s.performMove(s.currentLevel, s.moveFuncs[currentMove][0], s.moveFuncs[currentMove][1])

#####################################################################
####################         Program Loop        ####################
#####################################################################
if __name__=='__main__':
    root = Tk()
    app = App(root)
    path, gamePath = "./testLevels/", "./gameLevels/"
    testFiles = ["level1.csv", "level2.csv","level3.csv","level4.csv",
                 "level5.csv","level6.csv","level7.csv","level8.csv"]
    gameFiles = ["level1.csv","level2.csv"]
    # app.loadLevels(path, testFiles)
    app.loadLevels(gamePath, gameFiles)

    def startFunction():
        for i in range(0, len(app.levels)):
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
