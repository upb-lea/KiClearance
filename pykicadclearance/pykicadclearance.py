import pandas as pd
import os
import importlib.util
import getopt
import sys
import numpy as np


def write_design_rule_file(table_data, folder, project_name, factor_inner_layers: float = 0.5,
                           min_track_distance: float = 0.15):
    """
    Write the data to the design rule file. Creates the file if necessary.

    :param table_data:
    :param project_name:
    :param factor_inner_layers: factor for inner layers distance. Default is 0.5
    :type factor_inner_layers: float

    """
    start_comment = "# Auto-Generated for voltage distances - start"
    end_comment = "# Auto-Generated - end"

    # Create text from table_data
    new_lines = [start_comment]
    for data in table_data:
        first_net_name = data[0]
        second_net_name = data[1]
        distance = data[2]
        if distance <= min_track_distance:
            # This is the minimum distance between two tracks for both, inner and outer layers.
            new_lines.append(f"(rule {first_net_name}_{second_net_name}_inner_outer")
            new_lines.append(f"\t(constraint clearance (min \"{min_track_distance}mm\"))")
            new_lines.append(
                f"\t(condition \"A.NetClass == '{first_net_name}' && B.NetClass == '{second_net_name}'\"))")
        elif distance < 2 * min_track_distance:
            new_lines.append(f"(rule {first_net_name}_{second_net_name}_outer")
            new_lines.append(f"\t(layer outer)")
            new_lines.append(f"\t(constraint clearance (min \"{distance}mm\"))")
            new_lines.append(f"\t(condition \"A.NetClass == '{first_net_name}' && B.NetClass == '{second_net_name}'\"))")
            new_lines.append(f"(rule {first_net_name}_{second_net_name}_inner")
            new_lines.append(f"\t(layer inner)")
            new_lines.append(f"\t(constraint clearance (min \"{min_track_distance}mm\"))")
            new_lines.append(f"\t(condition \"A.NetClass == '{first_net_name}' && B.NetClass == '{second_net_name}'\"))")
        elif distance >= 2 * min_track_distance:
            new_lines.append(f"(rule {first_net_name}_{second_net_name}_outer")
            new_lines.append(f"\t(layer outer)")
            new_lines.append(f"\t(constraint clearance (min \"{distance}mm\"))")
            new_lines.append(f"\t(condition \"A.NetClass == '{first_net_name}' && B.NetClass == '{second_net_name}'\"))")
            new_lines.append(f"(rule {first_net_name}_{second_net_name}_inner")
            new_lines.append(f"\t(layer inner)")
            new_lines.append(f"\t(constraint clearance (min \"{distance * factor_inner_layers}mm\"))")
            new_lines.append(f"\t(condition \"A.NetClass == '{first_net_name}' && B.NetClass == '{second_net_name}'\"))")

    new_lines.append(end_comment)

    # Add text to file
    dru_file = os.path.join(folder, f"{project_name}.kicad_dru")

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


def parse_excel_table(table_file):
    """
    Parse data from table.

    Data will be stored in the following format:
    List of lists: [[Net_1, Net_2, distance], [Net_1, Net_3, distance], ...]
    """
    if table_file.endswith(".ods"):
        # Check if odfpy is installed
        odfpy = importlib.util.find_spec("odf")
        if odfpy is None:
            raise Exception("The python package odfpy is not installed. This is needed in order to parse .ods files. Use pip or conda to install odfpy.")

    df = pd.read_excel(table_file, index_col=0)
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
            value = column[k]
            if np.isnan(value):
                raise Exception("A nan value is found. Is the given table a upper triangular matrix or a symmetrical matrix?")
            data.append([column_name, row_name, value])

    return data


def look_for_table_file(folder, file_name=None):
    """Tries to find the table file in the given folder.
    This file has either the default name 'clearance' or a name given
    by the user. The file has to be: .ods, .xls or .xlsx.
    """
    if not os.path.isdir(folder):
        raise Exception(f"Folder {folder} not found.")

    # Check if file is ods or Excel file
    if file_name is not None and \
            not (file_name.endswith(".ods") or file_name.endswith(".xls") or file_name.endswith(".xlsx")):
        raise Exception("Given file must have one of the following endings: .ods, .xls, .xlsx")

    # Get file from folder
    for file in os.listdir(folder):
        if file in ["clearance.ods", "clearance.xls", "clearance.xlsx"] or file == file_name:
            if file.startswith("~$"):
                raise Exception("Please close the clearance table file and re-run the script.")
            return os.path.join(folder, file)

    raise Exception(f"Clearance table file was not found in folder {folder}.")


def look_for_kicad_project(folder, project_name=None):
    """Tries to find the kicad project automatically if no project_name is given.
    This is done by searching for kicad_pro files.
    """
    if not os.path.isdir(folder):
        raise Exception(f"Folder {folder} not found.")

    if project_name is not None:
        for file in os.listdir(folder):
            if file == project_name + ".kicad_pro":
                return project_name
        raise Exception(f"{project_name}.kicad_pro not found in folder {folder}")
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


def usage():
    text = \
        "The following arguments are possible:\n\
            -h, --help: Prints this information,\n\
            -f, --project_folder (Optional): Path to the folder in which the project is located. Default: Folder in which this python script is located.\n\
            -n, --project_name (Optional): Name of the kicad project (file prefix). Default: Script will look for a file with .kicad_pro in the set folder.\n\
            -t, --table_file (Optional): Name (and ending) of the file containing the distance values. Default: Script will look for a file which is named clearance."
    print(text)


if __name__ == "__main__":
    project_folder = os.path.dirname(os.path.realpath(__file__))
    table_name = None
    project_name = None

    # Parse command line arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hf:n:t:", ["help", "project_folder=", "project_name=", "table_file="])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-f", "--project_folder"):
            project_folder = a
        elif o in ("-n", "--project_name"):
            project_name = a
        elif o in ("-t", "--table_file_name"):
            table_name = a

    # Run script
    table_file = look_for_table_file(project_folder, table_name)
    project_name = look_for_kicad_project(project_folder, project_name)
    table_data = parse_excel_table(table_file)
    write_design_rule_file(table_data, project_folder, project_name)