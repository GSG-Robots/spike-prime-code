.. _debugmode:

Debugmode
=========

Der Debugmode ist defür gedacht, die Entwicklung von Code zu unterstüzen und zu vereinfachen.

Folgende Dinge sind speziell im Debugmode:

* Fehlernachrichten werden auf dem Bildschirm angezeigt
* Der Roboter fährt nicht weiter, wenn die Batterie zu schwach geladen ist
* Beim anschließen eines Kabels beendet der Roboter das Menü selbstständig
* Der :ref:`Verbindungsmodus <connectionmode>` kann (muss) gestartet werden
* *Weitere Features gibt es zum aktuellen Zeitpunkt nicht, sind aber geplant*

Der Debugmode kann über die :ref:`Konfigurationsdatei <config>` aktiviert werden.

.. _connectionmode:

Verbindungsmodus
----------------

Der Verbundungsmodus erlaubt es, sich auch im Debugmode mit dem Roboter zu Verbinden, um z.B. Fehlernachrichten zu lesen.
Das ist nötig, da der Roboter beim Verbinden das Menü automatisch schließt, wenn der :ref:`Debugmode <debugmode>` aktiviert ist.
Der Verbindungsmodus deaktiviert diese Funktion des Debugmode,
ohne das das Program erneut hochgeladen werden muss und die Konfiguration bearbeitet werden muss.

Verbindungsmodus starten
^^^^^^^^^^^^^^^^^^^^^^^^

.. note::
    Dies ist nur im Debugmode möglich und notwendig.

Wenn du den Roboter während des Ausführens mit dem Computer verbunden lassen willst, um z.B. Lognachrichten auszulesen, kannst du den Verbindungsmodus starten.

Starte dazu das Menü mit eingestecktem Kabel. Du solltest einen Punkt auf dem Bildschirm sehen. Drücke jetzt die Bluetooth-Taste. Du solltest ins Menü kommen, ohne dass der Roboter das Menü beendet.
Jetzt kannst du den Roboter ganz normal Verwenden und am COmputer die Lognachrichten auslesen.

Verbindungsmodus für einen einzelnen Run starten
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Wenn du bereits im Menü bist und den Verbindungsmodus nur für das Ausführen von einem Run brauchst, kannst du während dem Einstecken des Kabels die Bluetooth-Taste gedrückt halten.
Jetzt kannst du einen beliebigen Run starten.

Beachte: Wenn der Run fertig ist, schließt sich das Menü, außer du hälst während des Beendens die Bluetooth-Taste gedrückt.
