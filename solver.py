from constraint import *

# Empty space is 0
# Brick is a 1
# Block is a 2
# West facing player - 3
# East facing player - 4
# Door - 5
level = [[1,1,1,1,1,1,1,1,1,1],
         [1,0,0,0,0,0,0,0,0,1],
         [1,0,0,0,0,0,0,0,0,1],
         [1,0,0,0,0,0,0,0,0,1],
         [1,0,0,0,0,0,0,0,0,1],
         [1,0,0,0,0,0,0,0,0,1],
         [1,0,0,0,0,0,0,0,0,1],
         [1,0,0,0,0,0,0,0,0,1],
         [1,5,0,0,0,0,0,3,0,1],
         [1,1,1,1,1,1,1,1,1,1]]

problem = Problem()

# moves
# move east - e
# move west - w
# more nortwest - nw
# more norteast - ne
# pickup block - p
# drop block - d
# fall - f
problem.addVariable("e", [[4,0],[3,0],[3,1],[3,2]] )
problem.addVariable("w", [[0,3],[0,4], [1,4],[2,4]])
problem.addVariable("nw", [0])
problem.addVariable("ne", [0])
problem.addVariable("p", [0])
problem.addVariable("d", [0])





solutions = problem.getSolutions()
print(solutions)
