"""
LEGO provided functions and values.
"""

FRONT=RIGHT=BACK=LEFT=0


def power_off(fast=True, restart=False) -> None: # pylint: disable=unused-argument
    """Power off the hub

    Args:
        fast (bool, optional): Whether to stop fast. Defaults to True.
        restart (bool, optional): Whether to restart afterwards. Defaults to False.
    """
