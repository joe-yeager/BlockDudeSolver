import sys
from Tkinter import Tk, Frame, Canvas
from PIL import ImageTk
import csv
import time
import math
from collections import OrderedDict
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

    def copy(s, level):
        s.width = level.width
        s.height = level.height
        s.layout = list(level.layout)

class Node:
    def __init__(s):
        s.move = None
        s.level = Level(0,0,0)
        s.player = Player()
        s.moveList, s.children, s.blockLocs, s.blockGoals = [],[],[],[]

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
        s.levels, s.imageArray = [],[]
        filenames = ["brick.png","block.png","dudeLeft.png","dudeRight.png","door.png"]

        s.imageArray.append("")
        for i in range(0,len(filenames)):
            s.imageArray.append(ImageTk.PhotoImage(file="./assets/" + filenames[i]))

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
        return s.getAdj()

    def dropBlock(s):
        s.isHoldingBlock = False
        return s.getAdj()

    def setIndex(s, index):
        s.index = index

    def getAdj(s):
        if s.dir == WEST:
            return s.index - 1
        else:
            return s.index + 1

#####################################################################
####################        Solver Class        #####################
#####################################################################
class Solver:
    def __init__(s):
        
        # Set up the search tree root node
        s.dt = OrderedDict()
        s.dt[0] = Node()
        s.root = s.dt[0]
        s.root.moveList = []
        s.root.children = s.getChildren(0)

        s.obstacleFlag, s.victory = False, False
        s.spacesBelow, s.obstacleHeights, s.blockGoals, s.blockLocs, s.moveQuadrants, s.moveList,s.quadMoves = [],[],[],[],[],[],[]

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

        s.victoryMoves = {
            "e":    [[0,0,4,5]],
            "w":    [[0,0,5,3]],
            "nw":   [[5,0,1,3],[5,0,2,3]],
            "ne":   [[0,5,4,1],[0,5,4,2]],
            "fa": [[3,1,5,1],[3,1,5,0],[3,0,5,0],[3,2,5,1],[3,2,5,0],[3,1,5,2],[3,2,5,2],[3,0,5,1],[3,0,5,2],
                        [1,4,1,5],[1,4,0,5],[0,4,0,5],[2,4,1,5],[2,4,0,5],[1,4,2,5],[2,4,2,5],[0,4,1,5],[0,4,2,5]]
        }
        s.cyclicalMoves = [
            ["w", "fa", "fe", "ne"], ["e", "fa", "fw", "nw"],
            ["fw", "w", "fe", "e"], ["fe", "e", "fw", "w"],
            ["w", "w", "fe", "e"], ["e", "e", "fw", "w"],
            ["w", "w", "w", "fe"], ["e", "e", "e", "fw"],
            ["w", "fe", "e"], ["e", "fw", "w"],
            ["ne", "fw", "w"], ["nw", "fe", "e"],
            ["w", "w", "fe"], ["e", "e", "fw"],
            ["fw", "fe"], ["fe", "fw"],
            ["dr", "pu"], ["pu", "dr"]
        ]

    def setLevel(s,level):
        s.root.level = Level(level.width,level.height,list(level.layout) )
        s.level = Level(level.width,level.height,list(level.layout) )
        s.currentLevel = s.root.level
        s.length = len(s.level.layout)
        s.root.player = Player()

    def locateStartAndGoalState(s):
        s.goalPos = Coordinate(-1,-1)
        s.root.player.setPos(-1,-1)
        for i in range(0,s.length):
            if s.level.layout[i] == DOOR:
                x, y = i % s.level.width, (i - (i%s.level.width))/s.level.width
                s.goalPos = Coordinate(x,y)
            elif s.level.layout[i] == WEST or s.level.layout[i] == EAST:
                x, y = i % s.level.width, (i - (i%s.level.width))/s.level.width
                s.root.player.setPos(x,y)
                s.root.player.setIndex(i)
                s.root.player.setDirection(s.level.layout[i])

    def taxiCabDistance(s, player):
        s.taxiCab = Coordinate(s.goalPos.x - player.pos.x, s.goalPos.y - player.pos.y)
        s.modifier = s.taxiCab.x / abs(s.taxiCab.x)

    def findBlockGoals(s):
        s.blockGoals = []
        lenIndices, lenHeights = len(s.obstacleIndices), len(s.obstacleHeights)
        for k in range(0, lenIndices ):
            tempI = s.obstacleIndices[k] + (s.level.width)
            reset = 0
            for l in range(0, lenHeights ):
                for i in range (1, s.obstacleHeights[l]):
                    for j in range (1, i+1):
                        reset += s.modifier
                        tempI -= s.modifier
                        if s.level.layout[tempI] != BRCK:
                            s.blockGoals.append(tempI)
                    tempI += s.level.width + reset

    def checkObstaclesHelper(s, prevHeight, height, depth, index, level, modifier):
        spaceAbove = level.layout[index - level.width]
        if (height + 1) - prevHeight > 1 and spaceAbove == EMPY:
            s.obstacleFlag = True
            s.obstacleHeights.append(height + 1)
            s.obstacleIndices.append(index)
        if index % level.width ==  0 or index < 0 or index > s.length or level.layout[index] == DOOR:
            return

        elif level.layout[index] == EMPY:
            spaceBelow = level.layout[index + level.width]
            if spaceBelow == BLCK or spaceBelow == BRCK: # If space below is brick/block go forward
                newIndex = index + modifier
                s.checkObstaclesHelper(0, 0, 0, newIndex, level, modifier)
            elif spaceBelow == EMPY: # If space below is brick/block go down
                newIndex = index  +  s.level.width
                s.checkObstaclesHelper(0, 0, depth+1, newIndex, level, modifier)
            elif spaceBelow == DOOR:
                return

        else:
            spaceAbove = level.layout[index - level.width]
            if spaceAbove == BLCK or spaceAbove == BRCK: # move up when the block above is a block
                newIndex = index -  level.width
                s.checkObstaclesHelper(prevHeight, height+1, 0, newIndex, level, modifier)
            elif spaceAbove == EMPY: # move forward when the block above is empty 
                newIndex = index  +  modifier
                s.checkObstaclesHelper(height+1, 0, 0, newIndex, level, modifier)
            elif spaceAbove == DOOR:
                return

    def checkObstaclesSolvable(s, index):
        s.obstacleIndices = []
        s.taxiCabDistance(s.dt[index].player)
        s.obstacleFlag = False
        s.checkObstaclesHelper(0,0,0, s.dt[index].player.index + s.modifier, s.dt[index].level, s.modifier)
        if s.obstacleFlag:
            s.findBlockGoals()


    def checkObstacles(s, index):
        s.obstacleIndices = []
        s.obstacleFlag = False
        mod = 1
        s.checkObstaclesHelper(0,0,0, s.dt[index].player.index + mod, s.dt[index].level, mod)
        s.checkObstaclesHelper(0,0,0, s.dt[index].player.index - mod, s.dt[index].level, -mod)

    def checkVictory(s, move, moveList):
        for k,v in s.victoryMoves.iteritems():
            if move in v:
                moveList.append(k)
                s.moveList = list(moveList)
                s.victory = True
                break

    def generateMoveQuads(s, i, l, w, level, moveList):
        pg = [ l[i-w-1], l[i-w], l[i-w+1], l[i-1], l[i], l[i+1], l[i+w-1], l[i+w],l[i+w+1] ]
        s.moveQuadrants = []
        for i in range(0,5):
            if i != 2:
                s.moveQuadrants.append([ pg[i], pg[i+1], pg[i+3], pg[i+4] ])

        # s.moveQuadrants.append([ pg[0], pg[1], pg[3], pg[4] ])
        # s.moveQuadrants.append([ pg[1], pg[2], pg[4], pg[5] ])
        # s.moveQuadrants.append([ pg[3], pg[4], pg[6], pg[7] ])
        # s.moveQuadrants.append([ pg[4], pg[5], pg[7], pg[8] ])

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
            playerAdj = player.pickupBlock()
            level.layout[playerAdj] = EMPY          
        elif move == "dr":
            playerAdj = player.dropBlock()
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
        # print "moveList: ", newChild.moveList
        newChild.player.copy(parent.player)
        newChild.level.copy(parent.level)
        newChild.children = s.getChildren(s.i)
        newChild.blockLocs = list(s.blockLocs)
        newChild.blockGoals = list(s.blockGoals)
        s.performMove(newChild.level, newChild, newChild.player, move)
        tree[s.i] = newChild

    def prioritizeMoves(s, move, moves):
        if move in moves:
            s.addToTree(s.dt, s.dt[s.par], move)

    def checkCycles(s, move):
        s.isNotACycle = True
        gp =  s.getGrandParentIndex(s.par)
        ggp = s.getGrandParentIndex(gp)

        moveSeq = [s.dt[ggp].move, s.dt[gp].move, s.dt[s.par].move, move]
        for i in range(0, 3):
            if moveSeq[i:] in s.cyclicalMoves:
                s.isNotACycle = False
                break

    def generateAdjacent(s, level):
        s.playerAdj = []
        tempI = s.dt[s.par].player.getAdj()
        s.playerAdj.append(tempI)
        tempI += level.width
        while tempI < s.length:
            if level.layout[tempI] == EMPY:
                s.playerAdj.append(tempI)
            tempI += level.width

    def pickMoves(s):
        cur = s.dt[s.par]
        if "fa" in s.quadMoves:  # If fall is a choice, it is the only choice.
            s.addToTree(s.dt, s.dt[s.par], "fa")
            s.counter += 1
            return
        else:
            if s.obstacleFlag:
                s.checkObstacles(s.par)
            for move in s.quadMoves:
                s.checkCycles(move)
                if not s.obstacleFlag:
                    if s.modifier < 0:
                        s.prioritizeMoves(move,["w","nw","fw"])
                    else:
                        s.prioritizeMoves(move,["e","ne","fe"])
                elif s.isNotACycle:
                    if move == "dr":
                        s.generateAdjacent(cur.level)
                        inBlockGoals = any(i in s.playerAdj for i in s.blockGoals)
                        if inBlockGoals and cur.level.layout[cur.player.getAdj()] == EMPY:
                            s.addToTree(s.dt, cur, move)
                    elif move == "pu":
                         if not s.checkCreatedObstacle(cur.player,cur.level):
                            s.addToTree(s.dt, cur, move)
                    else:
                        s.addToTree(s.dt, cur, move)
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
        if s.goalPos.x == -1 or s.root.player.pos.x == -1:
            print "Level unsolvable, either door or player is missing(Or both)."
            return

        s.i = 1
        s.checkObstaclesSolvable(0)
        
        bottom, s.counter = 0, 0
        startTime = time.clock()
        while not s.victory:
            lenDt = len(s.dt)
            if bottom == lenDt:
                print "Over pruned :("
                return
            for i in range(bottom, lenDt):
                s.par = s.dt.keys()[s.counter]
                cur = s.dt[s.par]
                s.generateMoveQuads(cur.player.index, cur.level.layout, s.root.level.width, cur.level, cur.moveList)
                for move in s.moveQuadrants:
                    s.checkVictory(move, cur.moveList)
                    if s.victory:
                        break
                    s.analyzeMoveQuads(move,s.par)
                s.pickMoves()
                s.quadMoves = []
                bottom = s.counter
        endTime = time.clock()
        print "\nTime taken(secs): ", endTime - startTime
        print "Solved!!!"

    def stepThroughSolution(s):
        currentMove = s.moveList.pop(0)
        s.performMove(s.root.level, s,s.root.player, currentMove)

