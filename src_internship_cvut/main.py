import GenerateMacroFields
def main():
    vtu_files = [
        "mechanics-000000_tension_11.vtu",
        "mechanics-000000_tension_22.vtu",
        "mechanics-000000_tension_33.vtu",
        "mechanics-000000_shear_12.vtu",
        "mechanics-000000_shear_13.vtu",
        "mechanics-000000_shear_23.vtu"
    ]
    volume_RVE = 1
    GenerateMacroFields.generate_macro_deformation_for_all_files(vtu_files, volume_RVE)
    GenerateMacroFields.generate_macro_stress_for_all_files(vtu_files, volume_RVE)

if __name__ == "__main__":
    main()
