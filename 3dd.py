import open3d as o3d
import numpy as np
import os
import sys

FILE_NAME = "ship.ply"
PLANE_SIZE = 10.0


def print_geometry_info(step, name, geometry, notes=""):
    print(f"\n--- {step}. {name} Information ---")
    print(f"Explanation: {notes}")
    
    
    if isinstance(geometry, o3d.geometry.TriangleMesh):
        num_vertices = len(geometry.vertices)
        num_triangles = len(geometry.triangles)
        print(f"Number of Vertices (Points): {num_vertices:,}")
        print(f"Number of Triangles: {num_triangles:,}")
        
    elif isinstance(geometry, o3d.geometry.PointCloud):
        num_vertices = len(geometry.points)
        print(f"Number of Vertices (Points): {num_vertices:,}")
        print(f"Number of Triangles: N/A")
    
    elif isinstance(geometry, o3d.geometry.VoxelGrid):
        try:
            voxels = geometry.get_voxels()
            num_voxels = len(voxels)
        except Exception:
            num_voxels = "Check VoxelGrid properties"
        
        print(f"Number of Voxels (Occupied): {num_voxels}")
        print(f"Number of Vertices (Points): N/A (Object is a Voxel Grid)")
        print(f"Number of Triangles: N/A")

    has_color = False
    has_normals = False
    
    if hasattr(geometry, 'has_vertex_colors') and callable(geometry.has_vertex_colors):
        has_color = geometry.has_vertex_colors()
    if hasattr(geometry, 'has_vertex_normals') and callable(geometry.has_vertex_normals):
        has_normals = geometry.has_vertex_normals()
        
    print(f"Presence of Color (Vertex): {'Yes' if has_color else 'No'}")
    print(f"Presence of Normals: {'Yes' if has_normals else 'No'}")
    print("-" * 40)


# --- Initial Check and Load ---
if not os.path.exists(FILE_NAME):
    print(f"Error: The file '{FILE_NAME}' was not found.")
    sys.exit(1)

o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Warning)


print("STAGE 1: Loading and Visualization")
mesh_original = o3d.io.read_triangle_mesh(FILE_NAME)

if not mesh_original.has_vertex_normals():
    mesh_original.compute_vertex_normals()

o3d.visualization.draw_geometries([mesh_original], window_name="Stage 1: Original Mesh")

print_geometry_info(
    1, 
    "Loaded Mesh", 
    mesh_original, 
    "The 3D model was loaded as a Triangle Mesh."
)


print("STAGE 2: Conversion to Point Cloud")
pcd_original = o3d.io.read_point_cloud(FILE_NAME)

o3d.visualization.draw_geometries([pcd_original], window_name="Stage 2: Point Cloud")

print_geometry_info(
    2, 
    "Point Cloud", 
    pcd_original, 
    "The model was read directly as a Point Cloud. Triangle information is lost."
)


print("STAGE 3: Surface Reconstruction from Point Cloud (Poisson)")
pcd_original.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
pcd_original.orient_normals_consistent_tangent_plane(50)

mesh_poisson, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
    pcd_original, depth=9, scale=1.1
)

bbox_pcd = pcd_original.get_axis_aligned_bounding_box()
mesh_poisson_cropped = mesh_poisson.crop(bbox_pcd)
mesh_poisson_cropped.compute_vertex_normals()

o3d.visualization.draw_geometries(
    [mesh_poisson_cropped], 
    window_name="Stage 3: Poisson Reconstructed and Cropped Mesh"
)

print_geometry_info(
    3, 
    "Poisson Reconstructed Mesh", 
    mesh_poisson_cropped, 
    "A new mesh was created from the point cloud. Color presence reflects if the original point cloud had vertex colors."
)


print("STAGE 4: Voxelization")
voxel_size = 0.1
voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(pcd_original, voxel_size=voxel_size)

o3d.visualization.draw_geometries([voxel_grid], window_name="Stage 4: Voxel Grid")

