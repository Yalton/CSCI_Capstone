# Creation Date 9/7/22
# Author: Dalton Bailey
# Course: CSCI 490
# Instructor Sam Siewert

import numpy as np
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
# ax = fig.gca(projection='3d')
#fig2, (ax1, ax2, ax3) = plt.subplots(1, 3)


class pholeCalc():

    # Class variables (Initialize all as none until they are required)
    input_file = None
    debug = None
    densInput = None
    pcd = None
    size = None 
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
    conn = None
    c = None

    # Init function
    def __init__(self):
        # Initialize all variable, and database connection
        self.input_file = "data/ply/p1.ply"
        self.debug = 1
        self.conn = sqlite3.connect('data/localstorage.db')
        self.c = self.conn.cursor()

        # Create databse if it does not exist
        self.c.execute("""CREATE TABLE IF NOT EXISTS phole_VMP_Data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hash TEXT,
        date TEXT,
        position REAL,
        volume REAL,
        density REAL,
        mass REAL
        )""")
        return

    # Function to wrap closing the database connection
    def closeDBconn(self):
        self.conn.commit()
        self.conn.close()
        return

    # API Function, allows the GUI to call all the functions of this class and use it like a backend.
    def api(self, yn, dens, db):
        self.debug = db
        print(f"____      _            _       _   _ \n / ___|__ _| | ___ _   _| | __ _| |_(_) ___  _ __  ___      \n| |   / _` | |/ __| | | | |/ _` | __| |/ _ \| '_ \/ __|     \n| |__| (_| | | (__| |_| | | (_| | |_| | (_) | | | \__ \     \n \____\__,_|_|\___|\__,_|_|\__,_|\__|_|\___/|_| |_|___/     \n \n ____  _             _   _ \n/ ___|| |_ __ _ _ __| |_(_)_ __   __ _ \n\___ \| __/ _` | '__| __| | '_ \ / _` | \n ___) | || (_| | |  | |_| | | | | (_| | \n|____/ \__\__,_|_|   \__|_|_| |_|\__, | \n                                 |___/") if self.debug else None
        print(f"\n----------------------------------------") if self.debug else None
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

        print(f"____      _            _       _   _ \n / ___|__ _| | ___ _   _| | __ _| |_(_) ___  _ __  ___ \n| |   / _` | |/ __| | | | |/ _` | __| |/ _ \| '_ \/ __| \n| |__| (_| | | (__| |_| | | (_| | |_| | (_) | | | \__ \ \n \____\__,_|_|\___|\__,_|_|\__,_|\__|_|\___/|_| |_|___/ \n \n  ____                      _      _ \n / ___|___  _ __ ___  _ __ | | ___| |_ ___ \n| |   / _ \| '_ ` _ \| '_ \| |/ _ \ __/ _ \ \n| |__| (_) | | | | | | |_) | |  __/ ||  __/ \n \____\___/|_| |_| |_| .__/|_|\___|\__\___| \n                     |_|")
        self.c.execute("INSERT INTO phole_VMP_Data VALUES (NULL, '{hash}', DATE('now'), '{pos}', '{vol}', '{dens}', '{mass}')".
                       format(hash=self.hash((str(self.volume)+str(self.density)+str(self.mass)+(self.input_file))), vol=self.volume, dens=self.density, mass=self.mass, pos='pos_placeholder'))
        self.closeDBconn()
        return



    # Mesh generation
    def meshgen(self):
        print(f"\t[QUAD_P]-[calc](debug) Attempting Open3d translation of .ply") if self.debug else None
        self.pcd = o3d.io.read_point_cloud(
            self.input_file)  # Read the point cloud
        print(f"\t[QUAD_P]-[calc](debug) open3d point cloud read successfully") if self.debug else None
        self.meshvis() if self.debug else None

        # Convert open3d format to numpy array
        self.untrimmed_point_cloud = np.asarray(self.pcd.points)
        self.size = self.untrimmed_point_cloud.shape[0]
        print(f"\t[QUAD_P]-[calc](debug) open3d point cloud read into numpy array successfully") if self.debug else None
        return

    # Reference plane calculation
    def refest(self):
        print(f"\t[QUAD_P]-[calc](debug) Establishing reference plane using least square fit algorithm") if self.debug else None
        
        (rows, cols) = self.untrimmed_point_cloud.shape 
        if(cols != 3):
            raise Exception("Inavlid col num; likely scanner error")
        G = np.ones((rows, cols))                   # create new numpy array of all 1's based on shape of pointcloud
        G[:, 0] = self.untrimmed_point_cloud[:, 0]  # X 
        G[:, 1] = self.untrimmed_point_cloud[:, 1]  # Y
        Z = self.untrimmed_point_cloud[:, 2]        # Z
        (a, b, c), resid, rank, s = np.linalg.lstsq(G, Z, rcond=None)
        normal = (a, b, -1)
        nn = np.linalg.norm(normal)
        normal = normal / nn
        # Get max & mins
        maxx = np.max(self.untrimmed_point_cloud[:, 0])
        maxy = np.max(self.untrimmed_point_cloud[:, 1])
        minx = np.min(self.untrimmed_point_cloud[:, 0])
        miny = np.min(self.untrimmed_point_cloud[:, 1])
        point = np.array([0.0, 0.0, c])
        d = -point.dot(normal)

        # Compute bounding points for ref plane
        self.refx, self.refy = np.meshgrid([minx, maxx], [miny, maxy])
        self.refz = (-normal[0]*self.refx - normal[1]
                     * self.refy - d)*1. / normal[2]
        
        # Save bounding points of reference plane to 3D numpy array 
        self.ref_points = np.dstack((self.refx, self.refy, self.refz)).reshape((4, 3))
        
        # Interpolate space in between bounding points
        x = np.linspace(self.ref_points[0][0], self.ref_points[-1][0], rows)
        y = np.linspace(self.ref_points[0][1], self.ref_points[-1][1], rows)
        z = np.linspace(self.ref_points[0][2], self.ref_points[-1][2], rows)
        self.reference_plane = np.array([x,y,z]).T
        
        # self.interped_plane = np.linspace(self.reference_plane[0], self.reference_plane[-1], self.size)
        print(f"\t[QUAD_P]-[calc](debug) Reference plane established successfully!") if self.debug else None
        self.datadump() if self.debug else None
        return



    # Numpy array trimming
    def trimcloud(self):
        print(f"\t[QUAD_P]-[calc](debug) Trimming numpy array based on established reference plane using marching cubes algorithm...") if self.debug else None
        distances = np.linalg.norm(self.untrimmed_point_cloud - self.reference_plane, axis=2)
        self.trimmed_point_cloud = self.untrimmed_point_cloud[distances <= np.percentile(distances, 95)]

        self.trimmed_point_cloud = self.untrimmed_point_cloud
        print(f"\t[QUAD_P]-[calc](debug) Trim successful!") if self.debug else None

        return

    # Volume calculation
    def volcalc(self):
        print(
            f"\t[QUAD_P]-[calc](debug) Calculating volume of trimmed numpy pointcloud...") if self.debug else None
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
    def meshvis(self):
        # Visualize the point cloud within open3d
        o3d.visualization.draw_geometries([self.pcd])
        print("\t[QUAD_P]-[calc](debug) open3d visualization successful") if self.debug else None
        return

    # Reference plane plotting (DEBUG)
    def refplot(self):
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        # plot fitted plane
        print(f"\t[QUAD_P]-[calc](debug) Plotting reference plane juxtaposed with numpy array...")

        print(f"\t[QUAD_P]-[calc](debug) Plotting original points")
        # Plot original pointcloud
        ax.scatter(self.untrimmed_point_cloud[:, 0], self.untrimmed_point_cloud[:, 1], self.untrimmed_point_cloud[:, 2])

        print(f"\t[QUAD_P]-[calc](debug) Plotting hyperplane")
        # Plot reference plane
        # ax.scatter(self.reference_plane[:, 0], self.reference_plane[:, 1], self.reference_plane[:, 2])
        ax.plot_surface(self.refx, self.refy, self.refz, alpha=0.2)

        # Set labels for graph
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')

        ax.set_title("Untrimmed pointcloud of scan")
        # Show graph
        plt.savefig("data/img/refest.png")
        plt.show()
        ax.cla()
        return

    # Plot trimmed numpy array (DEBUG)
    def plottrim(self):
        fig = plt.figure()
        ax = fig.gca(projection='3d')
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

        ax.set_title("Trimmed pointcloud of scan")
        # Show graph
        plt.savefig("data/img/trimest.png")
        plt.show()
        ax.cla()
        return
    
    def datadump(self):
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        fig2, (ax1, ax2, ax3) = plt.subplots(1, 3)
        
        print(f"\t[QUAD_P]-[calc](debug) Shape of refx ", self.refx.shape)
        print(f"\t[QUAD_P]-[calc](debug) Shape of refy ", self.refz.shape)
        print(f"\t[QUAD_P]-[calc](debug) Shape of refz ", self.refz.shape)
        print(f"\t[QUAD_P]-[calc](debug) Shape of ref_points ",
              self.ref_points.shape)
        print(f"\t[QUAD_P]-[calc](debug) Shape of reference_plane ",
              self.reference_plane.shape)
        print(f"\t[QUAD_P]-[calc](debug) Shape of point cloud",
              self.untrimmed_point_cloud.shape)


        ## Save all data to CSVs
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

        print(f"\t[QUAD_P]-[calc](debug) Saving ref_points points to data/csv/ref_points.csv...")
        np.savetxt("data/csv/ref_points.csv",
                   self.ref_points, delimiter=",")
        print(f"\t[QUAD_P]-[calc](debug) Saving reference_plane points to data/csv/reference_plane.csv...")
        np.savetxt("data/csv/reference_plane.csv",
                   self.reference_plane, delimiter=",")

        ## Plot each axis of scanned pothole and juxtapose it with a 3D scan
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
        print("\t[QUAD_P]-[calc](debug) Plotting entire untrimmed pointcloud for comparison...")
        ax.scatter(
            self.untrimmed_point_cloud[:, 0], self.untrimmed_point_cloud[:, 1], self.untrimmed_point_cloud[:, 2])

        # ax.plot_surface(self.ref_points[:, 0], self.ref_points[:, 1], self.ref_points[:, 2], alpha=0.2)
        # self.reference_plane
        ax.scatter(self.reference_plane[:, 0], self.reference_plane[:, 1], self.reference_plane[:, 2], alpha=0.2)
        ax.set_title("Untrimmed pointcloud of scan")
        plt.savefig("data/img/datadump.png")
        plt.show()
        ax.cla()
        ax1.cla()
        ax2.cla()
        ax3.cla()
        return

