from gui.load_Windows import *


class MainMenu:
    def __init__(self):
        # Main Menu Window Intialization
        self.window = Tk()
        self.window.title("Main Menu - " + app_title)
        self.choice = None  # Main Menu Option Choice

        generateTopBottomBar(window=self.window, title=app_title)  # from functions.py

        # OPTION 1 #
        self.option1 = Button(self.window, text=option1, width=option_width, bg=option_color,
                              activebackground=option_btn_active_color,
                              command=lambda: mainMenuSwitch(0))
        self.option1.grid(row=1, column=0, ipadx=option_inner_padding_x, ipady=option_inner_padding_y,
                          pady=option_outer_padding_y)

        # OPTION 2 #
        self.option2 = Button(self.window, text=option2, width=option_width, bg=option_color, activebackground=option_btn_active_color,
                              command=lambda: mainMenuSwitch(1))
        self.option2.grid(row=2, column=0, ipadx=option_inner_padding_x, ipady=option_inner_padding_y,
                          pady=option_outer_padding_y)

        def mainMenuSwitch(option):
            self.choice = option  # After button is pressed, save choice and destroy this window.
            self.window.destroy()
            self.window.quit()

        self.window.mainloop()
        self.switchLoadWindow()  # this part executes after window has been destroyed.

    def switchLoadWindow(self):
        if self.choice is not None:
            if self.choice == 0:
                ParkingViolationLoadWindow()  # Proceed to functionality/parking_Violation.py
            else:
                LaneViolationLoadWindow()  # Proceed to functionality/lane_Violation.py
