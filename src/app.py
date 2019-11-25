from src import data
from Tkinter import Tk, Frame, Canvas
from PIL import ImageTk
import csv
from src import constants as c

width, height = c.WIDTH, c.HEIGHT


#  The app class is responsible for loading and parsing the CSV files that
#  contain the levels.  It is also responsible for displaying the GUI and
#  updating it when a change has been made.
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Block Dude Solver")
        self.frame = Frame(self.root)
        self.frame.pack()
        self.canvas = Canvas(self.frame, bg="white", width=(width * 24) + 100, height=(height * 24) + 100)
        self.canvas.pack()
        self.levels, self.imageArray = [], []
        file_names = ["brick.png", "block.png", "dudeLeft.png", "dudeRight.png", "door.png"]

        self.imageArray.append("")
        for i in range(0, len(file_names)):
            self.imageArray.append(ImageTk.PhotoImage(file="./assets/" + file_names[i]))

    def update_canvas_dimensions(self, _width, _height):
        new_width = (_width * 24) + 100
        new_height = (_height * 24) + 100
        self.canvas.config(width=new_width, height=new_height)

    def display_level(self, level):
        self.canvas.delete("all")
        self.update_canvas_dimensions(level.width, level.height)
        length = len(level.layout)
        row = 0
        for i in range(0, length):
            if i % level.width == 0:
                row += 1
            x = ((i % level.width) * 24) + 65
            y = (row * 24) + 40
            self.canvas.create_image(x, y, image=self.imageArray[level.layout[i]])

    def load_levels(self, path, file_array):
        length = len(file_array)
        for i in range(0, length):
            with open(path + file_array[i], 'rb') as f:
                reader = csv.reader(f)
                reader = list(reader).pop(0)
                level = map(int, reader)
                _width = level.pop(0)
                _height = level.pop(0)
                new_level = data.Level(_width, _height, level)
                self.levels.append(new_level)

    def run(self):
        self.root.mainloop()
