Fahren und Drehen
=================

Geradeaus Fahren
----------------

Um geradeaus zu Fahren, wird die Funktion :py:func:`~gsgr.movement.gyro_drive` verwendet.

.. autofunction:: gsgr.movement.gyro_drive

Die einfachste Verwendung sieht so aus:

.. code-block:: python

    #          Zielgradzahl
    #          .   Geschwindigkeit in %
    #          .   .    Ziel (Endingcondition)
    #          .   .    .
    gyro_drive(0, 75, cm(5))

Hier fährt der Roboter also 5 cm geradeaus mit 75% Geschwindigkeit.

Geschwindigkeit
^^^^^^^^^^^^^^^

Um Ungleichheiten der Motoren und Probleme mit schwächerer Batterieladung zu umgehen,
sollte die Geschwindigkeit nicht zu niedrich gewählt werden. Unter 20-25 zu gehen, sollte vermieden werden.

Wichtig ist auch, die Geschwindigkeit nicht zu hoch einzustellen: Wenn der Roboter z.B. mit 100%iger Geschwindigkeit fährt,
können die Korrekturwerte nur noch auf einem Rad effektiv angewandt werden; die Korrektur wird praktisch halbiert.
Siehe :ref:`drive-pid` für weitere Details.
Dieser Effekt tritt, wenn auch nicht so stark, bereits bei Geschwindigkeiten von 90+ auf.
Generell kannd er Roboter bei Geschwindigkeiten über 80-85 nicht mehr so genau fahren (Motoren unterschiedlich, weitere Faktoren),
allein deshalb sollten zu hohe Geschwindigkeiten gemieden werden.

Auf die sog. :ref:`Endingcondition <endingconditions>` gehen wir weiter unten genauer ein. Wichtig sind hier erstmal die anderen Werte.

Be- und Entschleunigung
^^^^^^^^^^^^^^^^^^^^^^^

Die Be- und Entschleunigung kann über die Parameter :code:`accelerate` und :code:`deccelerate` eingestellt werden.
Standartmäßig ist sie ausgeschaltet.

Wenn ein Wert angegeben wird, wird er als Prozentsatz der angegeben :ref:`Endingcondition <endingconditions>` verstanden.

Im folgenden Codeblock wird also für 5 cm be- und für 10 cm entschleunigt:

.. code-block:: python

    gyro_drive(0, 75, cm(20), accelerate=25, deccelerate=50)

Es ist wichtig, die Be- und Entschleunigungsstrecken nicht zu hoch einzustellen,
da der Roboter bei schwächerer Batterieladung sonst verzieht, oder sogar nur mit einem Rad losfährt.

Die Strecken sollten, auch aus diesem Grund, jeweils nicht mehr als 7-10 cm betragen, je nach Geschwindigkeit.

"Bremsen"
^^^^^^^^^

Mit :code:`brake=False` hat man die Möglichkeit, zu deaktivieren, das der Roboter nach der Bewegung anhält.
Das kann sinnvoll sein, wenn man mehere Bewegungen direkt hintereinander ausführen will, ohne dass der Roboter kurz stehenbleibt.

Beispiel:

.. code-block:: python

    gyro_drive(0, 75, cm(10), brake=False)

.. _drive-pid:

PID-Korrektur
^^^^^^^^^^^^^

Der Roboter korrieiert mithilfe eines PID-Controllers zu der angegebenen Gradzahl hin.
Das funktioniert, indem er regelmäßig die aktuelle Drehung des Roboters ausließt
und entsprechend die Geschwindigkeit der Räder anpasst, sodass er sich wieder "von selbst" in die richtige Richtung dreht.

Der Roboter berechnet die Differenz zwischen der aktuellen und der gewünschten Gradzahl. Dieser Wert heißt *Fehler*.

.. math::
    \Delta Fehler = \alpha_{aktuell} - \alpha_{Ziel}

Dann kommen die PID-Werte ins Spiel. P steht für *Proportional*, I für *Integral* und D für *Ableitung (engl. derivative)*.

Der proportionale Korrekturwert :math:`p` gibt an, wie stark auf basis des aktuellen Fehlers korrigiert werden soll.

.. math::
    Korrektur_P = \Delta Fehler * p

Der integrale Korrekturwert :math:`i` bezieht sich auf die Summe aller bisherigen Fehler.
Er hilft, wenn

.. math::
    Korrektur_I = \int_{t_{start}}^{t_{jetzt}} Fehler(t) dx * i

(oder in einfach, hatte gerade Spaß)

.. math::
    Korrektur_I = Fehlersumme * i

Der letzte Korrekturwert :math:`p` wird auf die Veränderung angewandt:

.. math::
    Korrektur_D = (Fehler_{jetzt} - Fehler_{gerade \space eben}) * d

Das soll einer zu starken Korrektur vorauswirken, daher wird hier auch ein negativer Korrekturwert :math:`d` verwendet.

Daraus wird dann die Summe berechnet:

.. math::
    Korrektur = Korrektur_P + Korrektur_I + Korrektur_D

Dann wird diese auf beide Radgeschwindigkeiten angewandt:

.. math::
    v_{links}=v_{links} + \frac{Korrektur}{2}

.. math::
    v_{rechts}=v_{rechts} - \frac{Korrektur}{2}

Dadurch dreht das eine Rad dann langsamer und das andere schneller, wodurch sich der Roboter wieder zuer Wunschrichtung ausrichtet.

Für weitere Details zum wählen der richtigen Korrekturwerte, siehe auch :ref:`Fahrprobleme <driving-problems>`

.. _endingconditions:

Endingconditions
^^^^^^^^^^^^^^^^

.. note:: WIP
