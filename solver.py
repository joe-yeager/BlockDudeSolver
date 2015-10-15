from constraint import *
import sys

from Tkinter import Tk, Frame, Canvas
from PIL import ImageTk

# Empty space is 0
# Brick is a 1
# Block is a 2
# West facing player - 3
# East facing player - 4
# Door - 5
levl1 = [1,1,1,1,1,1,1,1,1,1,
         1,0,0,0,0,0,0,0,0,1,
         1,0,0,0,0,0,0,0,0,1,
         1,0,0,0,0,0,0,0,0,1,
         1,0,0,0,0,0,0,0,0,1,
         1,0,0,0,0,0,0,0,0,1,
         1,0,0,0,0,0,0,0,0,1,
         1,0,0,0,0,0,0,0,0,1,
         1,5,0,0,0,0,0,0,3,1,
         1,1,1,1,1,1,1,1,1,1]


levl2 = [1,0,0,0,0,0,0,0,0,1,
         1,0,0,0,0,0,0,0,0,1,
         1,0,0,0,0,0,0,0,0,1,
         1,0,0,0,0,0,0,0,0,1,
         1,0,0,0,0,0,0,0,0,1,
         1,0,0,0,0,0,0,0,0,1,
         1,0,0,0,0,0,0,0,0,1,
         1,0,0,0,0,0,0,0,0,1,
         1,5,0,0,0,0,0,0,3,1,
         1,1,1,1,1,1,1,1,1,1]

height = 10
width = 10

# moves
# move east - e
# move west - w
# more nortwest - nw
# more norteast - ne
# pickup block - p
# drop block - d
# fall - f
problem = Problem()

problem.addVariable("e", [[4,0],[3,0],[3,1],[3,2]] )
problem.addVariable("w", [[0,3],[0,4], [1,4],[2,4]])
problem.addVariable("nw", [[[0,0],[1,3]], [[0,0],[2,3]] ])
problem.addVariable("ne", [[[0,0],[4,1]], [[0,0],[4,2]] ])
problem.addVariable("p", [[4,2],[2,3]])
problem.addVariable("d", [[4,0],[0,3]])
problem.addVariable("f", [[4,0],[0,3]])

solutions = problem.getSolutions()


# GUI Code borrowed from:
# http://stackoverflow.com/questions/3270209/how-do-i-make-tkinter-support-png-transparency
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Block Dude Solver")
        self.frame = Frame(self.root)
        self.frame.pack()
        self.canvas = Canvas(self.frame, bg="white", width=(width*24)+100, height=(height*24)+100)
        self.canvas.pack()
        self.imageArray = []
        self.imageArray.append("")
        self.imageArray.append(ImageTk.PhotoImage(file="./assets/brick.png"))
        self.imageArray.append(ImageTk.PhotoImage(file="./assets/block.png"))
        self.imageArray.append(ImageTk.PhotoImage(file="./assets/dudeLeft.png"))
        self.imageArray.append(ImageTk.PhotoImage(file="./assets/dudeRight.png"))
        self.imageArray.append(ImageTk.PhotoImage(file="./assets/door.png"))

    def displayLevel(self,level):

        length = len(level)
        row = 0
        for i in range(0,length):
            if i % (width) == 0:
                row += 1
            if level[i] != 0:
                x = ((i%(width))*24) + 65
                y = (row*24) + 40
                self.canvas.create_image(x,y, image=self.imageArray[level[i]])

    def clearCanvas(self):
        self.canvas.delete("all")
        
    def run(self):
        self.root.mainloop()


if __name__=='__main__':
    root = Tk()
    app = App(root)
    app.displayLevel(levl1)
    app.clearCanvas()
    app.displayLevel(levl2)
    app.run()