import src import solver, player, app, data
import sys
from Tkinter import Tk, Frame, Canvas
from PIL import ImageTk
import csv
import time
import math
from collections import OrderedDict
EMPY, BRCK, BLCK, WEST, EAST, DOOR = 0,1,2,3,4,5
width, height = 0,0

if __name__=='__main__':
    root = Tk()
    app = App(root)
    setPause = False
    testFiles = ["level1.csv", "level2.csv","level3.csv","level4.csv","level5.csv","level6.csv","level7.csv"]
    gameFiles = ["level1.csv","level2.csv"]

    if len(sys.argv) >= 2:
        if "test" in sys.argv:
            print "Loading test sets..."
            app.loadLevels("./testLevels/", testFiles)
        if "game" in sys.argv:
            print "Loading game levels..."
            app.loadLevels("./gameLevels/", gameFiles)
        if "pause" in sys.argv:
            setPause = True
    else:
        print "Please provide an arugment:\n\ttest: runs the test sets\n\tgame: runs the levels"
        sys.exit(0)

    def startFunction():
        for i in range(0, len(app.levels)):
            solver = Solver()
            solver.setLevel(app.levels[i])
            app.displayLevel(app.levels[i])
            root.update()
            solver.solve()
            
            if setPause:
                raw_input("Press Enter to view solution...")
            while(len(solver.moveList) > 0):
                root.update()
                solver.stepThroughSolution()
                app.displayLevel(solver.currentLevel)
                time.sleep(0.13)
            if setPause:
                if i != len(app.levels) -1:
                    raw_input("Press Enter to begin solving next level")
                else:
                    raw_input("Done!  Press enter to exit.")

        sys.exit(0)

    root.after(500, startFunction)
    app.run()