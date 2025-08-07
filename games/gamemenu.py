# LEGO type:standard slot:6 autostart

from spike import PrimeHub
import hub as hb
import tictactoe2
import spike_invator
import howmany
import rollthedice
import guessthenumber

hub = PrimeHub()


cb = hb.button.center.callback()
hb.button.center.callback(lambda _: None)


game = 0
hb.display.show(hb.Image("33333:39393:33933:39393:33333"))


games_cover = [
    hb.Image("33333:39393:33933:39393:33333"),
    hb.Image("00509:05500:00900:00500:95550"),
    hb.Image("05559:00950:05590:95000:05590"),
    hb.Image("95550:90950:05550:99950:99550"),
    hb.Image("95059:05050:05950:00050:90059"),
    hb.Image("05950:09900:05950:00950:05950"),
]

hub.left_button.was_pressed()
hub.right_button.was_pressed()
hb.button.center.was_pressed()
while not hb.button.center.was_pressed():
    if hub.right_button.was_pressed():
        game += 1
        if game > len(games_cover) -1:
            game = len(games_cover) -1
        # hub.light_matrix.write(game)
        hb.display.show(games_cover[game])


    if hub.left_button.was_pressed():
        game -= 1
        if game < 0:
            game = 0

            # hub.light_matrix.write(game)
        hb.display.show(games_cover[game])
            

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
if game == 5:
    hub.light_matrix.off()
    guessthenumber.main()

hb.button.center.callback(cb)
