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
        print("open3d visualization successful") if self.debug else print("")
        return 
    
    # Mesh generation
    def meshgen(self): 
        print(f"Program starting\n Attempting Open3d translation of .ply") if self.debug else print("")
        self.pcd = o3d.io.read_point_cloud(self.input_file) # Read the point cloud
        print("open3d point cloud read successfully") if self.debug else print("")
        self.meshvis() if self.debug else print("")
        
        # Convert open3d format to numpy array
        # Here, you have the point cloud in numpy format. 
        self.point_cloud_in_numpy = np.asarray(self.pcd.points) 
        print("open3d point cloud read into numpy successfully") if self.debug else print("")
        return 

    # Reference plane estimation 
    def refest(self): 
        return 

    # Volume calculation
    def volcalc(self): 
        return 

    # Mass calculation
    def masscalc(self): 
        return 

if __name__ == "__main__":
    calc = pholeCalc()
    calc.meshgen()