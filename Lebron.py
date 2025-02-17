import sys
import copy
import math
import time

stalemate_threshold = 20
game_state = {
    "board": {key: None for key in [
        "a1", "a4", "a7", "b2", "b4", "b6", "c3", "c4", "c5",
        "d1", "d2", "d3", "d5", "d6", "d7", "e3", "e4", "e5",
        "f2", "f4", "f6", "g1", "g4", "g7"
    ]},
    "turn": "blue",
    "players": {
        "blue": {"stone_count": 10},
        "orange": {"stone_count": 10}
    },
    "move_count": 0
}

def minimax(game, a, b, depth):
    value, move = max_value(game, a, b, depth)
    return move

def max_value(game, a, b, depth):
    # check if game is in a terminal state, if it is then return the utility value
    if is_terminal(game, depth):
        return utility(game), None

    v = -math.inf
    move = None

    for action in actions(game):
        new_game = simulate_move(game)
        v2, a2 = min_value(new_game, a, b, depth + 1)  # Swap player
        if v2 > v:
            v, move = v2, action
            a = max(a, v)
        if v >= b:
            return v, move
    return v, move

def min_value(game, a, b, depth):
    # check if game is terminal, if so return utility
    if game.is_terminal(game, depth):
        return game.utility(), None

    v = math.inf
    move = ""
    for action in game.actions(game):
        # make copy of game with move made to not change the actual game board
        new_game = game.simulate_move(action)
        v2, a2 = max_value(new_game, a, b, depth + 1)  # Swap player
        if v2 < v:
            v, move = v2, action
            b = min(b, v)
        if v <= a:
            return v, move
    return v, move

def switch_turn(game):
    game["turn"] = "orange" if game["turn"] == "blue" else "blue"

def is_mill(game, source, target):
    color = game["turn"]
    mills = [
        # Horizontal mills
        ["a1", "a4", "a7"],
        ["b2", "b4", "b6"],
        ["c3", "c4", "c5"],
        ["d1", "d2", "d3"],
        ["d5", "d6", "d7"],
        ["e3", "e4", "e5"],
        ["f2", "f4", "f6"],
        ["g1", "g4", "g7"],
        # Vertical mills
        ["a1", "d1", "g1"],
        ["b2", "d2", "f2"],
        ["c3", "d3", "e3"],
        ["a4", "b4", "c4"],
        ["e4", "f4", "g4"],
        ["c5", "d5", "e5"],
        ["b6", "d6", "f6"],
        ["a7", "d7", "g7"],
    ]

    for mill in mills:
        if target in mill:
            stones_in_mill = 0
            for pos in mill:
                if pos == target and game["board"][pos] == color:
                    stones_in_mill += 1
                elif pos != source and game["board"][pos] == color:
                    stones_in_mill += 1

            if stones_in_mill == 3:
                return True

    return False

def is_valid_move(game, source, target, remove):
    current_turn = game["players"]["turn"]
    stone_count = game["players"]["turn"]["stone_count"]
    if target not in game["board"] or game["board"][target] is not None:
        return False

    if source in ['h1', 'h2']:
        if source != ('h1' if current_turn == "blue" else 'h2'):
            return False
    else:
        if source not in game["board"] or game["board"][source] != current_turn:
            return False

        if stone_count > 3:
            if not check_correct_step(source, target):
                return False
    if remove != "r0":
        if remove not in game["board"] or game["board"][remove] is None or game["board"][remove] == current_turn:
            return False
        if not is_mill(source, target):
            return False
    # Player must remove an opponents stone if a mill is formed
    elif is_mill(source, target):
        return False
    return True

def check_correct_step(source, target):
    neighbors = {
        "a1": ["a4", "d1"],
        "a4": ["a1", "a7", "b4"],
        "a7": ["a4", "d7"],
        "b2": ["b4", "d2"],
        "b4": ["b2", "b6", "a4", "c4"],
        "b6": ["b4", "d6"],
        "c3": ["c4", "d3"],
        "c4": ["c3", "c5", "b4"],
        "c5": ["c4", "d5"],
        "d1": ["a1", "d2", "g1"],
        "d2": ["b2", "d1", "d3", "f2"],
        "d3": ["c3", "d2", "e3"],
        "d5": ["c5", "d6", "e5"],
        "d6": ["b6", "d5", "d7", "f6"],
        "d7": ["a7", "d6", "g7"],
        "e3": ["d3", "e4"],
        "e4": ["e3", "e5", "f4"],
        "e5": ["d5", "e4"],
        "f2": ["d2", "f4"],
        "f4": ["e4", "f2", "f6", "g4"],
        "f6": ["d6", "f4"],
        "g1": ["d1", "g4"],
        "g4": ["f4", "g1", "g7"],
        "g7": ["d7", "g4"]
    }
    return source in neighbors and target in neighbors[source]

