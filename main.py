import sys
from src import solver, app
from Tkinter import Tk
import time


def check_args(_app):
    test_files = ["level1.csv", "level2.csv", "level3.csv", "level4.csv", "level5.csv", "level6.csv", "level7.csv"]
    game_files = ["level1.csv", "level2.csv", "level3.csv"]
    if len(sys.argv) >= 2:
        if "test" in sys.argv:
            print "Loading test sets..."
            _app.load_levels("./levels/test/", test_files)
        if "game" in sys.argv:
            print "Loading game levels..."
            _app.load_levels("./levels/game/", game_files)
    else:
        print "Please provide an argument:\n\ttest: runs the test sets\n\tgame: runs the levels"
        sys.exit(1)


def start_function():
    for i in range(0, len(_app.levels)):
        _solver = solver.Solver("./data/data.json", _app.levels[i])
        _app.display_level(_app.levels[i])
        root.update()
        _solver.solve()

        raw_input("Press Enter to view solution...")
        while len(_solver.moveList) > 0:
            root.update()
            _solver.step_through_solution()
            _app.display_level(_solver.get_level())
            time.sleep(0.13)
        if i != len(_app.levels) - 1:
            raw_input("Press Enter to begin solving next level")
        else:
            raw_input("Done!  Press enter to exit.")
    sys.exit(0)


if __name__ == '__main__':
    root = Tk()
    _app = app.App(root)
    check_args(_app)
    root.after(500, start_function)
    _app.run()
