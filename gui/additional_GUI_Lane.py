# System Modules ##
import time
import threading
import os

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
        self.violation_log_num = 0
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

        self.violation_log['columns'] = ("Vehicle ID", "Vehicle Type", "Violation At", "Violation Type")

        self.violation_log.column("#0", anchor=CENTER, width=75)
        self.violation_log.column("Vehicle ID", anchor=W, width=80)
        self.violation_log.column("Vehicle Type", anchor=W, width=85)
        self.violation_log.column("Violation At", anchor=W, width=85)
        self.violation_log.column("Violation Type", anchor=W, width=105)


        self.violation_log.heading("#0", text="#", anchor=W)
        self.violation_log.heading("Vehicle ID", text="Vehicle ID", anchor=W)
        self.violation_log.heading("Vehicle Type", text="Vehicle Type", anchor=W)
        self.violation_log.heading("Violation At", text="Violation At", anchor=W)
        self.violation_log.heading("Violation Type", text="Violation Type", anchor=W)

        self.violation_log.configure(yscrollcommand=self.violation_log_scrollbar.set)
        self.violation_log.bind("<<TreeviewSelect>>", self.additionalLogInfo)

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

    def showViolationFrame(self, violation_log, lock):
        lock.acquire()
        log_in_loop = False
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
                self.logUpdate(log=violation_log, log_updated=log_in_loop)
                log_in_loop = True
        time.sleep(1)
        self.showNoneFrame()
        lock.release()

    def logUpdate(self, log=None, log_updated=True):
        if log is not None and not log_updated:
            for i in range(len(log['ids'])):
                # addition of data
                self.violation_log.insert(parent='', index='end', iid=self.violation_log_num, text=str(self.violation_log_num),
                                              values=(log['ids'][i], log['class_names'][i], str(log['times'][i]), log['types'][i]))
                self.violation_log_num += 1


    def additionalLogInfo(self, record):
        violation = self.violation_log.item(self.violation_log.selection())
        self.createLogInfoWindow()

        self.log_window.title('Info for Vehicle ID: ' + str(violation['values'][0]))

        self.vehicle_image = tk.Canvas(self.log_window)
        self.vehicle_image.config(height='100', relief='groove', width='100')

        violator_image = cv2.imread(self.extractLocation(id=int(violation['values'][0])))
        violator_image = cv2.resize(violator_image, (100, 100))
        global tkinter_readable_frame
        tkinter_readable_frame = ImageTk.PhotoImage(Image.fromarray(violator_image))
        self.vehicle_image.create_image(0, 0, image=tkinter_readable_frame, anchor=NW)
        self.vehicle_image.grid(row='0', column='0')

        self.log_window_info = tk.LabelFrame(self.log_window)
        self.vehicle_id = tk.Label(self.log_window_info)
        self.vehicle_id.config(cursor='arrow', font='{Yu Gothic Medium} 12 {}', highlightcolor='#030505',
                               relief='ridge')
        self.vehicle_id.config(text='Vehicle ID:')
        self.vehicle_id.grid(column='0', padx='5', pady='2', sticky='w')
        self.vehicle_id_value = tk.Label(self.log_window_info)
        self.vehicle_id_value.config(font='{Yu Gothic Medium} 12 {}', text=violation['values'][0])
        self.vehicle_id_value.grid(column='1', padx='130', row='0')
        self.vehicle_type = tk.Label(self.log_window_info)
        self.vehicle_type.config(font='{Yu Gothic Medium} 12 {}', relief='ridge', text='Vehicle Type:')
        self.vehicle_type.grid(column='0', padx='5', pady='2', row='1', sticky='w')
        self.vehicle_type_value = tk.Label(self.log_window_info)
        self.vehicle_type_value.config(font='{Yu Gothic Medium} 12 {}', text=violation['values'][1])
        self.vehicle_type_value.grid(column='1', padx='150', row='1', sticky='e')
        self.violation_at = tk.Label(self.log_window_info)
        self.violation_at.config(font='{Yu Gothic Medium} 12 {}', relief='ridge', text='Violation At:')
        self.violation_at.grid(column='0', padx='5', pady='2', row='2', sticky='w')
        self.violation_at_value = tk.Label(self.log_window_info)
        self.violation_at_value.config(font='{Yu Gothic Medium} 12 {}', text=violation['values'][2])
        self.violation_at_value.grid(column='1', padx='150', row='2')
        self.violation_type = tk.Label(self.log_window_info)
        self.violation_type.config(font='{Yu Gothic Medium} 12 {}', relief='ridge', text='Violation Type:')
        self.violation_type.grid(column='0', padx='5', pady='2', row='3', sticky='w')
        self.violation_type_value = tk.Label(self.log_window_info)
        self.violation_type_value.config(font='{Yu Gothic Medium} 12 {}', text=violation['values'][3])
        self.violation_type_value.grid(column='1', padx='150', row='3')
        self.video_proof_link = tk.Label(self.log_window_info)
        self.video_proof_link.config(font='{Yu Gothic Medium} 12 {}', relief='ridge', text='Video Proof Link:')
        self.video_proof_link.grid(column='0', padx='5', pady='2', row='4', sticky='w')
        self.video_proof_link_value = tk.Label(self.log_window_info)
        self.video_proof_link_value.config(cursor='hand2', font='{Yu Gothic Medium} 12 {underline}',
                                           foreground='#3064b1', highlightcolor='#3064b1')
        self.video_proof_link_value.config(justify='left', text='violations/lane/violation-id-5.mp4', wraplength='200')
        self.video_proof_link_value.grid(column='1', padx='30', row='4', sticky='w')
        self.video_proof_link_value.bind("<Button-1>", self.videoPlay)

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

    def videoPlay(self, event):
        violation = self.violation_log.item(self.violation_log.selection())
        path = os.getcwd()
        path += '/' + self.extractLocation(id=int(violation['values'][0]), video=True)
        os.startfile(path)

    def extractLocation(self, id=None, video=False):
        print(id)
        violation_log_len = len(self.object.violation_log)

        for i in range(violation_log_len):
            batch_len = len(self.object.violation_log[i])

            for j in range(batch_len):
                if self.object.violation_log[i]['ids'][j] == id:
                    if not video:
                        return self.object.violation_log[i]['pictures'][j]
                    else:
                        return self.object.violation_log[i]['video_proof_links'][j]