# Placeholder main function; calc will eventually be called via api function
if __name__ == "__main__":
    calc = pholeCalc()
    dyn = str(input(f"[QUAD_P]-[calc] Would you like to output debug data?\n(y/n): "))
    if dyn == 'y':
        calc.debug = 1
    else:
        calc.debug = 0
    print(f"____      _            _       _   _ \n / ___|__ _| | ___ _   _| | __ _| |_(_) ___  _ __  ___      \n| |   / _` | |/ __| | | | |/ _` | __| |/ _ \| '_ \/ __|     \n| |__| (_| | | (__| |_| | | (_| | |_| | (_) | | | \__ \     \n \____\__,_|_|\___|\__,_|_|\__,_|\__|_|\___/|_| |_|___/     \n \n ____  _             _   _ \n/ ___|| |_ __ _ _ __| |_(_)_ __   __ _ \n\___ \| __/ _` | '__| __| | '_ \ / _` | \n ___) | || (_| | |  | |_| | | | | (_| | \n|____/ \__\__,_|_|   \__|_|_| |_|\__, | \n                                 |___/") if calc.debug else None
    yn = str(input(f"[QUAD_P]-[calc] Do you have the density of the desired patching material?\n\tNote: This will not affect volume calculation\n(y/n): "))

    if yn == 'y':
        calc.density = float(input("\n[QUAD_P]-[calc] Input density: "))
    else:
        calc.density = -1

    print(f"\n----------------------------------------") if calc.debug else None
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

    calc.c.execute("INSERT INTO phole_VMP_Data VALUES (NULL, '{hash}', DATE('now'), '{pos}', '{vol}', '{dens}', '{mass}')".
                   format(hash=calc.hash((str(calc.volume)+str(calc.density)+str(calc.mass)+(calc.input_file))), vol=calc.volume, dens=calc.density, mass=calc.mass, pos='pos_placeholder'))
    calc.closeDBconn()
    print(f"____      _            _       _   _ \n / ___|__ _| | ___ _   _| | __ _| |_(_) ___  _ __  ___ \n| |   / _` | |/ __| | | | |/ _` | __| |/ _ \| '_ \/ __| \n| |__| (_| | | (__| |_| | | (_| | |_| | (_) | | | \__ \ \n \____\__,_|_|\___|\__,_|_|\__,_|\__|_|\___/|_| |_|___/ \n \n  ____                      _      _ \n / ___|___  _ __ ___  _ __ | | ___| |_ ___ \n| |   / _ \| '_ ` _ \| '_ \| |/ _ \ __/ _ \ \n| |__| (_) | | | | | | |_) | |  __/ ||  __/ \n \____\___/|_| |_| |_| .__/|_|\___|\__\___| \n                     |_|") if calc.debug else None
