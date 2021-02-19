# Local Modules ##
from gui.main_Menu import *

# Third Party Modules ##
from absl import app


def main(_argv):
    # pass the control to gui/main_Menu.py and till user doesn't press exit,
    # keep on showing main menu.

    main_menu = MainMenu()
    while not main_menu.exit:
        main_menu = MainMenu()

    # delete main menu object
    del main_menu


if __name__ == "__main__":
    # if there is a main function inside this file, then call it
    app.run(main)  # for absl.

    # REASON FOR USING absl: some of the internal features for YOLOv4 require absl
    # for functioning.
