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

Create a table (clearance.ods/xls/csv) in your KiCad project directory with voltage clearances defined by your requirements (e.g. standards).
Use this template as a guide: `clearance.ods <https://github.com/upb-lea/KiClearance/blob/main/examples/clearance.ods>`__.

Add the net classes to each connection in the circuit diagram.

.. image:: docs/source/figures/net_class_directive_labels.png

Add the same net classes in the net classes of the PCB editor:
`KiCad PCB Editor`: `File` -> `Board Setup` -> `Design Rules` -> `Net classes`

.. image:: docs/source/figures/board_setup.png

Navigate to the project folder with the KiCad project and the clearance.ods/.xls/.csv file. Open a terminal and execute :

::

    python -m kiclearance

Now a file yourprojectname.kicad_dru is generated, which contains the rule sets.

Open your Kicad project, the rule sets are now stored and you can start the routing.

Example
---------------------------------------
A complete example can be found `here <https://github.com/upb-lea/KiClearance/tree/main/examples>`__.

Documentation
---------------------------------------

Find the documentation `here <https://upb-lea.github.io/KiClearance/intro.html>`__.


Troubleshooting
---------------------------------------
This program has so far been tested only on linux.
