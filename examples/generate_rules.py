import pykicadclearance as pkc
import os

if __name__ == '__main__':
    project_folder = os.path.dirname(os.path.realpath(__file__))

    table_name = None
    project_name = None

    # Run script
    table_file = pkc.look_for_table_file(project_folder, table_name)
    project_name = pkc.look_for_kicad_project(project_folder, project_name)
    table_data = pkc.parse_excel_table(table_file)
    pkc.write_design_rule_file(table_data, project_folder, project_name)
