Einen Run erstellen
===================

.. warning::
    Document may be out of date.
    
Erstelle eine Datei im ``src/runs`` Ordner. Der Dateiname entscheidet,
an welcher Position im Menü der Run stehen wird,
da die Runs alphabetisch nach dem Dateinamen sortiert werden.

Starte mit diesem Code:

.. code-block:: python

    from gsgr.enums import Color

    # Das Zeichen (Buchstabe/Zahl), welches im Menü für diesen Run angezeigt werden soll.
    display_as = 1
    # Die Farbe, die das Statuslicht im Menü haben soll, wenn dieser Run ausgewählt ist.
    color = Color.RED

    def run():
        # Der Code, der ausgeführt werden soll.
        ...


Der Code in der ``run`` Funktion wird ausgeführt, wenn der Run gestartet wird.
Die Variablen ``display_as`` und ``color`` legen jeweils das Symbol und die Farbe des Statuslichts fest, welche angezeigt werden, wenn der Run gerade im Menü ausgewählt ist.

Die verschiedenen Farben kannst du hier finden: :py:class:`gsgr.enums.Color`.

.. hint:: Die Symbole sind noch nicht dokumentiert, aber du kannst jede Ziffer und einige Buchstaben verwenden.

.. .. warning::
..     Die ``config`` Variable kann aktuell nicht verwendet werden!

.. Um zusätzliche Standartwerte zu einem Run hinzuzufügen kann zusätzlich die ``config`` Variable verwendet werden:

.. .. code-block:: python

..     from gsgr.enums import Color
..     from gsgr.configuration import config

..     config_override = config(p_correction=1000)  # Den Roboter beim Fahren tanzen lassen
..     display_as = 1
..     color = Color.RED

..     def run():
..         ...
