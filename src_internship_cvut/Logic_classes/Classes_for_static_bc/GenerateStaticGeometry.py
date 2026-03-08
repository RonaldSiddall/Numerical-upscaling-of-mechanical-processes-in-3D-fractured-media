import gmsh
import os
from Logic_classes.ConfigManager import ConfigManager


class GenerateStaticGeometry:
    """
    Generates a .geo file for a 3D Representative Volume Element (RVE) with static boundary conditions.

    Unlike kinematic conditions, static BCs apply traction to surfaces. To prevent
    rigid body motion (translation or rotation), this class adds small support
    patches at specific corners to statically determine the cube's position.
    """

    def __init__(self, config_file):
        """
        Initializes the geometry generator with configuration parameters.

        Args:
            config_file (str): Path to the configuration file.
        """
        self.config = ConfigManager(config_file)
        self.L = self.config.get_cube_edge_length_L()

        # Support fraction d defines the size of the corner support patches
        self.support_fraction_d = self.config.get_support_fraction_d()
        self.mesh_step_max = self.config.get_mesh_step_max()

        # Output settings
        self.dir_geo = self.config.get_dir_where_geo_file_is_created_static_bc()
        self.name_geo = self.config.get_name_of_geo_file_static_bc()

    def create_points(self):
        """
        Creates 22 points required to define the cube and its support surfaces.
        """
        d = self.support_fraction_d * self.L
        points_data = [
            # Corner 1: Origin and support corners on X, Y, Z planes
            (0, 0, 0), (d, 0, 0), (0, d, 0), (0, 0, d), (d, d, 0), (d, 0, d), (0, d, d),

            # Corner 2: Point (L,0,0) and support corners on Y and Z planes
            (self.L, 0, 0), (self.L - d, 0, 0), (self.L, d, 0), (self.L, 0, d), (self.L - d, d, 0), (self.L - d, 0, d),

            # Corner 3: Point (0,L,0) and support corners on X and Y planes
            (0, self.L, 0), (d, self.L, 0), (0, self.L - d, 0), (d, self.L - d, 0),

            # Standard cube corners (remaining vertices)
            (self.L, self.L, 0), (0, 0, self.L), (self.L, 0, self.L), (self.L, self.L, self.L), (0, self.L, self.L)
        ]
        for tag, (x, y, z) in enumerate(points_data, start=1):
            gmsh.model.geo.addPoint(x, y, z, 0, tag)

        print(f"[STATIC] [GEOMETRY]: Created {len(points_data)} points.")

    def create_lines(self):
        """
        Connects the 22 points to form 32 lines defining the RVE skeleton.
        """
        lines_data = [
            # Bottom face (Z=0)
            (1, 2), (2, 9), (9, 8), (8, 10), (10, 18),
            (18, 15), (15, 14), (14, 16), (16, 3), (3, 1),

            # Support boundary lines
            (2, 5), (5, 3), (9, 12), (12, 10), (16, 17), (17, 15),

            # Front face (Y=0)
            (8, 11), (11, 20), (20, 19), (19, 4), (4, 1),
            (2, 6), (6, 4), (9, 13), (13, 11),

            # Left face (X=0)
            (14, 22), (22, 19), (3, 7), (7, 4),

            # Standard cube edges
            (20, 21), (21, 22), (18, 21)
        ]

        for tag, (start_point, end_point) in enumerate(lines_data, start=1):
            gmsh.model.geo.addLine(start_point, end_point, tag)

        print(f"[STATIC] [GEOMETRY]: Created {len(lines_data)} lines.")

    def create_surfaces(self):
        """
        Defines 12 surfaces required for the RVE with corner patches.
        """
        loops_data = [
            # Plane Z=0 (Bottom)
            [1, 11, 12, 10], [3, 4, -14, -13], [7, 8, 15, 16],
            [2, 13, 14, 5, 6, -16, -15, 9, -12, -11],

            # Plane Y=0 (Front)
            [1, 22, 23, 21], [3, 17, -25, -24],
            [2, 24, 25, 18, 19, 20, -23, -22],

            # Plane X=0 (Left)
            [-10, 28, 29, 21], [-9, -8, 26, 27, 20, -29, -28],

            # Remaining solid faces
            [-19, 30, 31, 27], [-7, -6, 32, 31, -26], [4, 5, 32, -30, -18, -17]
        ]

        for tag, lines in enumerate(loops_data, start=1):
            gmsh.model.geo.addCurveLoop(lines, tag)
            gmsh.model.geo.addPlaneSurface([tag], tag)

        print(f"[STATIC] [GEOMETRY]: Created {len(loops_data)} surfaces.")

    def create_volume(self):
        """
        Combines all surfaces into a surface loop to create the 3D volume.
        """
        surface_tags = list(range(1, 13))
        gmsh.model.geo.addSurfaceLoop(surface_tags, 1)
        gmsh.model.geo.addVolume([1], 1)

        print("[STATIC] [GEOMETRY]: Created 1 volume.")

    def create_physical_groups(self):
        """
        Names physical parts for identification in Flow123d configuration files.
        """
        gmsh.model.addPhysicalGroup(3, [1], name="rock")

        # Support surfaces
        gmsh.model.addPhysicalGroup(2, [1, 2, 3], name=".support_z")
        gmsh.model.addPhysicalGroup(2, [5, 6], name=".support_y")
        gmsh.model.addPhysicalGroup(2, [8], name=".support_x")

        # Boundary faces for static loading
        gmsh.model.addPhysicalGroup(2, [4], name=".surface_z_minus")
        gmsh.model.addPhysicalGroup(2, [7], name=".surface_y_minus")
        gmsh.model.addPhysicalGroup(2, [9], name=".surface_x_minus")
        gmsh.model.addPhysicalGroup(2, [10], name=".surface_z_plus")
        gmsh.model.addPhysicalGroup(2, [11], name=".surface_y_plus")
        gmsh.model.addPhysicalGroup(2, [12], name=".surface_x_plus")

    def make_geometry_static_boundary_conditions(self):
        """
        Executes the full geometry generation sequence for static BCs.
        """
        print("-------------------------------------------------------------------------------------------")
        print("[STATIC] [INFO]: Starting geometry generation for static boundary conditions, settings:")
        print(f"          - Cube edge length L: {self.L}m")
        print(f"          - Support fraction d: {self.support_fraction_d} (or {self.support_fraction_d * 100}% of L)")

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

        print(f"[STATIC] [GEOMETRY]: File saved to: {output_geo}")
        return output_geo