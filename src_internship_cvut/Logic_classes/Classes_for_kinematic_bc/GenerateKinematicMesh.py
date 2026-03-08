import gmsh
import os
from Logic_classes.ConfigManager import ConfigManager


class GenerateKinematicMesh:
    """
    Generates the 3D finite element mesh for kinematic boundary conditions.

    Since kinematic BCs prescribe continuous displacements across entire faces,
    localized corner supports are not needed. This allows for a more uniform
    mesh distribution without complex local refinement zones.
    """

    def __init__(self, config_file):
        self.config = ConfigManager(config_file)
        self.L = self.config.get_cube_edge_length_L()
        self.mesh_step_max = self.config.get_mesh_step_max()

        # Paths for input geometry and output mesh
        self.dir_geo = self.config.get_dir_where_geo_file_is_created_kinematic_bc()
        self.name_geo = self.config.get_name_of_geo_file_kinematic_bc()
        self.input_geo_path = os.path.join(self.dir_geo, f"{self.name_geo}.geo_unrolled").replace("\\", "/")

        # Output path for the generated mesh
        self.dir_msh = self.config.get_dir_where_msh_file_is_created_kinematic_bc()
        self.name_msh = self.config.get_name_of_msh_file_kinematic_bc()
        self.output_msh_path = os.path.join(self.dir_msh, f"{self.name_msh}.msh").replace("\\", "/")

    def generate_mesh_for_kinematic_boundary_conditions(self):
        print("-------------------------------------------------------------------------------------------")
        print("[KINEMATIC] [INFO]: Starting mesh generation for kinematic boundary conditions...\n")

        if not os.path.exists(self.input_geo_path):
            print(f"[KINEMATIC] [ERROR]: Geometry file not found: {self.input_geo_path}")
            return None

        gmsh.initialize()
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.merge(self.input_geo_path)
        print(f"[KINEMATIC] [MESH]: Geometry loaded from {self.name_geo}.geo_unrolled")

        # Sets global mesh size
        gmsh.option.setNumber("Mesh.MeshSizeMin", self.mesh_step_max)
        gmsh.option.setNumber("Mesh.MeshSizeMax", self.mesh_step_max)

        print("[KINEMATIC] [MESH]: Generating 3D mesh...")
        gmsh.model.mesh.generate(3)

        print("[KINEMATIC] [MESH]: Optimizing mesh quality using Netgen...")
        gmsh.model.mesh.optimize("Netgen")

        # Extracts mesh statistics
        node_tags, _, _ = gmsh.model.mesh.getNodes()
        _, surface_elem_tags, _ = gmsh.model.mesh.getElements(dim=2)
        _, volume_elem_tags, _ = gmsh.model.mesh.getElements(dim=3)

        total_nodes = len(node_tags)
        total_surf = sum(len(tags) for tags in surface_elem_tags) if surface_elem_tags else 0
        total_vol = sum(len(tags) for tags in volume_elem_tags) if volume_elem_tags else 0

        print("[KINEMATIC] [MESH]: General info about the generated mesh:")
        print(f"           - Global mesh step: {self.mesh_step_max}")
        print(f"           - Number of nodes: {total_nodes}")
        print(f"           - Number of 2D surface elements: {total_surf}")
        print(f"           - Number of 3D volume elements: {total_vol}\n")

        os.makedirs(self.dir_msh, exist_ok=True)
        gmsh.write(self.output_msh_path)
        gmsh.finalize()

        print(f"[KINEMATIC] [MESH]: Mesh successfully saved to: {self.output_msh_path}\n")
        return self.output_msh_path