print_geometry_info(
    4, 
    "Voxel Grid", 
    voxel_grid, 
    f"The point cloud was converted to a Voxel Grid with a size of {voxel_size}."
)


print("STAGE 5: Adding a Plane (Perpendicular to X-axis) - ENLARGED")

aabbox = mesh_original.get_axis_aligned_bounding_box()
center_x, center_y, center_z = aabbox.get_center()

plane = o3d.geometry.TriangleMesh.create_box(width=0.1, height=PLANE_SIZE, depth=PLANE_SIZE)
plane.paint_uniform_color([0.5, 0.5, 0.5]) 

clipping_x = center_x 
plane.translate([clipping_x - 0.05, center_y - PLANE_SIZE / 2, center_z - PLANE_SIZE / 2])

o3d.visualization.draw_geometries(
    [mesh_original, plane], 
    window_name="Stage 5: Object and Vertical Plane (ENLARGED) Together"
)

print("\n--- 5. Adding a Plane Information ---")
print(f"Explanation: A gray vertical plane, {PLANE_SIZE}x{PLANE_SIZE} in size, was created and placed at the object's center X coordinate ({clipping_x:.2f}).")
print("-" * 40)


print("STAGE 6: Surface Clipping")

new_aabbox = o3d.geometry.AxisAlignedBoundingBox(
    min_bound=aabbox.min_bound,
    max_bound=[clipping_x, aabbox.max_bound[1], aabbox.max_bound[2]]
)

mesh_clipped = mesh_original.crop(new_aabbox)

o3d.visualization.draw_geometries(
    [mesh_clipped], 
    window_name="Stage 6: Clipped Mesh (Removed 'Right Side' along X-axis)"
)

print_geometry_info(
    6, 
    "Clipped Mesh", 
    mesh_clipped, 
    "The original mesh was clipped by removing all geometry on the 'right side' (positive X-axis) of the plane from Stage 5."
)


print("STAGE 7: Working with Color and Extremes")
mesh_colorized = o3d.io.read_triangle_mesh(FILE_NAME)

mesh_colorized.vertex_colors = o3d.utility.Vector3dVector([])

vertices = np.asarray(mesh_colorized.vertices)
z_coords = vertices[:, 2]
z_min, z_max = np.min(z_coords), np.max(z_coords)
z_range = z_max - z_min

if z_range > 1e-6:
    z_normalized = (z_coords - z_min) / z_range
else:
    z_normalized = np.zeros_like(z_coords)

colors = np.zeros((len(vertices), 3))
colors[:, 0] = z_normalized
colors[:, 2] = 1 - z_normalized

mesh_colorized.vertex_colors = o3d.utility.Vector3dVector(colors)

min_z_index = np.argmin(z_coords)
max_z_index = np.argmax(z_coords)

min_z_coord = vertices[min_z_index]
max_z_coord = vertices[max_z_index]

bb_original = mesh_colorized.get_axis_aligned_bounding_box()
extent = bb_original.get_max_bound() - bb_original.get_min_bound()
highlight_radius = np.linalg.norm(extent) * 0.01

min_sphere = o3d.geometry.TriangleMesh.create_sphere(radius=highlight_radius)
min_sphere.translate(min_z_coord).paint_uniform_color([0, 0, 1])

max_sphere = o3d.geometry.TriangleMesh.create_sphere(radius=highlight_radius)
max_sphere.translate(max_z_coord).paint_uniform_color([1, 0, 0])

o3d.visualization.draw_geometries(
    [mesh_colorized, min_sphere, max_sphere], 
    window_name="Stage 7: Z-Axis Gradient Color and Extrema (Original Mesh)"
)

print("\n--- 7. Working with Color and Extremes Information ---")
print("Explanation: The **original** mesh was used. Original colors were removed, a Red-to-Blue gradient was applied along the Z-axis, and the Z-extrema were highlighted.")
print("Coordinates of the Extrema (along Z-axis):")
print(f"  Minimum Z Coordinate (Blue sphere): {min_z_coord}")
print(f"  Maximum Z Coordinate (Red sphere): {max_z_coord}")
print("-" * 40)