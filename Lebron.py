import sys
import copy
import math
import time

stalemate_threshold = 20


def minimax(game, a, b, depth):
    value, move = max_value(game, a, b, depth)
    return move


def max_value(game, a, b, depth):
    # check if game is in a terminal state, if it is then return the utility value
    if is_terminal(game, depth):
        return utility(game, depth), None

    v = -math.inf
    move = None

    for action in actions(game):
        new_game = simulate_move(game, action)
        if heuristic(new_game) >= v:
            v2, a2 = min_value(new_game, a, b, depth + 1)  # Swap player
            if v2 > v:
                v, move = v2, action
                a = max(a, v)
            if v >= b:
                return v, move
    return v, move


def min_value(game, a, b, depth):
    # check if game is terminal, if so return utility
    if is_terminal(game, depth):
        return utility(game, depth), None

    v = math.inf
    move = ""
    for action in actions(game):
        # make copy of game with move made to not change the actual game board
        new_game = simulate_move(game, action)
        if heuristic(new_game) <= v:
            v2, a2 = max_value(new_game, a, b, depth + 1)  # Swap player
            if v2 < v:
                v, move = v2, action
                b = min(b, v)
            if v <= a:
                return v, move
    return v, move


def heuristic(game):
    current_turn = game["turn"]
    opponent_turn = "orange" if current_turn == "blue" else "blue"

    # Difference in stone count between the current player and the opponent
    stone_count_diff = (
            game["players"][current_turn]["stone_count"]
            - game["players"][opponent_turn]["stone_count"]
    )

    # The number of mills formed by each player
    current_mills = count_mills(game, current_turn)
    opponent_mills = count_mills(game, opponent_turn)
    mills_diff = current_mills - opponent_mills

    # Control is determined by the number of spaces occupied by the current player
    current_control = sum(
        1 for pos in game["board"] if game["board"][pos] == current_turn
    )
    opponent_control = sum(
        1 for pos in game["board"] if game["board"][pos] == opponent_turn
    )
    control_diff = current_control - opponent_control

    # The more valid moves a player has, the better their position
    current_valid_moves = len(actions(game))
    opponent_valid_moves = len(actions(game))
    move_diff = current_valid_moves - opponent_valid_moves

    # Combine all heuristics to form a final heuristic value
    heuristic_value = (
            10 * stone_count_diff  # Stone count is important, but not as much as mills
            + 50 * mills_diff  # Mills are very important (can control the game)
            + 5
            * control_diff  # Board control matters, but less than mills and less than stone count
            + 2 * move_diff  # Future potential is useful, but less crucial
    )

    return heuristic_value


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


def count_mills(game, color):
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

    mill_count = 0

    for mill in mills:
        if all(game["board"][pos] == color for pos in mill):
            mill_count += 1

    return mill_count


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
        "g7": ["d7", "g4"],
    }
    return source in neighbors and target in neighbors[source]


def actions(game):
    possible_moves = []
    current_turn = game["turn"]
    hand = game["players"][current_turn]["hand"]
    # Moves from hand
    if game["players"][current_turn]["stone_count"] > 0:
        for target in game["board"]:
            if game["board"][target] is None:  # if position is empty
                source = hand
                move = f"{source} {target} r0"

                # Check for mill
                if is_mill(game, hand, target):  # Only pass the position
                    for remove in game["board"]:
                        if (
                                game["board"][remove] is not None
                                and game["board"][remove] != current_turn
                        ):
                            move = f"{source} {target} {remove}"

                            if move not in possible_moves and is_valid_move(
                                    game, source, target, remove
                            ):
                                possible_moves.append(move)
                else:
                    if move not in possible_moves:
                        possible_moves.append(move)

        # Moving stones on the board
        for source in game["board"]:
            if game["board"][source] == current_turn:  # current player's stone
                for target in game["board"]:
                    if game["board"][target] is None:
                        if check_correct_step(source, target):  # valid move check
                            move = f"{source} {target} r0"

                            # Check for mill
                            if is_mill(
                                    game, source, target
                            ):  # Only pass the target position
                                for remove in game["board"]:
                                    if (
                                            game["board"][remove] is not None
                                            and game["board"][remove] != current_turn
                                    ):
                                        move = f"{source} {target} {remove}"
                                        if move not in possible_moves and is_valid_move(
                                                game, source, target, remove
                                        ):
                                            possible_moves.append(move)

                            else:
                                if move not in possible_moves and is_valid_move(
                                        game, source, target, "r0"
                                ):
                                    possible_moves.append(move)

    # Flying phase (moving a stone)
    if game["players"][current_turn]["stone_count"] == 3:
        for source in game["board"]:
            if game["board"][source] == current_turn:  # current player's stone
                for target in game["board"]:
                    if game["board"][target] is None:  # target must be empty
                        move = f"{source} {target} r0"

                        # Check for mill
                        if is_mill(game, source, target):
                            for remove in game["board"]:
                                if (
                                        game["board"][remove] is not None
                                        and game["board"][remove] != current_turn
                                ):
                                    move = f"{source} {target} {remove}"
                                    if move not in possible_moves and is_valid_move(
                                            game, source, target, remove
                                    ):
                                        possible_moves.append(
                                            f"{source} {target} {remove}"
                                        )
                        else:
                            if move not in possible_moves and is_valid_move(
                                    game, source, target, "r0"
                            ):
                                possible_moves.append(move)

    return possible_moves


