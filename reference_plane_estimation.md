I think however, rather than complex curve fitting, the best approach, and simplest is brute force LUT with interpolation (linear or spline) and Riemann integration in 3D.
If you have a depth map, then you have an XY surface of the sides and bottom of the hole, and if you have a reference plane, you simply need a function that returns depth orthogonal to the reference plane as a function of XY location.
Then use 3D Riemann (or Trapezoidal, Simplson’s, etc.).
The 1D interpolation and LUT for an area simply becomes 2D bi-linear interpolation and the Riemann becomes a volume.
You can make step sizes smaller and smaller – interpolating between actual depth measurements, either linearly or with a spline


Produce multiple planes and perform root solving in order to attempt to find an orthoganal plabne to the 3D numpy array 

Use these reference planes in order to isolate an area in between the reference planes in order to fine tune the "perfect reference plane"

The more reference planes we generate the more accurate the final reference plane generation will likely be, but 

Piecewise: Is great to isolate individual 

Polynomials: Are great for linear functions, but not so great for nonlinear functions 

__Toss out the convex hull method__

Splines: splines might be worth looking into, but their accuracy is dubious at best

Bi-Linear Interpolation will be required; possibly Tri-Linear

Jacobian: Every surface or line is locally linear (piecewise linear)

Do a transfer of ownership on the Jetson 

__Use C in order to do the actual integration__