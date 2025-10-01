"""Generate clearance rules for kicad from a human-readable table."""
# python libraries
import os
import importlib.util
import yaml

# 3rd party libraries
import numpy as np
import pandas as pd


def write_design_rule_file(clearance_table_data: list, folder: str, kicad_project_name: str,
                           factor_inner_layers: float | None = None, min_track_distance: float | None = None) -> None:
    """
    Write the rules to the design rule file (your_project.kicad_dru).

    A reduction factor for the inner layers can be applied, as there is less pollution, typically inner clearance can be reduced.

    :param clearance_table_data: clearance table data
    :type clearance_table_data: list
    :param kicad_project_name: kicad project name
    :type kicad_project_name: str
    :param factor_inner_layers: distance factor for inner layers distance. Default is 1.0
    :type factor_inner_layers: float
    :param min_track_distance: minimum track distance in mm
    :type min_track_distance: float
    :param folder: directory
    :type folder: str

    """
    if factor_inner_layers is None:
        factor_inner_layers = 1.0
    if min_track_distance is None:
        min_track_distance = 0.15

    start_comment = "# Auto-Generated for voltage distances - start"
    end_comment = "# Auto-Generated - end"

    # Create text from table_data
    new_lines = [start_comment]
    for data in clearance_table_data:
        first_net_name = data[0]
        second_net_name = data[1]
        distance = data[2]
        if distance <= min_track_distance:
            # This is the minimum distance between two tracks for both, inner and outer layers.
            new_lines.append(f"(rule {first_net_name}_{second_net_name}_min_self_distance")
            new_lines.append(f"\t(constraint clearance (min \"{min_track_distance}mm\"))")
            new_lines.append(
                f"\t(condition \"A.NetClass == '{first_net_name}' && B.NetClass == '{second_net_name}'\"))")
        elif distance < 2 * min_track_distance:
            # simplify rules in case of factor for inner layers is 1
            if factor_inner_layers == 1:
                # no distinction between inner and outer layers
                new_lines.append(f"(rule {first_net_name}_{second_net_name}")
                new_lines.append(f"\t(constraint clearance (min \"{distance}mm\"))")
                new_lines.append(f"\t(condition \"A.NetClass == '{first_net_name}' && B.NetClass == '{second_net_name}'\"))")
            else:
                # distinguish between inner and outer layers
                new_lines.append(f"(rule {first_net_name}_{second_net_name}_outer")
                new_lines.append("\t(layer outer)")
                new_lines.append(f"\t(constraint clearance (min \"{distance}mm\"))")
                new_lines.append(f"\t(condition \"A.NetClass == '{first_net_name}' && B.NetClass == '{second_net_name}'\"))")
                new_lines.append(f"(rule {first_net_name}_{second_net_name}_inner")
                new_lines.append("\t(layer inner)")
                new_lines.append(f"\t(constraint clearance (min \"{min_track_distance}mm\"))")
                new_lines.append(f"\t(condition \"A.NetClass == '{first_net_name}' && B.NetClass == '{second_net_name}'\"))")

        elif distance >= 2 * min_track_distance:
            # simplify rules in case of factor for inner layers is 1
            if factor_inner_layers == 1:
                # no distinction between inner and outer layers
                new_lines.append(f"(rule {first_net_name}_{second_net_name}")
                new_lines.append(f"\t(constraint clearance (min \"{distance}mm\"))")
                new_lines.append(f"\t(condition \"A.NetClass == '{first_net_name}' && B.NetClass == '{second_net_name}'\"))")
            else:
                # distinguish between inner and outer layers
                new_lines.append(f"(rule {first_net_name}_{second_net_name}_outer")
                new_lines.append("\t(layer outer)")
                new_lines.append(f"\t(constraint clearance (min \"{distance}mm\"))")
                new_lines.append(f"\t(condition \"A.NetClass == '{first_net_name}' && B.NetClass == '{second_net_name}'\"))")
                new_lines.append(f"(rule {first_net_name}_{second_net_name}_inner")
                new_lines.append("\t(layer inner)")
                new_lines.append(f"\t(constraint clearance (min \"{distance * factor_inner_layers}mm\"))")
                new_lines.append(f"\t(condition \"A.NetClass == '{first_net_name}' && B.NetClass == '{second_net_name}'\"))")

    new_lines.append(end_comment)

    # Add text to file
    dru_file = os.path.join(folder, f"{kicad_project_name}.kicad_dru")

    text = ""
    if os.path.exists(dru_file):
        with open(dru_file, "r") as fd:
            lines = fd.read().splitlines()

        # Search for the voltage_distances part in the file
        line_start_index = -1
        line_end_index = -1
        for index, line in enumerate(lines):
            if line == start_comment:
                line_start_index = index
            elif line == end_comment:
                line_end_index = index

        if line_start_index == -1 or line_end_index == -1:
            # Append the text at end of file
            lines = lines + new_lines
        else:
            # Remove old lines and add new ones
            lines = lines[:line_start_index] + new_lines + lines[line_end_index + 1:]
    else:
        text = "(version 1)\n"
        lines = new_lines

    for new_line in lines:
        text += new_line + "\n"

    with open(dru_file, "w+") as fd:
        fd.write(text)


