import sys
from Tkinter import Tk, Frame, Canvas
from PIL import ImageTk
import csv
import time
import math
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
        s.dt = []
        s.dt.append(Node())
        s.dt[0].moveList = []

        s.validMoves = {
            "e":  [[0,0,4,0],[4,0,1,1]],
            "w":  [[0,0,0,3],[0,3,1,1]],
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

    def taxiCabDistance(s):
        s.taxiCab = Coordinate(s.goalPos.x-s.dt[0].player.pos.x, s.goalPos.y-s.dt[0].player.pos.y)
        s.modifier = s.taxiCab.x / abs(s.taxiCab.x)

    def checkVictory(s, move, moveList):
        for k,v in s.V.iteritems():
            if move in v:
                moveList.append(k)
                s.moveList = list(moveList)
                s.victory = True
                break

    def generateMoveQuads(s, i, l, w):
        print "i: ", i
        print "w: ", w

        print l[i-w-1]
        print l[i-w]
        print l[i-w+1]
        print l[i-1]
        print l[i]
        print l[i+1]
        print l[i+w-1]
        print l[i+w]
        print l[i+w+1]
        pg = [ l[i-w-1], l[i-w], l[i-w+1], l[i-1], l[i], l[i+1], l[i+w-1], l[i+w],l[i+w+1] ]
        s.moveQuadrants = []
        s.moveQuadrants.append([ pg[0], pg[1], pg[3], pg[4] ])
        s.moveQuadrants.append([ pg[1], pg[2], pg[4], pg[5] ])
        s.moveQuadrants.append([ pg[3], pg[4], pg[6], pg[7] ])
        s.moveQuadrants.append([ pg[4], pg[5], pg[7], pg[8] ])
        print "index: ", i, "  moveQuads: ", s.moveQuadrants

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

    def performMove(s,level, player, move):
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
        elif move == "dr":
            player.dropBlock

        level.layout[oldIndex] = 0
        level.layout[player.index] = player.dir

    def applyMove(s, moveCode, level, player):
        s.prettyPrintLevel(level)
        print " "
        s.performMove(level, player, moveCode)
        s.prettyPrintLevel(level)

    def getParentIndex(s):
        s.par =  int ( math.floor( (s.i - 1) / 3 ) )
        if s.par < 0:
            s.par = 0

    def getNthChild(s, index, nthChild):
        return (3 * index + 1 + nthChild)

    def createDeadSpace(s,numOfSpaces):
        for i in range(0, numOfSpaces):
            s.dt.append(None)
        s.i += numOfSpaces

    def addToTree(s, tree, parent, move):
        newChild = Node()
        newChild.move = move
        newChild.moveList = list(parent.moveList)
        newChild.moveList.append(move)
        newChild.player, newChild.level = Player(), Level(0,0,0)
        newChild.player.copy(parent.player)
        newChild.level.copy(parent.level)
        s.applyMove(move,newChild.level,newChild.player)
        tree.append(newChild)

    def pickMoves(s):
        if "fa" in s.quadMoves:  # If fall is a choice, it is the only choice.
            print "i: ", s.i, "  parent: ", s.par, "  move: fa"
            s.getParentIndex()
            s.addToTree(s.dt, s.dt[s.par], "fa")
            s.createDeadSpace(2)
        else:
            count = 0
            for move in s.quadMoves:
                s.getParentIndex()
                print "i: ", s.i, "  parent: ", s.par, "  move: ", move
                if s.dt[s.par] == None:
                    s.createDeadSpace(3)
                    s.getParentIndex()
                elif move == "dr":
                    if s.dt[s.par].player.isHoldingBlock:
                        s.addToTree(s.dt, s.dt[s.par], move)
                        count += 1
                elif move == "pu":
                    if not s.dt[s.par].player.isHoldingBlock:
                        s.addToTree(s.dt, s.dt[s.par], move)
                        count += 1
                else:
                    s.addToTree(s.dt, s.dt[s.par], move)
                    count += 1
                s.i += 1

            if count != 3:
                dif = 3 - count
                s.createDeadSpace(dif)

    def solve(s):

        s.locateStartAndGoalState()
        if s.goalPos.x == -1 or s.dt[0].player.pos.x == -1:
            print ("Level unsolvable, either door or player is missing(Or both).")
            return

        s.i = 1
        s.getParentIndex()
        while not s.victory:
            if s.dt[s.par] == None:
                s.createDeadSpace(3)
            else:
                s.generateMoveQuads(s.dt[s.par].player.index, s.dt[s.par].level.layout, s.dt[0].level.width)
                for move in s.moveQuadrants:
                    s.checkVictory(move, s.dt[s.par].moveList)
                    if s.victory:
                        break
                    s.analyzeMoveQuads(move,s.par)
                if not s.victory:
                    s.pickMoves()
                s.quadMoves = []

            s.getParentIndex()



        print("Solved!!!")

    def resetState(s):
        s.dt[0].player.index = s.dt[0].player.index2

    def stepThroughSolution(s):
        print(s.moveList)
        currentMove = s.moveList.pop(0)
        if currentMove == "dr":
            playerAdj = s.dt[0].player.index - 1 if s.dt[0].player.dir == WEST else s.dt[0].player.index + 1
            s.dt[0].level.layout[playerAdj] = BLCK
        s.performMove(s.dt[0].level,s.dt[0].player, currentMove)

#####################################################################
####################         Program Loop        ####################
#####################################################################
if __name__=='__main__':
    root = Tk()
    app = App(root)
    path, gamePath = "./testLevels/", "./gameLevels/"
    testFiles = [
    "level1.csv", 
    "level2.csv",
    # "level3.csv"]
    "level4.csv"]
        # ,"level5.csv","level6.csv","level7.csv","level8.csv"]
    gameFiles = ["level1.csv","level2.csv"]
    app.loadLevels(path, testFiles)
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
            if i != len(app.levels) -1:
                raw_input("Press Enter to begin solving next level")
            else:
                raw_input("Done!  Press enter to exit.")

        sys.exit(0)

    root.after(2000, startFunction)
    app.run()
