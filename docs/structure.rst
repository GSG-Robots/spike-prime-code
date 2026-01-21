Funktionsweise & Strukturierung des Codes
=========================================

Der verwendete Code ist in mehrere Bereiche bzw. Ebenen aufgeteilt. Im folgenden wird jede Ebene einmal vorgestellt.
Im Rest der Dokumentation werden immer diese Bezeichungen verwendet, es macht also Sinn, sie sich zu merken.

Firmware
--------

Wir verwenden die offizielle Firmware Spike V3 von LEGO.
Dadurch können wir alle Funktionen des Roboters, wie von Motoren und Sensoren, nutzen, ohne selber Firmware schreiben zu müssen.

Spielzeug
---------

"Spielzeug" ist das Betriebssystem des Roboters.
Anstatt das mit der Firmware mitgelieferte Betriebssystem zu verwenden, haben wir ein eigenes Betriebssystem entwickelt.
Das ermöglicht uns, eigene Software zum Kommunizieren mit dem Roboter über Bluetooth zu schreiben und
so unser LiveCode-Feature zu realisieren.
Diese Ebene kümmert sich also um die Bluetooth-Kommunikation und das Starten der Menüsoftware.

Menüsoftware
------------

Die Menüsoftware ist die Software, die das Menü und die Ladeanzeige des Roboters steuert.
Hier sind alle unserer Fahrfunktionen usw. in der ``gsgr``-Bibliothek implementiert.

Runs
----

Das ist der Code, den wir jedes Jahr verändern, um die Aufgaben des Wettbewerbs zu lösen.
Jeder Run ist in einer eigenen Datei im ``src/runs/``-Ordner implementiert.
Die Runs verwenden die ``gsgr``-Bibliothek, um auf die Funktionen des Roboters zuzugreifen.


