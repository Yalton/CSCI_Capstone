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

import numpy as np
import random
from os.path import exists
import string
import matplotlib as plot
from os.path import exists
import sys
import atexit
import open3d as o3d
import sqlite3
import scipy.optimize
import hashlib
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

# fig = plt.figure()
# ax = plt.axes(projection="3d")
#fig2, (ax1, ax2, ax3) = plt.subplots(1, 3)


class pholeCalc():

    # Class variables (Initialize all as none until they are required)
    input_file = None
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
    salt = None
    conn = None
    c = None

    # Init function
    def __init__(self):
        self.salt = ''.join(random.choice(string.ascii_letters) for i in range(10))
        try:
            self.conn = sqlite3.connect('data/localstorage.db')
        except: 
            raise Exception("Database connection has failed; potentially corrupted/malformed, or permission error")
        self.c = self.conn.cursor()
        # Create databse if it does not exist
        try:
            self.c.execute("""CREATE TABLE IF NOT EXISTS phole_VMP_Data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hash_id TEXT,
            input_file TEXT,
            date TEXT,
            position REAL,
            volume REAL,
            density REAL,
            mass REAL
            )""")
        except: 
            raise Exception("Database creation has failed; potentially corrupted/malformed, or permission error")

        return

    # Function to wrap closing the database connection
    def closeDBconn(self):
        self.debugout(13, None)
        try:
            self.conn.commit()
            self.conn.close()
        except: 
            raise Exception("Database comitting & closing has failed; potentially corrupted/malformed, or permission error")
        return

    # API Function, allows the GUI to call all the functions of this class and use it like a backend.
    def api(self, yn, dens, infile):
        self.input_file = infile
        self.debugout(1, None)
        self.debugout(12, None)
        self.debugout(3, None)
        self.meshgen()
        self.refest()
        self.refplot() if self.debug else None
        self.trimcloud()
        self.plottrim() if self.debug else None
        self.volcalc()
        # If density value was provided, calculate mass
        if yn == 'y':
            self.density = dens
            self.masscalc()

        # Otherwise, set both mass and density to -1
        else:
            self.density = -1
            self.mass = -1

        self.debugout(2, None)
        try:
            self.c.execute("INSERT INTO phole_VMP_Data VALUES (NULL, '{hash}', '{input_file}', DATE('now'), '{pos}', '{vol}', '{dens}', '{mass}')".
                       format(hash=self.hash((str(self.volume)+str(self.density)+str(self.mass)+(self.input_file) + str(self.salt))), input_file = str(self.input_file), vol=self.volume, dens=self.density, mass=self.mass, pos='pos_placeholder'))
        except: 
            raise Exception("Database writing has failed; potentially corrupted/malformed, or permission error")
        # self.closeDBconn()
        return

    # Mesh generation
    def meshgen(self):
        self.debugout(4, None)
        pcd = o3d.io.read_point_cloud(
            self.input_file)  # Read the point cloud
        self.debugout(5, None)
        self.meshvis(pcd) if self.debug else None

        # Convert open3d format to numpy array
        self.untrimmed_point_cloud = np.asarray(pcd.points)
        self.debugout(6, None)
        return

    # Reference plane calculation using linear best fit algorithm
    def refest(self):
        self.debugout(7, None)

        # Calculate reference hyperplane
        (rows, cols) = self.untrimmed_point_cloud.shape

        if (cols != 3):
            raise Exception("Inavlid col num; likely scanner error")

        # create new numpy array of all 1's based on shape of pointcloud
        G = np.ones((rows, cols))
        G[:, 0] = self.untrimmed_point_cloud[:, 0]  # X
        G[:, 1] = self.untrimmed_point_cloud[:, 1]  # Y
        Z = self.untrimmed_point_cloud[:, 2]        # Z
        (a, b, c), resid, rank, s = np.linalg.lstsq(G, Z, rcond=None)

        # Compute the normal
        normal = (a, b, -1)
        nn = np.linalg.norm(normal)
        normal = normal / nn

        # get negative dot product of the normal
        point = np.array([0.0, 0.0, c])
        d = -point.dot(normal)

        # Get max & mins
        maxx = np.max(self.untrimmed_point_cloud[:, 0])
        maxy = np.max(self.untrimmed_point_cloud[:, 1])
        minx = np.min(self.untrimmed_point_cloud[:, 0])
        miny = np.min(self.untrimmed_point_cloud[:, 1])

        # Compute bounding points for ref plane
        self.refx, self.refy = np.meshgrid([minx, maxx], [miny, maxy])
        self.refz = (-normal[0]*self.refx - normal[1]
                     * self.refy - d)*1. / normal[2]

        # Save bounding points of reference plane to 3D numpy array
        self.ref_points = np.dstack(
            (self.refx, self.refy, self.refz)).reshape((4, 3))

        self.debugout(8, None)

        self.datadump() if self.debug else None
        return

    # Numpy array trimming

    def trimcloud(self):
        self.debugout(9, None)
        plane_normal = np.cross(
            self.ref_points[1] - self.ref_points[0], self.ref_points[2] - self.ref_points[0])
        plane_normal = plane_normal / np.linalg.norm(plane_normal)
        plane_d = -np.dot(plane_normal, self.ref_points[0])
        self.trimmed_point_cloud = self.untrimmed_point_cloud[np.dot(
            self.untrimmed_point_cloud, plane_normal) + plane_d <= 0]
        self.debugout(10, None)
        return

    # Volume calculation
    def volcalc(self):
        self.debugout(11, None)
        self.volume = np.sum(self.trimmed_point_cloud) * \
            0.000001  # This is not correct
        print(f"\t[QUAD_P]-[calc] Volume calculation successful!\n----------------------------------------\n\t[QUAD_P]-[calc] Volume is",
              self.volume, "m^3")
        return

    # Mass calculation
    def masscalc(self):
        self.mass = (self.density * self.volume)
        print(f"\t[QUAD_P]-[calc] Using input density and calculated volume to determine mass\n\t[QUAD_P]-[calc] Mass of patching material required is ",
              self.mass) if self.debug else None
        return

    def hash(self, hashingvalue):
        hash = hashlib.sha256()
        hash.update(hashingvalue.encode("utf-8"))
        return hash.hexdigest()

    # Open3D Visualization (DEBUG)
    def meshvis(self, pcd):
        o3d.visualization.draw_geometries([pcd])# Visualize the point cloud within open3d
        print("\t[QUAD_P]-[calc](debug) open3d visualization successful")
        return

    # Reference plane plotting (DEBUG)
    def refplot(self):
        fig = plt.figure()
        ax = plt.axes(projection="3d")
        # plot fitted plane
        print(
            f"\t[QUAD_P]-[calc](debug) Plotting reference plane juxtaposed with numpy array...")

        print(f"\t[QUAD_P]-[calc](debug) Plotting original points")
        # Plot original pointcloud
        ax.scatter(
            self.untrimmed_point_cloud[:, 0], self.untrimmed_point_cloud[:, 1], self.untrimmed_point_cloud[:, 2])

        print(f"\t[QUAD_P]-[calc](debug) Plotting hyperplane")
        # Plot reference plane
        ax.plot_surface(self.refx, self.refy, self.refz, alpha=0.2)

        # Set labels for graph
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')

        ax.set_title("Untrimmed scan w/ reference plane")
        # Show graph
        plt.savefig("data/img/refest.png")
        plt.show()
        ax.cla()
        return

    # Plot trimmed numpy array (DEBUG)
    def plottrim(self):
        fig = plt.figure()
        ax = plt.axes(projection="3d")
        # Plot trimmed pointcloud
        print(f"\t[QUAD_P]-[calc](debug) Plotting trimmed points")
        ax.scatter(
            self.trimmed_point_cloud[:, 0], self.trimmed_point_cloud[:, 1], self.trimmed_point_cloud[:, 2])

        # Plot reference plane
        print(f"\t[QUAD_P]-[calc](debug) Plotting hyperplane")
        ax.plot_surface(self.refx, self.refy, self.refz, alpha=0.2)

        # Set labels for graph
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')

        ax.set_title("Trimmed scan w/ reference plane")
        # Show graph
        plt.savefig("data/img/trimest.png")
        plt.show()
        ax.cla()
        return

    def datadump(self):
        fig = plt.figure()
        ax = plt.axes(projection="3d")
        fig2, (ax1, ax2, ax3) = plt.subplots(1, 3)

        print(f"\t[QUAD_P]-[calc](debug) Shape of refx ", self.refx.shape)
        print(f"\t[QUAD_P]-[calc](debug) Shape of refy ", self.refz.shape)
        print(f"\t[QUAD_P]-[calc](debug) Shape of refz ", self.refz.shape)
        print(f"\t[QUAD_P]-[calc](debug) Shape of ref_points ",
              self.ref_points.shape)
        # print(f"\t[QUAD_P]-[calc](debug) Shape of reference_plane ",
        #       self.reference_plane.shape)
        print(f"\t[QUAD_P]-[calc](debug) Shape of point cloud",
              self.untrimmed_point_cloud.shape)

        # Save all data to CSVs
        print(f"\t[QUAD_P]-[calc](debug) Saving untrimmed pointcloud points to data/csv/untrimmed_point_cloud.csv...")
        np.savetxt("data/csv/untrimmed_point_cloud.csv",
                   self.untrimmed_point_cloud, delimiter=",")

        print(f"\t[QUAD_P]-[calc](debug) Saving refx points to data/csv/refx.csv...")
        np.savetxt("data/csv/refx.csv",
                   self.refx, delimiter=",")
        print(f"\t[QUAD_P]-[calc](debug) Saving refy points to data/csv/refy.csv...")
        np.savetxt("data/csv/refy.csv",
                   self.refy, delimiter=",")
        print(f"\t[QUAD_P]-[calc](debug) Saving refz points to data/csv/refz.csv...")
        np.savetxt("data/csv/refz.csv",
                   self.refz, delimiter=",")

        print(
            f"\t[QUAD_P]-[calc](debug) Saving ref_points points to data/csv/ref_points.csv...")
        np.savetxt("data/csv/ref_points.csv",
                   self.ref_points, delimiter=",")
        # print(f"\t[QUAD_P]-[calc](debug) Saving reference_plane points to data/csv/reference_plane.csv...")
        # np.savetxt("data/csv/reference_plane.csv",
        #            self.reference_plane, delimiter=",")

        # Plot each axis of scanned pothole and juxtapose it with a 3D scan
        print("\t[QUAD_P]-[calc](debug) Plotting X axis of untrimmed pointcloud...")
        ax1.plot(self.untrimmed_point_cloud[:, 0])
        ax1.set_title("X axis")

        print("\t[QUAD_P]-[calc](debug) Plotting Y axis of untrimmed pointcloud...")
        ax2.plot(self.untrimmed_point_cloud[:, 1])
        ax2.set_title("Y axis")

        print("\t[QUAD_P]-[calc](debug) Plotting Z axis of untrimmed pointcloud...")
        ax3.plot(self.untrimmed_point_cloud[:, 2])
        ax3.set_title("Z axis")

        # plt.savefig("data/img/x_ax_untrimmed.png")
        print(
            "\t[QUAD_P]-[calc](debug) Plotting entire untrimmed pointcloud for comparison...")
        ax.scatter(
            self.untrimmed_point_cloud[:, 0], self.untrimmed_point_cloud[:, 1], self.untrimmed_point_cloud[:, 2])

        # ax.plot_surface(self.ref_points[:, 0], self.ref_points[:, 1], self.ref_points[:, 2], alpha=0.2)
        # self.reference_plane
        # ax.scatter(self.reference_plane[:, 0], self.reference_plane[:, 1], self.reference_plane[:, 2], alpha=0.2)
        ax.set_title("Untrimmed scan")
        plt.savefig("data/img/datadump.png")
        plt.show()
        ax.cla()
        ax1.cla()
        ax2.cla()
        ax3.cla()
        return

    # Debugout function; used to consolidate all debug outputs and keep source code relatively clean
    def debugout(self, id, data):
        if self.debug:
            if (id == 1):
                print(f"____      _            _       _   _ \n / ___|__ _| | ___ _   _| | __ _| |_(_) ___  _ __  ___      \n| |   / _` | |/ __| | | | |/ _` | __| |/ _ \| '_ \/ __|     \n| |__| (_| | | (__| |_| | | (_| | |_| | (_) | | | \__ \     \n \____\__,_|_|\___|\__,_|_|\__,_|\__|_|\___/|_| |_|___/     \n \n ____  _             _   _ \n/ ___|| |_ __ _ _ __| |_(_)_ __   __ _ \n\___ \| __/ _` | '__| __| | '_ \ / _` | \n ___) | || (_| | |  | |_| | | | | (_| | \n|____/ \__\__,_|_|   \__|_|_| |_|\__, | \n                                 |___/")
            elif (id == 2):
                print(f"____      _            _       _   _ \n / ___|__ _| | ___ _   _| | __ _| |_(_) ___  _ __  ___ \n| |   / _` | |/ __| | | | |/ _` | __| |/ _ \| '_ \/ __| \n| |__| (_| | | (__| |_| | | (_| | |_| | (_) | | | \__ \ \n \____\__,_|_|\___|\__,_|_|\__,_|\__|_|\___/|_| |_|___/ \n \n  ____                      _      _ \n / ___|___  _ __ ___  _ __ | | ___| |_ ___ \n| |   / _ \| '_ ` _ \| '_ \| |/ _ \ __/ _ \ \n| |__| (_) | | | | | | |_) | |  __/ ||  __/ \n \____\___/|_| |_| |_| .__/|_|\___|\__\___| \n                     |_|")
            elif (id == 3):
                print(f"\n----------------------------------------")
            elif (id == 4):
                print(
                    f"\t[QUAD_P]-[calc](debug) Attempting Open3d translation of .ply")
            elif (id == 5):
                print(
                    f"\t[QUAD_P]-[calc](debug) open3d point cloud read successfully")
            elif (id == 6):
                print(
                    f"\t[QUAD_P]-[calc](debug) open3d point cloud read into numpy array successfully")
            elif (id == 7):
                print(
                    f"\t[QUAD_P]-[calc](debug) Establishing reference plane using least square fit algorithm")
            elif (id == 8):
                print(
                    f"\t[QUAD_P]-[calc](debug) Reference plane established successfully!")
            elif (id == 9):
                print(
                    f"\t[QUAD_P]-[calc](debug) Trimming numpy array based on established reference plane using marching cubes algorithm...")
            elif (id == 10):
                print(f"\t[QUAD_P]-[calc](debug) Trim successful!")
            elif (id == 11):
                print(
                    f"\t[QUAD_P]-[calc](debug) Calculating volume of trimmed numpy pointcloud...")
            elif (id == 12):
                print(f"[QUAD_P]-[calc](debug) Hash salting value is: ", self.salt)
            elif (id == 13):
                print(f"\t[QUAD_P]-[calc](debug) Closing sqlite database connection...")
            else:
                raise Exception("Invalid debugout id")
        return


