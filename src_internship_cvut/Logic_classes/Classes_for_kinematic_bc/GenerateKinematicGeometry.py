import gmsh
import os
from Logic_classes.ConfigManager import ConfigManager


class GenerateKinematicGeometry:
    """
    Generates a .geo file for a 3D Representative Volume Element (RVE) with kinematic boundary conditions.

    Kinematic BCs prescribe displacements directly on the entire faces of the RVE.
    As a result, no artificial support surfaces are required to prevent rigid body
    motion, allowing for a standard 8-point cube geometry.
    """

    def __init__(self, config_file):
        """
        Initializes the geometry generator with configuration parameters.

        Args:
            config_file (str): Path to the configuration file.
        """
        self.config = ConfigManager(config_file)
        self.L = self.config.get_cube_edge_length_L()
        self.mesh_step_max = self.config.get_mesh_step_max()

        # Output settings
        self.dir_geo = self.config.get_dir_where_geo_file_is_created_kinematic_bc()
        self.name_geo = self.config.get_name_of_geo_file_kinematic_bc()

    def create_points(self):
        """
        Generates the 8 corner vertices of the RVE cube.
        """
        points_data = [
            (0, 0, 0),           # 1: Origin
            (self.L, 0, 0),      # 2: X-axis corner
            (self.L, self.L, 0), # 3: XY-plane corner
            (0, self.L, 0),      # 4: Y-axis corner
            (0, 0, self.L),      # 5: Z-axis corner
            (self.L, 0, self.L), # 6: XZ-plane corner
            (self.L, self.L, self.L), # 7: XYZ-corner
            (0, self.L, self.L)  # 8: YZ-plane corner
        ]

        for tag, (x, y, z) in enumerate(points_data, start=1):
            gmsh.model.geo.addPoint(x, y, z, 0, tag)

        print(f"[KINEMATIC] [GEOMETRY]: Created {len(points_data)} points.")

    def create_lines(self):
        """
        Connects points to form the 12 edges of the cube.
        """
        lines_data = [
            # Bottom face (Z=0)
            (1, 2), (2, 3), (3, 4), (4, 1),
            # Top face (Z=L)
            (5, 6), (6, 7), (7, 8), (8, 5),
            # Vertical pillars
            (1, 5), (2, 6), (3, 7), (4, 8)
        ]

        for tag, (start_point, end_point) in enumerate(lines_data, start=1):
            gmsh.model.geo.addLine(start_point, end_point, tag)

        print(f"[KINEMATIC] [GEOMETRY]: Created {len(lines_data)} lines.")

    def create_surfaces(self):
        """
        Defines the 6 boundary faces of the RVE using curve loops.
        """
        curve_loops_data = [
            [1, 2, 3, 4],       # 1: Bottom surface (Z=0)
            [5, 6, 7, 8],       # 2: Top surface (Z=L)
            [1, 10, -5, -9],    # 3: Front surface (Y=0)
            [3, 12, -7, -11],   # 4: Back surface (Y=L)
            [4, 9, -8, -12],    # 5: Left surface (X=0)
            [2, 11, -6, -10]    # 6: Right surface (X=L)
        ]

        for tag, lines in enumerate(curve_loops_data, start=1):
            gmsh.model.geo.addCurveLoop(lines, tag)
            gmsh.model.geo.addPlaneSurface([tag], tag)

        print(f"[KINEMATIC] [GEOMETRY]: Created {len(curve_loops_data)} surfaces.")

    def create_volume(self):
        """
        Creates the 3D domain (Volume) using the surface loop.
        """
        surface_tags = list(range(1, 7))
        gmsh.model.geo.addSurfaceLoop(surface_tags, 1)
        gmsh.model.geo.addVolume([1], 1)

        print("[KINEMATIC] [GEOMETRY]: Created 1 volume.")

    def create_physical_groups(self):
        """
        Assigns physical groups for BC identification.
        """
        gmsh.model.addPhysicalGroup(3, [1], name="rock")

        # Boundary faces for kinematic loading
        gmsh.model.addPhysicalGroup(2, [1], name=".surface_z_minus")
        gmsh.model.addPhysicalGroup(2, [2], name=".surface_z_plus")
        gmsh.model.addPhysicalGroup(2, [3], name=".surface_y_minus")
        gmsh.model.addPhysicalGroup(2, [4], name=".surface_y_plus")
        gmsh.model.addPhysicalGroup(2, [5], name=".surface_x_minus")
        gmsh.model.addPhysicalGroup(2, [6], name=".surface_x_plus")

    def make_geometry_for_kinematic_boundary_conditions(self):
        """
        Executes the full geometry generation sequence for kinematic BCs.
        """
        print("-------------------------------------------------------------------------------------------")
        print("[KINEMATIC] [INFO]: Starting geometry generation for kinematic boundary conditions, settings:")
        print(f"          - Cube edge length L: {self.L}m")

        gmsh.initialize()
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.model.add(self.name_geo)

        self.create_points()
        self.create_lines()
        self.create_surfaces()
        self.create_volume()

        gmsh.model.geo.synchronize()
        self.create_physical_groups()

        os.makedirs(self.dir_geo, exist_ok=True)
        output_geo = os.path.join(self.dir_geo, f"{self.name_geo}.geo_unrolled").replace("\\", "/")

        gmsh.write(output_geo)
        gmsh.finalize()

        print(f"[KINEMATIC] [GEOMETRY]: File saved to: {output_geo}")
        return output_geo