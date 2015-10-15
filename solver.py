from constraint import *
import sys
from Tkinter import Tk, Frame, Canvas
from PIL import ImageTk
import csv

EMPY, BRCK, BLCK, WEST, EAST, DOOR = 0,1,2,3,4,5
width, height = 0,0
HEADING = {3:"w",4:"e"}

class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def x(self,x):
        self.x = x

    def y(self,y):
        self.y = y

    def display(self):
        print("("+str(self.x)+","+str(self.y)+")")

class Level:
    def __init__(self, width,height,layout):
        self.width = width
        self.height = height
        self.layout = layout

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Block Dude Solver")
        self.frame = Frame(self.root)
        self.frame.pack()
        self.canvas = Canvas(self.frame, bg="white", width=(width*24)+100, height=(height*24)+100)
        self.canvas.pack()
        self.levels = []

        filedir = "./assets/"
        filenames = ["brick.png","block.png","dudeLeft.png","dudeRight.png","door.png"]
        
        self.imageArray = []        
        self.imageArray.append("")
        for i in range(0,len(filenames)):
            self.imageArray.append(ImageTk.PhotoImage(file=filedir + filenames[i]))

    def displayLevel(self,level):
        length = len(level)
        row = 0
        for i in range(0,length):
            if i % (width) == 0:
                row += 1
            if level[i] != EMPY:
                x = ((i%(width))*24) + 65
                y = (row*24) + 40
                self.canvas.create_image(x,y, image=self.imageArray[level[i]])

    def loadLevels(self,fileArray):
        length = len(fileArray)
        for i in range(0,length):
            with open(fileArray[i], 'rb') as f:
                reader = csv.reader(f)
                reader = list(reader).pop(0)
                level = map(int,reader)
                width = level.pop(0)
                height = level.pop(0)
                print(level)

    def clearCanvas(self):
        self.canvas.delete("all")

    def run(self):
        self.root.mainloop()

# class Solver:
#     def __init__(self):
#         self.constraints = Problem()
#         self.constraints.addVariable("e", [[4,0],[3,0],[3,1],[3,2]] )
#         self.constraints.addVariable("w", [[0,3],[0,4], [1,4],[2,4]])
#         self.constraints.addVariable("nw", [[[0,0],[1,3]], [[0,0],[2,3]] ])
#         self.constraints.addVariable("ne", [[[0,0],[4,1]], [[0,0],[4,2]] ])
#         self.constraints.addVariable("p", [[4,2],[2,3]])
#         self.constraints.addVariable("d", [[4,0],[0,3]])
#         self.constraints.addVariable("f", [[4,0],[0,3]])

#         self.solutions = self.constraints.getSolutions()

#     def setLevel(self,level):
#         self.level = level
#         self.length = len(self.level)

#     def scanMap(self):
#         self.goalPos, self.playerPos, self.playerDir = -1,-1,""
#         for i in range(0,self.length):
#             if self.level[i] == DOOR:
#                 x, y = i % width, (i - (i%width))/width
#                 self.goalPos = Coordinate(x,y)
#             elif self.level[i] == WEST or self.level[i] == EAST:
#                 x, y = i % width, (i - (i%width))/width
#                 self.playerPos = Coordinate(x,y)
#                 self.playerDir = HEADING[self.level[i]]

#         if self.goalPos == -1 or self.playerPos == -1 or self.playerDir == "":
#             return False
#         return True
    
#     def taxiCabDistance(self):
#         self.taxiCab = Coordinate(self.goalPos.x-self.playerPos.x, self.goalPos.y-self.playerPos.y)
#         self.taxiCab.display()



if __name__=='__main__':
    root = Tk()
    app = App(root)
    testFiles = ["./testLevels/level1.csv"]
    app.loadLevels(testFiles)
    # solver = Solver()
    # solver.setLevel()
    # app.displayLevel(solver.level)
    # if solver.scanMap() == True:
    #     solver.taxiCabDistance()
    # app.run()