# Placeholder main function; calc will eventually be called via api function
if __name__ == "__main__":
    calc = pholeCalc()
    calc.input_file = "data/ply/p1.ply"
    dyn = str(
        input(f"[QUAD_P]-[calc] Would you like to output debug data?\n(y/n): "))
    if dyn == 'y':
        calc.debug = 1
    else:
        calc.debug = 0
    calc.debugout(1, None)
    calc.debugout(12, None)
    yn = str(input(
        f"[QUAD_P]-[calc] Do you have the density of the desired patching material?\n\tNote: This will not affect volume calculation\n(y/n): "))

    if yn == 'y':
        calc.density = float(input("\n[QUAD_P]-[calc] Input density: "))
    else:
        calc.density = -1

    calc.debugout(3, None)
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
                   format(hash=calc.hash((str(calc.volume)+str(calc.density)+str(calc.mass)+(calc.input_file) + str(calc.salt))), input_file = str(calc.input_file), vol=calc.volume, dens=calc.density, mass=calc.mass, pos='pos_placeholder'))
    except: 
        raise Exception("Database writing failed; potentially corrupted/malformed, or permission error")
    
    calc.closeDBconn()
    calc.debugout(2, None)


## CODE GRAVEYARD ##
# Interpolate space in between bounding points
# x = np.linspace(self.ref_points[0][0], self.ref_points[-1][0], rows)
# y = np.linspace(self.ref_points[0][1], self.ref_points[-1][1], rows)
# z = np.linspace(self.ref_points[0][2], self.ref_points[-1][2], rows)
# self.reference_plane = np.array([x,y,z]).T

# self.interped_plane = np.linspace(self.reference_plane[0], self.reference_plane[-1], self.size)
