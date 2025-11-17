
#================================================
# ===           CARLA emulator client         ===
# ===   -----------------------------------   ===
# ===  Actions progress window implementation ===
#================================================

import tkinter as tk
import time
from tkinter import ttk

class ProgressWnd(object):

    #--------------------------
    #--- Public properties  ---
    #--------------------------

    # --- Parent window for this popup
    parent = None

    # --- Progress popup window object reference
    popupWnd = None

    exit = False

    #--------------------
    #--- Constructor  ---
    #--------------------

    # --- parent: Parent window for this popup
    def __init__(self, parent):

        self.parent = parent

    #-----------------------
    #--- Public methods  ---
    #-----------------------

    # --- Show progress window
    # --- text: progress text to be displayed
    def show(self, text):

        self.exit = False
        self.popupWnd = tk.Toplevel(background="blue2")
        self.popupWnd.grab_set()
        self.popupWnd.overrideredirect(True)
        frame = tk.Frame(self.popupWnd, background="blue2")
        frame.pack(padx=10, pady=10)
        progress = ttk.Progressbar(frame, orient='horizontal', 
                                   mode='indeterminate')
        progress.pack(expand=True, fill="x", padx=5, pady=5)
        progress.start(50)
        label = tk.Label(frame, text=text, background="blue2", foreground="white", font=("Roboto", 10)) 
        label.pack(side="top", fill="x", padx=5, pady=5)
        self.center_popup(self.popupWnd)

    # --- Destroy progress window
    def hide(self):

        if self.popupWnd is not None:
            self.exit = True
            self.popupWnd.destroy()
            self.popupWnd = None

    # --- Wait for background thread is running
    # --- thread: thread to waiting for
    def wait(self, thread):

        self.exit = False

        while self.exit == False:
            if self.popupWnd is not None:
                self.popupWnd.update()
                time.sleep(0.001)

    #-----------------------

    #------------------------------
    #--- Public service methods ---
    #------------------------------

    # --- Center popup window on the screen 
    # --- wnd: popup window to be centered
    def center_popup(self, wnd):
        wnd.update_idletasks()
        width = wnd.winfo_width()
        height = wnd.winfo_height()
        screen_width = wnd.winfo_screenwidth()
        screen_height = wnd.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        wnd.geometry(f"{width}x{height}+{x}+{y}")

    #------------------------------

