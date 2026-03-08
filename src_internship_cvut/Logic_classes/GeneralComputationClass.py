import pyvista as pv
import numpy as np


class GeneralComputationClass:
    """
    A class for processing .vtu files and calculating partial stress and strain tensors

    It uses surface integration over the external boundaries of a Representative
    Volume Element (RVE) to compute macroscopic properties. This serves as a
    universal calculator independent of specific boundary condition types
    """

    def __init__(self, cube_edge_length_L):
        self.cube_edge_length_L = cube_edge_length_L

    def compute_volume_of_RVE(self):
        return self.cube_edge_length_L ** 3

    def compute_partial_deformation_tensor(self, displacement_field, normals, areas):
        """
        Computes the average strain tensor via surface integration of displacements.

        The formula used is:
        \bar{\varepsilon} = \frac{1}{V} \int_{\partial V} \frac{1}{2} (u \otimes n + n \otimes u) dS

        Args:
            displacement_field (np.array): Array of displacement vectors at cell centers.
            normals (np.array): Array of outward unit normal vectors.
            areas (np.array): Array of surface area magnitudes for each cell.

        Returns:
            np.array: A 3x3 symmetric deformation tensor.
        """
        volume_RVE = self.compute_volume_of_RVE()
        partial_deformation_tensor = np.zeros((3, 3))
        N = len(areas)

        for k in range(N):
            u_k = displacement_field[k]
            nu_k = normals[k]
            delta_S_k = areas[k]
            # Symmetric part of the tensor product (outer product)
            partial_deformation_tensor += 0.5 * (np.outer(u_k, nu_k) + np.outer(nu_k, u_k)) * delta_S_k

        # Normalize by RVE volume
        partial_deformation_tensor = (1 / volume_RVE) * partial_deformation_tensor
        return partial_deformation_tensor

    def compute_partial_stress_tensor(self, stress_field, normals, positions_of_centers, areas):
        """
        Computes the average stress tensor via surface integration of tractions.

        The formula used is:
        \bar{\sigma} = \frac{1}{V} \int_{\partial V} \frac{1}{2} (t \otimes x + x \otimes t) dS
        where t = \sigma \cdot n is the traction vector and x is the position vector

        Args:
            stress_field (np.array): Array of stress vectors (9x1) at cell centers
            normals (np.array): Array of outward unit normal vectors
            positions_of_centers (np.array): Spatial coordinates of the cell centers
            areas (np.array): Array of surface area magnitudes

        Returns:
            np.array: A 3x3 symmetric stress tensor.
        """
        volume_RVE = self.compute_volume_of_RVE()
        partial_stress_tensor = np.zeros((3, 3))
        N = len(areas)

        for k in range(N):
            # Reshape from 9x1 vector to 3x3 stress matrix
            sigma_k = stress_field[k].reshape((3, 3))
            nu_k = normals[k]
            x_k = positions_of_centers[k]
            delta_S_k = areas[k]

            # Calculate the traction vector
            traction_k = np.dot(sigma_k, nu_k)

            # Symmetric part of the tensor product with the position vector
            partial_stress_tensor += 0.5 * (np.outer(traction_k, x_k) + np.outer(x_k, traction_k)) * delta_S_k

        # Normalize by RVE volume
        partial_stress_tensor = (1 / volume_RVE) * partial_stress_tensor
        return partial_stress_tensor

    def generate_mesh_data_in_one_file(self, vtu_file):
        """
        Extracts necessary geometric and physical data from a single .vtu file.

        Args:
            vtu_file (str): Path to the VTK Unstructured Grid file.

        Returns:
            tuple: (displacements, stresses, normals, center_positions, areas)
        """
        try:
            mesh = pv.read(vtu_file)
            cleaned = mesh.clean()
            surface = cleaned.extract_surface()

            # Computes normals and cell metrics
            surface_with_normals = surface.compute_normals(cell_normals=True, point_normals=False, flip_normals=True)
            surface_with_sizes = surface_with_normals.compute_cell_sizes()
            surface_cell_data = surface_with_sizes.point_data_to_cell_data()

            # Extracts data arrays
            displacement_field = surface_cell_data.cell_data['displacement']
            stress_field = surface_cell_data.cell_data['stress']
            normals = surface_with_normals.cell_data['Normals']
            positions_of_centers = surface_with_sizes.cell_centers().points
            areas = surface_with_sizes.cell_data['Area']

            return displacement_field, stress_field, normals, positions_of_centers, areas

        except FileNotFoundError:
            return None, None, None, None, None

    def get_amount_of_surface_elements(self, vtu_file):
        _, _, _, _, areas = self.generate_mesh_data_in_one_file(vtu_file)
        if areas is not None:
            return len(areas)
        else:
            return None

    def compute_partial_deformation_tensor_for_one_file(self, vtu_file):
        displacement_field, _, normals, _, areas = self.generate_mesh_data_in_one_file(vtu_file)
        if displacement_field is not None and normals is not None and areas is not None:
            partial_deformation_tensor = self.compute_partial_deformation_tensor(displacement_field, normals, areas)
            return partial_deformation_tensor
        else:
            return None

    def compute_partial_stress_tensor_for_one_file(self, vtu_file):
        _, stress_field, normals, positions_of_centers, areas = self.generate_mesh_data_in_one_file(vtu_file)
        if stress_field is not None and normals is not None and positions_of_centers is not None and areas is not None:
            partial_stress_tensor = self.compute_partial_stress_tensor(stress_field, normals, positions_of_centers,
                                                                       areas)
            return partial_stress_tensor
        else:
            return None

    def convert_partial_stress_tensor_to_voigt(self, partial_stress_tensor):
        """
        Converts a 3x3 stress tensor into a 6x1 Voigt notation vector.

        Order: [sigma_11, sigma_22, sigma_33, sigma_23, sigma_13, sigma_12]
        """
        voigt_vector_stress = np.array([
            partial_stress_tensor[0, 0],
            partial_stress_tensor[1, 1],
            partial_stress_tensor[2, 2],
            partial_stress_tensor[1, 2],
            partial_stress_tensor[0, 2],
            partial_stress_tensor[0, 1]
        ])
        return voigt_vector_stress

    def convert_partial_deformation_tensor_to_voigt(self, partial_deformation_tensor):
        """
        Converts a 3x3 strain tensor into a 6x1 Voigt notation vector.

        Note: Shear components are multiplied by 2 to represent engineering strain (gamma_ij).
        Order: [eps_11, eps_22, eps_33, gamma_23, gamma_13, gamma_12]
        """
        voigt_vector_deformation = np.array([
            partial_deformation_tensor[0, 0],
            partial_deformation_tensor[1, 1],
            partial_deformation_tensor[2, 2],
            2.0 * partial_deformation_tensor[1, 2],
            2.0 * partial_deformation_tensor[0, 2],
            2.0 * partial_deformation_tensor[0, 1]
        ])
        return voigt_vector_deformation