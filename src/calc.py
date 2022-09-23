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

fig = plt.figure()
ax = fig.gca(projection='3d')


class pholeCalc():

    # Class variables
    input_file = "data/input.ply"
    debug = 1
    densInput = None
    pcd = None
    refx = None
    refy = None
    refz = None
    reference_plane = None
    untrimmed_point_cloud = None
    trimmed_point_cloud = None
    volume = None
    density = None
    mass = None
    conn = sqlite3.connect('data/localstorage.db')
    c = conn.cursor()

    # Init function
    def __init__(self):
        self.c.execute("""CREATE TABLE IF NOT EXISTS phole_VMP_Data (
        id INTEGER PRIMARY KEY,
        hash TEXT,
        date TEXT,
        position REAL,
        volume REAL,
        density REAL,
        mass REAL
        )""")
        return

    def closeDBconn(self):
        self.conn.commit()
        self.conn.close()
        return

    # Mesh visualization
    def api(self, yn, dens):
        print(f"____      _            _       _   _ \n / ___|__ _| | ___ _   _| | __ _| |_(_) ___  _ __  ___      \n| |   / _` | |/ __| | | | |/ _` | __| |/ _ \| '_ \/ __|     \n| |__| (_| | | (__| |_| | | (_| | |_| | (_) | | | \__ \     \n \____\__,_|_|\___|\__,_|_|\__,_|\__|_|\___/|_| |_|___/     \n \n ____  _             _   _ \n/ ___|| |_ __ _ _ __| |_(_)_ __   __ _ \n\___ \| __/ _` | '__| __| | '_ \ / _` | \n ___) | || (_| | |  | |_| | | | | (_| | \n|____/ \__\__,_|_|   \__|_|_| |_|\__, | \n                                 |___/")
        print(f"\n----------------------------------------")
        self.meshgen()
        self.refest()
        self.trimcloud()
        self.volcalc()
        if yn == 'y':
            self.density = dens
            self.masscalc()
        print(f"____      _            _       _   _ \n / ___|__ _| | ___ _   _| | __ _| |_(_) ___  _ __  ___ \n| |   / _` | |/ __| | | | |/ _` | __| |/ _ \| '_ \/ __| \n| |__| (_| | | (__| |_| | | (_| | |_| | (_) | | | \__ \ \n \____\__,_|_|\___|\__,_|_|\__,_|\__|_|\___/|_| |_|___/ \n \n  ____                      _      _ \n / ___|___  _ __ ___  _ __ | | ___| |_ ___ \n| |   / _ \| '_ ` _ \| '_ \| |/ _ \ __/ _ \ \n| |__| (_) | | | | | | |_) | |  __/ ||  __/ \n \____\___/|_| |_| |_| .__/|_|\___|\__\___| \n                     |_|")
        self.c.execute("INSERT INTO phole_VMP_Data VALUES (1, '{hash}', DATE('now'), 'position_placeholder', '{vol}', '{dens}', '{mass}')".
                   format(hash=self.hash((str(self.volume)+str(self.density)+str(self.mass))), vol=self.volume, dens=self.density, mass=self.mass))
        self.closeDBconn()
        return

    # Mesh visualization
    def meshvis(self):
        # Visualize the point cloud within open3d
        o3d.visualization.draw_geometries([self.pcd])
        print("\topen3d visualization successful") if self.debug else print("")
        return

    # Mesh generation
    def meshgen(self):
        print(f"\tAttempting Open3d translation of .ply") if self.debug else print("")
        self.pcd = o3d.io.read_point_cloud(
            self.input_file)  # Read the point cloud
        print(f"\topen3d point cloud read successfully") if self.debug else print("")
        self.meshvis() if self.debug else print("")

        # Convert open3d format to numpy array
        self.untrimmed_point_cloud = np.asarray(self.pcd.points)
        print(f"\topen3d point cloud read into numpy array successfully") if self.debug else print("")
        return

    # Reference plane estimation
    def refest(self):
        print(f"\tEstablishing reference plane using least square fit algorithm") if self.debug else print("")
        (rows, cols) = self.untrimmed_point_cloud.shape
        G = np.ones((rows, 3))
        G[:, 0] = self.untrimmed_point_cloud[:, 0]  # X
        G[:, 1] = self.untrimmed_point_cloud[:, 1]  # Y
        Z = self.untrimmed_point_cloud[:, 2]
        (a, b, c), resid, rank, s = np.linalg.lstsq(G, Z, rcond=None)
        normal = (a, b, -1)
        nn = np.linalg.norm(normal)
        normal = normal / nn
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

        self.reference_plane = np.array([self.refx, self.refy, self.refz]).T
        # self.reference_plane = np.dstack((self.refx, self.refy, self.refz))

        print(f"\tReference plane established successfully!") if self.debug else print("")
        # self.refplot() if self.debug else print("")
        return

    # Reference plane plotting
    def refplot(self):
        # plot fitted plane
        print(f"\tPlotting reference plane juxtaposed with numpy array...") if self.debug else print("")

        print("Plotting original points")
        # Plot original pointcloud
        ax.scatter(
            self.untrimmed_point_cloud[:, 0], self.untrimmed_point_cloud[:, 1], self.untrimmed_point_cloud[:, 2])

        print("Plotting hyperplane")
        # Plot reference plane
        ax.plot_surface(self.refx, self.refy, self.refz, alpha=0.2)

        # Set labels for graph
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')

        # Show graph
        plt.savefig("refest.png")
        plt.show()
        ax.cla()
        return

    # Trim numpy array based on pointcloud
    def trimcloud(self):
        print(f"\tTrimming numpy array based on established reference plane using marching cubes algorithm...") if self.debug else print("")
        # ax.plot_surface(self.reference_plane[:, 0], self.reference_plane[:, 1], self.reference_plane[:, 2])

        self.trimmed_point_cloud = self.untrimmed_point_cloud
        print(f"\tTrim successful!") if self.debug else print("")
        # self.plottrim() if self.debug else print("")
        return

    def plottrim(self):
        # Plot trimmed pointcloud
        print("Plotting trimmed points")
        ax.scatter(
            self.trimmed_point_cloud[:, 0], self.trimmed_point_cloud[:, 1], self.trimmed_point_cloud[:, 2])

        # Plot reference plane
        print("Plotting hyperplane")
        ax.plot_surface(self.refx, self.refy, self.refz, alpha=0.2)

        # Set labels for graph
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')

        # Show graph
        plt.savefig("trimest.png")
        plt.show()
        ax.cla()
        return

    # Volume calculation
    def volcalc(self):
        print(f"\tCalculating volume of trimmed numpy pointcloud...") if self.debug else print("")
        self.volume = np.sum(self.trimmed_point_cloud) * \
            0.000001  # This is not correct
        print(f"\tVolume calculation successful!\n----------------------------------------\n\tVolume is",
              self.volume, "m^3") if self.debug else print("")
        return

    # Mass calculation
    def masscalc(self):
        self.mass = (self.volume/self.density)
        print(f"\tUsing input density and calculated volume to determine mass\n\tMass of patching material required is ",
              self.mass) if self.debug else print("")
        return

    def hash(self, hashingvalue):
        hash = hashlib.sha256()
        hash.update(hashingvalue.encode("utf-8"))
        return hash.hexdigest()


