How to Use
==================

Add a file in the ``runs`` folder. The order of appereance in the menu is alphabetically by the filename.

The file should look like this:

.. code-block:: python

    from gsgr.enums import Color
    from gsgr.run import run

    display_as = 1
    color = Color.RED

    def run():
        print(1)


The code in the ``run`` function is executed when the run is selected.
The variables ``display_as`` and ``color`` represent the symbol to show and the color to light the button with when the run is selected in the menu, respectively.
To add special config values to a run, you can additionally use the ``config`` variable like this:

.. code-block:: python

    from gsgr.enums import Color
    from gsgr.configuration import config

    config_override = config(p_correction=1000)  # Make the robot dance
    display_as = 1
    color = Color.RED

    def run():
        print(1)