def make_move(game, move):
    current_turn = game["players"]["turn"]
    board = game["board"]
    source, target, remove = move.split()
    if not source or not target or not remove:
        print("Invalid move")
        sys.exit(0)
    if is_valid_move(source, target, remove):
        execute_move(source, target, remove)
    else:
        print(f"invalid move {source} {target} {remove} {current_turn} {board}")
        sys.exit(0)

def execute_move(game, source, target, remove):
    current_turn = game["players"]["turn"]
    game["board"][target] = current_turn
    if source.startswith('h'):
        game["players"][current_turn]["stone_count"] -= 1
    else:
        game["board"][source] = None
    if remove != "r0":
        game["board"][remove] = None
    switch_turn(game)

def simulate_move(game, move):
    new_game = copy.deepcopy(game)
    make_move(new_game, move)
    return new_game

def actions(game):
    possible_moves = []
    current_turn = game["players"]["turn"]
    # Moves from hand
    if game["players"][current_turn]["stone_count"] > 0:
        for target in game["board"]:

            if game["board"][target] is None:  # if position is empty
                source = f"h{1 if current_turn == 'blue' else 2}"
                hand_move = f"{source} {target} r0"

                # Check for mill
                if is_mill(f"h{1 if current_turn == 'blue' else 2}", target):  # Only pass the position
                    for remove in game["board"]:

                        if game["board"][remove] is not None and game["board"][remove] != current_turn:

                            move = f"{source} {target} {remove}"

                            if move not in possible_moves and is_valid_move(source, target, remove):
                                possible_moves.append(f"{source} {target} {remove}")
                else:
                    if hand_move not in possible_moves:
                        possible_moves.append(hand_move)

        # Moving stones on the board
        for source in game["board"]:
            if game["board"][source] == current_turn:  # current player's stone

                for target in game["board"]:

                    if game["board"][target] is None:
                        if check_correct_step(source, target):  # valid move check
                            move = f"{source} {target} r0"

                            # Check for mill
                            if is_mill(source, target):  # Only pass the target position
                                for remove in game["board"]:
                                    if game["board"][remove] is not None and game["board"][remove] != current_turn:
                                        move = f"{source} {target} {remove}"
                                        if move not in possible_moves and is_valid_move(source, target, remove):
                                            possible_moves.append(f"{source} {target} {remove}")
                            else:
                                if move not in possible_moves and is_valid_move(source, target, "r0"):
                                    possible_moves.append(move)

    # Flying phase (moving a stone)
    if game["players"][current_turn]["stone_count"] == 3:

        for source in game["board"]:
            if game["board"][source] == current_turn:  # current player's stone
                for target in game["board"]:
                    if game["board"][target] is None:  # target must be empty
                        move = f"{source} {target} r0"

                        # Check for mill
                        if is_mill(source, target):
                            for remove in game["board"]:
                                if game["board"][remove] is not None and game["board"][remove] != current_turn:
                                    move = f"{source} {target} {remove}"
                                    if move not in possible_moves and is_valid_move(source, target, remove):
                                        possible_moves.append(f"{source} {target} {remove}")
                        else:
                            if move not in possible_moves and is_valid_move(source, target, "r0"):
                                possible_moves.append(move)

    return possible_moves if possible_moves else None


def is_terminal(game, depth):
    if depth == 3:
        return True
    if game["players"]["blue"]["stone_count"] == 2 or game["players"]["orange"]["stone_count"] == 2:
        return True
    if actions(game) is None:
        return True
    if game["move_count"] == 20:
        return True

def utility(game):
    current_turn = game["players"]["turn"]
    if game["players"]["blue"]["stone_count"] == 2:
        return -100
    if game["players"]["orange"]["stone_count"] == 2:
        return 100
    if actions(game) is None and current_turn == "orange":
        return 100
    if actions(game) is None and current_turn == "blue":
        return -100
    if game["move_count"] == 20:
        return 0
    # evaluation, intial thought is since the main goal is to remove as many of the opponents pieces from the board,
    # give states that give me a greater difference between both game["players"] stone count a larger value
    return game["players"]["blue"]["stone_count"] - game["players"]["orange"]["stone_count"]
    # will be negative for states favorable to orange and positive for blue, this aligns with the minimax algo


def main():
    # Read initial color/symbol
    player_id = input().strip()
    a = -math.inf
    b = math.inf
    if player_id == "blue":
        turn = "blue"
    elif player_id == "orange":
        turn = "orange"
    else:
        print("Please enter a valid player name. Either 'blue' or 'orange'")
        sys.exit(0)
    while True:
        # if I am X, produce the first move
        try:
            if turn == "orange":
                # collect move
                game_input = input().strip()
                make_move(game_state, game_input)
            else:
                start_time = time.time()
                # Your move logic here
                move = minimax(game_state, a, b, 1)
                make_move(game_state, move)
                end_time = time.time()
                elapsed_time = end_time - start_time
                # check if move was made in time
                if elapsed_time > 5:
                    print("Time limit exceeded")
                    sys.exit(0)
                # check if move is valid
                print(move, flush=True)
                # no longer our players turn

        except EOFError:
            break


if __name__ == "__main__":
    main()
