############################################################
# calc.py
# Calculation backend
# Calculates volume and mass from exported ply file
# Stores all calculations in a sqlite database
# Debug logging is incredibly verbose, use with caution
# Can be ran standalone, but only purpose is for debugging
############################################################
# Creation Date 9/7/22
# Author: Dalton Bailey
# Course: CSCI 490
# Instructor Sam Siewert
############################################################

# STD Python library imports
import random
import os
from os.path import exists
import time
import string

# Math imports
import numpy as np
from scipy.spatial import ConvexHull

# Visualization Imports
import matplotlib as plot
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

# Other imports
import open3d as o3d
import sqlite3
import hashlib

# Currently Unused imports
#import atexit
#import sys

class pholeCalc():

    # Class variables (Initialize all as none until they are required)
    input_file = None
    working_dir = None
    debug = None
    refx = None
    refy = None
    refz = None
    ref_points = None
    reference_plane = None
    untrimmed_point_cloud = None
    trimmed_point_cloud = None
    volume = None
    density = None
    mass = None
    units = None
    unitType = None
    salt = None
    conn = None
    c = None
    gui_print = None

    # Calculation backend initialization function
    def __init__(self):

        self.working_dir = os.path.dirname(os.path.realpath(__file__))
        self.salt = ''.join(random.choice(string.ascii_letters)
                            for i in range(10))
        #sqldb = self.working_dir+"/data/localstorage.db"
        sqldb = "data/localstorage.db"
        try:
            # self.conn = sqlite3.connect(self.working_dir+"/data/localstorage.db")
            self.conn = sqlite3.connect(sqldb)
        except:
            raise Exception(
                "Database connection to " + sqldb + " failed; potentially corrupted/malformed, or permission error")
        self.c = self.conn.cursor()
        # Create databse if it does not exist
        try:
            self.c.execute("""CREATE TABLE IF NOT EXISTS phole_VMP_Data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hash_id TEXT,
            username TEXT,
            input_file TEXT,
            date TEXT,
            position REAL,
            unit_type TEXT,
            volume REAL,
            density REAL,
            mass REAL
            )""")
        except:
            raise Exception(
                "Database creation has failed; potentially corrupted/malformed, or permission error")

    # Function to wrap closing the database connection
    def closeDBconn(self):
        self.debugout(13)
        try:
            self.conn.commit()
            self.conn.close()
        except:
            raise Exception(
                "Database comitting & closing has failed; potentially corrupted/malformed, or permission error")

    # Hash generator utility function
    def hash(self, hashingvalue):
        hash = hashlib.sha256()
        hash.update(hashingvalue.encode("utf-8"))
        return hash.hexdigest()

    # API Function, allows the GUI to call all the functions of this class and use it like a backend.
    def api(self, debug, username, dens, unitType, infile, print_to_gui):

        # Check if userdata file exists in current directory
        self.debug = debug
        self.gui_print = print_to_gui
        # file_exists = exists(infile)
        if (not exists(infile)):
            self.gui_print(text=("\n[QUAD_P]-[calc](exception)" , infile + " does not exist"))
            raise Exception(infile + " does not exist")
        
        # Populate member variables with data received from frontend
        self.density = float(dens)
        self.units = unitType
        self.input_file = infile
        unit_name = None

        if self.units:
            self.densityUnit = "ft3"
            unit_name = "imperial"
        else:
            self.densityUnit = "m3"
            unit_name = "metric"

        # start timer
        start_time = time.process_time()

        # Dump debug information to user
        self.debugout(1)
        self.debugout(14)
        self.debugout(4)
        self.debugout(12)
        self.debugout(15)
        self.debugout(3)
        
        # Perform calculations
        self.meshgen()
        self.plotarray() if self.debug else None
        self.refest()
        self.refplot() if self.debug else None
        self.trimcloud()
        self.plottrim() if self.debug else None
        self.volcalc()
        self.masscalc()
        self.debugout(2)

        # Save calculated values to database
        try:
            self.c.execute("INSERT INTO phole_VMP_Data VALUES (NULL, '{hash}', '{username}', '{input_file}', DATE('now'), '{pos}', '{db_unit_name}', '{vol}', '{dens}', '{mass}')".
                           format(hash=self.hash((str(self.volume)+str(self.density)+str(self.mass)+(self.input_file) + str(self.salt))), username=str(username), db_unit_name=str(unit_name), input_file=str(self.input_file), vol=self.volume, dens=self.density, mass=self.mass, pos='pos_placeholder'))
        except:
            raise Exception(
                "Database writing has failed; potentially corrupted/malformed, or permission error")

        # Calculate total time elapsed during calculation
        end_time = time.process_time()
        print(f"\t[QUAD_P]-[calc] Calculation time: ", (end_time - start_time) * 1000, "ms")
        self.gui_print(text=("\n[QUAD_P]-[calc] Calculation time: ", (end_time - start_time) * 1000, "ms"))

    # Generate open3d mesh from pointcloud, and convert it to a 3D numpy array
    # Code adapted from https://stackoverflow.com/questions/36920562/python-plyfile-vs-pymesh
    def meshgen(self):
        self.debugout(4)
        pcd = o3d.io.read_point_cloud(
            self.input_file)  # Read the point cloud
        self.debugout(5)
        #self.meshvis(pcd) if self.debug else None

        # Convert open3d format to numpy array
        self.untrimmed_point_cloud = np.asarray(pcd.points)
        self.debugout(6)
        return

    # Reference plane calculation using linear best fit algorithm
    # Adapted from https://gist.github.com/RustingSword/e22a11e1d391f2ab1f2c
    def refest(self):
        self.debugout(7)

        # Calculate reference hyperplane
        try:
            (rows, cols) = self.untrimmed_point_cloud.shape

            if (cols != 3):
                raise Exception("Inavlid col num; likely scanner error")

            # Compute a,b,c for function (ax + by + c = z) which defines plane that best fits the data
            G = np.ones((rows, cols))
            G[:, 0] = self.untrimmed_point_cloud[:, 0]  # X
            G[:, 1] = self.untrimmed_point_cloud[:, 1]  # Y
            Z = self.untrimmed_point_cloud[:, 2]        # Z
            (a, b, c), resid, rank, s = np.linalg.lstsq(G, Z, rcond=None)

            # Compute the normal vector for the best fitting plane
            normal = (a, b, -1)
            nn = np.linalg.norm(normal)
            normal = normal / nn

            # Compute distance (d) from origin to best fitting plane
            point = np.array([0.0, 0.0, c])
            d = -point.dot(normal)

            # Get x & y max & mins
            maxx = np.max(self.untrimmed_point_cloud[:, 0])
            maxy = np.max(self.untrimmed_point_cloud[:, 1])
            minx = np.min(self.untrimmed_point_cloud[:, 0])
            miny = np.min(self.untrimmed_point_cloud[:, 1])

            # Compute bounding x & y  points for ref plane
            self.refx, self.refy = np.meshgrid([minx, maxx], [miny, maxy])
            # Compute bounding z points for ref plane
            self.refz = (-normal[0]*self.refx - normal[1]
                         * self.refy - d)*1. / normal[2]

            # Save bounding points of reference plane to 3D numpy array
            self.ref_points = np.dstack(
                (self.refx, self.refy, self.refz)).reshape((4, 3))

            self.debugout(8)

            self.datadump() if self.debug else None
        except:
            raise Exception("Reference plane estimation has failed; " +
                            self.input_file + " may be corrupt or missing ")

    # Trim 3D numpy array based on generated reference plane
    # All points above reference plane are to be removed
    def trimcloud(self):
        self.debugout(9)

        # Compute normal vector for plane based on 4 edge points
        plane_normal = np.cross(
            self.ref_points[1] - self.ref_points[0], self.ref_points[2] - self.ref_points[0])
        plane_normal = plane_normal / np.linalg.norm(plane_normal)

        # Compute distance from plane_normal to origin of ref_points
        plane_d = -np.dot(plane_normal, self.ref_points[0])

        # Remove all points above plane using calculated normal
        self.trimmed_point_cloud = self.untrimmed_point_cloud[np.dot(self.untrimmed_point_cloud, plane_normal) + plane_d <= 0]
        # self.trimmed_point_cloud = self.untrimmed_point_cloud
        self.debugout(10)

    # Volume calculation using convex hull method
    def volcalc(self):
        self.debugout(11)
        hull = ConvexHull(self.trimmed_point_cloud)
        
        self.volume = hull.volume
        # Error correction method 1

        self.volume *= 0.6
        if(self.units):
            self.volume = self.volume / 0.028317
        
        print(f"\t[QUAD_P]-[calc] Volume calculation successful!\n----------------------------------------\n\t[QUAD_P]-[calc] Volume is", self.volume, " ", self.densityUnit)
        self.gui_print(text=("\n[QUAD_P]-[calc] Volume calculation successful!\n----------------------------------------\n[QUAD_P]-[calc] Volume is ", self.volume, " ", self.densityUnit))

    # Calculate mass of pothole
    def masscalc(self):
        if(self.density != -1):
            self.mass = (self.density * self.volume)
        else:
            self.mass = -1
        
        massUnit = 0
        if(self.units):
            massUnit = "lbs"
        else: 
            massUnit = "kg"
        
        if(self.density != -1):
            print(f"\t[QUAD_P]-[calc] Using input density and calculated volume to determine mass\n[QUAD_P]-[calc] Mass of patching material required is ",self.mass, " ", massUnit) 
            self.gui_print(text=("\n[QUAD_P]-[calc] Using input density and calculated volume to determine mass\n[QUAD_P]-[calc] Mass of patching material required is ",self.mass, " ", massUnit))


    #=================#
    # DEBUG FUNCTIONS
    #=================#

    # Open3D Visualization (DEBUG)
    def meshvis(self, pcd):
        # Visualize the point cloud within open3d
        o3d.visualization.draw_geometries([pcd])
        print("\t[QUAD_P]-[calc](debug) open3d visualization successful")
        self.gui_print(text=("\n[QUAD_P]-[calc](debug) open3d visualization successful"))


    # Plot numpy array (DEBUG)
    def plotarray(self):
        try:
            fig = plt.figure()
            ax = plt.axes(projection="3d")
            # Plot trimmed pointcloud
            print(f"\t[QUAD_P]-[calc](debug) Plotting trimmed points")
            self.gui_print(text=("\n[QUAD_P]-[calc](debug) Plotting trimmed points"))
            ax.scatter(self.untrimmed_point_cloud[:, 0], self.untrimmed_point_cloud[:, 1], self.untrimmed_point_cloud[:, 2])

            # Set labels for graph
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            ax.set_zlabel('z')

            ax.set_title("Untrimmed scan reference plane")
            # Show graph
            plt.savefig(self.working_dir+"/data/datadump/img/"+self.input_file.split('/')[-1]+"_array.png")
            plt.show()
            ax.cla()
        except:
            raise Exception("Trimmed pointcloud plotting has raised an exception ")

    # Reference plane plotting (DEBUG)
    def refplot(self):
        try:
            fig = plt.figure()
            ax = plt.axes(projection="3d")
            # plot fitted plane
            print(
                f"\t[QUAD_P]-[calc](debug) Plotting reference plane juxtaposed with numpy array...")
            
            self.gui_print(text=("\n[QUAD_P]-[calc](debug) Plotting reference plane juxtaposed with numpy array..."))

            print(f"\t[QUAD_P]-[calc](debug) Plotting original points")
            # Plot original pointcloud
            ax.scatter(
                self.untrimmed_point_cloud[:, 0], self.untrimmed_point_cloud[:, 1], self.untrimmed_point_cloud[:, 2])

            print(f"\t[QUAD_P]-[calc](debug) Plotting hyperplane")
            self.gui_print(text=("\n[QUAD_P]-[calc](debug) Plotting hyperplane"))

            # Plot reference plane
            ax.plot_surface(self.refx, self.refy, self.refz, color='red', alpha=0.2)

            # Set labels for graph
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            ax.set_zlabel('z')

            ax.set_title("Untrimmed scan w/ reference plane")
            # Show graph
            plt.savefig(self.working_dir+"/data/datadump/img/"+self.input_file.split('/')[-1]+"_refest.png")
            plt.show()
            ax.cla()
        except:
            raise Exception("Reference plane plotting has raised an exception ")
        
    # Plot trimmed numpy array (DEBUG)
    def plottrim(self):
        try:
            fig = plt.figure()
            ax = plt.axes(projection="3d")
            # Plot trimmed pointcloud
            print(f"\t[QUAD_P]-[calc](debug) Plotting trimmed points")
            self.gui_print(text=("\n[QUAD_P]-[calc](debug) Plotting trimmed points"))
            ax.scatter(self.trimmed_point_cloud[:, 0], self.trimmed_point_cloud[:, 1], self.trimmed_point_cloud[:, 2])

            # Plot reference plane
            print(f"\t[QUAD_P]-[calc](debug) Plotting hyperplane")
            self.gui_print(text=("\n[QUAD_P]-[calc](debug) Plotting hyperplane"))

            ax.plot_surface(self.refx, self.refy, self.refz, color='red', alpha=0.2)

            # Set labels for graph
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            ax.set_zlabel('z')

            ax.set_title("Trimmed scan w/ reference plane")
            # Show graph
            plt.savefig(self.working_dir+"/data/datadump/img/"+self.input_file.split('/')[-1]+"_trimest.png")
            plt.show()
            ax.cla()
        except:
            raise Exception("Trimmed pointcloud plotting has raised an exception ")

    # Dump all calculated data to .csvs and pngs (DEBUG)
    def datadump(self):
        try:
            fig = plt.figure()
            ax = plt.axes(projection="3d")
            fig2, (ax1, ax2, ax3) = plt.subplots(1, 3)

            print(f"\t[QUAD_P]-[calc](debug) Shape of refx ", self.refx.shape, "\t[QUAD_P]-[calc](debug) Shape of refy ", self.refz.shape, "\t[QUAD_P]-[calc](debug) Shape of refz ", self.refz.shape, "\t[QUAD_P]-[calc](debug) Shape of ref_points ",self.ref_points.shape)
            self.gui_print(text=("\n[QUAD_P]-[calc](debug) Shape of refx ", self.refx.shape, "\n[QUAD_P]-[calc](debug) Shape of refy ", self.refz.shape, "\n[QUAD_P]-[calc](debug) Shape of refz ", self.refz.shape, "\n[QUAD_P]-[calc](debug) Shape of ref_points ",self.ref_points.shape))

            # print(f"\t[QUAD_P]-[calc](debug) Shape of reference_plane ",
            #       self.reference_plane.shape)
            print(f"\t[QUAD_P]-[calc](debug) Shape of point cloud", self.untrimmed_point_cloud.shape)
            self.gui_print(text=("\n[QUAD_P]-[calc](debug) Shape of point cloud ", self.untrimmed_point_cloud.shape))

            # Save all data to CSVs
            print(f"\t[QUAD_P]-[calc](debug) Saving untrimmed pointcloud points to "+ self.working_dir+ "/data/datadump/csv/"+self.input_file.split('/')[-1]+"_untrimmed_point_cloud.csv...")
            self.gui_print(text=("\n[QUAD_P]-[calc](debug) Saving untrimmed pointcloud points to "+ self.working_dir+ "/data/datadump/csv/"+self.input_file.split('/')[-1]+"_untrimmed_point_cloud.csv..."))

            np.savetxt(self.working_dir+"/data/datadump/csv/"+self.input_file.split('/')[-1]+"_untrimmed_point_cloud.csv",
                    self.untrimmed_point_cloud, delimiter=",")

        
            np.savetxt(self.working_dir+"/data/datadump/csv/"+self.input_file.split('/')[-1]+"_untrimmed_point_cloud.csv",
                    self.untrimmed_point_cloud, delimiter=",")
                    
            # """Save untrimmed point cloud in a format that is easy for C to understand"""
            
            # shape = self.untrimmed_point_cloud.shape
            # print ("Will this work?", shape[0])
            # cpp_untrimmed_point_cloud = self.untrimmed_point_cloud.reshape(3, shape[0])
            
            # print(f"\t[QUAD_P]-[calc](debug) Saving cpp untrimmed pointcloud points to "+ self.working_dir+ "/data/datadump/csv/cpp_untrimmed_point_cloud.csv...")
            # np.savetxt(self.working_dir+"/data/datadump/csv/cpp_untrimmed_point_cloud.csv", cpp_untrimmed_point_cloud, delimiter=",")
            
            print(f"\t[QUAD_P]-[calc](debug) Saving refx points to "+self.working_dir+ "/data/datadump/csv/"+self.input_file.split('/')[-1]+"_refx.csv...")
            self.gui_print(text=("\n[QUAD_P]-[calc](debug) Saving refx points to "+self.working_dir+ "/data/datadump/csv/"+self.input_file.split('/')[-1]+"_refx.csv..."))

            np.savetxt(self.working_dir+"/data/datadump/csv/"+self.input_file.split('/')[-1]+"_refx.csv", self.refx, delimiter=",")
            print(f"\t[QUAD_P]-[calc](debug) Saving refy points to "+self.working_dir+ "/data/datadump/csv/"+self.input_file.split('/')[-1]+"_refy.csv...")
            self.gui_print(text=("\n[QUAD_P]-[calc](debug) Saving refy points to "+self.working_dir+ "/data/datadump/csv/"+self.input_file.split('/')[-1]+"_refy.csv..."))

            np.savetxt(self.working_dir+"/data/datadump/csv/"+self.input_file.split('/')[-1]+"_refy.csv", self.refy, delimiter=",")
            print(
                f"\t[QUAD_P]-[calc](debug) Saving refz points to "+self.working_dir+ "/data/datadump/csv/"+self.input_file.split('/')[-1]+"_refz.csv...")
            self.gui_print(text=("\n[QUAD_P]-[calc](debug) Saving refz points to "+self.working_dir+ "/data/datadump/csv/"+self.input_file.split('/')[-1]+"_refz.csv..."))

            np.savetxt(self.working_dir+"/data/datadump/csv/"+self.input_file.split('/')[-1]+"_refz.csv",self.refz, delimiter=",")

            print(
                f"\t[QUAD_P]-[calc](debug) Saving ref_points points to "+self.working_dir+ "/data/datadump/csv/"+self.input_file.split('/')[-1]+"_ref_points.csv...")
            self.gui_print(text=("\n[QUAD_P]-[calc](debug) Saving ref_points points to "+self.working_dir+ "/data/datadump/csv/"+self.input_file.split('/')[-1]+"_ref_points.csv..."))

            np.savetxt(self.working_dir+"/data/datadump/csv/"+self.input_file.split('/')[-1]+"_ref_points.csv", self.ref_points, delimiter=",")

            # Plot each axis of scanned pothole and juxtapose it with a 3D scan
            print(f"\t[QUAD_P]-[calc](debug) Plotting X axis of untrimmed pointcloud...")
            self.gui_print(text=("\n[QUAD_P]-[calc](debug) Plotting X axis of untrimmed pointcloud..."))

            ax1.plot(self.untrimmed_point_cloud[:, 0])
            ax1.set_title("X axis")

            print(f"\t[QUAD_P]-[calc](debug) Plotting Y axis of untrimmed pointcloud...")
            self.gui_print(text=("\n[QUAD_P]-[calc](debug) Plotting Y axis of untrimmed pointcloud..."))

            ax2.plot(self.untrimmed_point_cloud[:, 1])
            ax2.set_title("Y axis")

            print("\t[QUAD_P]-[calc](debug) Plotting Z axis of untrimmed pointcloud...")
            self.gui_print(text=("\n[QUAD_P]-[calc](debug) Plotting Z axis of untrimmed pointcloud..."))

            ax3.plot(self.untrimmed_point_cloud[:, 2])
            ax3.set_title("Z axis")

            # plt.savefig("data/datadump/img/x_ax_untrimmed.png")
            print(
                "\t[QUAD_P]-[calc](debug) Plotting entire untrimmed pointcloud for comparison...")
            self.gui_print(text=("\n[QUAD_P]-[calc](debug) Plotting entire untrimmed pointcloud for comparison..."))

            ax.scatter(
                self.untrimmed_point_cloud[:, 0], self.untrimmed_point_cloud[:, 1], self.untrimmed_point_cloud[:, 2])

            ax.set_title("Untrimmed scan")
            plt.savefig(self.working_dir+"/data/datadump/img/"+self.input_file.split('/')[-1]+"_datadump.png")
            #plt.show()
            ax.cla()
            ax1.cla()
            ax2.cla()
            ax3.cla()
        except: 
            raise Exception("[QUAD_P]-[calc] Dumping data has raised an exception")

    # Debugout function; used to consolidate all debug outputs and keep source code clean
    def debugout(self, id):
        if self.debug:
            if (id == 1):
                print(f"____      _            _       _   _ \n / ___|__ _| | ___ _   _| | __ _| |_(_) ___  _ __  ___      \n| |   / _` | |/ __| | | | |/ _` | __| |/ _ \| '_ \/ __|     \n| |__| (_| | | (__| |_| | | (_| | |_| | (_) | | | \__ \     \n \____\__,_|_|\___|\__,_|_|\__,_|\__|_|\___/|_| |_|___/     \n \n ____  _             _   _ \n/ ___|| |_ __ _ _ __| |_(_)_ __   __ _ \n\___ \| __/ _` | '__| __| | '_ \ / _` | \n ___) | || (_| | |  | |_| | | | | (_| | \n|____/ \__\__,_|_|   \__|_|_| |_|\__, | \n                                 |___/")
                self.gui_print(text=("\n____      _            _       _   _ \n / ___|__ _| | ___ _   _| | __ _| |_(_) ___  _ __  ___      \n| |   / _` | |/ __| | | | |/ _` | __| |/ _ \| '_ \/ __|     \n| |__| (_| | | (__| |_| | | (_| | |_| | (_) | | | \__ \     \n \____\__,_|_|\___|\__,_|_|\__,_|\__|_|\___/|_| |_|___/     \n \n ____  _             _   _ \n/ ___|| |_ __ _ _ __| |_(_)_ __   __ _ \n\___ \| __/ _` | '__| __| | '_ \ / _` | \n ___) | || (_| | |  | |_| | | | | (_| | \n|____/ \__\__,_|_|   \__|_|_| |_|\__, | \n                                 |___/"))if self.gui_print else None
            elif (id == 2):
                print(f"____      _            _       _   _ \n / ___|__ _| | ___ _   _| | __ _| |_(_) ___  _ __  ___ \n| |   / _` | |/ __| | | | |/ _` | __| |/ _ \| '_ \/ __| \n| |__| (_| | | (__| |_| | | (_| | |_| | (_) | | | \__ \ \n \____\__,_|_|\___|\__,_|_|\__,_|\__|_|\___/|_| |_|___/ \n \n  ____                      _      _ \n / ___|___  _ __ ___  _ __ | | ___| |_ ___ \n| |   / _ \| '_ ` _ \| '_ \| |/ _ \ __/ _ \ \n| |__| (_) | | | | | | |_) | |  __/ ||  __/ \n \____\___/|_| |_| |_| .__/|_|\___|\__\___| \n                     |_|")
                self.gui_print(text=("\n____      _            _       _   _ \n / ___|__ _| | ___ _   _| | __ _| |_(_) ___  _ __  ___ \n| |   / _` | |/ __| | | | |/ _` | __| |/ _ \| '_ \/ __| \n| |__| (_| | | (__| |_| | | (_| | |_| | (_) | | | \__ \ \n \____\__,_|_|\___|\__,_|_|\__,_|\__|_|\___/|_| |_|___/ \n \n  ____                      _      _ \n / ___|___  _ __ ___  _ __ | | ___| |_ ___ \n| |   / _ \| '_ ` _ \| '_ \| |/ _ \ __/ _ \ \n| |__| (_) | | | | | | |_) | |  __/ ||  __/ \n \____\___/|_| |_| |_| .__/|_|\___|\__\___| \n                     |_|"))if self.gui_print else None
            elif (id == 3):
                print(f"\n----------------------------------------")
                self.gui_print(text=("\n----------------------------------------"))if self.gui_print else None
            elif (id == 4):
                print(
                    f"\t[QUAD_P]-[calc](debug) Attempting Open3d translation of .ply")
                self.gui_print(text=("\n[QUAD_P]-[calc](debug) Attempting Open3d translation of .ply"))if self.gui_print else None
            elif (id == 5):
                print(
                    f"\t[QUAD_P]-[calc](debug) open3d point cloud read successfully")
                self.gui_print(text=("\n[QUAD_P]-[calc](debug) open3d point cloud read successfully"))if self.gui_print else None
            elif (id == 6):
                print(
                    f"\t[QUAD_P]-[calc](debug) open3d point cloud read into numpy array successfully")
                self.gui_print(text=("\n[QUAD_P]-[calc](debug) open3d point cloud read into numpy array successfully"))if self.gui_print else None
            elif (id == 7):
                print(
                    f"\t[QUAD_P]-[calc](debug) Establishing reference plane using least square fit algorithm")
                self.gui_print(text=("\n[QUAD_P]-[calc](debug) Establishing reference plane using least square fit algorithm"))if self.gui_print else None
            elif (id == 8):
                print(
                    f"\t[QUAD_P]-[calc](debug) Reference plane established successfully!")
                self.gui_print(text=("\n[QUAD_P]-[calc](debug) Reference plane established successfully!"))if self.gui_print else None
            elif (id == 9):
                print(
                    f"\t[QUAD_P]-[calc](debug) Trimming numpy array based on established reference plane using linear best square fit algorithm...")
                self.gui_print(text=("\n[QUAD_P]-[calc](debug) Trimming numpy array based on established reference plane using linear best square fit algorithm..."))if self.gui_print else None
            elif (id == 10):
                print(f"\t[QUAD_P]-[calc](debug) Trim successful!")
                self.gui_print(text=("\n[QUAD_P]-[calc](debug) Trim successful!"))if self.gui_print else None
            elif (id == 11):
                print(
                    f"\t[QUAD_P]-[calc](debug) Calculating volume of trimmed numpy pointcloud...")
                self.gui_print(text=("\n[QUAD_P]-[calc](debug) Calculating volume of trimmed numpy pointcloud..."))if self.gui_print else None
            elif (id == 12):
                print(
                    f"\t[QUAD_P]-[calc](debug) HashID salting value is: ", self.salt)
                self.gui_print(text=("\n[QUAD_P]-[calc](debug) HashID salting value is: ", self.salt))if self.gui_print else None
            elif (id == 13):
                print(
                    f"\t[QUAD_P]-[calc](debug) Closing sqlite database connection...")
                self.gui_print(text=("\n[QUAD_P]-[calc](debug) Closing sqlite database connection..."))if self.gui_print else None
            elif (id == 14):
                if (self.density == -1):
                    print(
                        f"\t[QUAD_P]-[calc](debug) Density of patching material not provided, using -1 as a placeholder. ")
                    self.gui_print(text=("\n[QUAD_P]-[calc](debug) Density of patching material not provided, using -1 as a placeholder. "))if self.gui_print else None
                else:
                    print(
                        f"\t[QUAD_P]-[calc](debug) Provided density is  ", self.density)
                    self.gui_print(text=("\n[QUAD_P]-[calc](debug) Provided density is  ", self.density))if self.gui_print else None

                if (self.units):
                    print(
                        f"\t[QUAD_P]-[calc](debug) Calculations will be perfomed using Imperial Units")
                    self.gui_print(text=("\n[QUAD_P]-[calc](debug) Calculations will be perfomed using Imperial Units"))if self.gui_print else None

                else:
                    print(
                        f"\t[QUAD_P]-[calc](debug) Calculations will be perfomed using SI Units")
                    self.gui_print(text=("\n[QUAD_P]-[calc](debug) Calculations will be perfomed using SI Units")) if self.gui_print else None
            elif (id == 15):
                    print(f"\t[QUAD_P]-[calc](debug) Calculations being performed on ", self.input_file)
                    self.gui_print(text=("\n[QUAD_P]-[calc](debug) Calculations being performed on ", self.input_file))if self.gui_print else None
            elif (id == 16):
                    print(f"\t[QUAD_P]-[calc] Saving calculated values to sqlite databse")
                    self.gui_print(text=("\n[QUAD_P]-[calc] Saving calculated values to sqlite databse"))
            else:
                raise Exception("[QUAD_P]-[calc] Invalid debugout id #", id)


