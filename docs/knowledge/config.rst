.. _config:

Konfiguration
=============

Die Konfiguration des Roboters wird in einer Datei gespeichert.
Diese Datei wird beim Starten des Roboters geladen und die Werte werden im Code verwendet.

Die folgenden Optionen können in der Konfigurationsdatei eingestellt werden:

* :code:`debug_mode`: Ob der :ref:`Debugmode <debugmode>` aktiviert sein soll
* :code:`tire_diameter`: Der Durchmesser der Räder in Zentimetern
* :code:`gyro_tolerance`: Die Toleranz des Gyrosensors in Grad
* :code:`gearbox`:
    * :code:`gear_selector`: Der Port des Motors, der den Ausgang auswählt
    * :code:`drive_shaft`: Der Port des Motors, der die Ausgänge am Ende drehen lässt
* :code:`driving_motors`:
    * :code:`left`: Der Port des linken Fahrmotors
    * :code:`right`: Der Port des rechten Fahrmotors
* :code:`color_sensors`:
    * :code:`left`: Der Port des linken Farbsensors
    * :code:`right`: Der Port des rechten Farbsensors
* :code:`correctors`:
    * :code:`gyro_drive`: Korrekturwerte :code:`p`, :code:`i` und :code:`d` für das normale Fahren
    * :code:`gyro_turn`: Korrekturwerte :code:`p`, :code:`i` und :code:`d` für das Drehen, sowie :code:`min_speed` und :code:`max_speed` um ein zu langesames Drehen (Roboter bleibt stehen) und zu schnelles Drehen (ungenau) zu verhindern


Hier ein Beispiel für eine Konfigurationsdatei:

.. code-block:: yaml

    debug_mode: on
    tire_diameter: 6.5
    gyro_tolerance: 1
    loop_throttle: 0.025

    gearbox:
        drive_shaft: B
        gear_selector: A

    driving_motors:
        left: F
        right: E

    color_sensors:
        left: D
        right: C

    correctors:
        gyro_turn:
            p: 1.4
            i: 0.0003
            d: -0.2

            # In deg/s:
            min_speed: 1
            max_speed: 90

        gyro_drive:
            p: 1.25
            i: 0
            d: -0.5

