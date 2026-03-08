import numpy as np
import os
from Logic_classes.ConfigManager import ConfigManager
from Logic_classes.GeneralComputationClass import GeneralComputationClass


class GenerateStaticEffectiveElasticTensor:
    """
    Computes the macroscopic effective elastic tensor for static boundary conditions.

    This class assembles the macroscopic stress and strain matrices from simulation
    results and solves for the stiffness tensor C_s (with dash) using the relationship:
    Sigma = C_s epsilon

    In static boundary conditions, the stress matrix is prescribed and the deformation
    matrix is calculated via surface integration of the displacement fields
    """

    def __init__(self, config_file):
        self.config = ConfigManager(config_file)
        self.cube_edge_length_L = self.config.get_cube_edge_length_L()
        self.output_path = self.config.get_output_dir_of_file_with_tensor_static_bc()
        self.alpha = float(self.config.get_stress_parameter_alpha())

        # Initialize the universal mesh processor for surface integration
        self.mesh_processor = GeneralComputationClass(self.cube_edge_length_L)

    def generate_macro_deformation_matrix(self, vtu_files):
        """
        Assembles the macroscopic deformation matrix E from .vtu result files.

        Each column represents the volume averaged strain vector integrated
        from one of the six independent loading cases.

        Args:
            vtu_files (list): Paths to the 6 simulation result files.

        Returns:
            np.array: A 6x6 macroscopic deformation matrix.
        """
        macro_deformation_matrix = np.zeros((6, 6))
        for i, vtu_file in enumerate(vtu_files):
            # Compute the 3x3 average strain tensor via surface integration
            partial_deformation_tensor = self.mesh_processor.compute_partial_deformation_tensor_for_one_file(vtu_file)

            if partial_deformation_tensor is not None:
                # Convert 3x3 tensor to 6x1 Voigt vector and insert as column
                voigt_vector = self.mesh_processor.convert_partial_deformation_tensor_to_voigt(
                    partial_deformation_tensor)
                macro_deformation_matrix[:, i] = voigt_vector
            else:
                print(f"[STATIC] [ERROR]: Failed to integrate deformation for {vtu_file}")
                return None
        return macro_deformation_matrix

    def generate_macro_stress_matrix(self):
        """
        Assembles the prescribed macroscopic stress matrix big Sigma.

        Returns:
            np.array: A 6x6 diagonal matrix, diagonal containing the alpha parameter.
        """
        return self.alpha * np.eye(6)

    def compute_static_effective_elastic_tensor(self, macro_deformation_matrix, macro_stress_matrix):
        """
        Calculates the effective stiffness tensor $C_s = \Sigma \cdot E^{-1}$.

        Args:
            macro_deformation_matrix (np.array): 6x6 resulting strain matrix.
            macro_stress_matrix (np.array): 6x6 prescribed stress matrix.

        Returns:
            np.array: 6x6 effective elastic tensor.
        """
        try:
            # Inverts the deformation matrix to solve the linear system
            inverted_deformation = np.linalg.inv(macro_deformation_matrix)
        except np.linalg.LinAlgError:
            print("[STATIC] [ERROR]: Macroscopic deformation matrix is singular and cannot be inverted.")
            return None

        # C_s = Sigma * E^-1
        return np.dot(macro_stress_matrix, inverted_deformation)

    def get_static_tensor_in_txt_formatted(self, vtu_files):
        """
        Computes the final tensor and exports a detailed report to a text file.

        Args:
            vtu_files (list): Paths to the 6 simulation result files.
        """
        print("-------------------------------------------------------------------------------------------")
        print("[STATIC] [INFO]: Starting macroscopic tensor evaluation...")

        stress_matrix = self.generate_macro_stress_matrix()
        deformation_matrix = self.generate_macro_deformation_matrix(vtu_files)

        if deformation_matrix is None:
            return

        effective_elastic_tensor_static = self.compute_static_effective_elastic_tensor(deformation_matrix, stress_matrix)

        if effective_elastic_tensor_static is None:
            return

        # Ensures output directory exists
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

        with open(self.output_path, "w") as txt_file:
            # Macroscopic stress matrix
            txt_file.write("=" * 118 + "\n")
            txt_file.write(" " * 26 + "Macroscopic stress matrix Sigma for static boundary conditions\n")
            txt_file.write("=" * 118 + "\n\n")
            for i in range(6):
                prefix = "Sigma =" if i == 2 else "        "
                row = " ".join([f"{stress_matrix[i, j]:>16.6e}" for j in range(6)])
                txt_file.write(f"{prefix} [ {row} ]\n")
            txt_file.write("\n\n")

            # Macroscopic deformation matrix
            txt_file.write("=" * 118 + "\n")
            txt_file.write(" " * 26 + "Macroscopic deformation matrix E for static boundary conditions\n")
            txt_file.write("=" * 118 + "\n\n")
            for i in range(6):
                prefix = "E =     " if i == 2 else "        "
                row = " ".join([f"{deformation_matrix[i, j]:>16.6e}" for j in range(6)])
                txt_file.write(f"{prefix} [ {row} ]\n")
            txt_file.write("\n\n")

            # Resulting effective elastic tensor C_s
            txt_file.write("=" * 118 + "\n")
            txt_file.write(" " * 18 + "Effective elastic tensor C_s (with dash) for static boundary conditions\n")
            txt_file.write("=" * 118 + "\n\n")
            for i in range(6):
                prefix = "C =     " if i == 2 else "        "
                row = " ".join([f"{effective_elastic_tensor_static[i, j]:>16.6e}" for j in range(6)])
                txt_file.write(f"{prefix} [ {row} ]\n")
            txt_file.write("\n\n")

            txt_file.write("-" * 118 + "\n")
            txt_file.write("Result computed using the following .vtu files:\n")
            for vtu_file in vtu_files:
                txt_file.write(f"- {vtu_file}\n")

        print(f"[STATIC] [POST-PROCESSING]: Final tensor C_s saved to: {self.output_path}\n")