def make_move(game, move):
    current_turn = game["turn"]
    board = game["board"]
    source, target, remove = move.split()
    if not source or not target or not remove:
        print("Invalid move")
        sys.exit(0)
    if is_valid_move(game, source, target, remove):
        execute_move(game, source, target, remove)
    else:
        print(f"invalid move {source} {target} {remove} {current_turn} {board}")
        sys.exit(0)


def execute_move(game, source, target, remove):
    current_turn = game["turn"]
    game["board"][target] = current_turn
    if source.startswith("h"):
        game["players"][current_turn]["stone_count"] -= 1
        game["move_count"] += 1
    else:
        game["board"][source] = None
        game["move_count"] += 1
    if remove != "r0":
        game["board"][remove] = None
        game["move_count"] = 0
    switch_turn(game)


def simulate_move(game, move):
    new_game = copy.deepcopy(game)
    current_turn = new_game["turn"]
    board = new_game["board"]
    source, target, remove = move.split()
    if not source or not target or not remove:
        print("Invalid move")
        sys.exit(0)
    if is_valid_move(new_game, source, target, remove):
        new_game["board"][target] = current_turn
        if source.startswith("h"):
            new_game["players"][current_turn]["stone_count"] -= 1
            new_game["move_count"] += 1
        else:
            new_game["board"][source] = None
            new_game["move_count"] += 1
        if remove != "r0":
            new_game["board"][remove] = None
            new_game["move_count"] = 0
    else:
        print(f"invalid move {source} {target} {remove} {current_turn} {board}")
        sys.exit(0)
    switch_turn(new_game)
    return new_game


def is_valid_move(game, source, target, remove):
    current_turn = game["turn"]
    stone_count = game["players"][current_turn]["stone_count"]
    current_hand = game["players"][current_turn]["hand"]
    if target not in game["board"] or game["board"][target] is not None:
        return False

    if source in ["h1", "h2"]:
        if source != current_hand:
            return False
    else:
        if source not in game["board"] or game["board"][source] != current_turn:
            return False

        if stone_count > 3:
            if not check_correct_step(source, target):
                return False
    if remove != "r0":
        if (
                remove not in game["board"]
                or game["board"][remove] is None
                or game["board"][remove] == current_turn
        ):
            return False
        if not is_mill(game, source, target):
            return False
    # Player must remove an opponents stone if a mill is formed
    elif is_mill(game, source, target):
        return False
    return True


def is_terminal(game, depth):
    blue_stone_count = game["players"]["blue"]["stone_count"] + sum(
        1 for cell in game["board"] if cell == "blue"
    )
    orange_stone_count = game["players"]["orange"]["stone_count"] + sum(
        1 for cell in game["board"] if cell == "orange"
    )
    if depth == 3:
        return True
    if blue_stone_count == 2 or orange_stone_count == 2:
        return True
    if actions(game) is None:
        return True
#    if game["move_count"] == 20:
#        return True


def utility(game, depth):
    current_turn = game["turn"]
    blue_stone_count = game["players"]["blue"]["stone_count"] + sum(
        1 for cell in game["board"] if cell == "blue"
    )
    orange_stone_count = game["players"]["orange"]["stone_count"] + sum(
        1 for cell in game["board"] if cell == "orange"
    )

    if blue_stone_count == 2:
        return -100
    if orange_stone_count == 2:
        return 100

    available_actions = actions(game)
    if available_actions is None:
        if current_turn == "orange":
            return 100
        if current_turn == "blue":
            return -100

    # Evaluate based on stone count difference if max depth is reached
    return heuristic(game)


def main():
    # Read initial color/symbol
    player_id = input().strip()
    a = -math.inf
    b = math.inf
    game_state = {
        "board": {
            key: None
            for key in [
                "a1",
                "a4",
                "a7",
                "b2",
                "b4",
                "b6",
                "c3",
                "c4",
                "c5",
                "d1",
                "d2",
                "d3",
                "d5",
                "d6",
                "d7",
                "e3",
                "e4",
                "e5",
                "f2",
                "f4",
                "f6",
                "g1",
                "g4",
                "g7",
            ]
        },
        "turn": "blue",
        "players": {
            "blue": {"stone_count": 10, "hand": "h1"},
            "orange": {"stone_count": 10, "hand": "h2"},
        },
        "move_count": 0,
    }
    if player_id == "blue":
        player_turn = True
    elif player_id == "orange":
        player_turn = False
    else:
        print("invalid player id")
        return
    initial_turn = True
    while True:
        # if I am X, produce the first move
        try:
            if not player_turn:
                # collect move
                game_input = input().strip()
                make_move(game_state, game_input)
                player_turn = True
                initial_turn = False
            else:
                start_time = time.time()
                # Your move logic here
                move = minimax(game_state, a, b, 1)
                make_move(game_state, move)
                print(move, flush=True)
                end_time = time.time()
                elapsed_time = end_time - start_time
                # check if move was made in time
                if elapsed_time > 5:
                    print("Time limit exceeded")
                    sys.exit(0)
                    # check if move is valid


                player_turn = False

            # no longer our players turn

        except EOFError:
            break


if __name__ == "__main__":
    main()
