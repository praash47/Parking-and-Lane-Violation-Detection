# Local Modules ##
from gui.main_Menu import *
from absl import app


def main(_argv):
    # pass the control to gui/main_Menu.py
    MainMenu()


if __name__ == "__main__":
    # if there is a main function inside this file, then call it
    app.run(main)
