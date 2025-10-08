Softwareseitige Fehler
======================

Der Hub zeigt eine Batterie-Ladeanimation an
--------------------------------------------

Siehe :ref:`problem-charging-in-robot`

.. _error:

Der Hub piept und/oder ein E wird auf dem Display angezeigt
-----------------------------------------------------------

* Wenn:
    * Der Powerbutton des Hubs fünf mal rot blinkt
    * Der Hub fünf mal kurz piept
    * Der Bluetooth Button eine Sekunde lang rot leuchtet
    * Auf dem Display ein E mit drei Punkten angezeigt wird,
      bei dem der untere der hellste ist

    Siehe :ref:`user-error`
  
* Wenn:
    * Der Powerbutton des Hubs fünf mal pink blinkt
    * Der Hub fünf mal lang-kurz mit abwechselnder Tonhöhe piept
    * Der Bluetooth Button eine Sekunde lang pink leuchtet
    * Auf dem Display ein E mit drei Punkten angezeigt wird,
      bei dem der mittlere der hellste ist

    Siehe :ref:`import-error`
  
* Wenn:
    * Der Powerbutton des Hubs fünf mal magenta blinkt
    * Der Hub fünf mal lang-kurz auf gleicher Tonhöhe piept
    * Der Bluetooth Button eine Sekunde lang magenta leuchtet
    * Auf dem Display ein E mit drei Punkten angezeigt wird,
      bei dem der obere der hellste ist

    Siehe :ref:`load-error`

* Wenn:
    * Der Hub einmal mal piept
    * Der Bluetooth Button eine Viertelsekunde lang rot leuchtet

    Siehe :ref:`communication-error`

.. _user-error:

Fehler beim Ausführen der Menüsoftware oder Runs
------------------------------------------------

Hierbei handelt es sich um einen Fehler in der Menüsoftware oder einem Run.

Bei laufender Bluetooth-Verbindung sollte die Fehlernachricht im Regelfall in der Konsole sichtbar sein.

* Siehe: :ref:`run-def-error`

Ebenfalls solltest du folgendes ausschließen:

* Überprüfe, ob der Hub richtig herum im Roboter sitzt.
* Überprüfe, ob alle Kabel korrekt angeschlossen sind.
* Überprüfe, ob die Kabel intakt und vollständig eingesteckt sind.
* Versuche, das Programm erneut herunteruladen.

.. _run-def-error:

Der Fehler lautet: :code:`AssertionError: RunDef: ...`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Ein Run hat nicht unterstützte Konfigurationswerte.
Die Fehlernachricht gibt Auskunft darüber, welcher Wert in welchem Run fehlerhaft ist.

.. _import-error:

Fehler beim Laden der Menüsoftware oder Runs
-------------------------------------------

Beim Laden der Menüsoftware oder den Runs ist ein Fehler aufgetreten

.. _load-error:

Menüsoftware nicht gefunden
---------------------------

Dies spricht für ein grundlegendes Problem in der Programmkonfiguration.

Wahrscheinlich wurden Dateien gelöscht oder verschoben, ohne das die Konfiguration angepasst wurde.
Überprüfe, ob es eine Datei namens :code:`src/__init__.py` gibt.

.. _communication-error:

BLEIO-Server-Fehler
-------------------

Es gab ein Kommunikationsproblem zwischen dem Hub und dem Computer.
Verbinde den Hub erneut und starte ihn ggf. neu.

Sollte sich der Fehler wiederholen, ist das schlecht.
