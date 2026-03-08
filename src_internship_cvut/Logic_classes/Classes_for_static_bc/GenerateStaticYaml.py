from Utility_methods.check_values_in_config_file import check_values_in_config_file_yaml
from Logic_classes.ConfigManager import ConfigManager
import os


class GenerateStaticYaml:
    """
        This class generates the Flow123d .yaml input files with the correct parameters and paths
        for static boundary conditions

        This works by reading baseline template .yaml files and injects
        the dynamically generated mesh path, material properties, and the kinematic
        loading parameter (beta) from the config_file into said templates
    """

    # Initiation of the used parameters from the config.yaml file
    def __init__(self, config_file, mesh_file_path):
        self.config = ConfigManager(config_file)
        self.mesh_file_path = mesh_file_path

        # Directory containing the blank .yaml templates
        self.dir_of_yaml_templates_for_static_bc = self.config.get_dir_of_yaml_templates_for_static_bc()

        # Output directories for the 6 independent simulation tasks
        self.dir_where_tension_sigma_11_yaml_is_created = self.config.get_dir_where_normal_sigma_11_yaml_is_created()
        self.dir_where_tension_sigma_22_yaml_is_created = self.config.get_dir_where_normal_sigma_22_yaml_is_created()
        self.dir_where_tension_sigma_33_yaml_is_created = self.config.get_dir_where_normal_sigma_33_yaml_is_created()
        self.dir_where_shear_sigma_23_yaml_is_created = self.config.get_dir_where_shear_sigma_23_yaml_is_created()
        self.dir_where_shear_sigma_13_yaml_is_created = self.config.get_dir_where_shear_sigma_13_yaml_is_created()
        self.dir_where_shear_sigma_12_yaml_is_created = self.config.get_dir_where_shear_sigma_12_yaml_is_created()

        # Names for the generated .yaml files
        self.name_of_tension_sigma_11_yaml_file = self.config.get_name_of_normal_sigma_11_yaml_file()
        self.name_of_tension_sigma_22_yaml_file = self.config.get_name_of_normal_sigma_22_yaml_file()
        self.name_of_tension_sigma_33_yaml_file = self.config.get_name_of_normal_sigma_33_yaml_file()
        self.name_of_shear_sigma_23_yaml_file = self.config.get_name_of_shear_sigma_23_yaml_file()
        self.name_of_shear_sigma_13_yaml_file = self.config.get_name_of_shear_sigma_13_yaml_file()
        self.name_of_shear_sigma_12_yaml_file = self.config.get_name_of_shear_sigma_12_yaml_file()

        # Physical parameters
        self.young_modulus_rock_gpa = self.config.get_young_modulus_rock_gpa()
        self.rock_poisson_ratio = self.config.get_poisson_ratio_rock()
        self.stress_parameter_alpha = self.config.get_stress_parameter_alpha()

    def generate_static_yamls(self):
        """
        This method executes the string-replacement logic to generate the 6 ready-to-run .yamls
        """

        # Converts GPa from the config_file.yaml into standard units (Pa) for the solver
        young_modulus_rock_pa = 1e9 * self.young_modulus_rock_gpa

        safe_mesh_file = self.mesh_file_path.replace("\\", "/").replace("C:", "/C").replace("c:", "/c")

        # The old words in the template .yaml files that we want to replace with actual values
        old_words = [
            "stress_parameter_alpha",
            "output_mesh_path",
            "rock_young_modulus",
            "rock_poisson_ratio"
        ]

        # The actual computed values we are injecting
        new_words = [
            self.stress_parameter_alpha,
            safe_mesh_file,  # Použijeme opravenou, pro Flow123d čitelnou cestu!
            young_modulus_rock_pa,
            self.rock_poisson_ratio
        ]

        # Mapping definition: (Source Template Name, Target Directory, Target Filename)
        file_mapping = [
            ("template_pure_normal_sigma_11.yaml", self.dir_where_tension_sigma_11_yaml_is_created,
             self.name_of_tension_sigma_11_yaml_file),
            ("template_pure_normal_sigma_22.yaml", self.dir_where_tension_sigma_22_yaml_is_created,
             self.name_of_tension_sigma_22_yaml_file),
            ("template_pure_normal_sigma_33.yaml", self.dir_where_tension_sigma_33_yaml_is_created,
             self.name_of_tension_sigma_33_yaml_file),
            ("template_pure_shear_sigma_23.yaml", self.dir_where_shear_sigma_23_yaml_is_created,
             self.name_of_shear_sigma_23_yaml_file),
            ("template_pure_shear_sigma_13.yaml", self.dir_where_shear_sigma_13_yaml_is_created,
             self.name_of_shear_sigma_13_yaml_file),
            ("template_pure_shear_sigma_12.yaml", self.dir_where_shear_sigma_12_yaml_is_created,
             self.name_of_shear_sigma_12_yaml_file)
        ]
        print("-------------------------------------------------------------------------------------------")
        print("[STATIC] [INFO] Starting YAML template generation...\n")

        generated_tasks = []
        for template_name, output_dir, output_name in file_mapping:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            current_template_path = os.path.join(self.dir_of_yaml_templates_for_static_bc, template_name)
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
                print(f"[STATIC] [YAML]: {output_name} saved to {output_dir}")

            except FileNotFoundError:
                print(f"[ERROR]: Template '{template_name}' not found in {self.dir_of_yaml_templates_for_static_bc}")
            except Exception as e:
                print(f"[ERROR]: Unexpected error while processing {template_name}: {e}")

        return generated_tasks