# Main function used for running the calculation backend in isolation, only for debug
if __name__ == "__main__":
    start_time = time.process_time()  # start timer
    calc = pholeCalc()
    calc.input_file = calc.working_dir+"/data/ply/control/p1.ply"
    dyn = str(
        input(f"[QUAD_P]-[calc] Would you like to output debug data?\n(y/n): "))
    if dyn == 'y':
        calc.debug = 1
    else:
        calc.debug = 0
    calc.debugout(1)
    calc.debugout(12)
    yn = str(input(
        f"[QUAD_P]-[calc] Do you have the density of the desired patching material?\n\tNote: This will not affect volume calculation\n(y/n): "))

    if yn == 'y':
        calc.density = float(input("\n[QUAD_P]-[calc] Input density: "))
    else:
        calc.density = -1

    calc.debugout(3)
    calc.meshgen()
    calc.refest()
    calc.refplot() if calc.debug else None
    calc.trimcloud()
    calc.plottrim() if calc.debug else None
    calc.volcalc()
    if yn == 'y':
        calc.masscalc()
    else:
        calc.mass = -1

    try:
        calc.c.execute("INSERT INTO phole_VMP_Data VALUES (NULL, '{hash}', '{input_file}', DATE('now'), '{pos}', '{vol}', '{dens}', '{mass}')".
                       format(hash=calc.hash((str(calc.volume)+str(calc.density)+str(calc.mass)+(calc.input_file) + str(calc.salt))), input_file=str(calc.input_file), vol=calc.volume, dens=calc.density, mass=calc.mass, pos='pos_placeholder'))
    except:
        raise Exception(
            "Database writing failed; potentially corrupted/malformed, or permission error")

    calc.closeDBconn()
    calc.debugout(2)
    print(f"\t[QUAD_P]-[calc](debug) Calculation time: ",
          (time.process_time() - start_time) * 1000, "ms")


####################
## CODE GRAVEYARD ##
####################

# Interpolate space in between bounding points
# x = np.linspace(self.ref_points[0][0], self.ref_points[-1][0], rows)
# y = np.linspace(self.ref_points[0][1], self.ref_points[-1][1], rows)
# z = np.linspace(self.ref_points[0][2], self.ref_points[-1][2], rows)
# self.reference_plane = np.array([x,y,z]).T
#self.working_dir = os.getcwd()
# self.interped_plane = np.linspace(self.reference_plane[0], self.reference_plane[-1], self.size)
