#Creation Date 9/7/22
#Author: Dalton Bailey 
#Course: CSCI 490
#Instructor Sam Siewert

import numpy as np
import matplotlib as plot
from os.path import exists
import sys
import atexit
import open3d as o3d

class pholeCalc():
    # Variables required by every function in the class
    input_file = "data/input.ply"
    debug  = 1
    densInput  = 1
    pcd = None
    point_cloud_in_numpy = None
    volume = None
    density = None
    mass = None
    
    #Init function
    def __init__(self):
        return 
    
    # Mesh visualization
    def meshvis(self): 
        # Visualize the point cloud within open3d
        o3d.visualization.draw_geometries([self.pcd]) 
        print("\topen3d visualization successful") if self.debug else print("")
        return 
    
    # Mesh generation
    def meshgen(self): 
        print(f"\tCalculation starting\n\tAttempting Open3d translation of .ply") if self.debug else print("")
        self.pcd = o3d.io.read_point_cloud(self.input_file) # Read the point cloud
        print(f"\topen3d point cloud read successfully") if self.debug else print("")
        self.meshvis() if self.debug else print("")
        
        # Convert open3d format to numpy array
        # Here, you have the point cloud in numpy format. 
        self.point_cloud_in_numpy = np.asarray(self.pcd.points) 
        print(f"\topen3d point cloud read into numpy array successfully") if self.debug else print("")
        return 

    # Reference plane estimation 
    def refest(self): 
        return 
    
    # Trim numpy array based on pointcloud
    def trimcloud(self): 
        return 

    # Volume calculation
    def volcalc(self): 
        print(f"\tCalculating volume of numpy pointcloud...") if self.debug else print("")
        self.volume = np.sum(self.point_cloud_in_numpy) * 0.001
        print(f"\n----------------------------------------") if self.debug else print("")
        print(f"\tVolume is ", self.volume, "m^3") if self.debug else print("")
        return 

    # Mass calculation
    def masscalc(self): 
        self.mass = (self.volume/self.density)
        print("Mass of patching material required is ", self.mass) if self.debug else print("")
        return 

if __name__ == "__main__":
    calc = pholeCalc()
    print(f"____      _            _       _   _ \n / ___|__ _| | ___ _   _| | __ _| |_(_) ___  _ __  ___      \n| |   / _` | |/ __| | | | |/ _` | __| |/ _ \| '_ \/ __|     \n| |__| (_| | | (__| |_| | | (_| | |_| | (_) | | | \__ \     \n \____\__,_|_|\___|\__,_|_|\__,_|\__|_|\___/|_| |_|___/     \n \n ____  _             _   _ \n/ ___|| |_ __ _ _ __| |_(_)_ __   __ _ \n\___ \| __/ _` | '__| __| | '_ \ / _` | \n ___) | || (_| | |  | |_| | | | | (_| | \n|____/ \__\__,_|_|   \__|_|_| |_|\__, | \n                                 |___/")
    yn = str(input(f"Do you have the density of the desired patching material?\nNote: This will not affect volume calculation\n(y/n): "))
    
    if yn == 'y':
        calc.density = float(input("\tInput density: "))

    print(f"\n----------------------------------------")
    calc.meshgen()
    calc.refest()
    calc.volcalc()
    if yn == 'y':
        calc.masscalc()
