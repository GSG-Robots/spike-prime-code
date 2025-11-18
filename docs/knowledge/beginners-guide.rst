Beginners-Guide
===============

Dieses Kapitel bringt dir die Grundlagen bei, um deinen ersten eigenen Run zu erstellen, und zeigt dir, welche Kapitel der Dokumentation du dir als nächstes anschauen solltest.

.. contents::
    :depth: 2
    :local:

Dein erster Run
---------------

Erstelle eine Datei im ``src/runs`` Ordner und nenne sie z.B. ``run_DEINNAME.py``. Der Dateiname entscheidet,
an welcher Position im Menü der Run stehen wird,
da die Runs alphabetisch nach dem Dateinamen sortiert werden.

Starte mit diesem Code:

.. code-block:: python
    :linenos:

    import color as col

    # Das Zeichen (Buchstabe/Zahl), welches im Menü für diesen Run angezeigt werden soll.
    display_as = "T"
    # Die Farbe, die das Statuslicht im Menü haben soll, wenn dieser Run ausgewählt ist.
    color = col.RED

    def run():
        # Der Code, der ausgeführt werden soll.
        ...


Der Code in der ``run`` Funktion wird ausgeführt, wenn der Run gestartet wird.
Die Variablen ``display_as`` und ``color`` legen jeweils das Symbol und die Farbe des Statuslichts fest, welche angezeigt werden, wenn der Run gerade im Menü ausgewählt ist.

.. hint::
    TODO: display_as&color possible values

Was der Roboter tun soll, kannst du in der ``run`` Funktion definieren.
Dazu kannst du die Funktionen aus der ``gsgr`` Bibliothek verwenden.

Füge oben in der Datei folgendes hinzu:

.. code-block:: python
    :linenos:
    :lineno-start: 2

    from ..gsgr.movement import gyro_set_origin, gyro_drive
    from ..gsgr.conditions import cm

Jetzt kannst du in der ``run``-Funktion folgendes schreiben: (Die Kommentare musst du nicht übernehmen.)

.. code-block:: python
    :linenos:
    :lineno-start: 10

    def run():
        gyro_set_origin()  # Setzt den Gyro-Sensor zurück.
        gyro_drive(0, 500, cm(10))  # Fahre 10 cm mit 50% Geschwindigkeit vorwärts.
                                    # Die Geschwindigkeit wird in zehntel Prozent
                                    # (also quasi Promille) angegeben.

Wenn der Roboter nicht bereits mit dem Computer verbunden ist, verbinde ihn jetzt über Bluetooth.
Siehe dazu: :ref:`how-to--connect-bluetooth`.

Sobald eine Verbindung besteht, werden Änderungen automatisch Live auf den Roboter übertragen.

Nachdem die Übertrangung abgeschlossen ist, startet die Menüsoftware am Roboter automatisch neu.
Starte den Run am Roboter, indem du das ``T`` im Menü auswählst und den mittleren Knopf drückst.
Der Roboter sollte sich jetzt 10 cm vorwärts bewegen.

Sehen wir uns jetzt einmal an, was der Code macht:

``gyro_set_origin``
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
    :linenos:
    :lineno-start: 11

    gyro_set_origin()

Diese Funktion verwenden wir am Anfang eines jeden Runs, um den Gyro-Sensor zurückzusetzen.
Unsere Fahr- und Drehfunktionen verwenden den Gyro-Sensor, um geradeaus zu fahren bzw. genau zu drehen.
D.h. die Richtung, in die der Roboter fährt, wird die ganze Zeit gemessen, und
sobald eine Abweichung von der ursprünglichen Richtung festgestellt wird, wird dagegen korrigiert.

``gyro_drive``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
    :linenos:
    :lineno-start: 12

    gyro_drive(0, 500, cm(10))

Diese Funktion fährt den Roboter vorwärts oder rückwärts.
Der erste Parameter ist der Winkel, in den der Roboter fahren soll.
Er wird relativ zu dem des letzten Aufrufs von ``gyro_set_origin`` angegeben.
Da wir gerade die Richtung zurückgesetzt haben, ist das 0°.
Damit Fahren wir genau geradeaus.
Der zweite Parameter ist die Geschwindigkeit in zehntel Prozent.
Also 500 = 50% Geschwindigkeit.
Der dritte Parameter ist eine Bedingung, wann der Roboter anhalten soll.
Hier verwenden wir ``cm(10)``, also 10 cm.
Es gibt auch andere Bedingungen, z.B. ``sec(5)`` (fahre 5 Sekunden lang) oder ``wheels_blocked()`` (fahre, bis die Räder blockiert sind),
aber die wichtigste ist erst einmal ``cm(x)``.

Drehen
------

Jetzt werden wir den Run erweitern, sodass der Roboter auch Drehbewegungen macht.

Ändere die ``from ..gsgr.movement import ...`` Zeile zu:

.. code-block:: python
    :linenos:
    :lineno-start: 2

    from ..gsgr.movement import gyro_set_origin, gyro_drive, gyro_turn

Und ändere die ``run`` Funktion zu:

.. code-block:: python
    :linenos:
    :lineno-start: 10

    def run():
        gyro_set_origin()  # Setzt den Gyro-Sensor zurück.

        gyro_drive(0, 500, cm(20))    # Fahre 20 cm vorwärts.
        gyro_turn(90)                 # Drehe um 90° nach rechts mit 30% Geschwindigkeit.
        gyro_drive(90, 500, cm(20))   # Fahre 20 cm vorwärts.
        # Jetzt wieder zurück:
        gyro_drive(90, -500, cm(20))  # Fahre 20 cm rückwärts.
        gyro_turn(0)                  # Drehe um 90° nach rechts mit 30% Geschwindigkeit.
        gyro_drive(0, -500, cm(20))   # Fahre 20 cm rückwärts.

Wenn die Verbundung abgebrochen ist, verbinde den Roboter wieder über Bluetooth: :ref:`how-to--connect-bluetooth`.

Warte Übertragungen ab und starte den Run wieder am Roboter.

Der Roboter sollte jetzt eine Art L fahren.

Schauen wir uns an, was wir hier geändert haben:

``gyro_drive`` mit negativer Geschwindigkeit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
    :linenos:
    :lineno-start: 17

    gyro_drive(90, -500, cm(20))

Wenn die Geschwindigkeit negativ ist, fährt der Roboter rückwärts.
Die Endbedingung funktioniert genauso wie bei vorwärts fahren, muss also nicht geändert werden.

``gyro_turn``
~~~~~~~~~~~~~

.. code-block:: python
    :linenos:
    :lineno-start: 14

    gyro_turn(90)

Diese Funktion dreht den Roboter um den angegebenen Winkel.
Der Winkel wird wieder relativ zum letzten Aufruf von ``gyro_set_origin`` angegeben.

.. note::
    
    TODO: Continue

Weiterlesen
-----------

Wenn du mit den hier vorgestellten Funktionen vertraut bist,
dann schaue dir diese Kapitel als nächstes an:

Um Runs zu erstellen:

* :doc:`/knowledge/driving-and-turning`
* :doc:`/knowledge/attachments`
* :doc:`API-Referenz </api/gsgr/index>`

Um die Konfiguration zu bearbeiten:

* :doc:`/knowledge/config`

Um einen neuen PC einzurichten:

* :doc:`/knowledge/setup-devenv`

