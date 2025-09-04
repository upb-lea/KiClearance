"""Unit and integration tests."""
# python libraries
import os

# 3rd party libraries
import pandas as pd

# own libraries
import kiclearance as kc

def compare_files(file_path_1: str, file_path_2: str) -> bool:
    """
    Compare two files.

    :param file_path_1: file path for file 1
    :type file_path_1: str
    :param file_path_2: file path for file 2
    :type file_path_2: str
    """
    with open(file_path_1, 'r') as file1, open(file_path_2, 'r') as file2:
        for line1, line2 in zip(file1, file2, strict=False):
            if line1.strip() != line2.strip():
                return False
        # Check if one file has more lines than the other
        if next(file1, None) is not None or next(file2, None) is not None:
            return False
        return True

def test_rules_factor_inner_layers_05():
    """Generate and test rule generation."""
    project_folder = os.path.dirname(os.path.realpath(__file__))

    table_name = None
    project_name = None

    # Run script
    table_file = kc.look_for_clearance_table_file(project_folder, table_name)
    project_name = kc.look_for_kicad_project(project_folder, project_name)
    table_data = kc.parse_excel_table(table_file)
    kc.write_design_rule_file(table_data, project_folder, project_name, factor_inner_layers=0.5)

    assert compare_files("tests/clearance_example.kicad_dru", "tests/results/clearance_example_factor_05.kicad_dru")

def test_rules_factor_inner_layers_1():
    """Generate and test rule generation."""
    project_folder = os.path.dirname(os.path.realpath(__file__))

    table_name = None
    project_name = None

    # Run script
    table_file = kc.look_for_clearance_table_file(project_folder, table_name)
    project_name = kc.look_for_kicad_project(project_folder, project_name)
    table_data = kc.parse_excel_table(table_file)
    kc.write_design_rule_file(table_data, project_folder, project_name, factor_inner_layers=1)

    assert compare_files("tests/clearance_example.kicad_dru", "tests/results/clearance_example_factor_1.kicad_dru")

def test_rules_no_table_exists():
    """Compare the initial generated clearance file."""
    project_folder = os.path.dirname(os.path.realpath(__file__))
    print(f"{project_folder=}")
    clearance_data_file = os.path.join(project_folder, "clearance.ods")
    if os.path.isfile(clearance_data_file):
        os.remove(clearance_data_file)

    table_name = None
    project_name = None

    # Run script
    table_file = kc.look_for_clearance_table_file(project_folder, table_name)
    project_name = kc.look_for_kicad_project(project_folder, project_name)
    print(f"{project_name=}")
    kc.update_net_classes_from_kicad_project_to_clearance_table_file(kicad_project_name=os.path.join(project_folder, project_name),
                                                                     clearance_table_file=table_file, folder=project_folder)

    new_generated_clearance_table = pd.read_excel(clearance_data_file, index_col=0)
    reference_clearance_table = pd.read_excel("tests/results/clearance_initial.ods", index_col=0)

    comparison = new_generated_clearance_table.compare(reference_clearance_table)
    assert comparison.empty
