"""
Video Related Module
"""
# Local Modules ##
from functionality.functions import *
from misc.settings import *

# Problem Creating Modules #
from PIL import ImageTk, Image


# tkinter images bug
global pause_icon, restart_icon, play_icon


class Video:
    def __init__(self, path):
        self.path = path

        self.cap = cv2.VideoCapture(self.path)

        if not self.cap.isOpened():
            raise ValueError("Video can't be played.")

        # Save video-name-extension, thumbnail, width and height #
        self.name = os.path.basename(self.path)
        self.thumbnail_there, self.thumbnail = self.cap.read()
        self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.controls = None

    def getThumbnail(self, non_tk=False):
        """
        returns the first frame of the video
        :param non_tk: true if we want in opencv format, default in tkinter format.
        :return: opencv frame or tkinter image
        """
        if self.thumbnail_there and not non_tk:
            return ImageTk.PhotoImage(Image.fromarray(self.thumbnail))  # convert to Tk Pillow
            # readable
            # image
        elif self.thumbnail_there and non_tk:
            return self.thumbnail

    def createCanvasControls(self, detection_object):
        """
        Creates a video canvas, place the canvas on screen and create controls and write on screen.

        :param detection_object: Parking or Lane Violation Object
        """
        detection_object.video_canvas = Canvas(detection_object.window, width=self.width, height=self.height)
        detection_object.video_canvas.grid(row=2, column=0, sticky=W)
        self.controls = Controls(self)
        self.controls.writeOnScreen(detection_object)


class Controls:
    def __init__(self, video):
        self.video_object = video
        self.video_controls_btn_font = ''

    def writeOnScreen(self, detection_object):
        """
        Writing controls on screen (play, restart)

        :param detection_object: Parking or Lane Violation object
        """
        detection_object.controls_frame = LabelFrame(detection_object.window, text=video_controls_title,
                                                     padx=video_controls_inner_padding_x,
                                                     pady=video_controls_inner_padding_y, width=self.video_object.width)
        detection_object.controls_frame.grid(row=3, column=0)

        self.video_controls_btn_font = tkFont.Font(family=video_controls_btn_font_family,
                                                   size=video_controls_btn_font_size)

        global pause_icon
        pause_icon = ImageTk.PhotoImage(file=video_controls_pause_icon)

        detection_object.pause_btn = Button(detection_object.controls_frame, text=video_controls_pause_text,
                                            bg=video_controls_btn_color,
                                            activebackground=video_controls_btn_active_color,
                                            command=lambda: self.pause(detection_object),
                                            font=self.video_controls_btn_font, image=pause_icon, compound=LEFT)
        detection_object.pause_btn.grid(row=0, column=0, padx=(0, video_controls_inner_padding_x))

        global restart_icon
        restart_icon = ImageTk.PhotoImage(file=video_controls_restart_icon)
        detection_object.restart_btn = Button(detection_object.controls_frame, text=video_controls_restart_text,
                                              bg=video_controls_btn_color,
                                              activebackground=video_controls_btn_active_color,
                                              command=lambda: self.restart(detection_object),
                                              font=self.video_controls_btn_font, image=restart_icon, compound=LEFT)
        detection_object.restart_btn.grid(row=0, column=1)

    def pause(self, detection_object):
        global play_icon
        play_icon = ImageTk.PhotoImage(file=video_controls_play_icon)
        detection_object.pause_btn.destroy()
        detection_object.play_btn = Button(detection_object.controls_frame, text=video_controls_play_text,
                                           bg=video_controls_btn_color,
                                           activebackground=video_controls_btn_active_color,
                                           command=lambda: self.play(detection_object),
                                           font=self.video_controls_btn_font, image=play_icon, compound=LEFT)
        detection_object.play_btn.grid(row=0, column=0, padx=(0, video_controls_inner_padding_x))
        detection_object.pause_video = True

    @staticmethod
    def restart(detection_object):
        detection_object.video = Video(detection_object.video.path)

    def play(self, detection_object):
        global pause_icon
        pause_icon = ImageTk.PhotoImage(file=video_controls_pause_icon)
        detection_object.play_btn.destroy()
        detection_object.pause_btn = Button(detection_object.controls_frame, text=video_controls_pause_text,
                                            bg=video_controls_btn_color,
                                            activebackground=video_controls_btn_active_color,
                                            command=lambda: self.pause(detection_object),
                                            font=self.video_controls_btn_font, image=pause_icon, compound=LEFT)
        detection_object.pause_btn.grid(row=0, column=0, padx=(0, video_controls_inner_padding_x))
        detection_object.pause_video = False
