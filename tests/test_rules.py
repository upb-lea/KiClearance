import os
import kiclearance as kc

def compare_files(file_path_1: str, file_path_2: str):
    with open(file_path_1, 'r') as file1, open(file_path_2, 'r') as file2:
        for line1, line2 in zip(file1, file2):
            if line1.strip() != line2.strip():
                return False
        # Check if one file has more lines than the other
        if next(file1, None) is not None or next(file2, None) is not None:
            return False
        return True

def test_rules():
    project_folder = os.path.dirname(os.path.realpath(__file__))

    table_name = None
    project_name = None

    # Run script
    table_file = kc.look_for_clearance_table_file(project_folder, table_name)
    project_name = kc.look_for_kicad_project(project_folder, project_name)
    table_data = kc.parse_excel_table(table_file)
    kc.write_design_rule_file(table_data, project_folder, project_name)

    assert compare_files("clearance_example.kicad_dru", "results/clearance_example.kicad_dru")



