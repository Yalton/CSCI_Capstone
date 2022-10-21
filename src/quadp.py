############################################################
# quadp.py
# GUI frontend for program
# Manages realsense cam vision and exporting to .ply file
############################################################
# Creation Date 9/7/22
# Author: Dalton Bailey
# Course: CSCI 490
# Instructor Sam Siewert
############################################################

# from tkinter import *
import yaml
import tkinter as tk
from tkinter import ttk
import numpy as np
import cv2 as cv2
import matplotlib.pyplot as plt
import atexit
import os
from os.path import exists
from themes import *
import calibration as cal
from calc import *
import pyrealsense2 as rs
import time
import PIL as pil
from PIL import ImageTk
from IPython.display import clear_output  # Clear the screen

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
    scanning = None
    units = None
    density = None
    
    screen_width = None
    screen_height = None

    # Global Tkinter Widgets
    video_out = None
    cam_controls = None
    s_scan_button = None
    export_button = None

    # Constructor for Interface object
    def __init__(self):
        self.root = tk.Tk()  # Calls tktinker object and sets self.root to be equal to it
        self.calcBackend = pholeCalc()  # Initialize the calculation backend

        # Generate unique hash to store export of scan (takes some time)
        self.output_file = "data/ply/" + self.calcBackend.hash(
            (''.join(random.choice(string.ascii_letters) for i in range(7)))) + ".ply"

        # Load configuration from yaml file
        self.loadConfig()

        self.screen_width = self.root.winfo_screenwidth()  # Get width of current screen
        self.screen_height = self.root.winfo_screenheight()  # Get height of current screen

        # Set program title and geometry of root gui
        self.root.title("Quad-P")
        self.root.geometry("%dx%d" % (self.screen_width, self.screen_height))

        # Configure GUI title and Geometry
        self.root.configure(background=themes[self.theme]['background_colo'])

        # # Create Location for video feed in GUI
        # self.video_out = tk.Canvas(
        #     self.root, bg="#000000", height=480, width=640, borderwidth=5, relief="sunken").place(relx=0, rely=0.4, relwidth=0.15, relheight=0.15)
        
        # Create Location for video feed in GUI
        self.video_out = tk.Canvas(
            self.root, bg="#000000", height=480, width=640, borderwidth=5, relief="sunken").grid(column=0, row=1, columnspan=10, pady=35, ipadx=5, ipady=5, sticky=tk.NS)

        # Create Location for text output in GUI
        self.cam_controls = tk.Label(self.root, fg=themes[self.theme]['background_colo'], bg=themes[self.theme]['background_colo'], height=round(
            self.screen_height*0.002555), width=round(self.screen_width*0.059))
        self.cam_controls.grid(column=0, row=2, columnspan=10,
                        sticky=tk.NS)

        self.s_scan_button = tk.Button(self.cam_controls, text="Enable Camera", command=lambda: self.startScan())
        self.s_scan_button.grid(column=1, row=0, padx=20)
        # us_scan_button = tk.Button(cam_controls, text="Disable Camera", command=lambda: gui.stopScan())
        # us_scan_button.grid(column=2, row=0, padx=20)
        self.export_button = tk.Button(self.cam_controls, text="Export Scan", command=lambda: self.exportScan())
        self.export_button.grid(column=3, row=0, padx=20)
        
        # Create Location for text output in GUI
        self.b_data = tk.Label(self.root, fg=themes[self.theme]['main_colo'], bg=themes[self.theme]['main_colo'], height=round(
            self.screen_height*0.00555), width=round(self.screen_width*0.059), borderwidth=5, relief="solid")
        self.b_data.grid(column=0, row=3, columnspan=10,
                    sticky=tk.SW)



    def startScan(self):
        pipe = rs.pipeline()                      # Create a pipeline
        cfg = rs.config()                         # Create a default configuration
        print("[QUAD_P] Pipeline is created") if gui.debug else None

        print("[QUAD_P] Searching For Realsense Devices..") if gui.debug else None
        selected_devices = []                     # Store connected device(s)

        for d in rs.context().devices:
            selected_devices.append(d)
            print(d.get_info(rs.camera_info.name))
        if not selected_devices:
            print("No RealSense device is connected!")
            return
        
        print("[QUAD_P] (debug) Streaming camera vision to GUI... ") if gui.debug else None


        rgb_sensor = depth_sensor = None

        for device in selected_devices:                         
            print("Required sensors for device:", device.get_info(rs.camera_info.name))
            for s in device.sensors:                              # Show available sensors in each device
                if s.get_info(rs.camera_info.name) == 'RGB Camera':
                    print("[QUAD_P] - RGB sensor found") if gui.debug else None
                    rgb_sensor = s                                # Set RGB sensor
                if s.get_info(rs.camera_info.name) == 'Stereo Module':
                    depth_sensor = s                              # Set Depth sensor
                    print("[QUAD_P] - Depth sensor found") if gui.debug else None
        colorizer = rs.colorizer()                                # Mapping depth data into RGB color space
        profile = pipe.start(cfg)                                 # Configure and start the pipeline

        fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(24,8)) # Show 1 row with 2 columns for Depth and RGB frames
        title = ["Depth Image", "RGB Image"]                      # Title for each frame

        for _ in range(10):                                       # Skip first frames to give syncer and auto-exposure time to adjust
            frameset = pipe.wait_for_frames()
            
        for _ in range(30):                                        # Increase to display more frames
            frameset = pipe.wait_for_frames()                     # Read frames from the file, packaged as a frameset
            depth_frame = frameset.get_depth_frame()              # Get depth frame
            color_frame = frameset.get_color_frame()              # Get RGB frame

            colorized_streams = []                                # This is what we'll actually display
            if depth_frame:
                colorized_streams.append(np.asanyarray(colorizer.colorize(depth_frame).get_data()))
            if color_frame:
                colorized_streams.append(np.asanyarray(color_frame.get_data()))
            
            for i, ax in enumerate(axs.flatten()):                # Iterate over all (Depth and RGB) colorized frames
                if i >= len(colorized_streams): continue          # When getting less frames than expected
                plt.sca(ax)                                       # Set the current Axes and Figure
                plt.imshow(colorized_streams[i])                  # colorized frame to display
                plt.title(title[i])                               # Add title for each subplot
            clear_output(wait=True)                               # Clear any previous frames from the display
            plt.tight_layout()                                    # Adjusts display size to fit frames
            plt.pause(1)                                          # Make the playback slower so it's noticeable
            
        pipe.stop()                                               # Stop the pipeline
        print("[QUAD_P] Done!")

        # # Declare RealSense pipeline, encapsulating the actual device and sensors
        # pipe = rs.pipeline()
        # config = rs.config()
        # # Enable depth stream
        # # config.enable_stream(rs.stream.depth)

        # # Start streaming with chosen configuration
        # pipe.start(config)
        
        # #Declare alligning variable
        # align = rs.align(rs.stream.depth)
        # #Declare booleans responsible for dataflow
        # self.export_scan = False
        # self.scanning = True
        # try:
        #     while self.scanning:
        #         print("[QUAD_P] (debug) ..................... ") if gui.debug else None
        #         # Get frameset of color and depth
        #         frames = pipe.wait_for_frames()

        #         color_frame = frames.get_color_frame()

        #         color_image = np.asanyarray(color_frame.get_data())

        #         # Render images
        #         # depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        #         img = pil.Image.fromarray(color_image)
        #         imgtk = ImageTk.PhotoImage(image=img)   
        #         img.save('debug.png') if gui.debug else None
        #         self.s_scan_button = tk.Button(self.cam_controls, text="Disable Camera", command=lambda: self.stopScan())
        #         self.s_scan_button.grid(column=1, row=0, padx=20)
        #         self.video_out = tk.Label(self.root, bg="#000000", height=480, width=640, borderwidth=5, relief="sunken", image=imgtk).grid(column=0, row=1, columnspan=10, pady=35, ipadx=5, ipady=5, sticky=tk.NS)
        #         # self.video_out.create_image(10, 10, anchor="nw", image=imgtk)

        # finally:
        #     pipe.stop()
        
    def stopScan(self):
        print("[QUAD_P] (debug) Disabling live feed...") if gui.debug else None
        self.scanning = False
        self.s_scan_button = tk.Button(self.cam_controls, text="Enable Camera", command=lambda: self.stopScan())
        self.s_scan_button.grid(column=1, row=0, padx=20)
        if self.export_scan: 
            self.exportScan()
    
    def viewScan(self):
        pcd = o3d.io.read_point_cloud(self.output_file)  # Read the point cloud
        o3d.visualization.draw_geometries([pcd])# Visualize the point cloud within open3d

    def exportScan(self):
        start_time = time.process_time()  # start timer
        print("Searching For Realsense Devices..")
        selected_devices = []                     # Store connected device(s)

        for d in rs.context().devices:
            selected_devices.append(d)
            print(d.get_info(rs.camera_info.name))
        if not selected_devices:
            print("No RealSense device is connected!")
            return

        print(
            "[QUAD_P] (debug) Exporting camera's vison as .ply file...") if gui.debug else None
        # Declare pointcloud object, for calculating pointclouds and texture mappings
        pc = rs.pointcloud()
        # We want the points object to be persistent so we can display the last cloud when a frame drops
        points = rs.points()

        # Declare RealSense pipeline, encapsulating the actual device and sensors
        pipe = rs.pipeline()
        config = rs.config()
        # Enable depth stream
        config.enable_stream(rs.stream.depth)

        # Start streaming with chosen configuration
        pipe.start(config)

        # We'll use the colorizer to generate texture for our PLY
        # (alternatively, texture can be obtained from color or infrared stream)
        colorizer = rs.colorizer()

        try:
            # Give camera time to adjust to exposure 
            for x in range(10): 
                pipe.wait_for_frames()

            # Wait for the next set of frames from the camera
            frames = pipe.wait_for_frames()
            colorized = colorizer.process(frames)

            # Create save_to_ply object
            ply = rs.save_to_ply(self.output_file)

            # Set options to the desired values
            # In this example we'll generate a textual PLY with normals (mesh is already created by default)
            ply.set_option(rs.save_to_ply.option_ply_binary, False)
            ply.set_option(rs.save_to_ply.option_ply_normals, True)

            print("[QUAD_P] (debug) Saving to ",
                  self.output_file, "...") if gui.debug else None

            # Apply the processing block to the frameset which contains the depth frame and the texture
            ply.process(colorized)

            stop_time = time.process_time()  # start timer
            print(f"[QUAD_P] (debug) Export Complete!\n Elapsed time was ", (stop_time - start_time) * 1000, "ms.\n") if gui.debug else None
        finally:
            pipe.stop()

    # Wrapper for calculation backend
    def startCalc(self):
        print("Performing calculations with debugout") if self.debug else print(
            "Performing calculations without debugout")
        self.calcBackend.api('y', self.density, self.output_file) if self.density else self.calcBackend.api('n', -1, self.output_file)
        # self.calcBackend.api('n', 0, self.output_file)
    
        # Wrapper for calculation backend
    def calibrate(self):
        start_time = time.process_time()  # start timer
        print("Performing calibrations on Realsense Device") if self.debug else None
        try:
            cal.main()
            print(f"[QUAD_P] (debug) Calibration Complete!\n Elapsed time was ", (stop_time - start_time) * 1000, "ms.\n") if gui.debug else None
        except:
            raise Exception(
                "[QUAD_P] (exception) Calibration has failed, realsense device potentially disconnected.")


    # Graceful exit function
    def quitWrapper(self):
        print("[QUAD_P] (debug) User has selected graceful exit") if self.debug else None
        try: 
            self.calcBackend.closeDBconn()
            self.saveConfig()
            self.root.quit()
        except:
            raise Exception(
                "[QUAD_P] (exception) Graceful exit has failed.")

    # Write the current config dictionary to the yaml file
    def saveConfig(self):
        print("[QUAD_P] (debug) Saving modifed configs to ",
              self.conf_file) if self.debug else None
        self.conf['debug'] = self.debug
        self.conf['theme'] = self.theme
        self.conf['username'] = self.username
        self.conf['units'] = self.units
        # Save any modified configs to the yaml file
        with open(self.conf_file, 'w') as f:
            yaml.dump(self.conf, f)

    # Load the config dictionary from the yaml file
    def loadConfig(self):
        # Check if userdata file exists in current directory
        file_exists = exists(self.conf_file)

        # If yaml file DNE create a fresh one and set all values to defaults
        if file_exists == 0:
            dict = {'username': 'guest', 'themechoice': 'default', 'debug': 0, 'units': 0}
            with open(self.conf_file, 'w') as f:
                yaml.dump(dict, f)

        # Load values from yaml file into self.conf
        try: 
            with open(self.conf_file) as f:
                self.conf = yaml.safe_load(f)
        except:
            # os.remove(self.conf_file)
            raise Exception(
                "[QUAD_P] (exception) Could not open configuration file.")

        # Try to load values from self.conf into respective vars
        try:
            self.debug = self.conf['debug']
            self.calcBackend.debug = self.debug
            self.theme = self.conf['theme']
            self.username = self.conf['username']
            self.units = self.conf['units']
            self.calcBackend.units = self.units
        except:
            # os.remove(self.conf_file)
            raise Exception(
                "[QUAD_P] (exception) Could not load data from configuration file, potentially corrupted/malformed; remove or correct")

    # Function responsible for creating the config edit popup window
    def changeConfig(self):
        self.loadConfig()

        # Init tkinter vars
        debug_var = tk.BooleanVar()
        unit_var = tk.IntVar()
        theme_var = tk.IntVar()

        debug_var.set(self.debug)
        # key = {i for i in themeidict if themeidict[i]==self.theme}
        # print(key)
        theme_var.set({i for i in themeidict if themeidict[i]==self.theme})
        
        # Create new window and base it off orginal window
        window = tk.Toplevel(self.root)
        # Set background color
        window.configure(background=themes[self.theme]['background_colo'])
        window.geometry("%dx%d" % (self.screen_width*0.5,
                        self.screen_height*0.75))  # Set size of window

        def get_name_input():
            self.username = inputname.get("1.0", "end-1c")
            # nameinputlabel2.config(text="Username is now: " + self.username)
        
        def commit_changes():
            self.theme = themeidict[theme_var.get()]
            self.debug = debug_var.get()
            self.units = unit_var.get()
            self.saveConfig()
            # commitchangeslabel.grid_configure(text="Changes Commited!")
            # window.quit()
            window.destroy()

        label = tk.Label(window, text='Configuration', font=(
            "Arial", 15), fg=themes[self.theme]['text_colo'], bg=themes[gui.theme]['background_colo'], height=2, width=20).grid(column=0, row=0, columnspan=10, sticky=tk.NS)
        
        # Create Horizontal seperator bar
        separator1 = ttk.Separator(window, orient='horizontal').grid(column=0, row=1, columnspan=10, sticky=tk.EW)
        # separator1.place(relx=0, rely=0.04, relwidth=1, relheight=0.005)

        # Username Buttons
        nameinputlabel = tk.Label(window, text='Name', font=(
            "Arial", 10), fg=themes[self.theme]['text_colo'], bg=themes[gui.theme]['background_colo'], height=2, width=8).grid(column=0, row=2, padx=20, pady=30)
        inputname = tk.Text(window,  height=2, width=40).grid(column=1, row=2, columnspan=10, padx=20, pady=30)
        enterbutton = tk.Button(window, text="✔", command=lambda: get_name_input()).grid(column=5, row=2, padx=20, pady=30)
        # nameinputlabel2 = tk.Label(window, text='', font=(
        #     "Arial", 10), fg=themes[self.theme]['text_colo'], bg=themes[gui.theme]['background_colo'], height=2, width=20).grid(column=2, row=3)

        # Theme buttons
        tk.Radiobutton(window, bg=themes[gui.theme]['main_colo'], text="Default", variable=theme_var, value=1).grid(column=0, row=4, padx=20, pady=30)
        tk.Radiobutton(window, bg=themes[gui.theme]['main_colo'], text="Spicy", variable=theme_var, value=2).grid(column=1, row=4, padx=20, pady=30)
        tk.Radiobutton(window, bg=themes[gui.theme]['main_colo'],text="Juicy", variable=theme_var, value=3).grid(column=2, row=4, padx=20, pady=30)

        # Unit Selection buttons
        tk.Radiobutton(window, bg=themes[gui.theme]['main_colo'], text="SI Units", variable=unit_var, value=0).grid(column=0, row=5, padx=20, pady=30)
        tk.Radiobutton(window, bg=themes[gui.theme]['main_colo'], text="Imperial Units", variable=unit_var, value=1).grid(column=1, row=5, padx=20, pady=30)

        # Debug button
        checkbutton = tk.Checkbutton(window, text="DEBUG", variable=debug_var).grid(column=0, row=6, padx=20, pady=30)
        
        # Commit changes button
        commitchanges = tk.Button(
            window, text="Confirm Changes ✔", command=lambda: commit_changes()).grid(column=0, row=7, padx=20, pady=30)

    def inputDensity(self):
        def inputDensity():
            def get_density_input():
                density = desnityinput.get("1.0", "end-1c")
                print(density)

        # Create new window and base it off orginal window
        window = tk.Toplevel(self.root)
        window.configure(background=themes[self.theme]['background_colo'])
        window.geometry("%dx%d" % (self.screen_width*0.4, self.screen_height*0.65))  # Set size of window
        # row0 = tk.Label(window,  fg=themes[self.theme]['background_colo'], bg=themes[gui.theme]['background_colo'], height=2, width=20).place(x=0, y=0)
        
        label = tk.Label(window, text='Input Material Density', font=("Arial", 15), fg=themes[self.theme]['text_colo'], bg=themes[gui.theme]['background_colo'], height=2, width=20).place(x=0, y=0)
        
        # Create Horizontal seperator bar
        separator = ttk.Separator(window, orient='horizontal').place(x=0, y=80, relwidth=1, relheight=0.005)

        # # Username Buttons
        desnityinputlabel = tk.Label(window, text='Density', font=("Arial", 10), fg='#000000', bg='#c0c0c0', height=2, width=8).place(x=0, y=160)
        desnityinput = tk.Text(window,  height=2, width=40).place(x=160, y=160)
        enterbutton = tk.Button(window, text="✔", command=lambda: get_density_input()).place(x=860, y=160)


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


    # Make main menu bar
    menubar = tk.Menu(gui.root, background=themes[gui.theme]
                      ['main_colo'],
                      fg=themes[gui.theme]
                      ['text_colo'], borderwidth=5, relief="solid")

    # Declare file and edit for showing in menubar
    scan = tk.Menu(menubar, tearoff=False, fg=themes[gui.theme]
                   ['text_colo'], background=themes[gui.theme]['main_colo'])
    view = tk.Menu(menubar, tearoff=False, fg=themes[gui.theme]
                   ['text_colo'], background=themes[gui.theme]['main_colo'])
    edit = tk.Menu(menubar, tearoff=False, fg=themes[gui.theme]
                   ['text_colo'], background=themes[gui.theme]['main_colo'])
    help = tk.Menu(menubar, tearoff=False, fg=themes[gui.theme]
                   ['text_colo'], background=themes[gui.theme]['main_colo'])

    # Add commands in in scan menu
    scan.add_command(label="New", command=lambda: gui.exportScan())
    scan.add_command(label="Calc", command=lambda: gui.startCalc())
    scan.add_command(label="Open", command=lambda: gui.viewScan())
    scan.add_separator()
    scan.add_command(label="Calibrate", command=lambda: gui.calibrate())

    # Add commands in view menu
    view.add_command(label="Database")
    view.add_separator()
    view.add_command(label="Fullscreen")

    # Add commands in edit menu
    edit.add_command(label="Config", command=lambda: gui.changeConfig())
    edit.add_separator()
    edit.add_command(label="M Density", command=lambda: gui.inputDensity())

    # Add commands in help menu
    help.add_command(label="About")
    help.add_command(label="Docs")
    # help.add_command(label="Diagnostics")
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

# # Get frameset of color and depth
# frames = pipe.wait_for_frames()
# # frames.get_depth_frame() is a 640x480 depth image

# # Align the depth frame to color frame
# aligned_frames = align.process(frames)

# # Get aligned frames
# # aligned_depth_frame is a 640x480 depth image
# aligned_depth_frame = aligned_frames.get_depth_frame()
# color_frame = aligned_frames.get_color_frame()

# # Validate that both frames are valid
# if not aligned_depth_frame or not color_frame:
#     continue

# depth_image = np.asanyarray(aligned_depth_frame.get_data())
# color_image = np.asanyarray(color_frame.get_data())

# # Render images
# depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)