#####################################################################
####################         Program Loop        ####################
#####################################################################
if __name__=='__main__':
    root = Tk()
    app = App(root)
    setPause = False
    testFiles = ["level1.csv", "level2.csv","level3.csv","level4.csv","level5.csv","level6.csv","level7.csv"]
    gameFiles = ["level1.csv","level2.csv"]


    if len(sys.argv) >= 2:
        if "test" in sys.argv:
            print "Loading test sets..."
            app.loadLevels("./testLevels/", testFiles)
        if "game" in sys.argv:
            print "Loading game levels..."
            app.loadLevels("./gameLevels/", gameFiles)
        if "pause" in sys.argv:
            setPause = True
    else:
        print "Please provide an arugment:\n\ttest: runs the test sets\n\tgame: runs the levels"
    def startFunction():
        for i in range(0, len(app.levels)):
            solver = Solver()
            solver.setLevel(app.levels[i])
            app.displayLevel(solver.level)
            solver.solve()
            
            if setPause:
                raw_input("Press Enter to view solution...")
            while(len(solver.moveList) > 0):
                root.update()
                solver.stepThroughSolution()
                app.displayLevel(solver.currentLevel)
                time.sleep(0.15)
            if setPause:
                if i != len(app.levels) -1:
                    raw_input("Press Enter to begin solving next level")
                else:
                    raw_input("Done!  Press enter to exit.")

        sys.exit(0)

    root.after(500, startFunction)
    app.run()
