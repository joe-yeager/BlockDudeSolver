from src import data
import time
import math
from collections import OrderedDict
import json
from src import constants as c
EMPY, BRCK, BLCK, WEST, EAST, DOOR = c.EMPY, c.BRCK, c.BLCK, c.WEST, c.EAST, c.DOOR

# The solver class contains all of the logic that is needed to solve
# the first two levels of Block Dude as well as all the test sets.
class Solver:
    def __init__(s, data_file, level):
        l = level
        
        # Set up the search tree root node
        s.dt = OrderedDict()
        s.dt[0] = data.Node(0,"",[], data.Player(), data.Level(l.width, l.height, l.layout), [])
        s.root = s.dt[0]

        s.level = data.Level(level.width, level.height, level.layout )
        s.length = len(s.level.layout)

        s.obstacleFlag, s.victory = False, False
        s.spacesBelow, s.blockGoals, s.moveQuadrants, s.moveList, s.availableMoves = [],[],[],[],[]
        s.obstacles = {}

        # validMoves contains all of the legal moves that can be made
        # Thhe moves are expressed as 2x2 matrices that have been linearized
        with open(data_file) as data_json:
            moves = json.load(data_json)

        s.validMoves = moves.get("valid_moves", None)
        s.victoryMoves = moves.get("victory_moves", None)
        s.cyclicalMoves = moves.get("cyclical_moves", None)

    def getLevel(s):
        return s.root.level

    def isPlayer(s, value):
        if value == WEST or value == EAST:
            return True
        return False
    
    def getXY(s, index, width):
        return index % width, (index - (index % width)) / width

    # Locates the player and the door in the level
    # Sets the x,y coords of the player and the goal
    def locateStartAndGoalState(s):
        width = s.level.width

        i = s.level.layout.index(DOOR)
        x,y = s.getXY(i, width)
        s.goalPos = data.Coordinate(x,y)
            
        try:
            i = s.level.layout.index(WEST)
        except:
            i = s.level.layout.index(EAST)

        x,y = s.getXY(i, width)
        s.root.player.setPos(x,y)
        s.root.player.setIndex(i)
        s.root.player.setDirection(s.level.layout[i])

    # Computes the taxi cab distance between the player and the door
    # Sets s.modifier to -1 if the value is negative and 1 otherwise
    # The modifer is used quite often in other computations
    def taxiCabDistance(s, player):
        s.taxiCab = data.Coordinate(s.goalPos.x - player.pos.x, s.goalPos.y - player.pos.y)
        s.modifier = s.taxiCab.x / abs(s.taxiCab.x)

    # Uses the list of obstacles computed by checkObstacles to determine
    # where blocks need to be placed to complete an obstacle.  It will check
    # to both the east and the west of the obstacle
    def findBlockGoals(s):
        s.blockGoals = []
        nonEmpty = [BRCK, BLCK]
        for index,height in s.obstacles.iteritems():
            reset = 0
            west = index - 1
            east = index + 1
            tempIR = index + (s.level.width)
            tempIL = tempIR
            for i in range (1, height):
                for j in range (1, i+1):
                    reset += s.modifier
                    tempIR -= s.modifier
                    tempIL += s.modifier
                    # Check to the east and the west,  if the block adjacent in either direction is nonEmpty
                    # don't add  blocks in that direction of the obstacle to the blockGoals list
                    if s.level.layout[east] not in nonEmpty and s.level.layout[tempIR] not in nonEmpty:
                        s.blockGoals.append(tempIR)
                    if s.level.layout[west] not in nonEmpty and s.level.layout[tempIL] not in nonEmpty:
                        s.blockGoals.append(tempIL)
                tempIR += s.level.width + reset
                tempIL += s.level.width - reset

    # Checks for obstacles only between the player and the goal
    # If obstacles are found, call findBlockGoals
    def checkObstaclesFindBlocks(s, index):
        cur = s.dt[index]
        s.taxiCabDistance(s.dt[index].player)
        s.obstacleFlag = False
        s.checkObstaclesHelper(0,0,0, cur.player.index + s.modifier, cur.level, s.modifier)
        if s.obstacleFlag:
            s.findBlockGoals()

    # checkFor obstacles in both directions.  This will clear the obstacle flag
    # if nothing is found.
    def checkObstacles(s, index):
        cur = s.dt[index]
        s.obstacles = {}
        s.obstacleFlag = False
        s.checkObstaclesHelper(0,0,0, cur.player.index + 1, cur.level, 1)
        s.checkObstaclesHelper(0,0,0, cur.player.index - 1, cur.level, -1)

    # Recursive helper function for finding obstacles.  It will scan along the ground and descend into pits
    # until an obstacle is found.  When an obstacle is found it will check its height, if its height is more that
    # 1 higher than obstacle adjacent to it, it will set the obstacle flag, and store the index of the highest point
    # of the obstacle as well as it's height.  If a pit of depth 2 or greater is found, it will store the index of 
    # the dropoff point.
    def checkObstaclesHelper(s, prevHeight, height, depth, index, level, modifier):
        spaceAbove = level.layout[index - level.width]
        if (height + 1) - prevHeight > 1 and (spaceAbove == EMPY or spaceAbove == DOOR):
            s.obstacleFlag = True
            s.obstacles[index] = height + 1
        if depth >= 2:
            s.obstacleFlag = True
            newIndex = index - ((depth -1) * level.width) - modifier
            if newIndex not in s.obstacles:
                s.obstacles[newIndex] = depth
        if index % level.width ==  0 or index < 0 or index > s.length or level.layout[index] == DOOR:
            return

        elif level.layout[index] == EMPY:
            spaceBelow = level.layout[index + level.width]
            if spaceBelow == BLCK or spaceBelow == BRCK: # If space below is brick/block go forward
                newIndex = index + modifier
                s.checkObstaclesHelper(0, 0, 0, newIndex, level, modifier)
            elif spaceBelow == EMPY: # If space below is empty go down
                newIndex = index  +  s.level.width
                s.checkObstaclesHelper(prevHeight, height, depth+1, newIndex, level, modifier)
            elif spaceBelow == DOOR:
                return

        else:
            spaceAbove = level.layout[index - level.width]
            if spaceAbove == BRCK: # move up when the block above is a block
                newIndex = index -  level.width
                s.checkObstaclesHelper(prevHeight, height+1, 0, newIndex, level, modifier)
            elif spaceAbove == BLCK  or spaceAbove == EMPY: # move forward when the block above is empty 
                newIndex = index  +  modifier
                if level.layout[newIndex] == EMPY:
                    depth += 1
                s.checkObstaclesHelper(0, 0, depth, newIndex, level, modifier)
            elif spaceAbove == DOOR:
                return

    # Check if any of the current moves are a victory move.  If one of them is,
    # add it to the move list and set the victory flag.
    def checkVictory(s, move, moveList):
        for k,v in s.victoryMoves.iteritems():
            if move in v:
                moveList.append(k)
                s.moveList = list(moveList)
                s.victory = True
                break

    # Takes a linear version of the 3x3 matrix surrounding the player and chops it
    # up into quadrants that can be scanned for moves.
    def generateMoveQuads(s, i, l, w, level, moveList):
        pg = [ l[i-w-1], l[i-w], l[i-w+1], l[i-1], l[i], l[i+1], l[i+w-1], l[i+w],l[i+w+1] ]
        s.moveQuadrants = []
        for i in range(0,5):
            if i != 2:
                s.moveQuadrants.append([ pg[i], pg[i+1], pg[i+3], pg[i+4] ])

    # analyze the move quadrants generated, and check them for legal moves.
    # Add legal moves into list
    def analyzeMove(s, move, index):
        cur = s.dt[index]
        for k,v in s.validMoves.iteritems():
            if move in v:
                if k == "pu" and not cur.player.isHoldingBlock:
                    s.addMove(k)
                elif k == "dr" and cur.player.isHoldingBlock:
                    s.addMove(k)
                elif k != "dr" and k != "pu":
                    s.addMove(k)

    # Add a move to the currently available moves list
    def addMove(s, move):
        if move not in s.availableMoves:
            s.availableMoves.append(move)

    # Recusively scans down until a non empty space is found
    def checkDown(s,index, level):
        if level.layout[index] != EMPY:
            index -= level.width
            return index
        return s.checkDown(index + level.width, level)

    # Have the player perform the move, and update the level
    def performMove(s,level,data, player, move):
        oldIndex = player.index
        width = s.level.width
        if move == "fa":
            player.fall(width)
        elif move == "w":
            player.moveWest()
        elif move == "e":
            player.moveEast()
        elif move == "nw":
            player.moveNWest(width)
        elif move == "ne":
            player.moveNEast(width)
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

        level.layout[oldIndex] = 0
        level.layout[player.index] = player.dir

    # Pops a child index of the parents list of children
    # Creates a new node and deep copies the parents data
    # Generates the list of children for the new node
    # Takes the move that caused the branch and adds it to the new
    # nodes move list, then performs using the new nodes player and level
    # adds the node to the tree
    def addToTree(s, tree, parent, move):
        p = parent
        s.i = s.dt[s.par].popChild()
        newChild = data.Node(s.i, move, p.moveList, p.player, p.level, s.blockGoals )
        s.performMove(newChild.level, newChild, newChild.player, move)
        tree[s.i] = newChild

    # Syntactic sugar used for prioritizing moves
    def prioritizeMoves(s, move, moves):
        if move in moves:
            s.addToTree(s.dt, s.dt[s.par], move)

    # Checks the move list in combination with the new 
    # potential move to see if it would generate a cyclical
    # move and sets a flag if it does.
    def checkCycles(s, move, moveList):
        l = 3
        s.isNotACycle = True
        moveSeq = moveList[-l:]
        moveSeq.append(move)
        for i in range(0, l):
            if moveSeq[i:] in s.cyclicalMoves:
                s.isNotACycle = False
                break

    # Generates the spaces that are adjacent to the player 
    # given the current direction they are facing.  If there
    # is a dropoff in front of the player, it decends the dropoff
    # and adds all of those spaces aswell.
    def generateAdjacent(s, level):
        s.playerAdj = []
        tempI = s.dt[s.par].player.getAdj()
        s.playerAdj.append(tempI)
        tempI += level.width
        while tempI < s.length:
            if level.layout[tempI] == EMPY:
                s.playerAdj.append(tempI)
            tempI += level.width

    # Checks if falling is a available move at the time, and 
    # if it is, falling is chosen due to the physics of the game.
    # Other wise it checks to see if there are still obstacles
    # and then loops through the list of available moves and 
    def pickMoves(s):
        cur = s.dt[s.par]
        if "fa" in s.availableMoves:  # If fall is a choice, it is the only choice.
            s.addToTree(s.dt, s.dt[s.par], "fa")
            s.counter += 1
            return

        if s.obstacleFlag: # If check to see if obstacles have been cleared
            s.checkObstacles(s.par)
        for move in s.availableMoves:
            s.checkCycles(move, s.dt[s.par].moveList)
            if not s.obstacleFlag:  # If there are no obstacles, run for the goal
                if s.modifier < 0:
                    s.prioritizeMoves(move,["w","nw","fw"])
                else:
                    s.prioritizeMoves(move,["e","ne","fe"])
            elif s.isNotACycle:  # Only pick moves that will not generate cycles
                if move == "dr":
                    s.generateAdjacent(cur.level)
                    #  Only drop a block if it is in one of the block goals.
                    if any(i in s.playerAdj for i in s.blockGoals):
                        s.addToTree(s.dt, cur, move)
                else:
                    s.addToTree(s.dt, cur, move)
        s.counter += 1

    def solve(s):
        s.i = 1
        s.locateStartAndGoalState()
        s.checkObstaclesFindBlocks(0)
        
        bottom, s.counter = 0, 0
        startTime = time.clock()

        while not s.victory:
            lenDt = len(s.dt)
            if bottom == lenDt:
                print "\nFailed to Solve"
                return
            for i in range(bottom, lenDt):
                s.par = s.dt.keys()[s.counter]
                cur = s.dt[s.par]
                s.generateMoveQuads(cur.player.index, cur.level.layout, s.root.level.width, cur.level, cur.moveList)
                for move in s.moveQuadrants:
                    s.checkVictory(move, cur.moveList)
                    s.analyzeMove(move,s.par)
                s.pickMoves()
                s.availableMoves = []
                bottom = s.counter
        
        endTime = time.clock() - startTime
        numMoves = len(s.moveList)
        print "\nTime taken(secs): {} \nSolved using {} moves!".format(endTime, numMoves)

    def stepThroughSolution(s):
        currentMove = s.moveList.pop(0)
        s.performMove(s.root.level, s,s.root.player, currentMove)
