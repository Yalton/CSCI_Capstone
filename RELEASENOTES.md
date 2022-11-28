# QuadP Release Notes 
## Author: Dalton Bailey
## Last Updated : 11-16-2022 
----

### Hardware 
- Should work for all intel realsense d400 series cameras; however as of right now it has only been tested on a D415 camera 
- Should work for any device with at least a 2.0 Ghz processor, and 2 GB of ram, it could work on hardware with lower hardware specs, but this is untested


### Software 
- Software should work with python versions 3.6-3.9 however currently it has been only been tested on version 3.9 
- Software can calculate the volume of potholes passed in with a .ply file within one standard deviation of error
- Installation script should work for all linux distributions, but was only tested on debian based distributions 
- Software should be fully functional on both windows and linux, but all of the development was done on linux, so there may be some unexpected bugs on windows
- Software should be able to recover from any unexptected behavior and report said behavior as an exception in the terminal
- Software currently streams cameras vision to matplotlib graph; goal is to stream directly to GUI using OpenCV, similar to what was done ![here](https://github.com/IntelRealSense/librealsense/blob/master/wrappers/python/examples/opencv_viewer_example.py)
- Software should print the vast majority of it's terminal output to the GUI screen, but there may be some unexpected output which will instead be written to the terminal