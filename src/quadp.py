# Creation Date 9/7/22
# Author: Dalton Bailey
# Course: CSCI 490
# Instructor Sam Siewert

from tkinter import *
import yaml
import tkinter as tk
from tkinter import ttk
import numpy as np
import cv2 as cv
import atexit
import os
from os.path import exists
from themes import *
from calc import *
import pyrealsense2 as rs

# Interface class; data structure to hold information about the user of the program and functions to make the GUI.
class interface():

    # Class variables (Initialize all as none until they are required)
    
    output_file = None
    # User config variables
    conf_file = 'data/conf.yml'
    conf = None
    theme = None
    username = None
    debug = None
    screen_width = None
    screen_height = None

    # Constructor for Interface object
    def __init__(self):
        self.root = Tk()  # Calls tktinker object and sets self.root to be equal to it
        self.calcBackend = pholeCalc() # Initialize the calculation backend
        
        self.screen_width = self.root.winfo_screenwidth() # Get width of current screen
        self.screen_height = self.root.winfo_screenheight() # Get height of current screen
        
        # Set program title and geometry of root gui
        self.root.title("Quad-P")
        self.root.geometry("%dx%d" % (self.screen_width, self.screen_height))
        
        #Generate unique hash to store export of scan (takes some time)
        self.output_file = "data/ply/" + self.calcBackend.hash((''.join(random.choice(string.ascii_letters) for i in range(7)))) + ".ply"
        
        # Load configuration from yaml file
        self.loadConfig()
    
    def exportScan(self):
        return 
    
    # Wrapper for calculation backend
    def startCalc(self):
        print("Performing calculations with debugout") if self.debug else print(
            "Performing calculations without debugout")
        self.calcBackend.api('n', 0, "data/ply/input.ply")
    
    def quitWrapper(self): 
        print("[QUAD_P] (debug) User has selected graceful exit") if gui.debug else None
        self.calcBackend.closeDBconn()
        self.saveConfig()
        self.root.quit()
        
    def saveConfig(self): 
        print("[QUAD_P] (debug) Saving modifed configs to ", self.conf_file) if gui.debug else None
        self.conf['debug'] = self.debug
        self.conf['username'] = self.username
        self.conf['theme'] = self.theme 
        # Save any modified configs to the yaml file
        with open(self.conf_file, 'w') as f:
            yaml.dump(self.conf, f)
            
    def loadConfig(self): 
        #Check if userdata file exists in current directory
        file_exists = exists(self.conf_file)  
        
        #If yaml file DNE create a fresh one and set all values to defaults
        if file_exists == 0: 
            dict = {'username': 'guest', 'themechoice': 'default', 'debug': 0}
            with open(self.conf_file, 'w') as f:
                yaml.dump(dict, f)
        
        #Load values from yaml file into self.conf       
        with open(self.conf_file) as f:
            self.conf = yaml.safe_load(f)
        
        #Try to load values from self.conf into respective vars
        try: 
            self.debug = self.conf['debug']
            self.calcBackend.debug = self.debug
            self.username = self.conf['username']
            self.theme = self.conf['theme']
        except: 
            # os.remove(self.conf_file)
            raise Exception("Could not load data from configuration file, potentially corrupted/malformed; remove or correct")
    
    def changeConfig(self):
        self.loadConfig()
        var = tk.BooleanVar()
        window = tk.Toplevel(self.root) #Create new window and base it off orginal window
        window.configure(background=themes[gui.theme]['background_colo']) #Set background color
        window.geometry("676x856") #Set size of window
        def get_name_input():
            self.username=inputname.get("1.0","end-1c")
            nameinputlabel2.config(text = "Username is now: " + self.username)
            
        def commit_changes():
            self.debug = var.get()
            self.saveConfig()
            commitchangeslabel.config(text = "Changes Commited!")
            window.destroy
            

        label = Label(window, text='Configuration', font=("Arial", 15), fg=themes[gui.theme]['text_colo'], bg=themes[gui.theme]['background_colo'], height=2, width=20)
        label.place(relx=0.5, rely=0, anchor=N)
        separator1 = ttk.Separator(window, orient='horizontal') # Create Horizontal seperator bar
        separator1.place(relx=0, rely=0.04, relwidth=1, relheight=0.005)
        separator2 = ttk.Separator(window, orient='vertical') # Create vertical seperator bar
        separator2.place(relx=0.05, rely=0.04, relwidth=0.005, relheight=1)
        
        nameinputlabel = Label(window, text='Name', font=("Arial", 10), fg=themes[gui.theme]['text_colo'], bg=themes[gui.theme]['background_colo'], height=2, width=8)
        nameinputlabel.place(relx=0.08, rely=0.1)
        inputname = tk.Text(window, height = 2, width = 40)
        inputname.place(relx=0.4, rely=0.1)
        enterbutton = tk.Button(window, text = "_/", command =lambda: get_name_input())
        enterbutton.place(relx=0.9, rely=0.1)
        nameinputlabel2 = Label(window, text='', font=("Arial", 10), fg=themes[gui.theme]['text_colo'], bg=themes[gui.theme]['background_colo'], height=2, width=20)
        nameinputlabel2.place(relx=0.35, rely=0.15)

        checkbutton = tk.Checkbutton(window, text="DEBUG", variable=var)
        checkbutton.place(relx=0.09, rely=0.5)

        commitchanges = tk.Button(window, text = "Confirm Changes", command =lambda: commit_changes())
        commitchanges.place(relx=0.09, rely=0.7)
        commitchangeslabel = Label(window, text='', font=("Arial", 10), fg=themes[gui.theme]['text_colo'], bg=themes[gui.theme]['background_colo'], height=2, width=20)
        commitchangeslabel.place(relx=0.35, rely=0.7)



