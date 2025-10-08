.. _problem-hw:

Hardwareseitige Fehler
======================

Der Roboter verzieht beim Losfahren
-----------------------------------

Wenn der Roboter beim Losfahren minimal verzieht, ist das normal, solange es sich in Grenzen hält und er sich schnell wieder korrigiert.

Einige Möglichkeiten, wie der Effekt verringert werden kann:

* Die Anbaute ist einseitig belastet. Man kann entweder ein Gegengewicht anbringen oder versuchen, so zu bauen, dass möglichts keine langen Arme seitlich abstehen oder diese möglichst leicht sind.
* Wenn die Anbaute viele Schleifpunkte auf der Matte hat, kann man versuchen, die Punkte/Fläche zu verringern, indem man 1/4-Blackies auf der Unterseite anbringt. Die Schleifpunkte sollten möglichst nach am Roboter liegen, um den Effekt zu minimieren.
* Wenn der Roboter einseitig belastet ist und durch plötzliches Losfahren verzieht, kann es sinnvoll sein, beim Fahren die Beschleunigungsfunktion zu nutzen. Wichtig ist, darauf zu achten, dass der Roboter auch nicht zu langsam beschleunigt. Durch leichte Verschiedenheiten in der Kraft der Motoren kann es passieren, dass einer der Motoeren bei einer langsamen Beschleunigung frühre startet als der andere, wodurch der Roboter wieder auf eine Seite verzieht.

Siehe auch: :ref:`problem-gyro`

Der Roboter ruckelt hin und her
-------------------------------

Das liegt an einer zu starken p-Korrektur. Das Problem lässt sich meistens aber durch das Herunterstellen des p-Korrekturwertes nicht lösen, sondern nur verschieben.
Stellt man den p-Korrekturwert herunter ruckelt der Roboter nämlich nicht mehr hin und her, fährt aber womöglich eine leichte Kurve.

Der Ursprung ist meistens schwache Batterieladung (je schwächer die Batterie, desto ungleicher fahren die Motoren) oder eine einseitige Belastung des Roboters.
Ist der Roboter einseitig belastet, sollte sich das Problem lösen lassen, indem man den i-Korrekturwert minimal anhebt und dafür den p-Korrekturwert senkt.

Der Roboter fährt eine Kurve
----------------------------

Die Korrekturwerte sind zu niedrig eingestellt. Es sollten der p- und/oder der i-Korrekturwert angehoben werden.

Siehe auch: :ref:`problem-gyro`

Der Roboter dreht sich im Kreis
-------------------------------

Siehe: :ref:`problem-gyro`

Der Roboter fährt nicht (und macht Summgeräusche)
-------------------------------------------------

Das kann daran liegen, dass die Geschwindigkeit zu niedrig ist. Das kann entweder direkt an einer zu niedrigen Geschwindigkeitseinstellung oder ein einer zu langen Be-/Entschleunigung liegen.
Wenn die Batterie schwach ist oder die Motoren mehr Kraft als gewöhnlich aufbringen müssen (schwere Anbaute) kann das auch passieren.

Zur Lösung solltest du darauf achten, das keine Be-/Entschleunigungsstrecke länger als 5-10 cm ist und die Geschwindigkeit nicht zu niedrig eingestellt ist.
Ohne Anbaute braucht der Roboter etwa eine Geschwindigkeit von 5, um loszufahren.

Beachte, dass die Geschwindigkeit bei der Verwendung von Be-/Entschleunigung am Anfang und Ende der Bewegung niedriger als die eingestellte Geschwindigkeit ist. Sollte das Gewicht des Roboters
es erfordern, die 5 zu überschreiten solltest du auf die Be- und Entschleunigungsfunktionen größtenteils verzichten oder die Stecken auf 1-3 cm heruntersetzen.

Tritt dieses Problem beim Schalten auf, siehe ebenfalls: :ref:`problem-gearselector`

Tritt dieses Problem beim Drehen auf, siehe ebenfalls: :ref:`problem-gyro`

Das Statuslicht blinkt rot und der Roboter fährt nicht weiter/los
-----------------------------------------------------------------

Siehe :ref:`error`

.. _problem-gyro:

Der Gyrosensor gibt falsche Werte an
------------------------------------

Versuche, den Roboter komplett auszuschalten und die Batterie für einige Sekunden zu entnehmen.
Setze die Batterie wieder ein, lege den Hub auf eine ebene Fläche und starte ihn. Fasse ihn nicht an und vermeide Erschütterungen, bis er vollständig hochgefahren ist.

Sollte das Problem bestehen bleiben, wechsle den Hub.

Alternativ kannst du auch versuchen, :code:`gyro-off` in der Konfiguration anzupassen. Mehr dazu unter :ref:`gyro-calib`.

.. hint::
  Es kann auch am Code liegen! Wenn der Roboter sich zum Beispiel bis zum Erreichen einer unerreichbaren Bedingung drehen soll, wird er sich auch endlos im Kreis drehen.

.. _problem-gearselector:

Der Schaltmotor macht nichts
----------------------------

TODO