def parse_excel_table(clearance_table_file: str) -> list:
    """
    Parse clearance data from the given clearance table file.

    Data will be stored in the following format:
    List of lists: [[Net_1, Net_2, distance], [Net_1, Net_3, distance], ...]

    :param clearance_table_file: clearance table file (.xls, .ods, .csv)
    :type clearance_table_file: str
    """
    if clearance_table_file.endswith(".ods"):
        # Check if odfpy is installed
        odfpy = importlib.util.find_spec("odf")
        if odfpy is None:
            raise Exception("The python package odfpy is not installed. This is needed in order to parse .ods files. Use pip or conda to install odfpy.")

    df = pd.read_excel(clearance_table_file, index_col=0)
    data = []

    # Check if table is in correct format
    headers = list(df.columns)
    row_names = list(df.index.values)

    if headers != row_names:
        raise Exception("The row names and column names have to be in the same order.")

    for index, column_name in enumerate(headers):
        column = df[column_name]
        for k in range(index + 1):
            row_name = headers[k]
            value = column.iloc[k]
            if np.isnan(value):
                raise Exception("A nan value is found. Is the given table a upper triangular matrix or a symmetrical matrix?")
            data.append([column_name, row_name, value])

    return data


def look_for_clearance_table_file(folder: str, clearance_table_file_name: str | None = None) -> str | None:
    """
    Try to find the clearance table file in the given folder.

    This file has either the default name 'clearance' or a name given
    by the user. The file has to be: .ods, .xls or .xlsx.

    :param folder: folder name to look for the clearance table file
    :type folder: str
    :param clearance_table_file_name: clearance table file name
    :type clearance_table_file_name: str
    """
    if not os.path.isdir(folder):
        raise Exception(f"Folder {folder} not found.")

    # Check if file is ods or Excel file
    if clearance_table_file_name is not None and \
            not (clearance_table_file_name.endswith(".ods") or clearance_table_file_name.endswith(".xls") or clearance_table_file_name.endswith(".xlsx")):
        raise Exception("Given file must have one of the following endings: .ods, .xls, .xlsx")

    # Get file from folder
    for file in os.listdir(folder):
        if file in ["clearance.ods", "clearance.xls", "clearance.xlsx"] or file == clearance_table_file_name:
            if file.startswith("~$"):
                raise Exception("Please close the clearance table file and re-run the script.")
            return os.path.join(folder, file)
    # no file found: message and return None
    print(f"Clearance table file was not found in folder {folder}.")
    return None


def look_for_kicad_project(folder: str, kicad_project_name: str | None = None) -> str:
    """
    Try to find the kicad project automatically if no project_name is given.

    This is done by searching for kicad_pro files.
    :param folder: folder of the kicad project
    :type folder: str
    :param kicad_project_name: Kicad project name, optional
    :type kicad_project_name: str
    """
    if not os.path.isdir(folder):
        raise Exception(f"Folder {folder} not found.")

    if kicad_project_name is not None:
        for file in os.listdir(folder):
            if file == kicad_project_name + ".kicad_pro":
                return kicad_project_name
        raise Exception(f"{kicad_project_name}.kicad_pro not found in folder {folder}")
    else:
        files = []
        for file in os.listdir(folder):
            if file.endswith(".kicad_pro"):
                files.append(file)
        if len(files) == 0:
            raise Exception(f"No kicad project found in {folder}.")
        if len(files) > 1:
            raise Exception(f"There are multiple kicad_projects found in {folder}. Please specify one project.")
        else:
            return files[0].split(".")[0]

