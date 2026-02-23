import GenerateMacroFields
def main():
    vtu_files = [
        "mechanics-000000_0.vtu",
        "mechanics-000000_1.vtu",
        "mechanics-000000_2.vtu",
        "mechanics-000000_3.vtu",
        "mechanics-000000_4.vtu",
        "mechanics-000000_5.vtu"
    ]
    volume_RVE = 1
    GenerateMacroFields.generate_macro_deformation_for_all_files(vtu_files, volume_RVE)
    GenerateMacroFields.generate_macro_stress_for_all_files(vtu_files, volume_RVE)

if __name__ == "__main__":
    main()
