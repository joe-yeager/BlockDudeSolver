from src import constants as c


#####################################################################
######################        Data Types        #####################
#####################################################################
class Coordinate:
    def __init__(self, x, y):
        self.x, self.y = x, y


class Level:
    def __init__(self, width, height, layout):
        self.width, self.height, self.layout = width, height, list(layout)

    def copy(self, level):
        self.width = level.width
        self.height = level.height
        self.layout = list(level.layout)


class Node:
    def __init__(self, index, move, move_list, player, level, block_goals):
        self.index = index

        self.move = None
        self.moveList = None
        self.blockGoals = None

        self.level = Level(0, 0, [])
        self.level.copy(level)

        self.player = Player()
        self.player.copy(player)

        self.set_move(move)
        self.set_move_list(move_list)
        self.add_to_move_list(move)

        self.set_block_goals(block_goals)

        self.children = [self.get_nth_child(0), self.get_nth_child(1), self.get_nth_child(2)]

    def get_nth_child(self, nth):
        return 3 * self.index + 1 + nth

    def pop_child(self):
        return self.children.pop(0)

    def set_move(self, move):
        self.move = move

    def get_move(self):
        return self.move

    def set_move_list(self, move_list):
        self.moveList = list(move_list)

    def get_move_list(self):
        return list(self.moveList)

    def add_to_move_list(self, move):
        self.moveList.append(move)

    def set_block_goals(self, block_goals):
        self.blockGoals = list(block_goals)

    def get_block_goals(self):
        return self.blockGoals

    def set_level(self, level):
        self.level.copy(level)


class Player:
    def __init__(self):
        self.pos = Coordinate(0, 0)
        self.dir, self.index, self.index2 = 0, 0, 0
        self.isHoldingBlock, self.falling = False, False

    def copy(self, player):
        self.set_pos(player.pos.x, player.pos.y)
        self.dir = player.dir
        self.index = player.index
        self.isHoldingBlock = player.isHoldingBlock
        self.falling = player.falling

    def set_pos(self, x, y):
        self.pos.x, self.pos.y = x, y

    def set_direction(self, player_value):
        self.dir = player_value

    def move_east(self):
        self.index += 1

    def move_west(self):
        self.index -= 1

    def move_north_east(self, width):
        self.move_east()
        self.index -= width

    def move_north_west(self, width):
        self.move_west()
        self.index -= width

    def fall(self, width):
        self.index += width

    def pickup_block(self):
        self.isHoldingBlock = True
        return self.get_adjacent()

    def drop_block(self):
        self.isHoldingBlock = False
        return self.get_adjacent()

    def set_index(self, index):
        self.index = index

    def get_adjacent(self):
        if self.dir == c.WEST:
            return self.index - 1
        else:
            return self.index + 1
