from src import constants as c
from collections import OrderedDict

# EMPY, BRCK, BLCK, WEST, EAST, DOOR = 0,1,2,3,4,5

#####################################################################
######################        Data Types        #####################
#####################################################################
class Coordinate:
    def __init__(s, x, y):
        s.x, s.y = x, y

class Level:
    def __init__(s, width,height,layout):
        s.width, s.height, s.layout = width, height, list(layout)

    def copy(s, level):
        s.width = level.width
        s.height = level.height
        s.layout = list(level.layout)

class Tree:
    def __init__(s):
        pass

class Node:
    def __init__(s, index, move, moveList, player, level, blockGoals):
        s.index = index
        
        s.level = Level(0,0,[])
        s.level.copy(level)
        
        s.player = Player()
        s.player.copy(player)
        
        s.setMove(move)
        s.setMoveList(moveList)
        s.addToMoveList(move)

        s.setBlockGoals(blockGoals)
        
        s.children = [ s.getNthChild(0), s.getNthChild(1), s.getNthChild(2)]

    def getNthChild(s,nth):
        return 3 * s.index + 1 + nth

    def popChild(s):
        return s.children.pop(0)

    def setMove(s, move):
        s.move = move

    def getMove(s):
        return s.move

    def setMoveList(s, moveList):
        s.moveList = list(moveList)

    def getMoveList(s):
        return list(s.moveList)

    def addToMoveList(s, move):
        s.moveList.append(move)

    def setBlockGoals(s, blockGoals):
        s.blockGoals = list(blockGoals)

    def getBlockGoals(s, blockGoals):
        return s.blockGoals

    def setLevel(s, level):
        s.level.copy(level)

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
        if s.dir == c.WEST:
            return s.index - 1
        else:
            return s.index + 1