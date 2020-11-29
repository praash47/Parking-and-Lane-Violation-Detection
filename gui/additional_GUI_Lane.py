# System Modules ##
import time

# Third Party Modules ##
import tkinter as tk
from tkinter import *
import tkinter.ttk as ttk

# Local Modules ##
from functionality.functions import *
from misc.settings import *
from misc.variables import *



class AdditionalGUILane:
    def __init__(self, detection_object):
        self.object = detection_object
        self.showNoneFrame()
        self.showLogFrame()

    def showLogFrame(self):
        # build ui
        self.violation_log_frame_wrapper = tk.LabelFrame(self.object.window)

        self.log_canvas = Canvas(self.violation_log_frame_wrapper)
        self.log_canvas.pack(side=LEFT)

        yscrollbar = ttk.Scrollbar(self.violation_log_frame_wrapper, orient="vertical", command=self.log_canvas.yview)
        yscrollbar.pack(side=RIGHT, fill="y")

        self.log_canvas.configure(yscrollcommand=yscrollbar.set)

        self.log_canvas.bind('<Configure>',
                             lambda e: self.log_canvas.configure(
                                 scrollregion=self.log_canvas.bbox('all')
                             ))

        self.violation_log_frame = tk.Frame(self.log_canvas)
        self.log_canvas.create_window((0,0), window=self.violation_log_frame, anchor="nw")

        self.logShow()

        self.violation_log_frame_wrapper.config(height='300', relief='flat', takefocus=False, text='Violation Log')
        self.violation_log_frame_wrapper.config(width='420')
        self.violation_log_frame_wrapper.pack_propagate(0)
        self.violation_log_frame_wrapper.grid(row=2, column=2)
        self.violation_log_frame_wrapper.grid_propagate(0)

    def showNoneFrame(self):
        # build ui
        self.recent_violation_frame = tk.LabelFrame(self.object.window)
        self.violation_message_title = tk.Message(self.recent_violation_frame)
        self.violation_message_title.config(background='#95ffff', font='{Lucida Sans Typewriter} 48 {}',
                                            foreground='#1b1b1b', justify='center')
        self.violation_message_title.config(relief='raised', text='NONE', width='400')
        self.violation_message_title.place(anchor='nw', relheight='1.0', relwidth='1.0', x='0', y='0')
        self.recent_violation_frame.config(height='300', relief='flat', takefocus=False, text='Recent Violation')
        self.recent_violation_frame.config(width='300')
        self.recent_violation_frame.grid(row=2, column=1)

    def showViolationFrame(self, violation_log):
        for i in range(len(violation_log['ids'])):
            self.recent_violation_frame = tk.LabelFrame(self.object.window)

            self.violation_message_title = tk.Message(self.recent_violation_frame)
            self.violation_message_title.config(background='#ff2424', font='{Haettenschweiler} 20 {}', foreground='#dddd00', justify='center')
            self.violation_message_title.config(relief='raised', text='WARNING ! !', width='400')
            self.violation_message_title.place(anchor='nw', relheight='0.31', relwidth='1.0', x='0', y='0')

            self.violation_message_type = tk.Message(self.recent_violation_frame)
            self.violation_message_type.config(anchor='w', aspect='0', background='#ffff80', borderwidth='2')
            self.violation_message_type.config(font='{Microsoft YaHei UI} 14 {}', foreground='#151515', highlightbackground='#ffff20', highlightcolor='#ffff20')
            self.violation_message_type.config(highlightthickness='1', justify='left', relief='groove', takefocus=True)
            self.violation_message_type.config(text='Type: ' + violation_log['types'][i], width='300')
            self.violation_message_type.place(anchor='nw', bordermode='ignore', height='0', relheight='0.16', relwidth='1.0', relx='0.0', rely='0.26', x='0', y='0')

            self.violation = tk.Message(self.recent_violation_frame)
            self.violation.config(anchor='w', background='#ffff80', cursor='arrow', font='{@Yu Gothic UI Light} 12 {}')
            self.violation.config(relief='groove', text='Description:  A vehicle commenced a ' + violation_log['types'][i] +
                                                       ' . Saving the violation video.', width='290')
            self.violation.place(anchor='nw', relheight='0.65', relwidth='1.0', relx='0.0', rely='0.38', x='0', y='0')
            self.recent_violation_frame.config(height='300', relief='flat', takefocus=False, text='Recent Violation')
            self.recent_violation_frame.config(width='300')
            self.recent_violation_frame.grid(row=2, column=1)
            time.sleep(lane_recent_violation_sleep_time)
        self.showNoneFrame()

    def logShow(self, log=None, photo_list=None):
        if log is not None:
            for i in range(len(log)):
                # Violator Photo
                self.violator_image = tk.Canvas(self.violation_log_frame)
                self.violator_image.config(height='70', width='70')
                tkinter_readable_frame = ImageTk.PhotoImage(Image.fromarray(photo_list[i]))
                self.violator_image.create_image(0, 0, image=tkinter_readable_frame, anchor=NW)
                self.violator_image.grid()

                # Violator Information
                self.violation_info_frame = tk.Frame(self.violation_log_frame)
                self.violator_info = tk.Text(self.violation_info_frame)
                self.violator_info.config(background='#d3d3d3', height='5', relief='flat', width='40')
                _text_ = '''"Vehicle Type: " +
                        Vehicle ID: 10
                        Violation at: 12.00.23 pm
                        Violation Type: Rt Ln Cross Violation
                        Video Proof:'''
                self.violator_info.insert('0.0', _text_)
                self.violator_info.config(state='disabled')
                self.violator_info.grid()
                self.text_4 = tk.Text(self.violation_info_frame)
                self.text_4.config(background='#d3d3d3', font='{consolas} 11 {underline}', foreground='#2510e4', height='2')
                self.text_4.config(width='40')
                _text_ = '''C:/Users/im_re/project/violations/lane/video-10202015'''
                self.text_4.insert('0.0', _text_)
                self.text_4.config(state='disabled')
                self.text_4.grid(column='0', row='1')
                self.violation_info_frame.config(background='#d3d3d3', height='100', width='100')
                self.violation_info_frame.grid(column='1', row=str(i))
