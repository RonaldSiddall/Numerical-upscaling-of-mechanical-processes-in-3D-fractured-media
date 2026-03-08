from Utility_methods.check_values_in_config_file import check_values_in_config_file_yaml
from Logic_classes.ConfigManager import ConfigManager
import os


class GenerateKinematicYaml:
    """
    This class generates the Flow123d .yaml input files with the correct parameters and paths
    for kinematic boundary conditions

    This works by reading baseline template .yaml files and injects
    the dynamically generated mesh path, material properties, and the kinematic
    loading parameter (beta) from the config_file into said templates
    """

    def __init__(self, config_file, mesh_file_path):
        self.config = ConfigManager(config_file)
        self.mesh_file_path = mesh_file_path

        # Directory containing the blank .yaml templates
        self.dir_of_yaml_templates_for_kinematic_bc = self.config.get_dir_of_yaml_templates_for_kinematic_bc()

        # Output directories for the 6 independent simulation tasks
        self.dir_where_tension_E_11 = self.config.get_dir_where_normal_E_11_yaml_is_created()
        self.dir_where_tension_E_22 = self.config.get_dir_where_normal_E_22_yaml_is_created()
        self.dir_where_tension_E_33 = self.config.get_dir_where_normal_E_33_yaml_is_created()
        self.dir_where_shear_E_23 = self.config.get_dir_where_shear_E_shear_23_yaml_is_created()
        self.dir_where_shear_E_13 = self.config.get_dir_where_shear_E_13_yaml_is_created()
        self.dir_where_shear_E_12 = self.config.get_dir_where_shear_E_12_yaml_is_created()

        # Names for the generated .yaml files
        self.name_of_tension_E_11 = self.config.get_name_of_normal_E_11_yaml_file()
        self.name_of_tension_E_22 = self.config.get_name_of_normal_E_22_yaml_file()
        self.name_of_tension_E_33 = self.config.get_name_of_normal_E_33_yaml_file()
        self.name_of_shear_E_23 = self.config.get_name_of_shear_E_23_yaml_file()
        self.name_of_shear_E_13 = self.config.get_name_of_shear_E_13_yaml_file()
        self.name_of_shear_E_12 = self.config.get_name_of_shear_E_12_yaml_file()

        # Physical parameters
        self.young_modulus_rock_gpa = self.config.get_young_modulus_rock_gpa()
        self.rock_poisson_ratio = self.config.get_poisson_ratio_rock()
        self.deformation_parameter_beta = self.config.get_deformation_parameter_beta()

    def generate_kinematic_yamls(self):
        """
        This method executes the string-replacement logic to generate the 6 ready-to-run .yamls
        """

        # Converts GPa from the config_file.yaml into standard units (Pa) for the solver
        young_modulus_rock_pa = 1e9 * self.young_modulus_rock_gpa

        safe_mesh_file_path = str(self.mesh_file_path).replace("C:", "/c").replace("c:", "/c").replace("\\", "/")

        # The old words in the template .yaml files that we want to replace with actual values
        old_words = [
            "deformation_parameter_beta",
            "output_mesh_path",
            "rock_young_modulus",
            "rock_poisson_ratio"
        ]

        # The actual computed values we are injecting
        new_words = [
            self.deformation_parameter_beta,
            safe_mesh_file_path,
            young_modulus_rock_pa,
            self.rock_poisson_ratio
        ]

        # Mapping definition: (Source Template Name, Target Directory, Target Filename)
        file_mapping = [
            ("template_pure_normal_E_11.yaml", self.dir_where_tension_E_11, self.name_of_tension_E_11),
            ("template_pure_normal_E_22.yaml", self.dir_where_tension_E_22, self.name_of_tension_E_22),
            ("template_pure_normal_E_33.yaml", self.dir_where_tension_E_33, self.name_of_tension_E_33),
            ("template_pure_shear_E_23.yaml", self.dir_where_shear_E_23, self.name_of_shear_E_23),
            ("template_pure_shear_E_13.yaml", self.dir_where_shear_E_13, self.name_of_shear_E_13),
            ("template_pure_shear_E_12.yaml", self.dir_where_shear_E_12, self.name_of_shear_E_12)
        ]
        print("[KINEMATIC] [INFO]: Starting YAML template generation...\n")

        generated_tasks = []
        for template_name, output_dir, output_name in file_mapping:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            current_template_path = os.path.join(self.dir_of_yaml_templates_for_kinematic_bc, template_name)
            current_output_path = os.path.join(output_dir, output_name)

            try:
                # Reads the blank template
                with open(current_template_path, 'r') as file:
                    data_in_template = file.read()

                # Performs the injection of dynamic variables
                for old_word, new_word in zip(old_words, new_words):
                    data_in_template = data_in_template.replace(old_word, str(new_word))

                # Saves the fully configured execution script
                with open(current_output_path, 'w') as file:
                    file.write(data_in_template)

                generated_tasks.append((current_output_path, output_dir))
                print(f"[KINEMATIC] [YAML]: {output_name} saved to {output_dir}")

            except FileNotFoundError:
                print(f"[KINEMATIC] [ERROR]: Template '{template_name}' not found in {self.dir_of_yaml_templates_for_kinematic_bc}")
            except Exception as e:
                print(f"[KINEMATIC] [ERROR]: Unexpected error while processing {template_name}: {e}")

        return generated_tasks