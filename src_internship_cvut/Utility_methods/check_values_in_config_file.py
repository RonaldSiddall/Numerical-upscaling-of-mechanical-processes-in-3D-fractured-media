from Logic_classes.ConfigManager import ConfigManager


def print_validation_error(param_name, value, reason):
    """
    Prints a formatted error message when a configuration parameter fails validation.

    Args:
        param_name (str): The name of the parameter that caused the error.
        value (any): The invalid value provided in the configuration.
        reason (str): A brief description of why the value is considered invalid.
    """
    print("\n=====================================================================================")
    print("             [ERROR] CONFIGURATION PARAMETER VALIDATION FAILED")
    print("=====================================================================================")
    print(f"[VALIDATION] Error: Parameter '{param_name}' = {value} is invalid.")
    print(f"[VALIDATION] Reason: {reason}")
    print("=====================================================================================\n")


def check_values_in_config_file_mesh(config_file):
    """
    Validates geometry and meshing parameters from the .yaml configuration file.

    This function checks if the spatial dimensions and mesh density settings
    fall within physically realistic and logically consistent ranges.

    Args:
        config_file (str): Path to the .yaml configuration file.

    Returns:
        bool: True if all parameters are valid, False otherwise.
    """
    config = ConfigManager(config_file)

    # Retrieve core geometry and mesh settings
    cube_edge_length_L = config.get_cube_edge_length_L()
    support_fraction_d = config.get_support_fraction_d()
    mesh_step_max = config.get_mesh_step_max()
    mesh_step_min = config.get_mesh_step_min()
    tolerance_initial_delaunay = config.get_tolerance_initial_delaunay()
    transition_zone_length = config.get_transition_zone_length()

    # Geometry validation
    if cube_edge_length_L <= 0:
        print_validation_error("cube_edge_length_L", cube_edge_length_L, "Edge length must be strictly greater than 0.")
        return False

    if support_fraction_d <= 0 or support_fraction_d >= 1:
        print_validation_error("support_fraction_d", support_fraction_d,
                               "Support fraction must be strictly between 0 and 1 (e.g., 0.005).")
        return False

    # Mesh step validation
    if mesh_step_max <= 0:
        print_validation_error("mesh_step_max", mesh_step_max, "Max mesh step must be strictly greater than 0.")
        return False

    if mesh_step_min <= 0:
        print_validation_error("mesh_step_min", mesh_step_min, "Min mesh step must be strictly greater than 0.")
        return False

    if mesh_step_max < mesh_step_min:
        print_validation_error("mesh_step_max / min", f"Max: {mesh_step_max}, Min: {mesh_step_min}",
                               "Max mesh step cannot be smaller than min mesh step.")
        return False

    # Algorithm and zone validation
    if tolerance_initial_delaunay <= 0:
        print_validation_error("tolerance_initial_delaunay", tolerance_initial_delaunay,
                               "Tolerance for Delaunay algorithm must be strictly positive.")
        return False

    if transition_zone_length <= 0 or transition_zone_length >= cube_edge_length_L:
        print_validation_error("transition_zone_length", transition_zone_length,
                               "Transition zone length must be greater than 0 and smaller than the cube edge length L.")
        return False

    return True


def check_values_in_config_file_yaml(config_file):
    """
    Validates physical material properties and boundary conditions.

    Checks the mechanical properties and simulation specific parameters
    to ensure the model remains stable.

    Args:
        config_file (str): Path to the .yaml configuration file.

    Returns:
        bool: True if all parameters are valid, False otherwise.
    """
    config = ConfigManager(config_file)

    # Retrieve material properties and simulation parameters
    young_modulus_rock_gpa = config.get_young_modulus_rock_gpa()
    poisson_ratio_rock = config.get_poisson_ratio_rock()
    stress_parameter_alpha = config.get_stress_parameter_alpha()
    deformation_parameter_beta = config.get_deformation_parameter_beta()
    boundary_condition_type = config.get_boundary_condition_type().lower()
    display_std_output_flag = config.get_display_std_output_flag()

    # Boundary condition type validation
    if boundary_condition_type not in ["static", "kinematic", "both"]:
        print_validation_error("boundary_condition_type", boundary_condition_type,
                               "Allowed values are strictly: 'static', 'kinematic', or 'both'.")
        return False

    # Material properties validation
    if young_modulus_rock_gpa <= 0:
        print_validation_error("young_modulus_rock_gpa", young_modulus_rock_gpa,
                               "Young's modulus must be strictly greater than 0.")
        return False

    if poisson_ratio_rock <= 0 or poisson_ratio_rock >= 0.5:
        print_validation_error("poisson_ratio_rock", poisson_ratio_rock,
                               "Poisson's ratio must be physically valid (between 0 and 0.5 exclusive).")
        return False

    # Boundary condition parameters validation
    if float(stress_parameter_alpha) <= 0:
        print_validation_error("stress_parameter_alpha", stress_parameter_alpha,
                               "Stress parameter alpha must be strictly greater than 0.")
        return False

    if abs(deformation_parameter_beta) >= 1 or deformation_parameter_beta == 0:
        print_validation_error("deformation_parameter_beta", deformation_parameter_beta,
                               "Deformation parameter beta must be non-zero and between -1 and 1.")
        return False

    if display_std_output_flag not in ["yes", "no"]:
        print_validation_error("display_std_output_flag", display_std_output_flag, "Must be exactly 'yes' or 'no'.")
        return False

    return True