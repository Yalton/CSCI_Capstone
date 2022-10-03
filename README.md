# Pothole Perusal, Predictor Program (QuadP)

**Planning Pothole potential using pointcloud from a ply file, powered by python, pacing on the pipad**

## Hardware requirements 
- [Intel Realsense Depth Mapping camera 400 series or greater](https://www.intelrealsense.com/introducing-intel-realsense-d400-product-family/)

## About 
- Software designed to scan potholes and calculate volume 
- Software will automatically establish reference plane and calculate volume of all spaces beneath plane
- Using this reference plane method, the volume of multiple potholes can be calculated
- Using the calculated volume and density provided by user mass of required material can be calculated
- Software is entirely written in python using as few libraries as possible
- Currently only compatible with python 3.6-3.9, but should function for 3.10 once Open3D releases the patch supporting it

## Python Requirements
- [Compatible Versions = 3.6 - 3.9](https://linuxhint.com/install-python-ubuntu-22-04/)
- [tkinter](https://docs.python.org/3/library/tk.html)
- [numpy](https://numpy.org/doc/)
- [matplotlib](https://matplotlib.org/stable/index.html)
- [open3d](http://www.open3d.org/docs/)
- [scipy](https://docs.scipy.org/doc/scipy/)
- [intelrealsenseSDK](https://dev.intelrealsense.com/docs)

## Algorithms used 
- Principal component analysis algorithm to establish a reference plane 
- Least square fit on a 3D plane to restablish reference plane
- Marching cubes algorithm to remove points



https://jakevdp.github.io/PythonDataScienceHandbook/04.12-three-dimensional-plotting.html