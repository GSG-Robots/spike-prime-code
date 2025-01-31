Ausgänge (Attachments) steuern
==============================

.. note::
    Obwohl du wahrscheinlich nur hier bist um eine bestimmte Sache nachzulesen,
    könnte es Sinn ergeben, die ganze Seite von Beginn an zu lesen,
    da die unteren Abschnitte das Wissen der vorangehenden voraussetzen.

    [TODO: Reference general tips (eg. function signature)]


Die Ausgangsmotoren heißen in unserer Programmierung "Attachments".
In dieser Anleitung wird der Begriff "Ausgang" verwendet, wenn es sich um einen Ausgangsmotor handelt. Wir nutzen weiterhin die Begriffe "Getriebewähler" und "Antriebsmotor", um die beiden Getriebemotoren zu bescheiben.
Der Getriebewähler ist der Motor, der die Ausgänge auswählt, und der Antriebsmotor ist der Motor, der die Ausgänge bewegt.

Die zwei wichtigsten Dinge beim Steuern von Ausgängen sind die Attachment-Funktionen im :py:mod:`gsgr.movement`-Modul und das :py:class:`~gsgr.enums.Attachment`-Enum.
Wie genau Sie verwendet werden, wird im Folgenden erklärt.


Einen Ausgang "festhalten"
--------------------------

Wir fangen mit der :py:func:`~gsgr.movement.hold_attachment`-Funktion an, da sie am einfachsten zu verstehen ist.
Hier ist ein Verwendungsbeispiel:


.. code-block:: python

    from gsgr.enums import Attachment
    from gsgr.movement import hold_attachment


    def run():
        hold_attachment(Attachment.FRONT_LEFT)

Die :py:func:`~gsgr.movement.hold_attachment`-Funktion erhält die Information, welcher Ausgang über den Getriebewähler ausgewählt und dann festgehalten werden soll.
Das :py:class:`~gsgr.enums.Attachment`-Enum ermöglicht es, verständliche Namen wie :py:attr:`~gsgr.enums.Attachment.FRONT_LEFT` oder :py:attr:`~gsgr.enums.Attachment.BACK_RIGHT` statt die normalerweise zufälligen Zahlenwerte zu verwenden, die mit den einzelnen Ausgängen assoziiert werden.

Der obenstehende Beispielcode würde den vorderen linken Ausgang auswählen, sodass er nicht mehr frei beweglich ist.
Das liegt daran, dass der Getriebewähler in eine Position gebracht wird, die den vorderen linken Ausgang mit dem Antriebsmotor verbindet.
Durch den Wiederstand des inaktiven Antriebsmotors wird der Ausgang festgehalten.
Das kann nützlich sein, wenn Arme nicht herunterfallen sollen oder andere Dinge festgehalten werden sollen.


Einem Ausgang freie Bewegung ermöglichen
----------------------------------------

Dies ist eine Ähnliche Sache, auch wenn es eigentlich genau das Gegenteil ist.
Es kann mit einem einfachen Codebeispiel erklärt werden, obwohl es ein paar spezielle Fälle gibt, die weiter unten behandelt werden:

.. code-block:: python

    from gsgr.enums import Attachment
    from gsgr.movement import free_attachment


    def run():
        free_attachment(Attachment.FRONT_LEFT)

Dieser Code ermöglicht es dem Ausgang vorne links, sich frei zu bewegen. Aber Vorsicht!
Dieser Code hat einen Nebeneffekt, der nicht auf den ersten Blick sichtbar ist:
Er blockiert einen der anderen Ausgänge.
Das liegt daran, dass das Getriebe nur 4 stabile bzw. sichere Zustände hat.
Um zu erreichen, dass der vordere linke Ausgang wirklich frei bewegt werden kann, müssen wir also eines der anderen auswählen und damit auch festhalten.

Wenn mehrere Ausgänge gleichzeitig freigegeben werden sollen, kannst du einfach einen der übrigen Motoren mit :py:func:`~gsgr.movement.hold_attachment` auswählen.

Wenn es, aus welchem Grund auch immer, gewünscht ist, alle Ausgänge auf einmal "abzuwählen",
kannst du die (unsichere!) :py:func:`~gsgr.movement.free_attachments`-Funktion verwenden,
die den Getriebewähler um 45° dreht, sodass keiner der Ausgänge ausgewählt ist.
Das ist möglich, aber da schon 5° Abweichung ausreichen, um einen der Ausgänge teilweise zu blockieren,
wird dies nicht immer funktionieren und ist nicht empfohlen.

Einen Ausgang bewegen
---------------------

Zuletzt, um einen Ausgang zu bewegen, kannst du die :py:func:`~gsgr.movement.run_attachment`-Funktion verwenden.

Die Parameter, die du angeben musst, sind:

- Der Ausgang, der bewegt werden soll
- Die Geschwindigkeit, mit der er bewegt werden soll
- Die Dauer, für die er bewegt werden soll

Das kann so aussehen:

.. code-block:: python

    from gsgr.enums import Attachment
    from gsgr.movement import run_attachment


    def run():
        run_attachment(Attachment.FRONT_LEFT, 100, 5)

Dieser Code bewegt den vorderen linken Ausgang mit voller Geschwindigkeit für 5 Sekunden.
:py:func:`~gsgr.movement.run_attachment` verwendet :py:func:`~gsgr.movement.hold_attachment` im Hintergrund, um den richtigen Ausgang auszuwählen, und startet dann die Antriebswelle mit der angegebenen Geschwindigkeit und für die angegebene Zeit.

