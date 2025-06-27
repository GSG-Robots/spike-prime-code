# LEGO type:standard slot:6 autostart

from spike import PrimeHub
import hub as hb
import tictactoe2
import spike_invator
import howmany
import rollthedice
hub = PrimeHub()


cb = hb.button.center.callback()
hb.button.center.callback(lambda _: None)


game = 0
hb.display.show(hb.Image("33333:39393:33933:39393:33333"))


hub.left_button.was_pressed()
hub.right_button.was_pressed()
hb.button.center.was_pressed()
while not hb.button.center.was_pressed():
    if hub.right_button.was_pressed():
        game += 1
        if game == 10:
            game = 9
        hub.light_matrix.write(game)

    if hub.left_button.was_pressed():
        game -= 1
        if game == -1:
            game = 0
        if game == 0:
            hb.display.show(hb.Image("33333:39393:33933:39393:33333"))
        else:
            hub.light_matrix.write(game)    

if game == 1:
    hub.light_matrix.off()
    tictactoe2.main()
if game == 2:
    hub.light_matrix.off()
    spike_invator.main()
if game == 3:
    hub.light_matrix.off()
    howmany.main()
if game == 4:
    hub.light_matrix.off()
    rollthedice.main()

hb.button.center.callback(cb)
