import sys
import copy
import math
import time
import heapq
stalemate_threshold = 20
N = 5
MAX_DEPTH = 5


def minimax(game, a, b, depth):
    value, move = max_value(game, a, b, depth)
    return move


def max_value(game, a, b, depth):
    # check if game is in a terminal state, if it is then return the utility value
    if is_terminal(game, depth):
        return utility(game), None

    v, move = -math.inf, None
    priority_queue = []
    # for each possible action in this game state
    for action in actions(game):
        # get the evaluation value for executing that action
        score = evaluation(simulate_move(game, action))
        # push score onto priority queue, but in this case, with a negative score value so that the moves with the highest values are popped off
        heapq.heappush(priority_queue, (-score, action))
    # pick the top N moves from the priority queue
    top_actions = [heapq.heappop(priority_queue)[1] for i in range(min(N, len(priority_queue)))]
    # simulate each move in top actions
    for action in top_actions:
        new_game = simulate_move(game, action)
        switch_turn(new_game)
        v2, a2 = min_value(new_game, a, b, depth + 1)  # Swap player
        if v2 > v:
            v, move = v2, action
            a = max(a, v)
        if v >= b:
            return v, move
    return v, move


def min_value(game, a, b, depth):
    # check if game is in a terminal state, if it is then return the utility value
    if is_terminal(game, depth):
        return utility(game), None

    v = math.inf
    move = None
    priority_queue = []
    # for each possible action in this game state
    for action in actions(game):
        # get the evaluation value for executing that action
        score = evaluation(simulate_move(game, action))
        # push score onto priority queue
        heapq.heappush(priority_queue, (score, action))
    # pick the top N moves from this priority queue
    top_actions = [heapq.heappop(priority_queue)[1] for i in range(min(N, len(priority_queue)))]
    # simulate each move in top actions
    for action in top_actions:
        new_game = simulate_move(game, action)
        switch_turn(new_game)  # swap player

        v2, a2 = max_value(new_game, a, b, depth + 1)  # Swap player

        if v2 < v:
            v, move = v2, action
            b = min(b, v)
        if v <= a:
            return v, move

    return v, move


def evaluation(game):
    current_turn = game["turn"]
    opponent_turn = "orange" if current_turn == "blue" else "blue"

    # difference in total stone count between the current player and the opponent
    stone_count_diff = ((game["players"]["blue"]["on_board_count"] + game["players"]["blue"]["in_hand_count"])
                        - (game["players"]["orange"]["on_board_count"] + game["players"]["orange"]["in_hand_count"]))

    # the number of mills formed by each player
    current_mills = count_mills(game, current_turn)
    opponent_mills = count_mills(game, opponent_turn)
    mills_diff = current_mills - opponent_mills

    # calculate control of the board, ie. the amount of spaces taken by the player
    current_control = sum(1 for pos in game["board"] if game["board"][pos] == current_turn)
    opponent_control = sum(1 for pos in game["board"] if game["board"][pos] == opponent_turn)
    control_diff = current_control - opponent_control

    # combine all evaluations to form a final evaluation value
    evaluation_value = (
            10 * stone_count_diff  # Stone count is important, but not as much as mills
            + 50 * mills_diff  # Mills are the most important as they are what help you win
            + 5 * control_diff  # Board control matters, but less than mills and less than stone count
    )

    return evaluation_value


def switch_turn(game):
    game["turn"] = "orange" if game["turn"] == "blue" else "blue"