# Placeholder main function; calc will eventually be called via api function
if __name__ == "__main__":
    calc = pholeCalc()
    print(f"____      _            _       _   _ \n / ___|__ _| | ___ _   _| | __ _| |_(_) ___  _ __  ___      \n| |   / _` | |/ __| | | | |/ _` | __| |/ _ \| '_ \/ __|     \n| |__| (_| | | (__| |_| | | (_| | |_| | (_) | | | \__ \     \n \____\__,_|_|\___|\__,_|_|\__,_|\__|_|\___/|_| |_|___/     \n \n ____  _             _   _ \n/ ___|| |_ __ _ _ __| |_(_)_ __   __ _ \n\___ \| __/ _` | '__| __| | '_ \ / _` | \n ___) | || (_| | |  | |_| | | | | (_| | \n|____/ \__\__,_|_|   \__|_|_| |_|\__, | \n                                 |___/")
    yn = str(input(f"Do you have the density of the desired patching material?\nNote: This will not affect volume calculation\n(y/n): "))

    if yn == 'y':
        calc.density = float(input("\nInput density: "))
    else:
        calc.density = -1

    print(f"\n----------------------------------------")
    calc.meshgen()
    calc.refest()
    calc.trimcloud()
    calc.volcalc()
    if yn == 'y':
        calc.masscalc()
    else:
        calc.mass = -1

    calc.c.execute("INSERT INTO phole_VMP_Data VALUES (1, '{hash}', DATE('now'), 'position_placeholder', '{vol}', '{dens}', '{mass}')".
                   format(hash=calc.hash((str(calc.volume)+str(calc.density)+str(calc.mass))), vol=calc.volume, dens=calc.density, mass=calc.mass))
    calc.closeDBconn()
    print(f"____      _            _       _   _ \n / ___|__ _| | ___ _   _| | __ _| |_(_) ___  _ __  ___ \n| |   / _` | |/ __| | | | |/ _` | __| |/ _ \| '_ \/ __| \n| |__| (_| | | (__| |_| | | (_| | |_| | (_) | | | \__ \ \n \____\__,_|_|\___|\__,_|_|\__,_|\__|_|\___/|_| |_|___/ \n \n  ____                      _      _ \n / ___|___  _ __ ___  _ __ | | ___| |_ ___ \n| |   / _ \| '_ ` _ \| '_ \| |/ _ \ __/ _ \ \n| |__| (_) | | | | | | |_) | |  __/ ||  __/ \n \____\___/|_| |_| |_| .__/|_|\___|\__\___| \n                     |_|")
