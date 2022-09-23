# Creation Date 9/7/22
# Author: Dalton Bailey
# Course: CSCI 490
# Instructor Sam Siewert

from tkinter import *
import tkinter as tk
from tkinter import ttk
import numpy as np
import cv2 as cv
import matplotlib as plot
import atexit
from os.path import exists
from themes import *
from calc import *

# Interface class; data structure to hold information about the user of the program and functions to make the GUI.
class interface():

    # Constructor for Interface object
    def __init__(self):
        self.root = Tk()  # Calls tktinker object and sets self.root to be equal to it
        self.calcBackend = pholeCalc()
    
    def startCalc(self):
        self.calcBackend.api('n', 0)

# Main of program, creates main window that pops up when program opns
if __name__ == "__main__":

    # create a root window
    gui = interface()
    print(f"___                  _ ____ \n / _ \ _   _  __ _  __| |  _ \ \n| | | | | | |/ _` |/ _` | |_) | \n| |_| | |_| | (_| | (_| |  __/ \n \__\_\\__,_|\__,_|\__,_|_|")
    
    # def move_window(event):
    #     gui.root.geometry('+{0}+{1}'.format(event.x_root, event.y_root))

    current_theme = 'default'
    background_colo = "#321325"
    main_colo = "#5F0F40"
    accent_colo = "#9A031E"
    text_colo = "#CB793A"
    accent2_colo = "#FCDC4D"
    dull_black = "#000000"

    gui.root.configure(background=background_colo)

    gui.root.title("Quad-P")

    screen_width = gui.root.winfo_screenwidth()
    screen_height = gui.root.winfo_screenheight()
    gui.root.geometry("%dx%d" % (screen_width, screen_height))

    # Create Title at top of main window
    # program_title = Label(gui.root, text='Pothole predictor and pruner program', font=("Verdana", 15), fg=text_colo, bg=main_colo, height=2, width=round(screen_width*0.1))
    # program_title.place(relx=0.5, rely=0, anchor=N)
    # program_title.grid(column=0, row=0)

    # buf_label0 = Label(gui.root, fg=background_colo, bg=background_colo, height=round(screen_height*0.00125), width=round(screen_width*0.059))

    # side_data_label = Label(gui.root, fg=main_colo, bg=main_colo, height=round(screen_height*0.0225), width=round(screen_width*0.05555))
    # side_data_label.grid(column=1, row=1)

    video_label = Label(gui.root, fg=dull_black, bg=dull_black, height=round(
        screen_height*0.0215), width=round(screen_width*0.03555), borderwidth=5, relief="sunken")

    bottom_data_label = Label(gui.root, fg=main_colo, bg=main_colo, height=round(
        screen_height*0.0555), width=round(screen_width*0.059), borderwidth=5, relief="solid")

    #video_label.place(relx=0.025, rely=0.05)

    # Make main menu bar
    menubar = Menu(gui.root, background=main_colo,
                   fg=text_colo, borderwidth=5, relief="solid")
    # menubar.place(relx=0.025, rely=0.05)
    # Declare file and edit for showing in menubar
    file = Menu(menubar, tearoff=False, fg=text_colo, background=main_colo)
    view = Menu(menubar, tearoff=False, fg=text_colo, background=main_colo)
    edit = Menu(menubar, tearoff=False, fg=text_colo, background=main_colo)
    help = Menu(menubar, tearoff=False, fg=text_colo, background=main_colo)

    # Add commands in in file menu
    file.add_command(label="New", command=lambda: gui.startCalc())
    file.add_command(label="Open")
    file.add_command(label="Save")
    file.add_command(label="Save As")
    file.add_command(label="Upload")
    file.add_separator()
    file.add_command(label="Exit", command=gui.root.quit)

    # Add commands in view menu
    view.add_command(label="Fullscreen")
    view.add_separator()
    view.add_command(label="Theme")

    # Add commands in edit menu
    edit.add_command(label="Cut")
    edit.add_command(label="Copy")
    edit.add_command(label="Paste")
    edit.add_command(label="Scan")
    edit.add_separator()
    edit.add_command(label="M Density")

    # Add commands in help menu
    help.add_command(label="About")
    help.add_command(label="Docs")
    help.add_command(label="Diagnostics")
    help.add_separator()
    help.add_command(label="Developer")

    # Display the file and edit declared in previous step
    menubar.add_cascade(label="File", menu=file)
    menubar.add_cascade(label="View", menu=view)
    menubar.add_cascade(label="Edit", menu=edit)
    menubar.add_cascade(label="Help", menu=help)

    # Displaying of menubar in the app

    gui.root.config(menu=menubar)

    # buf_label0.grid(column=0, row=0, columnspan=10)
    video_label.grid(column=0, row=1, columnspan=10, pady=35, ipadx=5, ipady=5)
    bottom_data_label.grid(column=0, row=2, columnspan=10,
                           pady=35, ipadx=5, ipady=5, sticky=SW)
    # Loop the main
    gui.root.mainloop()