def is_mill(game, source, target):
    current_turn = game["turn"]
    mills = [
        # Horizontal mills
        ["a1", "a4", "a7"], ["b2", "b4", "b6"], ["c3", "c4", "c5"],
        ["d1", "d2", "d3"], ["d5", "d6", "d7"], ["e3", "e4", "e5"],
        ["f2", "f4", "f6"], ["g1", "g4", "g7"],
        # Vertical mills
        ["a1", "d1", "g1"], ["b2", "d2", "f2"], ["c3", "d3", "e3"],
        ["a4", "b4", "c4"], ["e4", "f4", "g4"], ["c5", "d5", "e5"],
        ["b6", "d6", "f6"], ["a7", "d7", "g7"]
    ]

    for mill in mills:
        if target in mill:
            stones_in_mill = 0
            for pos in mill:
                # count the target the stone is being moved to, any stone that is of the color of the current player, but not if the source is in the mill
                if pos == target or (pos != source and game["board"][pos] == current_turn):
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
    if game["players"][current_turn]["in_hand_count"] > 0:
        # source is current players hand
        source = hand
        for target in game["board"]: # consider all positions on board
            if game["board"][target] is None:  # if position is empty
                move = f"{source} {target} r0" # a move is formed with source and valid target
                if is_mill(game, hand, target):  # check if a move to the target position forms a mill
                    for remove in game["board"]:
                        # if it does form a mill, find possibl opponent stones to remove
                        if game["board"][remove] is not None and game["board"][remove] != current_turn:
                            move = f"{source} {target} {remove}"
                            # check if move is valid, if so append it to possible moves
                            if is_valid_move(game, source, target, remove):
                                possible_moves.append(move)
                else:
                    # if a mill is not formed, still append to possible moves
                    if move not in possible_moves:
                        possible_moves.append(move)

    # Moving stones on the board
    if game["players"][current_turn]["on_board_count"] > 0:
        for source in game["board"]:
            if game["board"][source] == current_turn:  # current player's stone
                for target in game["board"]:
                    if game["board"][target] is None:
                        if check_correct_step(source, target):  # valid adjacent move check
                            move = f"{source} {target} r0"

                            # Check for mill
                            if is_mill(game, source, target):  # Only pass the target position
                                for remove in game["board"]:
                                    if game["board"][remove] is not None and game["board"][remove] != current_turn:
                                        move = f"{source} {target} {remove}"
                                        if is_valid_move(game, source, target, remove):
                                            possible_moves.append(move)
                            else:
                                if move not in possible_moves:
                                    possible_moves.append(move)

    # Flying phase if the current players total stone count is equal to 3
    if (game["players"][current_turn]["on_board_count"] + game["players"][current_turn]["in_hand_count"]) == 3:
        for source in game["board"]:
            if game["board"][source] == current_turn:  # current player's stone
                for target in game["board"]:
                    if game["board"][target] is None:  # target must be empty
                        move = f"{source} {target} r0"
                        # Check for mill
                        if is_mill(game, source, target):
                            for remove in game["board"]:
                                if game["board"][remove] is not None and game["board"][remove] != current_turn:
                                    move = f"{source} {target} {remove}"
                                    if is_valid_move(game, source, target, remove):
                                        possible_moves.append(move)
                        else:
                            if move not in possible_moves:
                                possible_moves.append(move)

    return possible_moves if possible_moves else None


def make_move(game, move):
    current_turn = game["turn"]
    board = game["board"]
    # split move into source, target, and remove
    source, target, remove = move.split()
    # if any are empty it is an invalid move
    if not source or not target or not remove:
        print("Invalid move")
        sys.exit(0)
    # if move is valid then execute
    if is_valid_move(game, source, target, remove):
        execute_move(game, source, target, remove)
    else:
        # if move is invalid, print game state and attempted move
        print(f"invalid move {source} {target} {remove} {current_turn} {board}")
        sys.exit(0)


def execute_move(game, source, target, remove):
    current_turn = game["turn"]
    # target populated with current players stone
    game["board"][target] = current_turn
    # if it was from the players hand, increment the number of on board stones, and decrement the amount of stones in hand
    if source.startswith("h"):
        game["players"][current_turn]["on_board_count"] += 1
        game["players"][current_turn]["in_hand_count"] -= 1
    # else, it was a stone moved on the board, amke source equal to none
    else:
        game["board"][source] = None
    # if there was a removal, set removed space to none, the move count back to zero, and decrement the opponents on board stone count
    if remove != "r0":
        game["board"][remove] = None
        game["move_count"] = 0
        game["players"]["blue" if current_turn == "orange" else "orange"]["on_board_count"] -= 1
    # switch the turn of the game
    switch_turn(game)


