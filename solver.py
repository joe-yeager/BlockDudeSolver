import sys
from Tkinter import Tk, Frame, Canvas
from PIL import ImageTk
import csv
import time
import math
from collections import OrderedDict
EMPY = 0
BRCK = 1
BLCK = 2
WEST = 3
EAST = 4
DOOR = 5
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

    def copy(s, level):
        s.width = level.width
        s.height = level.height
        s.layout = list(level.layout)

class Node:
    def __init__(s):
        s.move = None
        s.moveList = []
        s.level = None
        s.player = None
        s.blockLocs = None
        s.blockGoals = None
        s.children = []


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
        s.dir, s.index,s.index2 = 0, 0, 0
        s.isHoldingBlock, s.falling = False, False

    def copy(s, player):
        s.setPos(player.pos.x, player.pos.y)
        s.dir = player.dir
        s.index = player.index
        s.index2 = player.index2
        s.isHoldingBlock = player.isHoldingBlock
        s.falling = player.falling

    def setPos(s,x,y):
        s.pos.x, s.pos.y = x, y

    def setDirection(s, playerValue):
        s.dir = playerValue

    def moveEast(s):
        s.index += 1

    def moveWest(s):
        s.index -= 1

    def moveNEast(s, width):
        s.moveEast()
        s.index -= (width)

    def moveNWest(s,width):
        s.moveWest()
        s.index -= (width)

    def fall(s, width):
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
        
        s.victory = False;
        s.dt = OrderedDict()
        s.dt[0] = Node()
        s.dt[0].moveList = []
        s.dt[0].children = s.getChildren(0)
        s.validMoves = {
            "e":  [[0,0,4,0]],
            "w":  [[0,0,0,3]],
            "fe": [[0,0,3,0],[0,0,3,1],[0,0,3,2],[0,1,3,1],[0,2,3,2],[0,2,3,1],[0,1,3,2]],
            "fw": [[0,0,0,4],[0,0,1,4],[0,0,2,4],[1,0,1,4],[2,0,2,4],[2,0,1,4],[2,0,1,4]],
            "nw": [[0,0,1,3],[0,0,2,3]],
            "ne": [[0,0,4,1],[0,0,4,2]],
            "pu": [[0,0,4,2],[0,0,2,3]],
            "dr": [[0,0,4,0], [0,0,0,3],[0,0,4,1]],
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
        s.cyclicalMoves = [
            ["w", "fa", "fe", "ne"],
            ['pu', 'e', 'fw', 'dr'],
            ['pu', 'w', 'fe', 'dr'],
            ["e", "fa", "fw", "nw"],
            ["fw", "w", "fe", "e"],
            ["fe", "e", "fw", "w"],
            ["w", "w", "fe", "e"],
            ["e", "e", "fw", "w"],
            ["w", "w", "w", "fe"],
            ["e", "e", "e", "fw"],
            ["w", "fe", "e"],
            ["e", "fw", "w"],
            ["ne", "fw", "w"],
            ["nw", "fe", "e"],
            ["w", "w", "fe"],
            ["e", "e", "fw"],
            ["fw", "fe"],
            ["fe", "fw"],
            ["dr", "pu"],
            ["pu", "dr"]
        ]

        s.spacesBelow = []
        s.obstacleFlag, s.trapFlag = False, False
        s.obstacleHeights = []
        s.blocksRequired = []
        s.availableBlocks = 0
        s.blockGoals, s.blockLocs, s.moveQuadrants,s.moveList,s.quadMoves = [],[],[],[],[]
    
    def prettyPrintLevel(s, level):
        lower, upper = 0, 0
        temp = []
        length = len(level.layout)
        for i in range(0, length/level.width):
            upper += level.width
            for k in range(lower, upper):
                temp.append(level.layout[k])
            print(temp)
            temp = []
            lower += level.width

    def setLevel(s,level):
        s.dt[0].level = Level(level.width,level.height,list(level.layout) )
        s.level = Level(level.width,level.height,list(level.layout) )
        s.currentLevel = s.dt[0].level
        s.length = len(s.level.layout)
        s.dt[0].player = Player()

    def locateStartAndGoalState(s):
        s.goalPos = Coordinate(-1,-1)
        s.dt[0].player.setPos(-1,-1)
        for i in range(0,s.length):
            if s.level.layout[i] == DOOR:
                x, y = i % s.level.width, (i - (i%s.level.width))/s.level.width
                s.goalPos = Coordinate(x,y)
            elif s.level.layout[i] == WEST or s.level.layout[i] == EAST:
                x, y = i % s.level.width, (i - (i%s.level.width))/s.level.width
                s.dt[0].player.setPos(x,y)
                s.dt[0].player.index,s.dt[0].player.index2 = i,i
                s.dt[0].player.setDirection(s.level.layout[i])

    def taxiCabDistance(s, player):
        s.taxiCab = Coordinate(s.goalPos.x - player.pos.x, s.goalPos.y - player.pos.y)
        s.modifier = s.taxiCab.x / abs(s.taxiCab.x)

    def calculateBlocksRequired(s):
        s.blocksRequired = 0
        s.blockGoals = []
        for k in range(0, len(s.obstacleIndices) ):
            tempI = s.obstacleIndices[k] + (s.level.width)
            reset = 0
            for l in range(0, len(s.obstacleHeights) ):
                for i in range (1, s.obstacleHeights[l]):
                    for j in range (1, i+1):
                        reset += s.modifier
                        tempI -= s.modifier
                        try:
                            if s.level.layout[tempI] != BRCK:
                                s.blockGoals.append(tempI)
                                s.blocksRequired += 1
                        except IndexError:
                            break
                    tempI += s.level.width + reset

    def findBlocks(s, level):
        s.availableBlocks = 0
        s.blockLocs = []
        for k in range(0, len(s.obstacleIndices) ):
            tempX = s.obstacleIndices[k] % level.width
            reset = 0
            for l in range(0, len(s.obstacleHeights) ):
                for i in range (1, level.height+1):
                    endRow = i * level.width
                    for j in range (tempX, endRow):
                        if level.layout[j] == BLCK:
                            if j not in s.blockLocs:
                                s.blockLocs.append(j)
                                s.availableBlocks += 1
                    tempX += level.width

    def findClosestSubgoal(s, priority, restriction):
        s.closest = sys.maxint
        for i in range(0,len(priority)):
            if priority[i] not in restriction:
                dist = (priority[i] % s.level.width) - (s.player.index % s.level.width)
                if abs(dist) < s.closest and dist != 0:
                    s.closest = dist

    def checkObstaclesHelper(s, prevHeight, height, depth, index, level):
        spaceAbove = level.layout[index - level.width]
        if (height + 1) - prevHeight > 1 and spaceAbove == EMPY:
            s.obstacleFlag = True
            s.obstacleHeights.append(height + 1)
            s.obstacleIndices.append(index)
            if depth >= 2:
                s.trapFlag = True
        if index % level.width ==  0 or index < 0 or index > s.length or level.layout[index] == DOOR:
            return

        elif level.layout[index] == EMPY:
            spaceBelow = level.layout[index + level.width]
            if spaceBelow == BLCK or spaceBelow == BRCK: # If space below is brick/block go forward
                newIndex = index + s.modifier
                s.checkObstaclesHelper(0, 0, 0, newIndex, level)
            elif spaceBelow == EMPY: # If space below is brick/block go down
                newIndex = index  +  s.level.width
                s.checkObstaclesHelper(0, 0, depth+1, newIndex, level)
            elif spaceBelow == DOOR:
                return

        elif level.layout[index] == BRCK or level.layout[index] == BLCK:
            spaceAbove = level.layout[index - level.width]
            if spaceAbove == BLCK or spaceAbove == BRCK: # move up when the block above is a block
                newIndex = index -  level.width
                s.checkObstaclesHelper(prevHeight, height+1, 0, newIndex, level)
            elif spaceAbove == EMPY: # move forward when the block above is empty 
                newIndex = index  +  s.modifier
                s.checkObstaclesHelper(height+1, 0, 0, newIndex, level)
            elif spaceAbove == DOOR:
                return

    def checkObstaclesSolvable(s, index):
        s.obstacleIndices = []
        s.taxiCabDistance(s.dt[index].player)
        s.obstacleFlag = False
        s.checkObstaclesHelper(0,0,0, s.dt[index].player.index + s.modifier, s.dt[index].level)
        if s.obstacleFlag:
            s.calculateBlocksRequired()
            s.findBlocks(s.dt[index].level)
            if s.availableBlocks < s.blocksRequired:
                print "Level is unsolvable, not enough blocks"
                s.victory = True

    def checkObstacles(s, index):
        s.obstacleIndices = []
        s.taxiCabDistance(s.dt[index].player)
        s.obstacleFlag = False
        s.checkObstaclesHelper(0,0,0, s.dt[index].player.index + s.modifier, s.dt[index].level)


    def checkVictory(s, move, moveList):
        for k,v in s.V.iteritems():
            if move in v:
                moveList.append(k)
                s.moveList = list(moveList)
                s.victory = True
                break

    def generateMoveQuads(s, i, l, w, level, moveList):
        pg = [ l[i-w-1], l[i-w], l[i-w+1], l[i-1], l[i], l[i+1], l[i+w-1], l[i+w],l[i+w+1] ]
        s.moveQuadrants = []
        s.moveQuadrants.append([ pg[0], pg[1], pg[3], pg[4] ])
        s.moveQuadrants.append([ pg[1], pg[2], pg[4], pg[5] ])
        s.moveQuadrants.append([ pg[3], pg[4], pg[6], pg[7] ])
        s.moveQuadrants.append([ pg[4], pg[5], pg[7], pg[8] ])

    def addMove(s, move):
        if move not in s.quadMoves:
            s.quadMoves.append(move)

    def analyzeMoveQuads(s, move, index):
        for k,v in s.validMoves.iteritems():
            if move in v:
                if k == "pu" and not s.dt[index].player.isHoldingBlock:
                    s.addMove(k)
                elif k == "dr" and s.dt[index].player.isHoldingBlock:
                    s.addMove(k)
                elif k != "dr" and k != "pu":
                    s.addMove(k)

    def checkDown(s,index, level):
        if level.layout[index] != EMPY:
            index -= level.width
            return index
        return s.checkDown(index + level.width, level)

    def getSpaceBelow(s, index, level):
        if level.layout[index] != EMPY:
            s.spacesBelow.push(index)
            return 
        return s.getSpaceBelow(index + level.width, level)

    def performMove(s,level,data, player, move):
        oldIndex = player.index

        if move == "fa":
            player.fall(s.level.width)
        elif move == "w":
            player.moveWest()
        elif move == "e":
            player.moveEast()
        elif move == "nw":
            player.moveNWest(s.level.width)
        elif move == "ne":
            player.moveNEast(s.level.width)
        elif move == "fw":
            player.setDirection(WEST)
        elif move == "fe":
            player.setDirection(EAST)
        elif move == "pu":
            player.pickupBlock()
            playerAdj = player.index - 1 if player.dir == WEST else player.index + 1
            level.layout[playerAdj] = EMPY          
        elif move == "dr":
            player.dropBlock()
            playerAdj = player.index - 1 if player.dir == WEST else player.index + 1
            playerAdj = s.checkDown(playerAdj,level)
            level.layout[playerAdj] = BLCK
            return 

        level.layout[oldIndex] = 0
        level.layout[player.index] = player.dir

    def getParentIndex(s):
        s.par =  int ( math.floor( (s.i - 1) / 3 ) )
        if s.par < 0:
            s.par = 0

    def getGrandParentIndex(s, index):
        newGP =  int ( math.floor( (index - 1) / 3 ) )
        if newGP < 0:
            newGP = 0
        return newGP

    def getNthChild(s,index, nth):
        return 3 * index + 1 + nth

    def getChildren(s,index):
        return [ s.getNthChild(index,0), s.getNthChild(index, 1), s.getNthChild(index, 2)]

    def addToTree(s, tree, parent, move):
        s.i = s.dt[s.par].children.pop(0)
        newChild = Node()
        newChild.move = move
        newChild.moveList = list(parent.moveList)
        newChild.moveList.append(move)
        print "moveList: ", newChild.moveList
        newChild.player, newChild.level = Player(), Level(0,0,0)
        newChild.player.copy(parent.player)
        newChild.level.copy(parent.level)
        newChild.children = s.getChildren(s.i)
        newChild.blockLocs = list(s.blockLocs)
        newChild.blockGoals = list(s.blockGoals)
        s.performMove(newChild.level,newChild, newChild.player, move)
        tree[s.i] = newChild

    def prioritizeMoves(s, move, moves):
        if move in moves:
            s.addToTree(s.dt, s.dt[s.par], move)

    def checkCycles(s, move):
        s.isNotACycle = True
        gp =  s.getGrandParentIndex(s.par)
        ggp = s.getGrandParentIndex(gp)

        try:
            moveSeq = [s.dt[ggp].move, s.dt[gp].move, s.dt[s.par].move, move]
            for i in range(0, 3):
                if moveSeq[i:] in s.cyclicalMoves:
                    print "pruning"
                    s.isNotACycle = False
                    break

        except KeyError:
            return

    def pickMoves(s):

        if "fa" in s.quadMoves:  # If fall is a choice, it is the only choice.
            s.addToTree(s.dt, s.dt[s.par], "fa")
            s.counter += 1
            return
        else:
            if s.obstacleFlag:
                s.checkObstacles(s.par)
            for move in s.quadMoves:
                playerAdj = s.dt[s.par].player.index - 1 if s.dt[s.par].player.dir == WEST else s.dt[s.par].player.index + 1
                s.checkCycles(move)
                if not s.obstacleFlag:
                    if s.modifier < 0:
                        s.prioritizeMoves(move,["w","nw","fw"])
                    else:
                        s.prioritizeMoves(move,["e","ne","fe"])
                elif s.isNotACycle:
                    if move == "dr":
                        if s.dt[s.par].player.isHoldingBlock:
                            if playerAdj in s.blockGoals and s.dt[s.par].level.layout[playerAdj] == EMPY:
                                s.addToTree(s.dt, s.dt[s.par], move)
                    elif move == "pu":
                        if not s.dt[s.par].player.isHoldingBlock:
                             if not s.checkCreatedObstacle(s.dt[s.par].player,s.dt[s.par].level):
                                s.addToTree(s.dt, s.dt[s.par], move)
                    else:
                        s.addToTree(s.dt, s.dt[s.par], move)
            s.counter += 1

    def checkCreatedObstacle(s, player, level):
        height = 0
        xCoord = player.index % level.width

        if player.dir == WEST:
            if xCoord <= 2:
                return False
            indexToCheck = player.index - 2
        else:
            if xCoord >= level.width - 3:
                return False
            indexToCheck = player.index + 2
        
        while indexToCheck > 0:
            if level.layout[indexToCheck] != EMPY:
                height += 1
                indexToCheck -= level.width
            else:
                break

        return height > 1


    def solve(s):
        s.locateStartAndGoalState()
        if s.goalPos.x == -1 or s.dt[0].player.pos.x == -1:
            print ("Level unsolvable, either door or player is missing(Or both).")
            return

        s.i = 1
        s.checkObstaclesSolvable(0)
        startTime = time.clock()
        s.counter = 0
        while not s.victory:
            s.par = s.dt.keys()[s.counter]
            s.generateMoveQuads(s.dt[s.par].player.index, s.dt[s.par].level.layout, s.dt[0].level.width,s.dt[s.par].level, s.dt[s.par].moveList)
            for move in s.moveQuadrants:
                s.checkVictory(move, s.dt[s.par].moveList)
                if s.victory:
                    break
                s.analyzeMoveQuads(move,s.par)
            if not s.victory:
                s.pickMoves()
            else:
                break
            s.quadMoves = []

        endTime = time.clock()
        print "Time taken(secs): ", endTime - startTime
        print("Solved!!!")

    def resetState(s):
        s.dt[0].player.index = s.dt[0].player.index2

    def stepThroughSolution(s):
        print(s.moveList)
        currentMove = s.moveList.pop(0)
        s.performMove(s.dt[0].level, s,s.dt[0].player, currentMove)

#####################################################################
####################         Program Loop        ####################
#####################################################################
if __name__=='__main__':
    root = Tk()
    app = App(root)
    path, gamePath = "./testLevels/", "./gameLevels/"
    testFiles = [
    # "level1.csv", 
    # "level2.csv",
    # "level3.csv",
    # "level4.csv",
    # "level5.csv",
    "level6.csv",
    "level7.csv"]
        # "level8.csv"]
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
                time.sleep(0.1)
            if i != len(app.levels) -1:
                raw_input("Press Enter to begin solving next level")
            else:
                raw_input("Done!  Press enter to exit.")

        sys.exit(0)
    startFunction()
    root.after(500, startFunction)
    app.run()
