Ladezustandsanzeige
===================

Ebene: Menüsoftware

Verhalten
---------

Dieses Feature wurde so implementiert, dass für alle Hubs die selbe Software verwendet werden kann.
Das wird erreicht, indem der Hub nach dem Starten der Menüsoftware überprüft, ob die Ports :code:`C` und :code:`D`
verbunden sind.

Ist einer der beiden Ports nicht angeschlossen, startet der Ladebildschirm.
Er zeigt den Ladezustand mithilfe eines Balkens auf dem Bildschirm an.

Solange er an einem Ladegerät angeschlossen ist, wird eine Animation abgespiet, die dies signalisiert.
Nach zehn Sekunden schaltet sich der Bildschirm ab. Er kann durch das Betätigen einer beliebigen Taste (außer der BT-Taste)
wieder aktiviert werden.

Ablesen des Akkustands
----------------------

Der Akkustand kann wie folgt abgelesen werden:

+-----------------------+-----------------------------------------------------------+----------------------------+
| Powerbutton LED Farbe | Bedeutung                                                 | Skalierung Balken          |
+=======================+===========================================================+============================+
| Rot                   | Akkustand zu gering zum Verwenden im Robot Game           | In % von 0mV bis 7850mV    |
+-----------------------+-----------------------------------------------------------+----------------------------+
| Gelb                  | Akku kann im Robot Game verwendet werden, aber nicht voll | In % von 7850mv bis 8300mv |
+-----------------------+-----------------------------------------------------------+----------------------------+
| Grün                  | Akku voll (entspricht >= 8300mv)                          | 100%                       |
+-----------------------+-----------------------------------------------------------+----------------------------+

Bei vollem Akku fängt der Hub zusätzlich an zu piepen, um zu signalisieren, dass er nun vom Strom getrennt werden sollte.

.. note::
  Eine Funktion, dass er sich ausschaltet, wenn länger keine Stromquelle vorhanden ist, steht noch aus.
  
  Evtl. ist auch zu überlegen, bei ausgeschaltetem Bildschirm einen Pixel (langsam, alle 10s oder so)
  blinken zu lassen, um sicherzustellen, dass er beim Verlassen bemerkt wird.

.. _problem-charging-in-robot:

Fälschlicherweise im Ladebildschirm
-----------------------------------

Aufgrund der Überprüfung, ob die Ports :code:`C` und :code:`D` aktiv sind, kann es passieren, dass der Ladebildschirm startet,
obwohl der Hub sich im Roboter befindet.
Dann sollte man überprüfen, ob die Motoren bzw. Sensoren an diesen Anschlüssen komplett eingesteckt sind.
Ist das der Fall, kann man eine erneute Überprüfung auslösen, indem man den linken und rechten Knopf gedrückt hält,
bis der Bildschirm schwarz wird. Lässt man dann los, wird erneut überprüft, ob :code:`C` und :code:`D` angeschlossen sind.

Passiet das häufiger, und ist es mit einer erneuten Überprüfung lösbar, sollte man die Wartezeit vor dem Programmstart in Spielzeug-Server verlängern.