def simulate_move(game, move):
    # this function is solely used to simulate possible moves within the minimax function
    # make a deep copy as to not edit the actual game state
    new_game = copy.deepcopy(game)
    current_turn = new_game["turn"]
    board = new_game["board"]
    source, target, remove = move.split()
    # code similar to that of the execute function and make move function
    if not source or not target or not remove:
        print("Invalid move")
        sys.exit(0)
    if is_valid_move(new_game, source, target, remove):
        new_game["board"][target] = current_turn
        if source.startswith("h"):
            new_game["players"][current_turn]["on_board_count"] += 1
            new_game["players"][current_turn]["in_hand_count"] -= 1
            new_game["move_count"] += 1
        else:
            new_game["board"][source] = None
            new_game["move_count"] += 1
        if remove != "r0":
            new_game["board"][remove] = None
            new_game["move_count"] = 0
            new_game["players"]["blue" if current_turn == "orange" else "orange"]["on_board_count"] -= 1
    else:
        print(f"invalid move {source} {target} {remove} {current_turn} {board}")
        sys.exit(0)
    return new_game


def is_valid_move(game, source, target, remove):
    current_turn = game["turn"]
    stone_count = game["players"][current_turn]["on_board_count"]
    current_hand = game["players"][current_turn]["hand"]
    # if move is not in board, or the target is occupied
    if target not in game["board"] or game["board"][target] is not None:
        return False
    # if move comes from hand, heck if correct hand
    if source in ["h1", "h2"]:
        if source != current_hand:
            return False
    else:
        # else if didnt come from a hand, check if the source is not in the board, or if we are attempting to move an opponents piece
        if source not in game["board"] or game["board"][source] != current_turn:
            return False
        # if not in flying phase, make sure moves on board are adjacent
        if stone_count > 3:
            if not check_correct_step(source, target):
                return False

    if remove != "r0":
        # if we are removing an opponenets stone, make sure remove is in the board, is not none, or that we are not trying to remove one of our stones
        if (remove not in game["board"] or game["board"][remove] is None or game["board"][remove] == current_turn):
            return False
        # if a mill wasnt formed by the source and target, we should not be removing
        if not is_mill(game, source, target):
            return False
    # Player must remove an opponents stone if a mill is formed
    elif is_mill(game, source, target):
        return False
    return True


def is_terminal(game, depth):
    blue_stone_count = game["players"]["blue"]["in_hand_count"] + game["players"]["blue"]["on_board_count"]
    orange_stone_count = game["players"]["orange"]["in_hand_count"] + game["players"]["orange"]["on_board_count"]
    # at max depth
    if depth == MAX_DEPTH:
        return True
    # if one of our players has a stone count of 2
    if blue_stone_count == 2 or orange_stone_count == 2:
        return True
    # if there are no possible actions from this game state
    if actions(game) is None:
        return True
    # if weve reached a stale mate
    if game["move_count"] == 20:
        return True


def utility(game):
    current_turn = game["turn"]
    blue_stone_count = game["players"]["blue"]["in_hand_count"] + game["players"]["blue"]["on_board_count"]
    orange_stone_count = game["players"]["orange"]["in_hand_count"] + game["players"]["orange"]["on_board_count"]

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
    return evaluation(game)


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
            "blue": {"in_hand_count": 10, "on_board_count": 0, "hand": "h1"},
            "orange": {"in_hand_count": 10, "on_board_count": 0, "hand": "h2"},
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
    while True:
        # if I am X, produce the first move
        if game_state["move_count"] == 20:
            print("stalemate reached")
            sys.exit(0)
        try:
            if not player_turn:
                # collect move
                game_input = input().strip()
                make_move(game_state, game_input)
                game_state["move_count"] += 1
                player_turn = True
            else:
                start_time = time.time()
                # Your move logic here
                move = minimax(game_state, a, b, 1)
                make_move(game_state, move)
                game_state["move_count"] += 1
                print(move, flush=True)
                end_time = time.time()
                elapsed_time = end_time - start_time
                # check if move was made in time
                if elapsed_time > 5:
                    print("Time limit exceeded")
                    sys.exit(0)

                player_turn = False

            # no longer our players turn
        except EOFError:
            break


if __name__ == "__main__":
    main()
