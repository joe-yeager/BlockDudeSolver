from src import data
import time
from collections import OrderedDict
import json
from src import constants as c

EMPY, BRCK, BLCK, WEST, EAST, DOOR = c.EMPY, c.BRCK, c.BLCK, c.WEST, c.EAST, c.DOOR


# The solver class contains all of the logic that is needed to solve
# the first two levels of Block Dude as well as all the test sets.
def is_player(value):
    return value == WEST or value == EAST


def get_xy(index, width):
    return index % width, (index - (index % width)) / width


class Solver:
    def __init__(self, data_file, level):
        self.goalPos = None
        self.taxiCab = None
        self.modifier = None
        self.i = None
        self.par = None
        self.counter = 0
        self.playerAdj = None
        self.isNotACycle = None

        # Set up the search tree root node
        self.dt = OrderedDict()
        self.dt[0] = data.Node(0, "", [], data.Player(), data.Level(level.width, level.height, level.layout), [])
        self.root = self.dt[0]

        self.level = data.Level(level.width, level.height, level.layout)
        self.length = len(self.level.layout)

        self.obstacleFlag, self.victory = False, False
        self.spacesBelow, self.blockGoals, self.moveQuadrants, self.moveList, self.availableMoves = [], [], [], [], []
        self.obstacles = {}

        # validMoves contains all of the legal moves that can be made
        # The moves are expressed as 2x2 matrices that have been linearized
        with open(data_file) as data_json:
            moves = json.load(data_json)

        self.validMoves = moves.get("valid_moves", None)
        self.victoryMoves = moves.get("victory_moves", None)
        self.cyclicalMoves = moves.get("cyclical_moves", None)

    def get_level(self):
        return self.root.level

    # Locates the player and the door in the level
    # Sets the x,y coordinates of the player and the goal
    def locate_start_and_goal_state(self):
        width = self.level.width

        i = self.level.layout.index(DOOR)
        x, y = get_xy(i, width)
        self.goalPos = data.Coordinate(x, y)

        try:
            i = self.level.layout.index(WEST)
        except ValueError:
            i = self.level.layout.index(EAST)

        x, y = get_xy(i, width)
        self.root.player.set_pos(x, y)
        self.root.player.set_index(i)
        self.root.player.set_direction(self.level.layout[i])

    # Computes the taxi cab distance between the player and the door
    # Sets s.modifier to -1 if the value is negative and 1 otherwise
    # The modifier is used quite often in other computations
    def calc_taxi_cab_distance(self, player):
        self.taxiCab = data.Coordinate(self.goalPos.x - player.pos.x, self.goalPos.y - player.pos.y)
        self.modifier = self.taxiCab.x / abs(self.taxiCab.x)

    # Uses the list of obstacles computed by checkObstacles to determine
    # where blocks need to be placed to complete an obstacle.  It will check
    # to both the east and the west of the obstacle
    def find_block_goals(self):
        self.blockGoals = []
        non_empty = [BRCK, BLCK]
        for index, height in self.obstacles.iteritems():
            reset = 0
            west = index - 1
            east = index + 1
            temp_ir = index + self.level.width
            temp_il = temp_ir
            for i in range(1, height):
                for j in range(1, i + 1):
                    reset += self.modifier
                    temp_ir -= self.modifier
                    temp_il += self.modifier
                    # Check to the east and the west,  if the block adjacent in either direction is non_empty
                    # don't add  blocks in that direction of the obstacle to the blockGoals list
                    if self.level.layout[east] not in non_empty and self.level.layout[temp_ir] not in non_empty:
                        self.blockGoals.append(temp_ir)
                    if self.level.layout[west] not in non_empty and self.level.layout[temp_il] not in non_empty:
                        self.blockGoals.append(temp_il)
                temp_ir += self.level.width + reset
                temp_il += self.level.width - reset

    # Checks for obstacles only between the player and the goal
    # If obstacles are found, call findBlockGoals
    def check_obstacles_find_blocks(self, index):
        cur = self.dt[index]
        self.calc_taxi_cab_distance(self.dt[index].player)
        self.obstacleFlag = False
        self.check_obstacles_helper(0, 0, 0, cur.player.index + self.modifier, cur.level, self.modifier)
        if self.obstacleFlag:
            self.find_block_goals()

    # checkFor obstacles in both directions.  This will clear the obstacle flag
    # if nothing is found.
    def check_obstacles(self, index):
        cur = self.dt[index]
        self.obstacles = {}
        self.obstacleFlag = False
        self.check_obstacles_helper(0, 0, 0, cur.player.index + 1, cur.level, 1)
        self.check_obstacles_helper(0, 0, 0, cur.player.index - 1, cur.level, -1)

    # Recursive helper function for finding obstacles.  It will scan along the ground and descend into pits
    # until an obstacle is found.  When an obstacle is found it will check its height, if its height is more that
    # 1 higher than obstacle adjacent to it, it will set the obstacle flag, and store the index of the highest point
    # of the obstacle as well as it's height.  If a pit of depth 2 or greater is found, it will store the index of 
    # the dropoff point.
    def check_obstacles_helper(self, prev_height, height, depth, index, level, modifier):
        space_above = level.layout[index - level.width]
        if (height + 1) - prev_height > 1 and (space_above == EMPY or space_above == DOOR):
            self.obstacleFlag = True
            self.obstacles[index] = height + 1
        if depth >= 2:
            self.obstacleFlag = True
            new_index = index - ((depth - 1) * level.width) - modifier
            if new_index not in self.obstacles:
                self.obstacles[new_index] = depth
        if index % level.width == 0 or index < 0 or index > self.length or level.layout[index] == DOOR:
            return

        elif level.layout[index] == EMPY:
            space_below = level.layout[index + level.width]
            if space_below == BLCK or space_below == BRCK:  # If space below is brick/block go forward
                new_index = index + modifier
                self.check_obstacles_helper(0, 0, 0, new_index, level, modifier)
            elif space_below == EMPY:  # If space below is empty go down
                new_index = index + self.level.width
                self.check_obstacles_helper(prev_height, height, depth + 1, new_index, level, modifier)
            elif space_below == DOOR:
                return

        else:
            space_above = level.layout[index - level.width]
            if space_above == BRCK:  # move up when the block above is a block
                new_index = index - level.width
                self.check_obstacles_helper(prev_height, height + 1, 0, new_index, level, modifier)
            elif space_above == BLCK or space_above == EMPY:  # move forward when the block above is empty
                new_index = index + modifier
                if level.layout[new_index] == EMPY:
                    depth += 1
                self.check_obstacles_helper(0, 0, depth, new_index, level, modifier)
            elif space_above == DOOR:
                return

    # Check if any of the current moves are a victory move.  If one of them is,
    # add it to the move list and set the victory flag.
    def check_victory(self, move, move_list):
        for k, v in self.victoryMoves.iteritems():
            if move in v:
                move_list.append(k)
                self.moveList = list(move_list)
                self.victory = True
                break

    # Takes a linear version of the 3x3 matrix surrounding the player and chops it
    # up into quadrants that can be scanned for moves.
    def generate_move_quads(self, i, l, w):
        pg = [l[i - w - 1], l[i - w], l[i - w + 1], l[i - 1], l[i], l[i + 1], l[i + w - 1], l[i + w], l[i + w + 1]]
        self.moveQuadrants = []
        for i in range(0, 5):
            if i != 2:
                self.moveQuadrants.append([pg[i], pg[i + 1], pg[i + 3], pg[i + 4]])

    # analyze the move quadrants generated, and check them for legal moves.
    # Add legal moves into list
    def analyze_move(self, move, index):
        cur = self.dt[index]
        for k, v in self.validMoves.iteritems():
            if move in v:
                if k == "pu" and not cur.player.isHoldingBlock:
                    self.add_move(k)
                elif k == "dr" and cur.player.isHoldingBlock:
                    self.add_move(k)
                elif k != "dr" and k != "pu":
                    self.add_move(k)

    # Add a move to the currently available moves list
    def add_move(self, move):
        if move not in self.availableMoves:
            self.availableMoves.append(move)

    # Recursively scans down until a non empty space is found
    def check_down(self, index, level):
        if level.layout[index] != EMPY:
            index -= level.width
            return index
        return self.check_down(index + level.width, level)

    # Have the player perform the move, and update the level
    def perform_move(self, level, _data, player, move):
        old_index = player.index
        width = self.level.width
        if move == "fa":
            player.fall(width)
        elif move == "w":
            player.move_west()
        elif move == "e":
            player.move_east()
        elif move == "nw":
            player.move_north_west(width)
        elif move == "ne":
            player.move_north_east(width)
        elif move == "fw":
            player.set_direction(WEST)
        elif move == "fe":
            player.set_direction(EAST)
        elif move == "pu":
            player_adj = player.pickup_block()
            level.layout[player_adj] = EMPY
        elif move == "dr":
            player_adj = player.drop_block()
            player_adj = self.check_down(player_adj, level)
            level.layout[player_adj] = BLCK

        level.layout[old_index] = 0
        level.layout[player.index] = player.dir

    # Pops a child index of the parents list of children
    # Creates a new node and deep copies the parents data
    # Generates the list of children for the new node
    # Takes the move that caused the branch and adds it to the new
    # nodes move list, then performs using the new nodes player and level
    # adds the node to the tree
    def add_to_tree(self, tree, parent, move):
        p = parent
        self.i = self.dt[self.par].pop_child()
        new_child = data.Node(self.i, move, p.moveList, p.player, p.level, self.blockGoals)
        self.perform_move(new_child.level, new_child, new_child.player, move)
        tree[self.i] = new_child

    # Syntactic sugar used for prioritizing moves
    def prioritize_moves(self, move, moves):
        if move in moves:
            self.add_to_tree(self.dt, self.dt[self.par], move)

    # Checks the move list in combination with the new 
    # potential move to see if it would generate a cyclical
    # move and sets a flag if it does.
    def check_cycles(self, move, move_list):
        self.isNotACycle = True
        move_seq = move_list[-3:]
        move_seq.append(move)
        for i in range(0, 3):
            if move_seq[i:] in self.cyclicalMoves:
                self.isNotACycle = False
                break

    # Generates the spaces that are adjacent to the player 
    # given the current direction they are facing.  If there
    # is a dropoff in front of the player, fall down the dropoff
    # and adds all of those spaces as well.
    def generate_adjacent(self, level):
        self.playerAdj = []
        temp_i = self.dt[self.par].player.get_adjacent()
        self.playerAdj.append(temp_i)
        temp_i += level.width
        while temp_i < self.length:
            if level.layout[temp_i] == EMPY:
                self.playerAdj.append(temp_i)
            temp_i += level.width

    # Checks if falling is a available move at the time, and 
    # if it is, falling is chosen due to the physics of the game.
    # Other wise it checks to see if there are still obstacles
    # and then loops through the list of available moves and 
    def pick_moves(self):
        cur = self.dt[self.par]
        if "fa" in self.availableMoves:  # If fall is a choice, it is the only choice.
            self.add_to_tree(self.dt, self.dt[self.par], "fa")
            self.counter += 1
            return

        if self.obstacleFlag:  # If check to see if obstacles have been cleared
            self.check_obstacles(self.par)
        for move in self.availableMoves:
            self.check_cycles(move, self.dt[self.par].moveList)
            if not self.obstacleFlag:  # If there are no obstacles, run for the goal
                if self.modifier < 0:
                    self.prioritize_moves(move, ["w", "nw", "fw"])
                else:
                    self.prioritize_moves(move, ["e", "ne", "fe"])
            elif self.isNotACycle:  # Only pick moves that will not generate cycles
                if move == "dr":
                    self.generate_adjacent(cur.level)
                    #  Only drop a block if it is in one of the block goals.
                    if any(i in self.playerAdj for i in self.blockGoals):
                        self.add_to_tree(self.dt, cur, move)
                else:
                    self.add_to_tree(self.dt, cur, move)
        self.counter += 1

    def solve(self):
        self.i = 1
        self.locate_start_and_goal_state()
        self.check_obstacles_find_blocks(0)

        bottom, self.counter = 0, 0
        start_time = time.clock()

        while not self.victory:
            len_dt = len(self.dt)
            if bottom == len_dt:
                print "\nFailed to Solve"
                return
            for i in range(bottom, len_dt):
                self.par = self.dt.keys()[self.counter]
                cur = self.dt[self.par]
                self.generate_move_quads(cur.player.index, cur.level.layout, self.root.level.width)
                for move in self.moveQuadrants:
                    self.check_victory(move, cur.moveList)
                    self.analyze_move(move, self.par)
                self.pick_moves()
                self.availableMoves = []
                bottom = self.counter

        end_time = time.clock() - start_time
        num_moves = len(self.moveList)
        print "\nTime taken(secs): {} \nSolved using {} moves!".format(end_time, num_moves)

    def step_through_solution(self):
        current_move = self.moveList.pop(0)
        self.perform_move(self.root.level, self, self.root.player, current_move)
