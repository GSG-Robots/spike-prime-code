import hub


def pressed(button):
    if hub.button.pressed(button):
        while hub.button.pressed(button):
            ...
        return True
    return False
