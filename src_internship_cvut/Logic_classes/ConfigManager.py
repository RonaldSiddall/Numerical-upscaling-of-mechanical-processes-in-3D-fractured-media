import yaml
import os


class ConfigManager:
    # Initializes the ConfigManager with the path to the configuration file
    def __init__(self, config_file):
        self.config_file = config_file
        self.config_data = self.load_config()

    # Loads the YAML configuration file into a dictionary
    def load_config(self):
        with open(self.config_file, "r") as file:
            config_data = yaml.safe_load(file)
        return config_data

    # This absolute path is CRUCIAL, because literally every other directory is derived from this one
    def get_absolute_path_to_dir_with_project(self):
        return self.config_data["absolute_path_to_project"]

    # --- Geometry Settings ---
    def get_cube_edge_length_L(self):
        return self.config_data["geometry_settings"]["cube_edge_length_L"]

    def get_support_fraction_d(self):
        return self.config_data["geometry_settings"]["geometry_for_static_bc"]["support_fraction_d"]

    def get_dir_where_geo_file_is_created_static_bc(self):
        rel_path = self.config_data["geometry_settings"]["geometry_for_static_bc"][
            "dir_where_geo_file_is_created_static_bc"]
        abs_path = os.path.join(self.get_absolute_path_to_dir_with_project(), rel_path)
        os.makedirs(abs_path, exist_ok=True)
        return abs_path

    def get_name_of_geo_file_static_bc(self):
        return self.config_data["geometry_settings"]["geometry_for_static_bc"]["name_of_geo_file_static_bc"]

    def get_dir_where_geo_file_is_created_kinematic_bc(self):
        rel_path = self.config_data["geometry_settings"]["geometry_for_kinematic_bc"][
            "dir_where_geo_file_is_created_kinematic_bc"]
        abs_path = os.path.join(self.get_absolute_path_to_dir_with_project(), rel_path)
        os.makedirs(abs_path, exist_ok=True)
        return abs_path

    def get_name_of_geo_file_kinematic_bc(self):
        return self.config_data["geometry_settings"]["geometry_for_kinematic_bc"]["name_of_geo_file_kinematic_bc"]

    # --- Mesh Settings (ZCELA NOVÉ PODLE TVÉHO YAML) ---
    def get_mesh_step_max(self):
        return self.config_data["mesh_settings"]["mesh_parameters"]["mesh_step_max"]

    def get_mesh_step_min(self):
        return self.config_data["mesh_settings"]["mesh_parameters"]["mesh_step_min"]

    def get_dir_where_msh_file_is_created_static_bc(self):
        rel_path = self.config_data["mesh_settings"]["mesh_for_static_bc"]["dir_where_msh_file_is_created_static_bc"]
        abs_path = os.path.join(self.get_absolute_path_to_dir_with_project(), rel_path)
        os.makedirs(abs_path, exist_ok=True)
        return abs_path
    def get_transition_zone_length(self):
        return self.config_data["mesh_settings"]["mesh_parameters"]["transition_zone_length"]

    def get_name_of_msh_file_static_bc(self):
        return self.config_data["mesh_settings"]["mesh_for_static_bc"]["name_of_msh_file_static_bc"]

    def get_dir_where_msh_file_is_created_kinematic_bc(self):
        rel_path = self.config_data["mesh_settings"]["mesh_for_kinematic_bc"][
            "dir_where_msh_file_is_created_kinematic_bc"]
        abs_path = os.path.join(self.get_absolute_path_to_dir_with_project(), rel_path)
        os.makedirs(abs_path, exist_ok=True)
        return abs_path

    def get_name_of_msh_file_kinematic_bc(self):
        return self.config_data["mesh_settings"]["mesh_for_kinematic_bc"]["name_of_msh_file_kinematic_bc"]
    def get_tolerance_initial_delaunay(self):
        return self.config_data["mesh_settings"]["mesh_parameters"]["tolerance_initial_delaunay"]

    # --- Flow123d Simulation Settings ---
    def get_dir_of_all_yaml_templates(self):
        rel_path = self.config_data["yaml_creation_settings"]["dir_of_all_yaml_templates"]
        return os.path.join(self.get_absolute_path_to_dir_with_project(), rel_path)

    def get_dir_of_yaml_templates_for_static_bc(self):
        rel_path = self.get_dir_of_all_yaml_templates() + "Templates_static_boundary_conditions/"
        abs_path = rel_path  # Flow123d path format fix
        return abs_path

    def get_dir_of_yaml_templates_for_kinematic_bc(self):
        rel_path = self.get_dir_of_all_yaml_templates() + "Templates_kinematic_boundary_conditions/"
        abs_path = rel_path
        return abs_path

    def get_dir_where_normal_sigma_11_yaml_is_created(self):
        rel_path = self.config_data["yaml_creation_settings"]["settings_for_yamls_static_bc"][
            "dir_where_normal_sigma_11_yaml_is_created"]
        abs_path = os.path.join(self.get_absolute_path_to_dir_with_project(), rel_path)
        os.makedirs(abs_path, exist_ok=True)
        return abs_path

    def get_dir_where_normal_sigma_22_yaml_is_created(self):
        rel_path = self.config_data["yaml_creation_settings"]["settings_for_yamls_static_bc"][
            "dir_where_normal_sigma_22_yaml_is_created"]
        abs_path = os.path.join(self.get_absolute_path_to_dir_with_project(), rel_path)
        os.makedirs(abs_path, exist_ok=True)
        return abs_path

    def get_dir_where_normal_sigma_33_yaml_is_created(self):
        rel_path = self.config_data["yaml_creation_settings"]["settings_for_yamls_static_bc"][
            "dir_where_normal_sigma_33_yaml_is_created"]
        abs_path = os.path.join(self.get_absolute_path_to_dir_with_project(), rel_path)
        os.makedirs(abs_path, exist_ok=True)
        return abs_path

    def get_dir_where_shear_sigma_23_yaml_is_created(self):
        rel_path = self.config_data["yaml_creation_settings"]["settings_for_yamls_static_bc"][
            "dir_where_shear_sigma_23_yaml_is_created"]
        abs_path = os.path.join(self.get_absolute_path_to_dir_with_project(), rel_path)
        os.makedirs(abs_path, exist_ok=True)
        return abs_path

    def get_dir_where_shear_sigma_13_yaml_is_created(self):
        rel_path = self.config_data["yaml_creation_settings"]["settings_for_yamls_static_bc"][
            "dir_where_shear_sigma_13_yaml_is_created"]
        abs_path = os.path.join(self.get_absolute_path_to_dir_with_project(), rel_path)
        os.makedirs(abs_path, exist_ok=True)
        return abs_path

    def get_dir_where_shear_sigma_12_yaml_is_created(self):
        rel_path = self.config_data["yaml_creation_settings"]["settings_for_yamls_static_bc"][
            "dir_where_shear_sigma_12_yaml_is_created"]
        abs_path = os.path.join(self.get_absolute_path_to_dir_with_project(), rel_path)
        os.makedirs(abs_path, exist_ok=True)
        return abs_path

    def get_dir_where_normal_E_11_yaml_is_created(self):
        rel_path = self.config_data["yaml_creation_settings"]["settings_for_yamls_kinematic_bc"][
            "dir_where_normal_E_11_yaml_is_created"]
        abs_path = os.path.join(self.get_absolute_path_to_dir_with_project(), rel_path)
        os.makedirs(abs_path, exist_ok=True)
        return abs_path

    def get_dir_where_normal_E_22_yaml_is_created(self):
        rel_path = self.config_data["yaml_creation_settings"]["settings_for_yamls_kinematic_bc"][
            "dir_where_normal_E_22_yaml_is_created"]
        abs_path = os.path.join(self.get_absolute_path_to_dir_with_project(), rel_path)
        os.makedirs(abs_path, exist_ok=True)
        return abs_path

    def get_dir_where_normal_E_33_yaml_is_created(self):
        rel_path = self.config_data["yaml_creation_settings"]["settings_for_yamls_kinematic_bc"][
            "dir_where_normal_E_33_yaml_is_created"]
        abs_path = os.path.join(self.get_absolute_path_to_dir_with_project(), rel_path)
        os.makedirs(abs_path, exist_ok=True)
        return abs_path

    def get_dir_where_shear_E_shear_23_yaml_is_created(self):
        rel_path = self.config_data["yaml_creation_settings"]["settings_for_yamls_kinematic_bc"][
            "dir_where_shear_E_23_yaml_is_created"]
        abs_path = os.path.join(self.get_absolute_path_to_dir_with_project(), rel_path)
        os.makedirs(abs_path, exist_ok=True)
        return abs_path

    def get_dir_where_shear_E_13_yaml_is_created(self):
        rel_path = self.config_data["yaml_creation_settings"]["settings_for_yamls_kinematic_bc"][
            "dir_where_shear_E_13_yaml_is_created"]
        abs_path = os.path.join(self.get_absolute_path_to_dir_with_project(), rel_path)
        os.makedirs(abs_path, exist_ok=True)
        return abs_path

    def get_dir_where_shear_E_12_yaml_is_created(self):
        rel_path = self.config_data["yaml_creation_settings"]["settings_for_yamls_kinematic_bc"][
            "dir_where_shear_E_12_yaml_is_created"]
        abs_path = os.path.join(self.get_absolute_path_to_dir_with_project(), rel_path)
        os.makedirs(abs_path, exist_ok=True)
        return abs_path

    def ensure_yaml_extension(self, filename):
        return filename if filename.endswith(".yaml") else filename + ".yaml"

    def get_name_of_normal_sigma_11_yaml_file(self):
        name = self.config_data["yaml_creation_settings"]["settings_for_yamls_static_bc"][
            "name_of_normal_sigma_11_yaml_file"]
        return self.ensure_yaml_extension(name)

    def get_name_of_normal_sigma_22_yaml_file(self):
        name = self.config_data["yaml_creation_settings"]["settings_for_yamls_static_bc"][
            "name_of_normal_sigma_22_yaml_file"]
        return self.ensure_yaml_extension(name)

    def get_name_of_normal_sigma_33_yaml_file(self):
        name = self.config_data["yaml_creation_settings"]["settings_for_yamls_static_bc"][
            "name_of_normal_sigma_33_yaml_file"]
        return self.ensure_yaml_extension(name)

    def get_name_of_shear_sigma_23_yaml_file(self):
        name = self.config_data["yaml_creation_settings"]["settings_for_yamls_static_bc"][
            "name_of_shear_sigma_23_yaml_file"]
        return self.ensure_yaml_extension(name)

    def get_name_of_shear_sigma_13_yaml_file(self):
        name = self.config_data["yaml_creation_settings"]["settings_for_yamls_static_bc"][
            "name_of_shear_sigma_13_yaml_file"]
        return self.ensure_yaml_extension(name)

    def get_name_of_shear_sigma_12_yaml_file(self):
        name = self.config_data["yaml_creation_settings"]["settings_for_yamls_static_bc"][
            "name_of_shear_sigma_12_yaml_file"]
        return self.ensure_yaml_extension(name)

    def get_name_of_normal_E_11_yaml_file(self):
        name = self.config_data["yaml_creation_settings"]["settings_for_yamls_kinematic_bc"][
            "name_of_normal_E_11_yaml_file"]
        return self.ensure_yaml_extension(name)

    def get_name_of_normal_E_22_yaml_file(self):
        name = self.config_data["yaml_creation_settings"]["settings_for_yamls_kinematic_bc"][
            "name_of_normal_E_22_yaml_file"]
        return self.ensure_yaml_extension(name)

    def get_name_of_normal_E_33_yaml_file(self):
        name = self.config_data["yaml_creation_settings"]["settings_for_yamls_kinematic_bc"][
            "name_of_normal_E_33_yaml_file"]
        return self.ensure_yaml_extension(name)

    def get_name_of_shear_E_12_yaml_file(self):
        name = self.config_data["yaml_creation_settings"]["settings_for_yamls_kinematic_bc"][
            "name_of_shear_E_12_yaml_file"]
        return self.ensure_yaml_extension(name)

    def get_name_of_shear_E_13_yaml_file(self):
        name = self.config_data["yaml_creation_settings"]["settings_for_yamls_kinematic_bc"][
            "name_of_shear_E_13_yaml_file"]
        return self.ensure_yaml_extension(name)

    def get_name_of_shear_E_23_yaml_file(self):
        name = self.config_data["yaml_creation_settings"]["settings_for_yamls_kinematic_bc"][
            "name_of_shear_E_23_yaml_file"]
        return self.ensure_yaml_extension(name)

    def get_young_modulus_rock_gpa(self):
        return self.config_data["model_parameter_settings"]["material_properties"]["young_modulus_rock_gpa"]

    def get_poisson_ratio_rock(self):
        return self.config_data["model_parameter_settings"]["material_properties"]["poisson_ratio_rock"]

    def get_stress_parameter_alpha(self):
        return self.config_data["model_parameter_settings"]["boundary_conditions"]["stress_parameter_alpha"]

    def get_deformation_parameter_beta(self):
        return self.config_data["model_parameter_settings"]["boundary_conditions"]["deformation_parameter_beta"]

    def get_boundary_condition_type(self):
        return self.config_data["model_parameter_settings"]["boundary_conditions"]["boundary_condition_type"]

    # --- Post-processing and Tensor Evaluation ---
    def get_dir_of_flow123d_executable_bat_file(self):
        rel_path = self.config_data["simulation_output_and_effective_tensor_computation_settings"][
            "dir_of_flow123d_executable_bat_file"]
        abs_path = os.path.join(self.get_absolute_path_to_dir_with_project(), rel_path)
        return abs_path

    def get_name_of_file_with_tensor_static_bc(self) -> str:
        file = \
        self.config_data["simulation_output_and_effective_tensor_computation_settings"]["tensor_evaluation_settings"][
            "name_of_file_with_tensor_static_bc"]
        if not file.endswith(".txt"):
            file = file + ".txt"
        return file

    def get_output_dir_of_file_with_tensor_static_bc(self):
        rel_path = \
        self.config_data["simulation_output_and_effective_tensor_computation_settings"]["tensor_evaluation_settings"][
            "output_dir_of_file_with_tensor_static_bc"]
        abs_path = os.path.join(self.get_absolute_path_to_dir_with_project(), rel_path)
        os.makedirs(abs_path, exist_ok=True)
        file_path = abs_path + self.get_name_of_file_with_tensor_static_bc()
        return file_path

    def get_name_of_file_with_tensor_kinematic_bc(self) -> str:
        file = \
        self.config_data["simulation_output_and_effective_tensor_computation_settings"]["tensor_evaluation_settings"][
            "name_of_file_with_tensor_kinematic_bc"]
        if not file.endswith(".txt"):
            file = file + ".txt"
        return file

    def get_output_dir_of_file_with_tensor_kinematic_bc(self):
        rel_path = \
        self.config_data["simulation_output_and_effective_tensor_computation_settings"]["tensor_evaluation_settings"][
            "output_dir_of_file_with_tensor_kinematic_bc"]
        abs_path = os.path.join(self.get_absolute_path_to_dir_with_project(), rel_path)
        os.makedirs(abs_path, exist_ok=True)
        file_path = abs_path + self.get_name_of_file_with_tensor_kinematic_bc()
        return file_path

    def get_simulation_output_dir_for_normal_sigma_11(self):
        rel_path = self.config_data["simulation_output_and_effective_tensor_computation_settings"][
            "simulation_static_bc_output_settings"]["simulation_output_dir_for_normal_sigma_11"]
        abs_path = os.path.join(self.get_absolute_path_to_dir_with_project(), rel_path)
        os.makedirs(abs_path, exist_ok=True)
        return abs_path

    def get_simulation_output_dir_for_normal_sigma_22(self):
        rel_path = self.config_data["simulation_output_and_effective_tensor_computation_settings"][
            "simulation_static_bc_output_settings"]["simulation_output_dir_for_normal_sigma_22"]
        abs_path = os.path.join(self.get_absolute_path_to_dir_with_project(), rel_path)
        os.makedirs(abs_path, exist_ok=True)
        return abs_path

    def get_simulation_output_dir_for_normal_sigma_33(self):
        rel_path = self.config_data["simulation_output_and_effective_tensor_computation_settings"][
            "simulation_static_bc_output_settings"]["simulation_output_dir_for_normal_sigma_33"]
        abs_path = os.path.join(self.get_absolute_path_to_dir_with_project(), rel_path)
        os.makedirs(abs_path, exist_ok=True)
        return abs_path

    def get_simulation_output_dir_for_shear_sigma_23(self):
        rel_path = self.config_data["simulation_output_and_effective_tensor_computation_settings"][
            "simulation_static_bc_output_settings"]["simulation_output_dir_for_shear_sigma_23"]
        abs_path = os.path.join(self.get_absolute_path_to_dir_with_project(), rel_path)
        os.makedirs(abs_path, exist_ok=True)
        return abs_path

    def get_simulation_output_dir_for_shear_sigma_13(self):
        rel_path = self.config_data["simulation_output_and_effective_tensor_computation_settings"][
            "simulation_static_bc_output_settings"]["simulation_output_dir_for_shear_sigma_13"]
        abs_path = os.path.join(self.get_absolute_path_to_dir_with_project(), rel_path)
        os.makedirs(abs_path, exist_ok=True)
        return abs_path

    def get_simulation_output_dir_for_shear_sigma_12(self):
        rel_path = self.config_data["simulation_output_and_effective_tensor_computation_settings"][
            "simulation_static_bc_output_settings"]["simulation_output_dir_for_shear_sigma_12"]
        abs_path = os.path.join(self.get_absolute_path_to_dir_with_project(), rel_path)
        os.makedirs(abs_path, exist_ok=True)
        return abs_path

    def get_simulation_output_dir_for_normal_E_11(self):
        rel_path = self.config_data["simulation_output_and_effective_tensor_computation_settings"][
            "simulation_kinematic_bc_output_settings"]["simulation_output_dir_for_normal_E_11"]
        abs_path = os.path.join(self.get_absolute_path_to_dir_with_project(), rel_path)
        os.makedirs(abs_path, exist_ok=True)
        return abs_path

    def get_simulation_output_dir_for_normal_E_22(self):
        rel_path = self.config_data["simulation_output_and_effective_tensor_computation_settings"][
            "simulation_kinematic_bc_output_settings"]["simulation_output_dir_for_normal_E_22"]
        abs_path = os.path.join(self.get_absolute_path_to_dir_with_project(), rel_path)
        os.makedirs(abs_path, exist_ok=True)
        return abs_path

    def get_simulation_output_dir_for_normal_E_33(self):
        rel_path = self.config_data["simulation_output_and_effective_tensor_computation_settings"][
            "simulation_kinematic_bc_output_settings"]["simulation_output_dir_for_normal_E_33"]
        abs_path = os.path.join(self.get_absolute_path_to_dir_with_project(), rel_path)
        os.makedirs(abs_path, exist_ok=True)
        return abs_path

    def get_simulation_output_dir_for_shear_E_23(self):
        rel_path = self.config_data["simulation_output_and_effective_tensor_computation_settings"][
            "simulation_kinematic_bc_output_settings"]["simulation_output_dir_for_shear_E_23"]
        abs_path = os.path.join(self.get_absolute_path_to_dir_with_project(), rel_path)
        os.makedirs(abs_path, exist_ok=True)
        return abs_path

    def get_simulation_output_dir_for_shear_E_13(self):
        rel_path = self.config_data["simulation_output_and_effective_tensor_computation_settings"][
            "simulation_kinematic_bc_output_settings"]["simulation_output_dir_for_shear_E_13"]
        abs_path = os.path.join(self.get_absolute_path_to_dir_with_project(), rel_path)
        os.makedirs(abs_path, exist_ok=True)
        return abs_path

    def get_simulation_output_dir_for_shear_E_12(self):
        rel_path = self.config_data["simulation_output_and_effective_tensor_computation_settings"][
            "simulation_kinematic_bc_output_settings"]["simulation_output_dir_for_shear_E_12"]
        abs_path = os.path.join(self.get_absolute_path_to_dir_with_project(), rel_path)
        os.makedirs(abs_path, exist_ok=True)
        return abs_path

    def get_name_of_normal_sigma_11_simulation_output_file(self):
        return self.config_data["simulation_output_and_effective_tensor_computation_settings"][
            "simulation_static_bc_output_settings"]["name_of_normal_sigma_11_simulation_output_file"]

    def get_name_of_normal_sigma_22_simulation_output_file(self):
        return self.config_data["simulation_output_and_effective_tensor_computation_settings"][
            "simulation_static_bc_output_settings"]["name_of_normal_sigma_22_simulation_output_file"]

    def get_name_of_normal_sigma_33_simulation_output_file(self):
        return self.config_data["simulation_output_and_effective_tensor_computation_settings"][
            "simulation_static_bc_output_settings"]["name_of_normal_sigma_33_simulation_output_file"]

    def get_name_of_shear_sigma_23_simulation_output_file(self):
        return self.config_data["simulation_output_and_effective_tensor_computation_settings"][
            "simulation_static_bc_output_settings"]["name_of_shear_sigma_23_simulation_output_file"]

    def get_name_of_shear_sigma_13_simulation_output_file(self):
        return self.config_data["simulation_output_and_effective_tensor_computation_settings"][
            "simulation_static_bc_output_settings"]["name_of_shear_sigma_13_simulation_output_file"]

    def get_name_of_shear_sigma_12_simulation_output_file(self):
        return self.config_data["simulation_output_and_effective_tensor_computation_settings"][
            "simulation_static_bc_output_settings"]["name_of_shear_sigma_12_simulation_output_file"]

    def get_name_of_normal_E_11_simulation_output_file(self):
        return self.config_data["simulation_output_and_effective_tensor_computation_settings"][
            "simulation_kinematic_bc_output_settings"]["name_of_normal_E_11_simulation_output_file"]

    def get_name_of_normal_E_22_simulation_output_file(self):
        return self.config_data["simulation_output_and_effective_tensor_computation_settings"][
            "simulation_kinematic_bc_output_settings"]["name_of_normal_E_22_simulation_output_file"]

    def get_name_of_normal_E_33_simulation_output_file(self):
        return self.config_data["simulation_output_and_effective_tensor_computation_settings"][
            "simulation_kinematic_bc_output_settings"]["name_of_normal_E_33_simulation_output_file"]

    def get_name_of_shear_E_23_simulation_output_file(self):
        return self.config_data["simulation_output_and_effective_tensor_computation_settings"][
            "simulation_kinematic_bc_output_settings"]["name_of_shear_E_23_simulation_output_file"]

    def get_name_of_shear_E_13_simulation_output_file(self):
        return self.config_data["simulation_output_and_effective_tensor_computation_settings"][
            "simulation_kinematic_bc_output_settings"]["name_of_shear_E_13_simulation_output_file"]

    def get_name_of_shear_E_12_simulation_output_file(self):
        return self.config_data["simulation_output_and_effective_tensor_computation_settings"][
            "simulation_kinematic_bc_output_settings"]["name_of_shear_E_12_simulation_output_file"]

    # --- Global Optional Settings ---
    def get_display_std_output_flag(self):
        return self.config_data["optional_settings"]["display_std_output_flag"]