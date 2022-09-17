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

# Read .ply file
input_file = "input.ply"
debug  = 1
print(f"Program starting\n Attempting Open3d translation of .ply") if debug else print("")
pcd = o3d.io.read_point_cloud(input_file) # Read the point cloud
print("open3d point cloud read successfully") if debug else print("")

# Visualize the point cloud within open3d
o3d.visualization.draw_geometries([pcd]) 
print("open3d visualization successful") if debug else print("")

# Convert open3d format to numpy array
# Here, you have the point cloud in numpy format. 
point_cloud_in_numpy = np.asarray(pcd.points) 
print("open3d point cloud read into numpy successfully") if debug else print("")