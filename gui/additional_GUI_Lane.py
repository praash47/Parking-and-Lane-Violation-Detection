# System Modules ##
import time
import threading

# Third Party Modules ##
import tkinter as tk
from tkinter import *
import tkinter.ttk as ttk
from tkinter import messagebox
from playsound import playsound

# Local Modules ##
from functionality.functions import *
from misc.settings import *
from misc.variables import *

from PIL import ImageTk, Image

global tkinter_readable_frame

class AdditionalGUILane:
    def __init__(self, detection_object):
        self.object = detection_object
        self.violation_recent_shown = []
        self.showNoneFrame()
        self.showLogFrame()

    def showLogFrame(self):
        # build ui
        self.violation_log_frame_wrapper = tk.LabelFrame(self.object.window)

        self.violation_log = ttk.Treeview(self.violation_log_frame_wrapper)
        self.violation_log.grid(row="0", column="0")

        self.violation_log_scrollbar = ttk.Scrollbar(self.violation_log_frame_wrapper, orient=VERTICAL)
        self.violation_log_scrollbar.configure(command=self.violation_log.yview)
        self.violation_log_scrollbar.grid(row="0", column="1", sticky=N+S)

        self.violation_log['columns'] = ("Vehicle Type", "Violation At", "Violation Type")

        self.violation_log.column("#0", anchor=CENTER, width=75)
        self.violation_log.column("Vehicle Type", anchor=W, width=85)
        self.violation_log.column("Violation At", anchor=W, width=85)
        self.violation_log.column("Violation Type", anchor=W, width=105)

        self.violation_log.heading("#0", text="Vehicle ID", anchor=W)
        self.violation_log.heading("Vehicle Type", text="Vehicle Type", anchor=W)
        self.violation_log.heading("Violation At", text="Violation At", anchor=W)
        self.violation_log.heading("Violation Type", text="Violation Type", anchor=W)

        # addition of data
        for i in range(30):
            self.violation_log.insert(parent='', index='end', iid=i, text=str(i), values=("Car", "10:20:47", "Lane Cross"))

        self.violation_log.configure(yscrollcommand=self.violation_log_scrollbar.set)
        self.violation_log.bind("<<TreeviewSelect>>", self.additionalLogInfo)

        #self.logUpdate()
        self.violation_log_info_text = tk.Label(self.violation_log_frame_wrapper)
        self.violation_log_info_text.config(text='Select a record for picture of the culprit, proof video link and additional infos.',
                                            width='60')
        self.violation_log_info_text.grid(row="1")


        self.violation_log_frame_wrapper.config(background='#d3d3d3', height='300', relief='flat', text='Violation Log')
        self.violation_log_frame_wrapper.config(width='500')
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
            if violation_log['ids'][i] not in self.violation_recent_shown:
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
                self.violation_recent_shown.append(violation_log['ids'][i])
                playsound("resources/alarm.mp3")
        time.sleep(1)
        self.showNoneFrame()

    def logUpdate(self, log=None):
        if log is not None:
            for i in range(len(log['ids'])):
                # Violator Photo
                self.violator_image = tk.Canvas(self.violation_log_frame1)
                self.violator_image.config(background='#509f00', height='70', width='70')
                violator_image = cv2.imread(log['pictures'][i])
                global tkinter_readable_frame
                tkinter_readable_frame = ImageTk.PhotoImage(Image.fromarray(violator_image))
                self.violator_image.create_image(0, 0, image=tkinter_readable_frame, anchor=NW)
                self.violator_image.grid(row=str(i))

                # Violator Information
                self.violation_info_frame = tk.Frame(self.violation_log_frame1)
                self.violator_info = tk.Text(self.violation_info_frame)
                self.violator_info.config(background='#d3d3d3', height='5', relief='flat', width='40')
                _text_ = "Vehicle Type: " + log['class_names'][i] + "\n"
                _text_ += "Vehicle ID: " + str(log['ids'][i]) + "\n"
                _text_ += "Violation at: " + str(log['times'][i]) + "\n"
                _text_ += "Violation Type: " + log['types'][i] + "\n"
                _text_ += "Video Proof: " + "\n"
                self.violator_info.insert('0.0', _text_)
                self.violator_info.config(state='disabled')
                self.violator_info.grid(row=str(i), column='0')
                # self.text_4 = tk.Text(self.violation_info_frame)
                # self.text_4.config(background='#d3d3d3', font='{consolas} 11 {underline}', foreground='#2510e4', height='2')
                # self.text_4.config(width='40')
                #_text_ = log['video_proof_links'][i]
                #self.text_4.insert('0.0', _text_)
                #self.text_4.config(state='disabled')
                #self.text_4.grid(column='0', row='1')
                self.violation_info_frame.config(background='#d3d3d3', height='100', width='80')
                self.violation_info_frame.grid(column='1', row=str(i))

    def additionalLogInfo(self, record):
        violation = self.violation_log.item(self.violation_log.selection())
        self.createLogInfoWindow()

        self.log_window.title('Info for Vehicle ID: ' + violation['text'])

        self.vehicle_image = tk.Canvas(self.log_window)
        self.vehicle_image.config(background='#87bab4', height='100', relief='groove', width='100')
        self.vehicle_image.grid(row='0', column='0')

        self.log_window_info = tk.LabelFrame(self.log_window)
        self.vehicle_id = tk.Label(self.log_window_info)
        self.vehicle_id.config(cursor='arrow', font='{Yu Gothic Medium} 12 {}', highlightcolor='#030505',
                               relief='ridge')
        self.vehicle_id.config(text='Vehicle ID:')
        self.vehicle_id.grid(column='0', padx='5', pady='2', sticky='w')
        self.vehicle_id_value = tk.Label(self.log_window_info)
        self.vehicle_id_value.config(font='{Yu Gothic Medium} 12 {}', text=violation['text'])
        self.vehicle_id_value.grid(column='1', padx='130', row='0')
        self.vehicle_type = tk.Label(self.log_window_info)
        self.vehicle_type.config(font='{Yu Gothic Medium} 12 {}', relief='ridge', text='Vehicle Type:')
        self.vehicle_type.grid(column='0', padx='5', pady='2', row='1', sticky='w')
        self.vehicle_type_value = tk.Label(self.log_window_info)
        self.vehicle_type_value.config(font='{Yu Gothic Medium} 12 {}', text=violation['values'][0])
        self.vehicle_type_value.grid(column='1', padx='150', row='1', sticky='e')
        self.violation_at = tk.Label(self.log_window_info)
        self.violation_at.config(font='{Yu Gothic Medium} 12 {}', relief='ridge', text='Violation At:')
        self.violation_at.grid(column='0', padx='5', pady='2', row='2', sticky='w')
        self.violation_at_value = tk.Label(self.log_window_info)
        self.violation_at_value.config(font='{Yu Gothic Medium} 12 {}', text=violation['values'][1])
        self.violation_at_value.grid(column='1', padx='150', row='2')
        self.violation_type = tk.Label(self.log_window_info)
        self.violation_type.config(font='{Yu Gothic Medium} 12 {}', relief='ridge', text='Violation Type:')
        self.violation_type.grid(column='0', padx='5', pady='2', row='3', sticky='w')
        self.violation_type_value = tk.Label(self.log_window_info)
        self.violation_type_value.config(font='{Yu Gothic Medium} 12 {}', text=violation['values'][2])
        self.violation_type_value.grid(column='1', padx='150', row='3')
        self.video_proof_link = tk.Label(self.log_window_info)
        self.video_proof_link.config(font='{Yu Gothic Medium} 12 {}', relief='ridge', text='Video Proof Link:')
        self.video_proof_link.grid(column='0', padx='5', pady='2', row='4', sticky='w')
        self.video_proof_link_value = tk.Label(self.log_window_info)
        self.video_proof_link_value.config(cursor='hand2', font='{Yu Gothic Medium} 12 {underline}',
                                           foreground='#3064b1', highlightcolor='#3064b1')
        self.video_proof_link_value.config(justify='left', text='violations/lane/violation-id-5.jpg', wraplength='200')
        self.video_proof_link_value.grid(column='1', padx='30', row='4', sticky='w')
        self.log_window_info.config(font='{Century Schoolbook} 14 {bold}', height='225', labelanchor='n', padx='0')
        self.log_window_info.config(pady='0', takefocus=False, text='Culprit Info', width='400')
        self.log_window_info.grid(row='0', column='1')
        self.log_window_info.grid_propagate(0)

    def createLogInfoWindow(self):
        try:
            if self.log_window.state() != 'normal':
                self.log_window.mainloop()
        except:
            self.log_window = tk.Toplevel()
            self.log_window.config(borderwidth='0', padx='10', pady='10', takefocus=True)
            self.log_window.geometry('540x250')
