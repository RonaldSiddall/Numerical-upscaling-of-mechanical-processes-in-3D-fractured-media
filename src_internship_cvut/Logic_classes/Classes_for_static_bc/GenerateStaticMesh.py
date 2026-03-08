import gmsh
import os
from Logic_classes.ConfigManager import ConfigManager


class GenerateStaticMesh:
    """
    This class generates and refines the 3D finite element mesh

    Static boundary conditions require localized support surfaces at the corners
    to prevent rigid body motion. To avoid severe stress concentrations and
    mathematical instabilities at these supports (the element aspect ratios were worrying near these
    support, they were extremely bad!), which is the reason why this class applies targeted local mesh refinement
    """

    def __init__(self, config_file):
        self.config = ConfigManager(config_file)

        self.L = self.config.get_cube_edge_length_L()
        self.support_fraction_d = self.config.get_support_fraction_d()

        self.mesh_step_max = self.config.get_mesh_step_max()
        self.mesh_step_min = self.config.get_mesh_step_min()
        self.transition_zone_length = self.config.get_transition_zone_length()

        self.dir_with_geo = self.config.get_dir_where_geo_file_is_created_static_bc()
        self.name_of_geo = self.config.get_name_of_geo_file_static_bc()
        self.input_geo_path = os.path.join(self.dir_with_geo, f"{self.name_of_geo}.geo_unrolled").replace("\\", "/")

        self.dir_where_msh = self.config.get_dir_where_msh_file_is_created_static_bc()
        self.name_of_msh = self.config.get_name_of_msh_file_static_bc()
        self.output_msh_path = os.path.join(self.dir_where_msh, f"{self.name_of_msh}.msh").replace("\\", "/")

    def apply_mesh_local_refinement(self):
        # Define the 'hard zone' where the mesh size is strictly forced to the minimum value
        # In this case, we create a hard zone around each of the three supports (0,0,0), (L,0,0), and (0,L,0)
        # The hard zone is defined as a box around each support, with dimensions based on the support_fraction_d parameter
        dist_min = self.support_fraction_d * self.L

        # Defines the transition zone length for gradual element growth
        transition_zone_length_actual = self.L * self.transition_zone_length

        # Hard zone around the origin (0, 0, 0)
        gmsh.model.mesh.field.add("Box", 1)
        gmsh.model.mesh.field.setNumber(1, "VIn", self.mesh_step_min)
        gmsh.model.mesh.field.setNumber(1, "VOut", self.mesh_step_max)
        gmsh.model.mesh.field.setNumber(1, "XMin", 0.0)
        gmsh.model.mesh.field.setNumber(1, "XMax", dist_min)
        gmsh.model.mesh.field.setNumber(1, "YMin", 0.0)
        gmsh.model.mesh.field.setNumber(1, "YMax", dist_min)
        gmsh.model.mesh.field.setNumber(1, "ZMin", 0.0)
        gmsh.model.mesh.field.setNumber(1, "ZMax", dist_min)
        gmsh.model.mesh.field.setNumber(1, "Thickness", transition_zone_length_actual)

        # Hard around the second support (L, 0, 0)
        gmsh.model.mesh.field.add("Box", 2)
        gmsh.model.mesh.field.setNumber(2, "VIn", self.mesh_step_min)
        gmsh.model.mesh.field.setNumber(2, "VOut", self.mesh_step_max)
        gmsh.model.mesh.field.setNumber(2, "XMin", self.L - dist_min)
        gmsh.model.mesh.field.setNumber(2, "XMax", self.L)
        gmsh.model.mesh.field.setNumber(2, "YMin", 0.0)
        gmsh.model.mesh.field.setNumber(2, "YMax", dist_min)
        gmsh.model.mesh.field.setNumber(2, "ZMin", 0.0)
        gmsh.model.mesh.field.setNumber(2, "ZMax", dist_min)
        gmsh.model.mesh.field.setNumber(2, "Thickness", transition_zone_length_actual)

        # Hard zone around the third support (0, L, 0)
        gmsh.model.mesh.field.add("Box", 3)
        gmsh.model.mesh.field.setNumber(3, "VIn", self.mesh_step_min)
        gmsh.model.mesh.field.setNumber(3, "VOut", self.mesh_step_max)
        gmsh.model.mesh.field.setNumber(3, "XMin", 0.0)
        gmsh.model.mesh.field.setNumber(3, "XMax", dist_min)
        gmsh.model.mesh.field.setNumber(3, "YMin", self.L - dist_min)
        gmsh.model.mesh.field.setNumber(3, "YMax", self.L)
        gmsh.model.mesh.field.setNumber(3, "ZMin", 0.0)
        gmsh.model.mesh.field.setNumber(3, "ZMax", dist_min)
        gmsh.model.mesh.field.setNumber(3, "Thickness", transition_zone_length_actual)

        # This ensures that the minimum element size is strictly enforced within the hard zones,
        # and that there is a smooth transition to the maximum element size in the bulk of the material
        gmsh.model.mesh.field.add("Min", 4)
        gmsh.model.mesh.field.setNumbers(4, "FieldsList", [1, 2, 3])
        gmsh.model.mesh.field.setAsBackgroundMesh(4)

        gmsh.option.setNumber("Mesh.MeshSizeMin", self.mesh_step_min)
        gmsh.option.setNumber("Mesh.MeshSizeMax", self.mesh_step_max)

        # We change the 2D surface meshing algorithm to 'Frontal-Delaunay' (which is algorithm 6)
        gmsh.option.setNumber("Mesh.Algorithm", 6)
        print(f"           - Hard zone: {dist_min:}m")
        print(f"           - Mesh size in hard zones: {self.mesh_step_min:}")
        print(
            f"           - Transition zone length: {transition_zone_length_actual:} (or {self.transition_zone_length * 100:}% of L)")
        print(f"           - Mesh size in bulk: {self.mesh_step_max:}")
        print(f"           - Tolerance initial delaunay: {self.config.get_tolerance_initial_delaunay()}\n")

    def generate_mesh_for_static_boundary_conditions(self):
        """
        This method generates the 3D mesh for static boundary conditions, applying local refinement around the support surfaces

        Returns the absolute path to the generated .msh file.
        """
        print("-------------------------------------------------------------------------------------------")
        print("\n[STATIC] [INFO]: Starting mesh generation for static boundary conditions...\n")

        # Safety check to ensure the geometry was built before meshing
        if not os.path.exists(self.input_geo_path):
            print(f"\n[STATIC] [ERROR]: Geometry file not found: {self.input_geo_path}")
            return None

        gmsh.initialize()
        # Suppress the default GMSH console output
        gmsh.option.setNumber("General.Terminal", 0)

        # Loads the geometry from the .geo_unrolled file created by the GenerateStaticGeo class.
        # This file contains the cube RVE with the necessary support surfaces for static boundary conditions.
        gmsh.merge(self.input_geo_path)
        print(f"[STATIC] [MESH]: Geometry loaded from {self.name_of_geo}.geo_unrolled")

        # Applies local refinement to the mesh around the support surfaces to ensure better element quality
        # and numerical stability in these critical regions
        print(f"[STATIC] [MESH]: Applying local mesh refinement around support surfaces:")
        self.apply_mesh_local_refinement()

        # Generates mesh which will be used for all 6 static simulations, so we generate it only once here,
        # and then we just reuse the same .msh file for all 6 .yamls
        print("[STATIC] [MESH]: Generating 3D mesh...")
        gmsh.model.mesh.generate(3)

        # Optimizes mesh quality using the Netgen algorithm, which is particularly effective for tetrahedral meshes
        print("[STATIC] [MESH]: Optimizing mesh quality using Netgen...")
        gmsh.model.mesh.optimize("Netgen")

        # Extracts statistics about the generated mesh
        node_tags, _, _ = gmsh.model.mesh.getNodes()
        total_nodes = len(node_tags)

        _, surface_elem_tags, _ = gmsh.model.mesh.getElements(dim=2)
        total_surface_elements = sum(len(tags) for tags in surface_elem_tags) if surface_elem_tags else 0

        _, volume_elem_tags, _ = gmsh.model.mesh.getElements(dim=3)
        total_volume_elements = sum(len(tags) for tags in volume_elem_tags) if volume_elem_tags else 0

        print("\n[STATIC] [MESH]: General info about the generated mesh:")
        print(f"           - Number of nodes: {total_nodes}")
        print(f"           - Number of 2D surface elements: {total_surface_elements}")
        print(f"           - Number of 3D volume elements: {total_volume_elements}\n")

        # Saves file
        os.makedirs(self.dir_where_msh, exist_ok=True)
        gmsh.write(self.output_msh_path)

        gmsh.finalize()

        print(f"[STATIC] [MESH]: Mesh successfully saved to: {self.output_msh_path}\n")
        return self.output_msh_path