from functionality.parking_Violation import *
from functionality.lane_Violation import *
from misc.settings import *

from tkinter import filedialog


class SubWindow:  # Window for Parking and Lane Violation LOAD WINDOW
    def __init__(self, option):
        self.window = Tk()
        self.window.title(option + ' - ' + app_title)

        self.option = option
        self.video_path = ''

        generateTopBottomBar(window=self.window, title=self.window.title())
        generateSubtitleBar(window=self.window, title=option)

        load_video_font = tkFont.Font(family=load_video_font_family, size=load_video_font_size)

        self.load_video_btn = Button(self.window, text="Load Video", bg=load_video_color,
                                     activebackground=load_video_active_color, command=self.loadVideo,
                                     font=load_video_font)
        self.load_video_btn.grid(row=2, column=0, ipadx=load_video_inner_padding_x,
                                 ipady=load_video_inner_padding_y, pady=load_video_outer_padding_y)

        self.window.mainloop()

    def loadVideo(self):
        load_new_video = False
        self.video_path = filedialog.askopenfilename(initialdir='D:/',
                                                     title="Load video where you want to detect?",
                                                     filetypes=(
                                                         ("mp4 files", "*.mp4"),
                                                         ("all files", "*.*")
                                                     )
                                                     )
        video_path = self.video_path
        if self.option == option1:
            self.window.destroy()
            self.window.quit()
            ParkingViolation(self.video_path)
        else:
            self.window.destroy()
            self.window.quit()
            LaneViolation(self.video_path)


class ParkingViolationLoadWindow(SubWindow):
    def __init__(self):
        SubWindow.__init__(self, option1)


class LaneViolationLoadWindow(SubWindow):
    def __init__(self):
        SubWindow.__init__(self, option2)
