"""Example to generate kicad clearance rules from a human-readable table."""
import kiclearance as kc
import os

if __name__ == '__main__':
    project_folder = os.path.dirname(os.path.realpath(__file__))

    table_name = None
    project_name = None

    # Run script
    table_file = kc.look_for_clearance_table_file(project_folder, table_name)
    project_name = kc.look_for_kicad_project(project_folder, project_name)
    table_data = kc.parse_excel_table(table_file)
    kc.write_design_rule_file(table_data, project_folder, project_name)
