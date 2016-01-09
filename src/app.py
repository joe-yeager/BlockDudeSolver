from src import data
from Tkinter import Tk, Frame, Canvas
from PIL import ImageTk
import csv
from src import constants as c
width, height = c.WIDTH, c.HEIGHT

#  The app class is resonsible for loading and parsing the CSV files that
#  contain the levels.  It is also responsible for displaying the GUI and
#  updating it when a change has been made.
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

    def updateCanvasDems(s,width, height):
        newWidth = (width*24)+100
        newHeight = (height*24)+100
        s.canvas.config(width=newWidth,height=newHeight)

    def displayLevel(s,level):
        s.canvas.delete("all")
        s.updateCanvasDems(level.width,level.height)
        length = len(level.layout)
        row = 0
        for i in range(0,length):
            if i % (level.width) == 0:
                row += 1
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
                newLevel = data.Level(width,height,level)
                s.levels.append(newLevel)

    def run(s):
        s.root.mainloop()
