"""Make KiClearance executable by the terminal."""
import os
import getopt
import sys
from kiclearance.kiclearance import *

project_folder = os.path.curdir
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
table_file = look_for_clearance_table_file(project_folder, table_name)
project_name = look_for_kicad_project(project_folder, project_name)
table_data = parse_excel_table(table_file)
write_design_rule_file(table_data, project_folder, project_name)