Zusätzliche Optionen
^^^^^^^^^^^^^^^^^^^^

Alle der im Folgenden erklärten zusätzlichen Optionen sind kombinierbar, obwohl sie in separaten Absätzen erklärt werden,
um zu verstehen und zu unterscheiden, was jede von ihnen tatsächlich tut.

Einen Ausgang nur starten
"""""""""""""""""""""""""

Wenn keine Dauer angegeben ist, wird die :py:func:`~gsgr.movement.hold_attachment`-Funktion ebenfalls ausgeführt und dann der Motor mit der angegebenen Geschwindigkeit gestartet,
jedoch wird nicht auf etwas bestimmtes gewartet. Das bedeutet, dass direkt nach dem Aufruf von :py:func:`~gsgr.movement.run_attachment` der Motor gestartet wird und
die nächste Zeile des Codes ohne Verzögerung ausgeführt wird.
Wenn dies die letzte Zeile deines Programms war, wird fast nichts passieren, da der Lauf endet, bevor die Bewegung des Motors wirklich etwas beeinflussen kann.
Um dies zu nutzen, musst du danach eine Aktion ausführen.
Zum Beispiel könntest du dies verwenden, um einen Ausgang zu bewegen, während du fährst, wie hier:

.. code-block:: python

    from gsgr.enums import Attachment
    from gsgr.movement import run_attachment, stop_attachment, drive
    from gsgr.correctors import speed
    from gsgr.conditions import cm


    def run():
        run_attachment(Attachment.FRONT_LEFT, 100)
        drive(speed(75), cm(10)) # Die Details dieser Funktion sind hier nicht wichtig, der Roboter fährt 10 cm vorwärts.
        stop_attachment()

In diesem Codebeispiel bewegen wir den vorderen linken Ausgang mit voller Geschwindigkeit, während wir 10 cm vorwärts fahren.
Außerdem wird, wie du sehen kannst, eine neue Funktion verwendet: :py:func:`~gsgr.movement.stop_attachment`.
Wird sie aufgerufen, stoppt der Antriebsmotor. Nachdem wir also 10cm gefahren sind, wird diese also aufgerufen, um die Motorbewegung wieder zu beenden.


Spannung nach einer Bewegung lösen
""""""""""""""""""""""""""""""""""

Nachdem ein Ausgang bewegt wurde, könnte es unter Spannung stehen, da es gegen eine Blockade oder ein anderes Teil gedreht wurde.
Um die Spannung auf den Teilen zu minimieren und sicherzustellen,
dass der Lauf ohne Teile, die mit voller Kraft auf den Boden drücken, fortgesetzt werden kann,
kann es sinnvoll sein, diese Spannung zu lösen.
Dazu kannst du den :py:obj:`untension`-Parameter verwenden, wie in diesem Beispiel gezeigt:


.. code-block:: python

    from gsgr.enums import Attachment
    from gsgr.movement import run_attachment


    def run():
        run_attachment(Attachment.FRONT_LEFT, 100, 5, untension=True)


Bei Blockierung automatisch stoppen
"""""""""""""""""""""""""""""""""""

Um die Stall-Erkennung von LEGO zu aktivieren, während der Ausgang bewegt wird,
kannst du den :py:obj:`stop_on_resistance`-Parameter verwenden.
Das wird den Motor automatisch stoppen, wenn ein Widerstand gefühlt wird.
Aufgrund eines Bugs in der Firmware von LEGO wird die Funktion trotzdem warten, bis die angegebene Zeit abgelaufen ist,
auch wenn sich der Motor gar nicht mehr bewegt.


.. code-block:: python

    from gsgr.enums import Attachment
    from gsgr.movement import run_attachment


    def run():
        run_attachment(Attachment.FRONT_LEFT, 100, 5, stop_on_resistance=True)

Wird gleichzeitig keine Dauer angegeben, kann dies dazu benutzt werden, um den Motor zu starten und auf eine Blockierung zu warten, während der Rest des Codes weiter ausgeführt wird.
Man kann also z.B. eine Bewegung starten und dann weiterfahren, während die Bewegung durch eine Blockierung gestoppt wird.

Beispiel:

.. code-block:: python

    from gsgr.enums import Attachment
    from gsgr.movement import run_attachment, drive, stop_attachment
    from gsgr.correctors import speed
    from gsgr.conditions import cm


    def run():
        run_attachment(Attachment.FRONT_LEFT, 100, stop_on_resistance=True)
        drive(speed(75), cm(10)) # Die Details dieser Funktion sind hier nicht wichtig, der Roboter fährt 10 cm vorwärts.
        stop_attachment()

In diesem Beispiel wird der vordere linke Ausgang mit voller Geschwindigkeit bewegt, während der Roboter 10 cm vorwärts fährt.
Der Roboter wird weiterfahren, auch wenn der Ausgang blockiert wird, aber der Motor stoppt dann automatisch.
Wir rufen :py:func:`~gsgr.movement.stop_attachment` am Ende nocheinmal auf, um sicherzugehen, dass der Motor wirklich stoppt, sollte er nicht schon durch die Blockierung gestoppt worden sein oder sie nicht erkannt haben.
