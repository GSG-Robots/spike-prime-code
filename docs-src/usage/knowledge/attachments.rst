Controlling Attachments
=======================

.. note::
    Even though you are probably be here to look up one specific thing,
    you might profit of reading the hole page from the beginning,
    as you will need the knowledge gained in the upper paragraphs
    when reading the ones further down.

    [TODO: Reference general tips (eg. function signature)]


When speaking about the robot, we name the hole thing you can swap out on the robot "attachment".
However, when coding, an "attachment" simply refers to one of the output gears of the gearbox.

The two most important things when controlling attachments are the attachment functions in the :py:mod:`gsgr.movement` module and the :py:class:`~gsgr.enums.Attachment` enum.


Holding an attachment in place
------------------------------

We will begin with the :py:func:`~gsgr.movement.hold_attachment` function, as it is the easiest one to understand.
Here is an example code block:


.. code-block:: python

    from gsgr.enums import Attachment
    from gsgr.movement import hold_attachment


    def run():
        hold_attachment(Attachment.FRONT_LEFT)

The :py:func:`~gsgr.movement.hold_attachment` functions is given the information which attachment to select using the gear selector.
The enum :py:class:`~gsgr.enums.Attachment` serves as a place to store the arbitrary numbers which are asociated with the output
gears in relation to names like :py:attr:`~gsgr.enums.Attachment.FRONT_LEFT` or :py:attr:`~gsgr.enums.Attachment.BACK_RIGHT`.

The example code will simply select the front left gear, so it is no songer freely movable.
This can be useful for arms that should not fall or other things that should be held in place.


Allowing an attachment to move freely
-------------------------------------

This is a very similar thing, so most of it can be explained with a simple code example, altough there are a few special cases which are handled below the example:

.. code-block:: python

    from gsgr.enums import Attachment
    from gsgr.movement import free_attachment


    def run():
        free_attachment(Attachment.FRONT_LEFT)

This code will allow the attachment in the front left to move freely. But you have to be cautionous!
This code has a side effect that is not visible at first glance:
It blocks one of the other attachments.
This is because the gearbox only has 4 stable/safe states and we try to move out of the way as far as possible
to ensure the front left attachment can really move freely.

If you want to ensure multiple attachments are freed at the same time,
you can simply select one of the left over attachments using :py:func:`~gsgr.movement.hold_attachment`.

If you, for some unknown reasons, want to "unselect" all attachments at the same time,
you can use the (unsafe!) :py:func:`~gsgr.movement.free_attachments` function,
which turns the gear selector at a 45° angle so none of the attachments is selected.
This is possible, but because being just 5° off will already paritally block one of the attachments,
this will not always work and is discouraged.

Move an attachment
------------------

Finally, to move an attachment, you can use the :py:func:`~gsgr.movement.run_attachment` function.

Parameters you have to supply are:

- The attachment to move
- The speed to move it at
- The duration to move it for

This can look like this:

.. code-block:: python

    from gsgr.enums import Attachment
    from gsgr.movement import run_attachment


    def run():
        run_attachment(Attachment.FRONT_LEFT, 100, 5)

This code will move the front left attachment at full speed for 5 seconds.
:py:func:`~gsgr.movement.run_attachment` uses :py:func:`~gsgr.movement.hold_attachment` in the
background to select the right attachment, and then runs the drive shaft with the given speed and for the given time.

Additional options
^^^^^^^^^^^^^^^^^^

All additional options are combinable, although they are explained in seperate paragraphs,
so it is easier to understand and differenciate what each of them actually does.

Only start attachment
"""""""""""""""""""""

If no duration is given, the function will also run :py:func:`~gsgr.movement.hold_attachment` and then start the motor with the given speed,
but will not wait for anything. This means that right after running :py:func:`~gsgr.movement.run_attachment`, the motor is started and
the next line of the code will be executed without delay.
If this was the last line of your program, almost nothing will happen, as the run will finish before the movement of the motor can really affect
anything. To make use of this, you have to do some action afterwards.
For example, you could use this to move an attachment while driving like this:

.. code-block:: python

    from gsgr.enums import Attachment
    from gsgr.movement import run_attachment, stop_attachment, drive
    from gsgr.correctors import speed
    from gsgr.conditions import cm


    def run():
        run_attachment(Attachment.FRONT_LEFT, 100)
        drive(speed(75), cm(10)) # don't care about this line, the details are not important
        stop_attachment()

In this code example, we move the front_left attachment at full speed, while driving forward for 10 cm.
Also, as you can see, a new function is used here: :py:func:`~gsgr.movement.stop_attachment`.
It is used to stop the attachment when called. Here, after we drove for 10cm. In this case, it is actually not required,
as it is the last line of the run and all motors will be stopped anyways, but it is good practise
to always include it, as this will be the case rarely and the process to stop all motors at
the end of a run is not always successfull.


Release tension after movement
""""""""""""""""""""""""""""""

After moving the attachment, it might be under stress, as it was turned against a blockade or some other part.
To minimize the stress on the pieces and ensure to continue the run without pressing parts on the floor at full force,
it may be applicable to loosen the attachment for a moment, before fastening it again.
To do this, you can use the :py:obj:`untension` parameter like this:


.. code-block:: python

    from gsgr.enums import Attachment
    from gsgr.movement import run_attachment


    def run():
        run_attachment(Attachment.FRONT_LEFT, 100, 5, untension=True)


Stop automatically when stalled
"""""""""""""""""""""""""""""""

To enable LEGO's stall detection while moving the attachment,
you can use the :py:obj:`stop_on_resistance` parameter.
This will make the motor stop automatically when a resistance is
felt and will exit early if the given duration has not passed yet.

.. warning::
    This has never worked yet.


.. code-block:: python

    from gsgr.enums import Attachment
    from gsgr.movement import run_attachment


    def run():
        run_attachment(Attachment.FRONT_LEFT, 100, 5, stop_on_resistance=True)
