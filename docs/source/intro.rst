.. sectnum::

Welcome to KiClearance
==================================================

This Python program converts a given table of voltage distances into KiCad design rules.

.. image:: figures/overview.png


Installation
---------------------------------------
Install KiClearance directly from pyPI:

::

    pip install kiclearance


Usage
---------------------------------------

Create a table (clearance.ods/xls/csv) in your KiCad project directory with voltage clearances defined by your requirements (e.g. standards).
Use this template as a guide: `clearance.ods <https://github.com/upb-lea/KiClearance/blob/main/examples/clearance.ods>`__.

Add the net classes to each connection in the circuit diagram.

.. image:: figures/net_class_directive_labels.png

Add the same net classes in the net classes of the PCB editor:
``KiCad PCB Editor``: ``File`` -> ``Board Setup`` -> ``Design Rules`` -> ``Net classes``

.. image:: figures/board_setup.png

Navigate to the project folder with the KiCad project and the clearance.ods/.xls/.csv file. Open a terminal and execute :

::

    python -m kiclearance

Now a file yourprojectname.kicad_dru is generated, which contains the rule sets.

Open your Kicad project, the rule sets are now stored and you can start the routing.

Tips and tricks
---------------------------------------
If two network classes are assigned to a connection by mistake, this is displayed as an error in the Electrical Rules Checker (``Inspect`` -> ``Electrical Rules Checker``).

KiCad works through the rules from bottom to top:  Once an applicable rule has been found, kiCad will not search for further rules. Keep this in mind when adding your own rules. 

Example
---------------------------------------
A complete example can be found `here <https://github.com/upb-lea/KiClearance/tree/main/examples>`__.

Troubleshooting
---------------------------------------
This program has so far been tested only on linux.



KiClearance function documentation
==================================================
.. currentmodule:: kiclearance.kiclearance

.. automodule:: kiclearance.kiclearance
   :members: write_design_rule_file, parse_excel_table, look_for_clearance_table_file, look_for_kicad_project, usage
