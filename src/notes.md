# Notes for Project
---

## Python Requirements
- Version=3.9
- tkinter
- numpy
- matplotlib
- open3d
- intelrealsenseSDK

## Docs
### Open3D
- http://www.open3d.org/docs/

## Stack overflow links 
- https://stackoverflow.com/questions/36920562/python-plyfile-vs-pymesh



I have a 3D numpy array with a shape of (69293, 3) representing a 3D object, and another numpy array with a shape of (4, 3) representing the corners of a hyperplane, how would I remove all points in the first array which are above the hyperplane? 
I have tried using the following code:
<code>def remove_points_above_plane(points, plane):
    plane_normal = np.cross(plane[1] - plane[0], plane[2] - plane[0])
    plane_normal = plane_normal / np.linalg.norm(plane_normal)
    plane_d = -np.dot(plane_normal, plane[0])
    return points[np.dot(points, plane_normal) + plane_d &lt;= 0]
</code>
However, this is very slow, and I was wondering if there was a faster way to do this?


A:

You can use <code>np.einsum</code> to vectorize the calculation of the dot product:
<code>def remove_points_above_plane(points, plane):
    plane_normal = np.cross(plane[1] - plane[0], plane[2] - plane[0])
    plane_normal = plane_normal / np.linalg.norm(plane_normal)
    plane_d = -np.dot(plane_normal, plane[0])
    return points[np.einsum('ij,ij-&gt;i', points, plane_normal) + plane_d &lt;= 0]
</code>

Im receiving an &lt is not defined error 
<code>def remove_points_above_plane(points, plane):
    plane_normal = np.cross(plane[1] - plane[0], plane[2] - plane[0])
    plane_normal = plane_normal / np.linalg.norm(plane_normal)
    plane_d = -np.dot(plane_normal, plane[0])
    return points[np.einsum('ij,ij-&gt;i', points, plane_normal) + plane_d &lt;= 0]
</code>
