import pyvista as pv
import numpy as np


# ==============================================================================================
# Používané funkce pro výpočet makroskopické deformace a napětí na RVE podle teoretických vzorců
# ==============================================================================================

def compute_macro_deformation_on_RVE(displacement_field, normals, areas, volume_RVE):
    """
    Tato funkce vypočítá makroskopickou deformaci podle teoretického vzorce:
    <epsilon_ij> = (1/V) * sum_{k=1}^{N} [ 0.5 * (u_i*nu_j + u_j*nu_i)_k * Delta_S_k ]
    """
    epsilon_macro_tensor = np.zeros((3, 3))
    N = len(areas)

    for k in range(N):
        u_k = displacement_field[k]
        nu_k = normals[k]
        delta_S_k = areas[k]

        # Symetrická část tenzorového součinu v NumPy (vnější součin)
        epsilon_macro_tensor += 0.5 * (np.outer(u_k, nu_k) + np.outer(nu_k, u_k)) * delta_S_k

    # Vydělení celkovým objemem RVE
    epsilon_macro_tensor = (1 / volume_RVE) * epsilon_macro_tensor
    return -epsilon_macro_tensor


def compute_macro_stress_on_RVE(stress_field, normals, positions_of_centers, areas, volume_RVE):
    """
    Tato funkce vypočítá makroskopické napětí podle teoretického vzorce:
    <sigma_ij> = (1/V) * sum_{k=1}^{N} [ 0.5 * (t_i*x_j + t_j*x_i)_k * Delta_S_k ]
    kde t_k = sigma_k * nu_k je vektor trakce.
    """
    sigma_macro_tensor = np.zeros((3, 3))
    N = len(areas)

    for k in range(N):
        # Převod z vektoru 9x1 na 3x3 matici pro tenzor napětí
        sigma_k = stress_field[k].reshape((3, 3))
        nu_k = normals[k]
        x_k = positions_of_centers[k]
        delta_S_k = areas[k]

        # Výpočet vektoru trakce
        traction_k = np.dot(sigma_k, nu_k)

        # Symetrická část tenzorového součinu s polohovým vektorem
        sigma_macro_tensor += 0.5 * (np.outer(traction_k, x_k) + np.outer(x_k, traction_k)) * delta_S_k

    # Vydělení celkovým objemem RVE
    sigma_macro_tensor = (1 / volume_RVE) * sigma_macro_tensor
    return -sigma_macro_tensor


# ===================================================================================
# Načítání dat z .vtu souborů a jejich předzpracování pro výpočty
# ===================================================================================

def load_mesh_data_in_one_file(vtu_file):
    try:
        mesh = pv.read(vtu_file)
        cleaned = mesh.clean()
        surface = cleaned.extract_surface()
        surface_with_normals = surface.compute_normals(cell_normals=True, point_normals=False)
        surface_with_sizes = surface_with_normals.compute_cell_sizes()
        surface_cell_data = surface_with_sizes.point_data_to_cell_data()

        displacement_field = surface_cell_data.cell_data['displacement']
        stress_field = surface_cell_data.cell_data['stress']
        normals = surface_with_normals.cell_data['Normals']
        positions_of_centers = surface_with_sizes.cell_centers().points
        areas = surface_with_sizes.cell_data['Area']

        return displacement_field, stress_field, normals, positions_of_centers, areas

    except FileNotFoundError:
        print("\n---------------------------------------------------")
        print(f"POZOR: Soubor {vtu_file} nebyl nalezen. Přeskakuji...")
        print("\n---------------------------------------------------")
        return None, None, None, None, None

def get_amount_of_boundary_elements(vtu_file):
    _, _, _, _, areas = load_mesh_data_in_one_file(vtu_file)
    if areas is not None:
        return len(areas)
    else:
        return None

# ===================================================================================
# Generování makroskopických tenzorů pro jednotlivé soubory a jejich zpracování
# ===================================================================================

def generate_macro_deformation_for_one_file(vtu_file, volume_RVE):
    displacement_field, _, normals, _, areas = load_mesh_data_in_one_file(vtu_file)
    if displacement_field is not None and normals is not None and areas is not None:
        epsilon_final = compute_macro_deformation_on_RVE(displacement_field, normals, areas, volume_RVE)
        print(f"\nMakroskopický tenzor deformace pro {vtu_file}:")
        print(epsilon_final)
        return epsilon_final
    else:
        return None

def generate_macro_stress_for_one_file(vtu_file, volume_RVE):
    _, stress_field, normals, positions_of_centers, areas = load_mesh_data_in_one_file(vtu_file)

    if stress_field is not None and normals is not None and positions_of_centers is not None and areas is not None:
        sigma_macro_tensor = compute_macro_stress_on_RVE(stress_field, normals, positions_of_centers, areas, volume_RVE)
        print(f"\nMakroskopický tenzor napětí pro {vtu_file}:")
        print(sigma_macro_tensor)
        return sigma_macro_tensor
    else:
        return None

# ===================================================================================
# Zobrazení informací o zpracovávaných souborech a celkovém průběhu zpracování
# ===================================================================================

def generate_macro_deformation_for_all_files(vtu_files, volume_RVE):
    print("\n=====================================================================")
    print(f"Zpracovávají se následující .vtu soubory pro makro deformace:\n {vtu_files}")
    print(f"Objem RVE použitý pro výpočty: {volume_RVE}")
    print(
        f" Počet hraničních elementů: {get_amount_of_boundary_elements(vtu_files[0])} (pro první soubor, ostatní se předpokládají podobné)")
    print("=====================================================================")

    for vtu_file in vtu_files:
        generate_macro_deformation_for_one_file(vtu_file, volume_RVE)

    print("\n---------------------------------------------------")
    print(f"Bylo zpracováno celkem {len(vtu_files)} zadaných souborů.")
    print("---------------------------------------------------")


def generate_macro_stress_for_all_files(vtu_files, volume_RVE):
    print("\n=====================================================================")
    print(f"Zpracovávají se následující .vtu soubory pro makro napětí:\n {vtu_files}")
    print(f"Objem RVE použitý pro výpočty: {volume_RVE}")
    print(f" Počet hraničních elementů {get_amount_of_boundary_elements(vtu_files[0])} (pro první soubor, ostatní se předpokládají podobné)")
    print("=====================================================================")

    for vtu_file in vtu_files:
        generate_macro_stress_for_one_file(vtu_file, volume_RVE)

    print("\n---------------------------------------------------")
    print(f"Bylo zpracováno celkem {len(vtu_files)} zadaných souborů.")
    print("---------------------------------------------------")