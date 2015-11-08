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

    def copy(s, level):
        s.width = level.width
        s.height = level.height
        s.layout = level.layout

class Tree:
    def __init__(s):
        s.move = None
        s.moveList = []
        s.level = None
        s.player = None
        s.left = None
        s.middle = None
        s.right = None

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
        
        s.victory = False;
        s.decisionTree = Tree()
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
        s.decisionTree.level = Level(level.width,level.height,list(level.layout) )
        s.level = Level(level.width,level.height,list(level.layout) )
        s.currentLevel = Level(s.level.width, s.level.height, list(s.level.layout) )
        s.length = len(s.level.layout)
        s.decisionTree.player = Player()


    def locateStartAndGoalState(s):
        s.goalPos = Coordinate(-1,-1)
        s.decisionTree.player.setPos(-1,-1)
        for i in range(0,s.length):
            if s.level.layout[i] == DOOR:
                x, y = i % s.level.width, (i - (i%s.level.width))/s.level.width
                s.goalPos = Coordinate(x,y)
            elif s.level.layout[i] == WEST or s.level.layout[i] == EAST:
                x, y = i % s.level.width, (i - (i%s.level.width))/s.level.width
                s.decisionTree.player.setPos(x,y)
                s.decisionTree.player.index,s.decisionTree.player.index2 = i,i
                s.decisionTree.player.setDirection(s.level.layout[i])

    def taxiCabDistance(s):
        s.taxiCab = Coordinate(s.goalPos.x-s.decisionTree.player.pos.x, s.goalPos.y-s.decisionTree.player.pos.y)
        s.modifier = s.taxiCab.x / abs(s.taxiCab.x)

    def checkVictory(s, move):
        for k,v in s.V.iteritems():
            if move in v:
                s.moveList.append(k)
                s.victory = True
                break

    def generateMoveQuads(s, i, l, w):
        pg = [ l[i-w-1], l[i-w], l[i-w+1], l[i-1], l[i], l[i+1], l[i+w-1], l[i+w],l[i+w+1] ]
        s.moveQuadrants = []
        s.moveQuadrants.append([ pg[0], pg[1], pg[3], pg[4] ])
        s.moveQuadrants.append([ pg[1], pg[2], pg[4], pg[5] ])
        s.moveQuadrants.append([ pg[3], pg[4], pg[6], pg[7] ])
        s.moveQuadrants.append([ pg[4], pg[5], pg[7], pg[8] ])

    def analyzeMoveQuads(s, move):
        for k,v in s.validMoves.iteritems():
            if move in v:
                if k == "pu" and not s.decisionTree.player.isHoldingBlock:
                    s.quadMoves.append(k)
                elif k == "dr" and s.decisionTree.player.isHoldingBlock:
                    s.quadMoves.append(k)
                elif k != "dr" or k!= "pu":
                    s.quadMoves.append(k)

    def performMove(s,level, move, player, arg=None):
        oldIndex = player.index
        if arg == None:
            move()
        else:
            move(arg)
        level.layout[oldIndex] = 0
        level.layout[player.index] = player.dir

    def applyMove(s, moveCode, level, player):
        moveFuncs = {  #These depend on properties of the level, so define it after they are set
            "fa"    : [player.fall, s.level.width],
            "w"     : [player.moveWest, None],
            "e"     : [player.moveEast, None],
            "nw"    : [player.moveNWest, s.level.width],
            "ne"    : [player.moveNEast, s.level.width],
            "fw"    : [player.setDirection, WEST],
            "fe"    : [player.setDirection, EAST],
            "pu"    : [player.pickupBlock, None],
            "dr"    : [player.dropBlock, None],
        }
        print moveCode
        s.performMove(level, moveFuncs[moveCode][0], moveFuncs[moveCode][1])

    def pickMove(s, player):
        if "fa" in s.quadMoves: # if fall is a valid move, it must be chosen.
            s.addToTree(s.decisionTree, "fa")
        else:
            for move in s.quadMoves:
                if move == "dr":
                    if player.isHoldingBlock:
                        s.addToTree(s.decisionTree, move)
                elif move == "pu":
                    if not player.isHoldingBlock:
                        s.addToTree(s.decisionTree, move)
                else:
                    s.addToTree(s.decisionTree, move)
        s.quadMoves = []

    def addToTree(s, tree, move):
        if tree.left == None:
            tree.left = Tree()
            cur = tree.left
            s.addToTreeHelper(cur, tree, move)

        elif tree.middle == None:
            tree.middle = Tree()
            cur = tree.middle
            s.addToTreeHelper(cur, tree, move)
            
        elif tree.right == None:
            tree.right = Tree()
            cur = tree.right
            s.addToTreeHelper(cur, tree, move)

        else:
            sys.exit(1)
            
    def addToTreeHelper(s, cur, tree, move):
        cur.move = move
        cur.moveList = list(tree.moveList)
        cur.moveList.append(move)
        cur.player, cur.level = Player(), Level(0,0,0,)
        # Copy the parents state
        cur.player.copy(tree.player)
        cur.level.copy(tree.level)

    def bdfFilling(s,root, level, move):
        if root != None:
            if level == 0:
                print move
                s.addToTree(root,move)
                return
            s.bdfFilling(root.left, level - 1, move)
            s.bdfFilling(root.middle, level - 1, move)
            s.bdfFilling(root.right, level - 1, move)

    def solve(s):
        s.locateStartAndGoalState()
        if s.goalPos.x == -1 or s.decisionTree.player.pos.x == -1:
            print ("Level unsolvable, either door or player is missing (Or both)")
            return

        i = 0
        while not s.victory:
            s.generateMoveQuads(s.decisionTree.player.index, s.level.layout, s.level.width)
            for move in s.moveQuadrants:
                s.checkVictory(move)
                s.analyzeMoveQuads(move)
            if "fa" in s.quadMoves:
                s.addToTree(s.decisionTree, "fa")
            else:
                for move in s.quadMoves:
                    if move == "dr":
                        if s.decisionTree.player.isHoldingBlock:
                            s.bdfFilling(s.decisionTree, i, move)
                    elif move == "pu":
                        if not s.decisionTree.player.isHoldingBlock:
                            s.bdfFilling(s.decisionTree, i, move)
                    else:
                        s.bdfFilling(s.decisionTree, i, move)
            
            s.quadMoves = []
            i += 1


        print("Solved!!!")


    def resetState(s):
        s.decisionTree.player.index = s.decisionTree.player.index2

    def stepThroughSolution(s):
        print(s.moveList)
        currentMove = s.moveList.pop(0)
        if currentMove == "dr":
            playerAdj = s.decisionTree.player.index - 1 if s.decisionTree.player.dir == WEST else s.decisionTree.player.index + 1
            s.currentLevel.layout[playerAdj] = BLCK
        s.performMove(s.currentLevel, s.moveFuncs[currentMove][0], s.moveFuncs[currentMove][1])

#####################################################################
####################         Program Loop        ####################
#####################################################################
if __name__=='__main__':
    root = Tk()
    app = App(root)
    path, gamePath = "./testLevels/", "./gameLevels/"
    testFiles = [
    #"level1.csv", "level2.csv",
    "level3.csv",
    # "level4.csv"
    ]
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
