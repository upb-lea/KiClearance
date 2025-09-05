.. sectnum::

Welcome to KiClearance
==================================================

This Python program converts a given table of voltage distances into KiCad design rules.

.. image:: docs/source/figures/overview.png


Installation
---------------------------------------
Install KiClearance directly from pyPI:

::

    pip install kiclearance


Usage
---------------------------------------

Define net classes in your KiCad project
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Add the net classes to each connection in the circuit diagram.

.. image:: docs/source/figures/net_class_directive_labels.png

Add the same net classes in the net classes of the PCB editor:
``KiCad PCB Editor``: ``File`` -> ``Board Setup`` -> ``Design Rules`` -> ``Net classes``

.. image:: docs/source/figures/board_setup.png

Run KiClearance to initially generate the clearance table
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Navigate to the project folder with the KiCad project. Open a terminal and execute :

::

    python -m kiclearance

Now a file ``clearance.ods`` is generated, which contains the human-readable clearance table.
As of now, the table has been generated using fantasy values.


Adapt the table 'clearance.ods/xls/csv' containing clearance distances
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update the table (clearance.ods/xls/csv) in your KiCad project directory with voltage clearances defined by your requirements (e.g. standards).

The table contains the distances from a potential to another in ``mm``. The same net distance is optional.

.. image:: docs/source/figures/table.png

Run KiClearance again, to generate the final set of rules for KiCad
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Navigate to the project folder with the KiCad project and the clearance.ods/.xls/.csv file. Open a terminal and execute :

::

    python -m kiclearance

Now a file ``yourprojectname.kicad_dru`` is generated, which contains the rule sets.

Open your KiCad project, the rule sets are now stored and you can start the routing.

As the inner layers are exposed to less dirt and no air, the distance in the inner layers can be set as optional with a scaling factor (defaults to 1).
If this factor is to be set differently, this can be set with the following command (in the example: inner distance to 75% of outer distance):

::

    python -m kiclearance -i 0.75

To see help and options, run

::

    python -m kiclearance --help

::

    The following arguments are possible:
    -h, --help: Prints this information,
    -f, --project_folder (Optional): Path to the folder in which the project is located. Default: Folder in which this python script is located.
    -n, --project_name (Optional): Name of the kicad project (file prefix). Default: Script will look for a file with .kicad_pro in the set folder.
    -t, --table_file (Optional): Name (and ending) of the file containing the distance values. Default name: 'clearance'.
    -i, --factor_inner_layers (Optional): Reduced factor for the inner layers. Default: 1.0
    -d, --min_track_distance (Optional): minimum track distance between two tracks on the same potential. Default: 0.15 mm.


Tips and tricks
---------------------------------------
If two network classes are assigned to a connection by mistake, this is displayed as an error in the Electrical Rules Checker (``Inspect`` -> ``Electrical Rules Checker``).

KiCad works through the rules from bottom to top:  Once an applicable rule has been found, KiCad will not search for further rules. Keep this in mind when adding more own rules except from this script here.

Connections in the circuit diagram without a NetClass are automatically assigned to the ``default`` NetClass. 
To avoid careless errors due to missing NetClasses, the ``default`` NetClass should not be used and the distance from ``default`` to other NetClasses should also be set to an unrealistically high value (e.g. 100mm). 
This means that missing NetClasses are immediately noticeable in the layout and can then be assigned.

Example
---------------------------------------
A complete example can be found `here <https://github.com/upb-lea/KiClearance/tree/main/examples>`__.

Documentation
---------------------------------------

Find the documentation `here <https://upb-lea.github.io/KiClearance/index.html>`__.

Troubleshooting
---------------------------------------
* This program has so far been tested only on Linux and Windows.
* For performance reasons when routing, the number of NetClasses should be less than 10 (or not exceed this to any significant degree)
* Using another factor for the inner layers than 1 increases the rules and routing might be slower

