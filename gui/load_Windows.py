# Third Party Modules ##
from tkinter import filedialog

from functionality.lane_Violation import *
# Local Modules ##
from functionality.parking_Violation import *
from misc.settings import *


class SubWindow:  # Window for Parking and Lane Violation LOAD WINDOW
    def __init__(self, option):
        self.window = Tk()
        self.window.title(option + ' - ' + app_title)

        self.option = option
        self.video_path = ''
        self.quit = False

        # these functions are present in functionality/functions.py #
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
        self.video_path = filedialog.askopenfilename(initialdir='D:/',
                                                     title="Load video where you want to detect?",
                                                     filetypes=(
                                                         ("mp4 files", "*.mp4"),
                                                         ("all files", "*.*")
                                                     )
                                                     )
        # object_create holds the main parking and lane violation objects.
        if self.option == option1:
            self.window.destroy()
            self.window.quit()

            # this object_create contains info whether to create a new object
            # after or not.
            object_create = ParkingViolation(self.video_path)

            while object_create.new_object == 'Yes':
                start_frame = object_create.video.cap.get(cv2.CAP_PROP_POS_FRAMES) - 1
                video_path = object_create.video.path

                del object_create
                object_create = ParkingViolation(video_path, start_frame)
        else:
            self.window.destroy()
            self.window.quit()
            if not LaneViolation(self.video_path).lane_line_received:
                self.quit = True



class ParkingViolationLoadWindow(SubWindow):
    def __init__(self):
        SubWindow.__init__(self, option1)
        # option1 is described in misc/variables.py #


class LaneViolationLoadWindow(SubWindow):
    def __init__(self):
        SubWindow.__init__(self, option2)
        # option2 is described in misc/variables.py #