# Main of program, creates main window that pops up when program opns
if __name__ == "__main__":

    # create a root window
    gui = interface()

    
    print(f"___                  _ ____ \n / _ \ _   _  __ _  __| |  _ \ \n| | | | | | |/ _` |/ _` | |_) | \n| |_| | |_| | (_| | (_| |  __/ \n \__\_\\__,_|\__,_|\__,_|_|")
    print(f"\n----------------------------------------")
    print("[QUAD_P] Welcome: ", gui.username)
    print("[QUAD_P] Output file is: ", gui.output_file)
    print("[QUAD_P] Theme is: ", gui.theme)
    print("[QUAD_P] (debug) Debugging output is ENABLED") if gui.debug else None
    
    dull_black = "#000000"

    # Configure GUI title and Geometry
    gui.root.configure(background=themes[gui.theme]['background_colo'])

    # Create Location for video feed in GUI
    video_label = Label(gui.root, fg=dull_black, bg=dull_black, height=round(
        gui.screen_height*0.0215), width=round(gui.screen_width*0.03555), borderwidth=5, relief="sunken")
    video_label.grid(column=0, row=1, columnspan=10, pady=35, ipadx=5, ipady=5)
    
    
    text = Text(gui.root)
    # text.pack()
    text.insert(END, "This is a test")
    
    # Create Location for text output in GUI
    bottom_data_label = Label(gui.root, fg=themes[gui.theme]['main_colo'], bg=themes[gui.theme]['main_colo'], height=round(
        gui.screen_height*0.0555), width=round(gui.screen_width*0.059), borderwidth=5, relief="solid")
    bottom_data_label.grid(column=0, row=2, columnspan=10,
                           pady=35, ipadx=5, ipady=5, sticky=SW)

    bottom_data_label.config(text=text)
    
    # Make main menu bar
    menubar = Menu(gui.root, background=themes[gui.theme]
                   ['main_colo'],
                   fg=themes[gui.theme]
                   ['text_colo'], borderwidth=5, relief="solid")

    # Declare file and edit for showing in menubar
    scan = Menu(menubar, tearoff=False, fg=themes[gui.theme]
                ['text_colo'], background=themes[gui.theme]['main_colo'])
    view = Menu(menubar, tearoff=False, fg=themes[gui.theme]
                ['text_colo'], background=themes[gui.theme]['main_colo'])
    edit = Menu(menubar, tearoff=False, fg=themes[gui.theme]
                ['text_colo'], background=themes[gui.theme]['main_colo'])
    help = Menu(menubar, tearoff=False, fg=themes[gui.theme]
                ['text_colo'], background=themes[gui.theme]['main_colo'])

    # Add commands in in scan menu
    scan.add_command(label="New", command=lambda: gui.startCalc())
    scan.add_command(label="Open")
    scan.add_command(label="Save")

    # Add commands in view menu
    view.add_command(label="Database")
    view.add_separator()
    view.add_command(label="Fullscreen")

    # Add commands in edit menu
    edit.add_command(label="Config", command=lambda: gui.changeConfig())
    edit.add_separator()
    edit.add_command(label="M Density")

    # Add commands in help menu
    help.add_command(label="About")
    help.add_command(label="Docs")
    help.add_command(label="Diagnostics")
    help.add_command(label="Contact")
    help.add_separator()
    help.add_command(label="Exit", command=lambda: gui.quitWrapper())

    # Display the file and edit declared in previous step
    menubar.add_cascade(label="Scan", menu=scan)
    menubar.add_cascade(label="View", menu=view)
    menubar.add_cascade(label="Edit", menu=edit)
    menubar.add_cascade(label="Help", menu=help)

    # Displaying of menubar in the app
    gui.root.config(menu=menubar)

    # Loop the main
    gui.root.mainloop()

## CODE GRAVEYARD ##
# def toggleDebug(self):
#     if self.debug:
#         print("Debug DISABLED")
#         self.debug = 0
#     else:
#         self.debug = 1
#         print("Debug ENABLED")