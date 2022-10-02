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

    # Class variables (Initialize all as none until they are required)
    debug = None
    output_file = None
    conn = None
    c = None

    # Constructor for Interface object
    def __init__(self):
        self.root = Tk()  # Calls tktinker object and sets self.root to be equal to it
        self.debug = 0
        self.calcBackend = pholeCalc()
        #Generate unique hash to store export of scan
        self.output_file = "data/ply/" + self.calcBackend.hash((''.join(random.choice(string.ascii_letters) for i in range(20)))) + ".ply"

    def startCalc(self):
        print("Performing calculations with debugout") if self.debug else print(
            "Performing calculations without debugout")
        self.calcBackend.api('n', 0, "data/ply/input.ply", self.debug)

    def toggleDebug(self):
        if self.debug:
            print("Debug DISABLED")
            self.debug = 0
        else:
            self.debug = 1
            print("Debug ENABLED")


# Main of program, creates main window that pops up when program opns
if __name__ == "__main__":

    # create a root window
    gui = interface()
    print(f"___                  _ ____ \n / _ \ _   _  __ _  __| |  _ \ \n| | | | | | |/ _` |/ _` | |_) | \n| |_| | |_| | (_| | (_| |  __/ \n \__\_\\__,_|\__,_|\__,_|_|")
    print("Output file is: ", gui.output_file)

    # Setup theming
    current_theme = 'default'
    dull_black = "#000000"

    # Configure GUI title and Geometry
    gui.root.configure(background=themes[current_theme]['background_colo'])
    gui.root.title("Quad-P")
    screen_width = gui.root.winfo_screenwidth()
    screen_height = gui.root.winfo_screenheight()
    gui.root.geometry("%dx%d" % (screen_width, screen_height))

    # Create Location for video feed in GUI
    video_label = Label(gui.root, fg=dull_black, bg=dull_black, height=round(
        screen_height*0.0215), width=round(screen_width*0.03555), borderwidth=5, relief="sunken")
    video_label.grid(column=0, row=1, columnspan=10, pady=35, ipadx=5, ipady=5)
    
    # Create Location for text output in GUI
    bottom_data_label = Label(gui.root, fg=themes[current_theme]['main_colo'], bg=themes[current_theme]['main_colo'], height=round(
        screen_height*0.0555), width=round(screen_width*0.059), borderwidth=5, relief="solid")
    bottom_data_label.grid(column=0, row=2, columnspan=10,
                           pady=35, ipadx=5, ipady=5, sticky=SW)

    # Make main menu bar
    menubar = Menu(gui.root, background=themes[current_theme]
                   ['main_colo'],
                   fg=themes[current_theme]
                   ['text_colo'], borderwidth=5, relief="solid")

    # Declare file and edit for showing in menubar
    scan = Menu(menubar, tearoff=False, fg=themes[current_theme]
                ['text_colo'], background=themes[current_theme]['main_colo'])
    view = Menu(menubar, tearoff=False, fg=themes[current_theme]
                ['text_colo'], background=themes[current_theme]['main_colo'])
    edit = Menu(menubar, tearoff=False, fg=themes[current_theme]
                ['text_colo'], background=themes[current_theme]['main_colo'])
    help = Menu(menubar, tearoff=False, fg=themes[current_theme]
                ['text_colo'], background=themes[current_theme]['main_colo'])

    # Add commands in in scan menu
    scan.add_command(label="New", command=lambda: gui.startCalc())
    scan.add_command(label="Open")
    scan.add_command(label="Save")

    # Add commands in view menu
    view.add_command(label="Fullscreen")
    view.add_separator()
    view.add_command(label="Theming")

    # Add commands in edit menu
    edit.add_checkbutton(label="Toggle Debug", variable=gui.debug)
    edit.add_separator()
    edit.add_command(label="M Density")

    # Add commands in help menu
    help.add_command(label="About")
    help.add_command(label="Docs")
    help.add_command(label="Diagnostics")
    help.add_command(label="Contact")
    help.add_separator()
    help.add_command(label="Exit", command=gui.root.quit)

    # Display the file and edit declared in previous step
    menubar.add_cascade(label="Scan", menu=scan)
    menubar.add_cascade(label="View", menu=view)
    menubar.add_cascade(label="Edit", menu=edit)
    menubar.add_cascade(label="Help", menu=help)

    # Displaying of menubar in the app
    gui.root.config(menu=menubar)

    # Loop the main
    gui.root.mainloop()
