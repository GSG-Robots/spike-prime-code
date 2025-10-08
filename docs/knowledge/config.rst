.. _config:

Konfiguration
=============

Die Konfiguration des Roboters wird in einer Datei :code:`config.yaml` gespeichert.
Diese Datei wird beim Starten des Roboters geladen und die Werte werden im Code verwendet.

Die folgenden Optionen können in der Konfigurationsdatei eingestellt werden:

* :code:`tire_diameter`: Der Durchmesser der Räder in Zentimetern
* :code:`loop_throttle`: LEGACY, wird so gut wie nicht verwendet. Urspünglich: Verzögerung von Schleifen zum Verhindern von 100% CPU-Auslastung
* :code:`gyro_tolerance`: Die Toleranz des Gyrosensors in Grad
* :code:`gyro_off`: Die Abweichung des Gyrosensors nach einer Drehung um 360°. Dieser Wert wird verwendet, um den Fehler herauszurechnen. Siehe :ref:`gyro-calib`
* :code:`gearbox`:
    * :code:`drive_shaft`: Der Port des Motors, der die Ausgänge am Ende drehen lässt
    * :code:`gear_selector`: Der Port des Motors, der den Ausgang auswählt
    * :code:`offset`: Die Position in Grad, auf der der erste Ausgang ausgewählt ist.
* :code:`driving_motors`:
    * :code:`left`: Der Port des linken Fahrmotors
    * :code:`right`: Der Port des rechten Fahrmotors
* :code:`sensors`:
    * :code:`left`: Der Port des linken Sensors
    * :code:`right`: Der Port des rechten Sensors
* :code:`correctors`:
    * :code:`gyro_drive`: Korrekturwerte :code:`p`, :code:`i` und :code:`d` für das normale Fahren
    * :code:`gyro_turn`: Korrekturwerte :code:`p`, :code:`i` und :code:`d` für das Drehen, sowie :code:`min_speed` und :code:`max_speed` um ein zu langesames Drehen (Roboter bleibt stehen) und zu schnelles Drehen (ungenau) zu verhindern
* :code:`debugging`:
    * :code:`no_autoscroll`: Deaktiviert das automatische weiterscrollen nach Abschluss eines Runs
    * :code:`initial_focus`: Der wievielte Run beim Start ausgewählt sein soll. Zählt ab 0, dh. 0 -> erster Run, 1 -> zweiter Run, etc.
    * :code:`require_full_battery`: Aktiviert, dass der Hub den Akkustand überprüft und die Arbeit bei zu niedrigem verweigert.
    * :code:`display_errors`: Aktiviert, dass Fehlernachrichten auf dem Display des Hubs angezeigt werden. Bei bestehender Bluetooth-Verbindung unnötig.
  * :code:`competition`: Wenn ja werden Einstellungen aus :code:`debugging` ignoriert und stattdessen für den Wettbewerb optimierte Einstellungen verwendet.

Hier ein Beispiel für eine Konfigurationsdatei:

.. code-block:: yaml
    tire_diameter: 6.24
    loop_throttle: 0.025
    landscape: yes
    gyro_tolerance: 1
    gyro_off: -4

    gearbox:
        drive_shaft: A
        gear_selector: B
        offset: -7

    driving_motors:
        left: D
        right: C

    sensors:
        left: E
        right: F

    correctors:
        gyro_turn:
            p: 1.6
            i: 0
            d: -1

            # In deg/s:
            min_speed: 5
            max_speed: 90

        gyro_drive:
            p: 1.3
            i: 0.001
            d: -1

    competition: no
    debugging:
        no_autoscroll: yes
        initial_focus: 0
        require_battery_full: no
        display_errors: no


.. _gyro-calib:

Ermittlung des Gyro-Offsets
---------------------------

1. Richte den Roboter an einer Wand aus.
2. Starte bei laufender Bluetoothverbindung den Run :code:`run_calib.py`, erkennbar an dem kleinen Kreis / O.
3. Drehe den Roboter im Uhrzeigersinn um 360°
4. Drücke noch einmal den mittleren Knopf

Jetzt kannst du in der Konsole den gemessenen Offset ablesen und kannst ihn in die Konfigurationsdatei eintragen.

.. hint::
    Am besten wiederholst du den Prozess mehrmals und berechnest den ungefähren Mittelwert, um die Präzision zu maximieren.
