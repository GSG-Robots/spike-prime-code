# LEGO type:standard slot:11 autostart

from spike import PrimeHub, control

from hub import led

brick = PrimeHub()


def draw_board(_board, focus: bool, selected: tuple[int, int]):
    for coord, state in zip(positions, _board):
        x, y = coord
        if selected[0] == x and selected[1] == y:
            brick.light_matrix.set_pixel(y, x, 100)
        else:
            brick.light_matrix.set_pixel(
                y, x, 90 if state is focus else (65 if state is not None else 0)
            )
            
def bot():
    wins: list[tuple] = []
    for x in range(3):
        row = ((x * 3, x * 3 + 1, x * 3 + 2), (board[x * 3], board[x * 3 + 1], board[x * 3 + 2]))
        col = ((x, x + 3, x +6), (board[x], board[x + 3], board[x + 6]))
        wins.append(row)
        wins.append(col)
    wins.append(((0, 4, 8), (board[0] , board[4] , board[8])))
    wins.append(((2, 4, 6), (board[2] , board[4] , board[6])))

    for win in wins:
        if win.count(None) == 3:
            continue
        
    
BOT_PLAYER = False
HUMAN_PLAYER = True
board = [None, None, None, None, None, None, None, None, None]
positions = ((0, 0), (0, 2), (0, 4), (2, 0), (2, 2), (2, 4), (4, 0), (4, 2), (4, 4))
free_positions = list(range(9))
current_player = True
has_winner = None
while True:
    selected = 0
    led(9 if current_player else 3)
    try:
        while True:
            if brick.left_button.was_pressed():
                selected -= 1
            if brick.right_button.was_pressed():
                selected += 1
            if selected < 0:
                selected = 0
            if selected > len(free_positions) - 1:
                selected = len(free_positions) - 1

            selected_position = free_positions[selected]
            x, y = positions[selected_position]
            draw_board(board, current_player, (x, y))
    except KeyboardInterrupt:
        free_positions.pop(selected)
        board[selected_position] = current_player
        for x in range(3):
            if (board[x * 3] is board[x * 3 + 1] is board[x * 3 + 2]) and board[x * 3] is not None:
                has_winner = True
            if (board[x] is board[x + 3] is board[x + 6]) and board[x] is not None:
                has_winner = True
        if (board[0] is board[4] is board[8] or board[2] is board[4] is board[6]) and (
            board[4] is not None
        ):
            has_winner = True
        if len(free_positions) == 0:
            has_winner = False
        if has_winner is not None:
            break
        current_player = not current_player

try:
    while True:
        if has_winner:
            led(9 if current_player else 3)
        else:
            led(6)
        brick.light_matrix.off()
        control.wait_for_seconds(0.1)
        led(0)
        draw_board(board, current_player, (-1, -1))
        control.wait_for_seconds(0.1)
except KeyboardInterrupt:
    raise SystemExit
# except IndexError
