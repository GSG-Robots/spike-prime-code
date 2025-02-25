Typische Probleme und Fehler
============================

.. _driving-problems:

Fahrprobleme
------------

Der Roboter verzieht beim Losfahren
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Wenn der Roboter beim Losfahren minimal verzieht, ist das normal, solange es sich in Grenzen hält und er sich schnell wieder korrigiert.

Einige Möglichkeiten, wie der Effekt verringert werden kann:

* Die Anbaute ist einseitig belastet. Man kann entweder ein Gegengewicht anbringen oder versuchen, so zu bauen, dass möglichts keine langen Arme seitlich abstehen oder diese möglichst leicht sind.
* Wenn die Anbaute viele Schleifpunkte auf der Matte hat, kann man versuchen, die Punkte/Fläche zu verringern, indem man 1/4-Blackies auf der Unterseite anbringt. Die Schleifpunkte sollten möglichst nach am Roboter liegen, um den Effekt zu minimieren.
* Wenn der Roboter einseitig belastet ist und durch plötzliches Losfahren verzieht, kann es sinnvoll sein, beim Fahren die Beschleunigungsfunktion zu nutzen. Wichtig ist, darauf zu achten, dass der Roboter auch nicht zu langsam beschleunigt. Durch leichte Verschiedenheiten in der Kraft der Motoren kann es passieren, dass einer der Motoeren bei einer langsamen Beschleunigung frühre startet als der andere, wodurch der Roboter wieder auf eine Seite verzieht.

Siehe auch: :ref:`gyro`

Der Roboter ruckelt hin und her
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Das liegt an einer zu starken p-Korrektur. Das Problem lässt sich meistens aber durch das Herunterstellen des p-Korrekturwertes nicht lösen, sondern nur verschieben.
Stellt man den p-Korrekturwert herunter ruckelt der Roboter nämlich nicht mehr hin und her, fährt aber womöglich eine leichte Kurve.

Der Ursprung ist meistens schwache Batterieladung (je schwächer die Batterie, desto ungleicher fahren die Motoren) oder eine einseitige Belastung des Roboters.
Ist der Roboter einseitig belastet, sollte sich das Problem lösen lassen, indem man den i-Korrekturwert minimal anhebt und dafür den p-Korrekturwert senkt.

Der Roboter fährt eine Kurve
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Die Korrekturwerte sind zu niedrig eingestellt. Es sollten der p- und/oder der i-Korrekturwert angehoben werden.

Siehe auch: :ref:`gyro`

Der Roboter dreht sich im Kreis
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Siehe: :ref:`gyro`

Der Roboter fährt nicht (und macht Summgeräusche)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Das kann daran liegen, dass die Geschwindigkeit zu niedrig ist. Das kann entweder direkt an einer zu niedrigen Geschwindigkeitseinstellung oder ein einer zu langen Be-/Entschleunigung liegen.
Wenn die Batterie schwach ist oder die Motoren mehr Kraft als gewöhnlich aufbringen müssen (schwere Anbaute) kann das auch passieren.

Zur Lösung solltest du darauf achten, das keine Be-/Entschleunigungsstrecke länger als 5-10 cm ist und die Geschwindigkeit nicht zu niedrig eingestellt ist.
Ohne Anbaute braucht der Roboter etwa eine Geschwindigkeit von 5, um loszufahren.

Beachte, dass die Geschwindigkeit bei der Verwendung von Be-/Entschleunigung am Anfang und Ende der Bewegung niedriger als die eingestellte Geschwindigkeit ist. Sollte das Gewicht des Roboters
es erfordern, die 5 zu überschreiten solltest du auf die Be- und Entschleunigungsfunktionen größtenteils verzichten oder die Stecken auf 1-3 cm heruntersetzen.

Tritt dieses Problem beim Drehen auf, siehe ebenfalls: :ref:`gyro`

Der Roboter zeigt Text auf dem Bildschirm an
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Wenn der Text :code:`RuntimeError()` ist, wechledie Batterie durch eine mit ausreichender Ladung.

Andernfalls, siehe :ref:`general-error`

Das Statuslicht blinkt rot und der Roboter fährt nicht weiter/los
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Ist der Fehler direkt beim Starten des Menüs aufgetreten?
Dann siehe :ref:`startup-error`.

Siehe :ref:`general-error`

Andere Fehler
--------------

.. _gyro:

Der Gyrosensor gibt falsche Werte an
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Versuche, den Roboter komplett auszuschalten und die Batterie für einige Sekunden zu entnehmen.
Setze die Batterie wieder ein, lege den Hub auf eine ebene Fläche und starte ihn. Fasse ihn nicht an und vermeide Erschütterungen, bis er vollständig hochgefahren ist.

Sollte das Problem bestehen bleiben, wechsle den Hub.

Beachte: Es kann auch am Code liegen! Wenn der Roboter sich zum Beispiel bis zum Erreichen einer unerreichbaren Bedingung drehen soll, wird er sich auch endlos im Kreis drehen.

.. _startup-error:

Beim Starten des Menüs blinkt das Statuslicht rot und es schließt sich direkt wieder
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Das kann eine Vielzahl von Gründen haben.

* Überprüfe, ob der Hub richtig herum im Roboter sitzt.
* Überprüfe, ob alle Kabel korrekt angeschlossen sind.
* Überprüfe, ob die Kabel intakt und vollständig eingesteckt sind.
* Versuche, das Programm erneut herunteruladen.
* Lade das Programm erneut hoch und trenne die Kabelverbindung nicht.
  Lese die Lognachrichten, um die Ursache des Fehler zu ermitteln.

.. _general-error:

Genereller Programmfehler
^^^^^^^^^^^^^^^^^^^^^^^^^

.. hint::
    Schließe Hardwarefehler aus und überprüfe, ob alle Kabel korrekt angeschlossen und vollständig eingesteckt sind.
    Wenn Kabel zwischenzeitlich getrennt waren, starte das Programm erneut und prüfe, ob der Fehler immernoch auftritt.

Hilft das nicht, liegt es vermutlich an einem Fehler im Code.

.. hint::
  Falls du im :ref:`Debugmode <debugmode>` bist, kannst du die Fehlernachricht im Bildschirm ablesen.
  Willst du weitere Details erfahren, musst du den :ref:`Verbindungsmodus <connectionmode>` starten. Dann kannst du wie im, Folgenden beschrieben fortfahren.

Verbinde den Roboter mit dem Computer und lade das Programm erneut hoch. Trenne die Verbindugn nicht und provoziere den Fehler. Das heißt z.B.: Starte den Run, der den Fehler erzeugt hat.

Sobald der Fehler auftritt, kannst du dann im Terminal die Fehlermerlung ablesen.
Es wird die auch die Datei und die Zeile angezeigt, in der der Fehler aufgetreten ist.

Mit diesen Information solltest du die Probleme lösen, oder zumindest deren Ursprung ermitteln können.
Nutze am besten Google, um herauszufinden, warum ein bestimmter Fehler aufgetreten ist.