def update_net_classes_from_kicad_project_to_clearance_table_file(kicad_project_name: str, folder: str, clearance_table_file: str | None) -> str:
    """
    Read the net class names from the kicad project and update the labels in the clearance table file.

    In case of no clearance file is given as parameter, a new one is generated.
    All fields are filled with default values. These need to be added.
    :param kicad_project_name: kicad project name
    :type kicad_project_name: str
    :param clearance_table_file: name of the clearance table file
    :type clearance_table_file: str
    :param folder: kicad project folder name
    :type folder: str
    :return: clearance table file path
    :rtype: str
    """
    # default values to fill new table entries
    distance_to_default = 20
    distance_all_other_classes = 5
    self_to_self_distance = 0.15

    # Read net_classes from project file
    with open(kicad_project_name + ".kicad_pro", 'r') as stream:
        data_loaded = yaml.safe_load(stream)

    # check for multiple assigned net classes to nets
    net_class_assignments = data_loaded["net_settings"]["netclass_assignments"]
    error_net_name_net_classes_list = []
    for net_name, net_class_assignment in net_class_assignments.items():
        if len(net_class_assignment) > 1:
            error_net_name_net_classes_list.append((net_name, net_class_assignment))

    if error_net_name_net_classes_list:
        error_message = "The following nets have multiple assignments: \n"
        for net_name_error, net_class_assignment_error in error_net_name_net_classes_list:
            error_message += f" * '{net_name_error}' has multiple net classes assigned: {net_class_assignment_error}\n"
        raise ValueError(error_message)

    net_classes = [d['name'] for d in data_loaded["net_settings"]["classes"]]

    if net_classes.count("Default") < 1:
        raise Exception("No net class named Default in project. Please define it")

    # Read existing table or create a new one
    if clearance_table_file is not None:
        # read existing clearance table file
        old_clearance_table = pd.read_excel(clearance_table_file, index_col=0)
    else:
        # new_or_updated_clearance_table_file is None: generate a new clearance table file
        old_clearance_table = pd.DataFrame(columns=["Default"], data=pd.Series([self_to_self_distance], index=["Default"]), dtype=np.float64)
        clearance_table_file = os.path.join(folder, "clearance.ods")
    old_headers = list(old_clearance_table.columns)

    new_clearance_table = pd.DataFrame(columns=net_classes, index=net_classes, dtype=np.float64)

    is_message_table_changes: bool = False

    for _, column_name in enumerate(net_classes):
        for _, row_name in enumerate(net_classes[net_classes.index(column_name):]):
            # check if values exist in the table and copy it to the new table
            if old_headers.count(column_name) > 0 and old_headers.count(row_name) > 0:
                if np.isnan(old_clearance_table.at[column_name, row_name]):
                    new_clearance_table.at[column_name, row_name] = old_clearance_table.at[row_name, column_name]
                else:
                    new_clearance_table.at[column_name, row_name] = old_clearance_table.at[column_name, row_name]

            # no values in old table available: write the default space into the table
            else:
                # check if column/row is default net class
                if row_name == "Default" or column_name == "Default":
                    new_clearance_table.at[column_name, row_name] = distance_to_default

                # self-to-self distance
                elif row_name == column_name:
                    new_clearance_table.at[column_name, row_name] = self_to_self_distance

                # all other net classes
                else:
                    new_clearance_table.at[column_name, row_name] = distance_all_other_classes
                    is_message_table_changes = True

    new_clearance_table.to_excel(clearance_table_file)

    if is_message_table_changes:
        print("Clearance table file has been updated. Check table and adapt values.")
    else:
        print("In case of already existing clearance table, no updates have been made. In case of not existing clearance table, a new one was initialized.\n"
              f"    see file: {clearance_table_file}")
    return clearance_table_file


def usage():
    """For terminal usage."""
    text = \
        "The following arguments are possible:\n\
            -h, --help: Prints this information,\n\
            -f, --project_folder (Optional): Path to the folder in which the project is located. Default: Folder in which this python script is located.\n\
            -n, --project_name (Optional): Name of the kicad project (file prefix). Default: Script will look for a file with .kicad_pro in the set folder.\n\
            -t, --existing_clearance_table_file (Optional): Name (and ending) of the file containing the distance values. Default name: 'clearance'.\n\
            -i, --factor_inner_layers (Optional): Reduced factor for the inner layers. Default: 1.0\n\
            -d, --min_track_distance (Optional): minimum track distance between two tracks on the same potential. Default: 0.15 mm."

    print(text)


if __name__ == "__main__":
    pass
