import numpy as np
import os
from Logic_classes.ConfigManager import ConfigManager
from Logic_classes.GeneralComputationClass import GeneralComputationClass


class GenerateKinematicEffectiveElasticTensor:
    """
    Computes the macroscopic effective elastic tensor for kinematic boundary conditions.

    This class assembles the macroscopic stress and strain matrices from simulation
    results and solves for the stiffness tensor C_k using the relationship:
    Sigma = C_k epsilon
    """

    def __init__(self, config_file):
        self.config = ConfigManager(config_file)
        self.output_path = self.config.get_output_dir_of_file_with_tensor_kinematic_bc()
        self.beta = float(self.config.get_deformation_parameter_beta())

        # Initialize the universal mesh processor for surface integration
        self.mesh_processor = GeneralComputationClass(self.config.get_cube_edge_length_L())

    def generate_macro_deformation_matrix(self):
        """
        Analytically assembles the prescribed macroscopic strain matrix E.

        The matrix is diagonal, containing the normal strain parameter

        Returns:
            np.array: A 6x6 diagonal matrix of prescribed strains.
        """
        macro_deformation_matrix = np.zeros((6, 6))

        # Normal components (E_11, E_22, E_33)
        for i in range(3):
            macro_deformation_matrix[i, i] = self.beta

        # Shear components (E_23, E_13, E_12) - engineering strain requires 2 * beta
        for i in range(3, 6):
            macro_deformation_matrix[i, i] = 2.0 * self.beta

        return macro_deformation_matrix

    def generate_macro_stress_matrix(self, vtu_files):
        """
        Assembles the macroscopic stress matrix Sigma from .vtu result files.

        Each column represents the volume-averaged stress vector integrated
        from one of the six independent loading cases.

        Args:
            vtu_files (list): Paths to the 6 simulation result files.

        Returns:
            np.array: A 6x6 macroscopic stress matrix.
        """
        macro_stress_matrix = np.zeros((6, 6))
        for i, vtu_file in enumerate(vtu_files):
            # Computes the 3x3 average stress tensor via surface integration
            partial_stress_tensor = self.mesh_processor.compute_partial_stress_tensor_for_one_file(vtu_file)

            if partial_stress_tensor is not None:
                # Converts 3x3 tensor to 6x1 Voigt vector and inserts as column
                voigt_vector = self.mesh_processor.convert_partial_stress_tensor_to_voigt(partial_stress_tensor)
                macro_stress_matrix[:, i] = voigt_vector
            else:
                print(f"[KINEMATIC] [ERROR]: Failed to integrate stress for {vtu_file}")
                return None

        return macro_stress_matrix

    def compute_kinematic_effective_elastic_tensor(self, macro_deformation_matrix, macro_stress_matrix):
        """
        Calculates the effective stiffness tensor C_k = Sigma E^-1.

        Args:
            macro_deformation_matrix (np.array): 6x6 prescribed strain matrix.
            macro_stress_matrix (np.array): 6x6 resulting stress matrix.

        Returns:
            np.array: 6x6 effective elastic tensor.
        """
        try:
            # Invert the diagonal strain matrix to solve the linear system
            inverted_deformation = np.linalg.inv(macro_deformation_matrix)
        except np.linalg.LinAlgError:
            print("[KINEMATIC] [ERROR]: Macroscopic deformation matrix is singular and cannot be inverted.")
            return None

        # C_k = Sigma * E^-1
        effective_elastic_tensor_kinematic = np.dot(macro_stress_matrix, inverted_deformation)
        return effective_elastic_tensor_kinematic

    def get_kinematic_tensor_in_txt_formatted(self, vtu_files):
        """
        Computes the final tensor and exports a detailed report to a text file.

        Args:
            vtu_files (list): Paths to the 6 simulation result files.
        """
        print("-------------------------------------------------------------------------------------------")
        print("[KINEMATIC] [INFO]: Starting macroscopic tensor evaluation...")

        stress_matrix = self.generate_macro_stress_matrix(vtu_files)
        deformation_matrix = self.generate_macro_deformation_matrix()

        if stress_matrix is None or deformation_matrix is None:
            return

        effective_elastic_tensor_kinematic = self.compute_kinematic_effective_elastic_tensor(deformation_matrix, stress_matrix)

        if effective_elastic_tensor_kinematic is None:
            return

        # Ensures output directory exists
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

        with open(self.output_path, "w") as txt_file:
            # Macroscopic stress matrix
            txt_file.write("=" * 118 + "\n")
            txt_file.write(" " * 26 + "Macroscopic stress matrix Sigma for kinematic boundary conditions\n")
            txt_file.write("=" * 118 + "\n\n")
            for i in range(6):
                prefix = "Sigma =" if i == 2 else "        "
                row = " ".join([f"{stress_matrix[i, j]:>16.6e}" for j in range(6)])
                txt_file.write(f"{prefix} [ {row} ]\n")
            txt_file.write("\n\n")

            # Macroscopic deformation matrix
            txt_file.write("=" * 118 + "\n")
            txt_file.write(" " * 26 + "Macroscopic deformation matrix E for kinematic boundary conditions\n")
            txt_file.write("=" * 118 + "\n\n")
            for i in range(6):
                prefix = "E =     " if i == 2 else "        "
                row = " ".join([f"{deformation_matrix[i, j]:>16.6e}" for j in range(6)])
                txt_file.write(f"{prefix} [ {row} ]\n")
            txt_file.write("\n\n")

            # Resulting effective elastic tensor
            txt_file.write("=" * 118 + "\n")
            txt_file.write(" " * 18 + "Effective Elastic Tensor C_k (with dash) for kinematic boundary conditions\n")
            txt_file.write("=" * 118 + "\n\n")
            for i in range(6):
                prefix = "C =     " if i == 2 else "        "
                row = " ".join([f"{effective_elastic_tensor_kinematic[i, j]:>16.6e}" for j in range(6)])
                txt_file.write(f"{prefix} [ {row} ]\n")
            txt_file.write("\n\n")

            txt_file.write("-" * 118 + "\n")
            txt_file.write("Result computed using the following .vtu files:\n")
            for vtu_file in vtu_files:
                txt_file.write(f"- {vtu_file}\n")

        print(f"[KINEMATIC] [POST-PROCESSING]: Final tensor C_k saved to: {self.output_path}\n")