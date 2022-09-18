# Computer science capstone project

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

## Stack overflow & github links 
- [Loading .ply with Open3D](https://stackoverflow.com/questions/36920562/python-plyfile-vs-pymesh)
- [Ubuntu pip with python 3.9](https://stackoverflow.com/questions/65644782/how-to-install-pip-for-python-3-9-on-ubuntu-20-04)
- [Least Square fit with 3D plane](https://gist.github.com/RustingSword/e22a11e1d391f2ab1f2c)