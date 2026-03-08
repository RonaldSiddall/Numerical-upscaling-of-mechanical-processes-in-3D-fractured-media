import sys
from datetime import datetime

from Logic_classes.ConfigManager import ConfigManager
from Logic_classes.Classes_for_static_bc.GenerateStaticGeometry import GenerateStaticGeometry
from Logic_classes.Classes_for_kinematic_bc.GenerateKinematicGeometry import GenerateKinematicGeometry
from Logic_classes.Classes_for_static_bc.GenerateStaticMesh import GenerateStaticMesh
from Logic_classes.Classes_for_kinematic_bc.GenerateKinematicMesh import GenerateKinematicMesh
from Logic_classes.Classes_for_static_bc.GenerateStaticYaml import GenerateStaticYaml
from Logic_classes.Classes_for_kinematic_bc.GenerateKinematicYaml import GenerateKinematicYaml
from Logic_classes.Classes_for_static_bc.GenerateStaticVtuFiles import GenerateStaticVtuFiles
from Logic_classes.Classes_for_kinematic_bc.GenerateKinematicVtuFiles import GenerateKinematicVtuFiles
from Logic_classes.Classes_for_static_bc.GenerateStaticEffectiveElasticTensor import \
    GenerateStaticEffectiveElasticTensor
from Logic_classes.Classes_for_kinematic_bc.GenerateKinematicEffectiveElasticTensor import \
    GenerateKinematicEffectiveElasticTensor

from Utility_methods.check_values_in_config_file import check_values_in_config_file_yaml, \
    check_values_in_config_file_mesh


def main(config_file):
    print("\n[INFO] Initializing configuration and validating input parameters...\n")
    config = ConfigManager(config_file)
    bc_type = config.get_boundary_condition_type().lower()

    # Validation of all physical and geometrical parameters
    is_yaml_valid = check_values_in_config_file_yaml(config_file)
    is_mesh_valid = check_values_in_config_file_mesh(config_file)

    # Terminates if any validation check fails
    if not is_yaml_valid or not is_mesh_valid:
        sys.exit(1)

    print("[INFO] All configuration parameters are valid. Proceeding...\n")

    # Processing of static boundary conditions
    if bc_type in ["static", "both"]:
        start_time_formatted = datetime.now()
        print("\n=====================================================================================")
        print("             STARTING FLOW123D SIMULATIONS WITH STATIC BOUNDARY CONDITIONS")
        print("=====================================================================================")
        print(f"[STATIC] [INFO] Process started at: {start_time_formatted}\n")

        # Geometry and mesh generation
        GenerateStaticGeometry(config_file).make_geometry_static_boundary_conditions()
        mesh_file_static = GenerateStaticMesh(config_file).generate_mesh_for_static_boundary_conditions()

        # YAML template generation
        static_tasks = GenerateStaticYaml(config_file, mesh_file_static).generate_static_yamls()

        # Simulation execution
        static_generator = GenerateStaticVtuFiles(config_file)
        static_raw_vtu_results = static_generator.run_static_simulations(static_tasks)

        # Extraction and tensor computation
        static_final_vtu_files = [f for f in static_raw_vtu_results if f.endswith("000000.vtu")]

        if len(static_final_vtu_files) == 6:
            print("-------------------------------------------------------------------------------------------")
            print("\n[STATIC] [INFO]: Starting computation of the effective tensor for static boundary conditions...")
            static_tensor_generator = GenerateStaticEffectiveElasticTensor(config_file)
            static_tensor_generator.get_static_tensor_in_txt_formatted(static_final_vtu_files)
        else:
            print(f"\n[STATIC] [ERROR]: Expected 6 static .vtu files, but found {len(static_final_vtu_files)}!")

    # Processing of kinematic boundary conditions
    if bc_type in ["kinematic", "both"]:
        start_time_formatted = datetime.now()
        print("\n=====================================================================================")
        print("             STARTING FLOW123D SIMULATIONS WITH KINEMATIC BOUNDARY CONDITIONS")
        print("=====================================================================================")
        print(f"[KINEMATIC] [INFO] Process started at: {start_time_formatted}\n")

        # Geometry and mesh generation
        GenerateKinematicGeometry(config_file).make_geometry_for_kinematic_boundary_conditions()
        mesh_file_kinematic = GenerateKinematicMesh(config_file).generate_mesh_for_kinematic_boundary_conditions()

        # YAML template generation
        kinematic_tasks = GenerateKinematicYaml(config_file, mesh_file_kinematic).generate_kinematic_yamls()

        # Simulation execution
        kinematic_generator = GenerateKinematicVtuFiles(config_file)
        kinematic_raw_vtu_results = kinematic_generator.run_kinematic_simulations(kinematic_tasks)

        # Extraction and tensor computation
        kinematic_final_vtu_files = [f for f in kinematic_raw_vtu_results if f.endswith("000000.vtu")]

        if len(kinematic_final_vtu_files) == 6:
            print("-------------------------------------------------------------------------------------------")
            print(
                "\n[KINEMATIC] [INFO] Starting computation of the effective tensor for kinematic boundary conditions...")
            kinematic_tensor_generator = GenerateKinematicEffectiveElasticTensor(config_file)
            kinematic_tensor_generator.get_kinematic_tensor_in_txt_formatted(kinematic_final_vtu_files)
        else:
            print(
                f"\n[KINEMATIC] [ERROR]: Expected 6 kinematic .vtu files, but found {len(kinematic_final_vtu_files)}!")


# Program entry point
if __name__ == "__main__":
    # Checks for required configuration file argument in gitbash
    if len(sys.argv) < 2:
        print("-----------------------------------------------------------------------------")
        print("\n[ERROR] Missing configuration file argument.")
        print("Please run the script using the following format:\n")
        print(f"python {sys.argv[0]} <config_file.yaml>\n")
        print("-----------------------------------------------------------------------------")
        sys.exit(1)

    config_path = sys.argv[1]
    # TODO: for now left the try expect block, so better error messages can be printed
    #  in case of errors, but it can be removed later
    # try:
    main(config_path)

    # except Exception as error_message:
    #     print("--------------------------------------------------------------------------------")
    #     print("\n[CRITICAL ERROR] An unexpected error occurred during execution:\n")
    #     print(str(error_message)+"\n")
    #     print("------------------------------------------------------------------------------")