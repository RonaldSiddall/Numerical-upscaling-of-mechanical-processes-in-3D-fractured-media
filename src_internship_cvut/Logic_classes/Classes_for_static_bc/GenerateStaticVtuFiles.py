import subprocess
import os
import time
from Logic_classes.ConfigManager import ConfigManager


class GenerateStaticVtuFiles:
    """
    This class is responsible for managing and executing a series of Flow123d simulations with static boundary conditions.
    It takes care of preparing the simulation tasks, running them, and extracting the resulting .vtu files
    """

    def __init__(self, config_file):
        """
        Args:
            config_file (str): Path to the configuration file.
        """
        self.config = ConfigManager(config_file)
        self.bat_file_path = self.config.get_dir_of_flow123d_executable_bat_file()
        self.display_std_output_flow = self.config.get_display_std_output_flag()

    def run_static_simulations(self, generated_yaml_tasks):
        # Directory mapping and task preparation
        mappings = [
            (self.config.get_simulation_output_dir_for_normal_sigma_11(),
             self.config.get_name_of_normal_sigma_11_simulation_output_file()),
            (self.config.get_simulation_output_dir_for_normal_sigma_22(),
             self.config.get_name_of_normal_sigma_22_simulation_output_file()),
            (self.config.get_simulation_output_dir_for_normal_sigma_33(),
             self.config.get_name_of_normal_sigma_33_simulation_output_file()),
            (self.config.get_simulation_output_dir_for_shear_sigma_23(),
             self.config.get_name_of_shear_sigma_23_simulation_output_file()),
            (self.config.get_simulation_output_dir_for_shear_sigma_13(),
             self.config.get_name_of_shear_sigma_13_simulation_output_file()),
            (self.config.get_simulation_output_dir_for_shear_sigma_12(),
             self.config.get_name_of_shear_sigma_12_simulation_output_file())
        ]

        detailed_tasks = []
        # This loop prepares the list of tasks with their corresponding output directories and case names
        # based on the provided .yaml paths and the configuration mappings
        for i, task in enumerate(generated_yaml_tasks):
            yaml_path = task[0] if isinstance(task, tuple) else task
            base_dir = mappings[i][0]
            sub_folder = mappings[i][1]
            final_output_dir = os.path.join(base_dir, sub_folder)
            detailed_tasks.append((yaml_path, final_output_dir, sub_folder))

        print("-------------------------------------------------------------------------------------------")
        print("\n[STATIC] [INFO]: Starting Flow123d simulations with static boundary conditions...")
        print(f"[STATIC] [FLOW123D] Used parameters: ")
        print(f"           - Young's Modulus: {self.config.get_young_modulus_rock_gpa()} GPa")
        print(f"           - Poisson's Ratio: {self.config.get_poisson_ratio_rock()}")
        print(f"           - Stress Parameter Alpha: {self.config.get_stress_parameter_alpha()}")

        all_extracted_vtu_files = []
        batch_start_time = time.time()

        # This loop iterates through each prepared task, runs the corresponding Flow123d simulation using the .bat file
        # and extracts the resulting .vtu files from the mechanics subfolder of the output directory
        for yaml_path, final_output_dir, case_name in detailed_tasks:
            yaml_name = os.path.basename(yaml_path)

            abs_yaml_python = os.path.abspath(yaml_path).replace("\\", "/")
            abs_output_python = os.path.abspath(final_output_dir).replace("\\", "/")

            os.makedirs(abs_output_python, exist_ok=True)

            abs_yaml_flow = abs_yaml_python.replace("C:", "/c").replace("c:", "/c")
            abs_output_flow = abs_output_python.replace("C:", "/c").replace("c:", "/c")
            safe_bat_file = os.path.normpath(self.bat_file_path)

            command = f'"{safe_bat_file}" -s "{abs_yaml_flow}" -o "{abs_output_flow}"'

            print(f"\n[STATIC] [FLOW123D]: {yaml_name}...", end="", flush=True)
            sim_start_time = time.time()

            if self.display_std_output_flow == "yes":
                subprocess.run(command, shell=True)
            else:
                subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            sim_end_time = time.time()
            elapsed_time = sim_end_time - sim_start_time
            sim_time_str = f"{elapsed_time:.2f} s" if elapsed_time < 60 else f"{int(elapsed_time // 60)} min {int(elapsed_time % 60)} s"

            print(f" simulation done in {sim_time_str}")
            print(f"           - Output directory: {abs_output_python}")
            print(f"           - Case name: {case_name}")

            # Extracts resulting .vtu files (specifically the one ending with "000000.vtu") from the mechanics subfolder
            mechanics_dir = os.path.join(abs_output_python, "mechanics").replace("\\", "/")
            if os.path.exists(mechanics_dir):
                for f in os.listdir(mechanics_dir):
                    if f.endswith("000000.vtu"):
                        all_extracted_vtu_files.append(os.path.join(mechanics_dir, f).replace("\\", "/"))

        batch_duration = time.time() - batch_start_time
        total_time_str = f"{batch_duration:.2f} s" if batch_duration < 60 else f"{int(batch_duration // 60)} min {int(batch_duration % 60)} s"

        print(f"\n[STATIC] [INFO]: All {len(detailed_tasks)} simulations completed. Total time: {total_time_str}")
        return all_extracted_vtu_files