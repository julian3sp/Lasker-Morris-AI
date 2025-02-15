import sys
import copy
import math
import time

stalemate_threshold = 20

class LaskerMorris:
    def __init__(self):
        self.players = {"blue": {"stone_count": 10},
                        "orange": {"stone_count": 10}}
        self.board = {key: None for key in ["a1", "a4", "a7", "b2", "b4", "b6", "c3", "c4",
                                            "c5", "d1", "d2", "d3", "d5", "d6", "d7", "e3",
                                            "e4", "e5", "f2", "f4", "f6", "g1", "g4", "g6"]}
        self.turn = "blue"
        # move count is instantiated at the class level so it is copied with the deepcopy function
        self.move_count = 0

    def minimax(self, game, a, b, depth):
        value, move = self.max_value(self.board, a, b)
        return move

    def max_value(self, game, a, b, depth):
        # check if game is in a terminal state, if it is then return the utility value
        if self.is_terminal(self.board):
            return self.utility(self.board), None
    
        v = -math.inf
        move = ""
    
        for action in self.actions(self.board):
            new_game = self.simulate_move(action)
            v2, a2 = self.min_value(new_game, a, b, depth + 1)  # Swap player
            if v2 > v:
                v, move = v2, action
                a = max(a, v)
            if v >= b:
                return v, move
        return v, move



    def min_value(self, game, a, b, depth):
        # check if game is terminal, if so return utility
        if self.is_terminal(self.board):
            return self.utility(self.board), None
    
        v = math.inf
        move = ""
        for action in self.actions(self.board):
            # make copy of game with move made to not change the actual game board
            new_game = self.simulate_move(action)
            v2, a2 = self.max_value(new_game, a, b, depth + 1)  # Swap player
            if v2 < v:
                v, move = v2, action
                b = min(b, v)
            if v <= a:
                return v, move
        return v, move

    def switch_turn(self):
        self.turn = "orange" if self.turn == "blue" else "blue"

    def is_mill(self, source, target):
        current_color = self.turn
        mills = [
            ["a1", "a4", "a7"], ["b2", "b4", "b6"], ["c3", "c4", "c5"],
            ["d1", "d2", "d3"], ["d5", "d6", "d7"], ["e3", "e4", "e5"],
            ["f2", "f4", "f6"], ["g1", "g4", "g7"],
            ["a1", "d1", "g1"], ["b2", "d2", "f2"], ["c3", "d3", "e3"],
            ["a4", "b4", "c4"], ["e4", "f4", "g4"], ["c5", "d5", "e5"],
            ["b6", "d6", "f6"], ["a7", "d7", "g7"]
        ]
        for mill in mills:
            if target in mill:
                mill_count = sum(1 for pos in mill if self.board[pos] == current_color)
                if mill_count == 3:
                    move_count = 0
                    return True
        return False

    def is_valid_move(self, source, target, remove):
        if target not in self.board or self.board[target] is not None:
            return False
        if source in ['h1', 'h2']:
            if source != ('h1' if self.turn == "blue" else 'h2'):
                return False
        elif source not in self.board or self.board[source] != self.turn:
            return False

        if self.players[self.turn]["stone_count"] > 3 and not self.check_correct_step(source, target):
            return False
        
        if remove != "r0":
            if remove not in self.board or self.board[remove] is None or self.board[remove] == self.turn:
                return False
            if not self.is_mill(source, target):
                return False
        # Player must remove an opponents stone if a mill is formed
        elif self.is_mill(source, target):
            return False
        return True

    def check_correct_step(self, source, target):
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

    def make_move(self, move):
        source, target, remove = move.split()
        if not source or not target or not remove:
            print("Invalid move")
            sys.exit(0)
        if self.is_valid_move(source, target, remove):
            self.execute_move(source, target, remove)

    def execute_move(self, source, target, remove):
        self.board[target] = self.turn
        if source.startswith('h'):
            self.players[self.turn]["stone_count"] -= 1
        else:
            self.board[source] = None
        if remove != "r0":
            self.board[remove] = None
        self.switch_turn()

    def simulate_move(self, move):
        new_game = copy.deepcopy(self)
        new_game.make_move(move)
        return new_game

    def actions(self, board):
        possible_moves = []
        # Moves from hand
        if self.players[self.turn]["stone_count"] > 0:
            for pos in board:
                # if the board position is not populated
                if self.board[pos] is None:
                    # add a move where you place a stone there
                    move = f"h{1 if self.turn == 'blue' else 2} {pos} r0"
                    # if placing a stone here results in a mill
                    if self.is_mill(f"h{1 if self.turn == 'blue' else 2}", pos):
                        # calculate all the stones you can remove
                        for remove in board:
                            if self.board[remove] is not None and self.board[remove] != self.turn:
                                possible_moves.append(f"{1 if self.turn == 'blue' else 2} {pos} {remove}")
                    else:
                        # if it is not a mill, then simply append the normal move
                        possible_moves.append(move)
            for source in board:
                # if the board position is not populated
                if self.board[source] == self.turn:
                    # add a move where you place a stone there
                    for target in self.board:
                        if self.check_correct_step(source, target):
                            move = f"{source} {target} r0"
                    # if placing a stone here results in a mill
                        if self.is_mill(source, target):
                            # calculate all the stones you can remove
                            for remove in board:
                                if self.board[remove] is not None and self.board[remove] != self.turn:
                                    possible_moves.append(f"{source} {target} {remove}")
                        else:
                            # if it is not a mill, then simply append the normal move
                            possible_moves.append(move)
        # flying phase
        elif self.players[self.turn]["stone_count"] == 3:
            for source in board:
                if self.board[source] == self.turn:
                    for target in self.board:
                        if self.board[target] is None:
                            move = f"{source} {target} r0"
                            if self.is_mill(source, target):
                                for remove in self.board:
                                    if self.board[remove] is not None and self.board[remove] != self.turn:
                                        possible_moves.append(f"{source} {target} {remove}")
                            else:
                                possible_moves.append(move)
        return possible_moves if possible_moves else None










    def is_terminal(self, board, depth):
        if depth == 15:
            return True
        if self.players["blue"]["stone_count"] == 2 or self.players["orange"]["stone_count"] == 2:
            return True
        if self.actions(self.board) == None:
            return True
        if self.move_count == 20:
            return True

    def utility(self, board):
        if self.players["blue"]["stone_count"] == 2:
            return 100
        if self.players["orange"]["stone_count"] == 2:
            return -100
        if self.actions(self.board) is None and self.turn == "orange":
            return 100
        if self.actions(self.board) is None and self.turn == "blue":
            return -100
        if self.move_count == 20:
            return 0
        # evaluation, intial thought is since the main goal is to remove as many of the opponents pieces from the board,
        # give states that give me a greater difference between both players stone count a larger value
        return self.players["blue"]["stone_count"] - self.players["orange"]["stone_count"]
        # will be negative for states favorable to orange and positive for blue, this aligns with the minimax algo

    def main(self):
        # Read initial color/symbol
        player_id = input().strip()
        a = -math.inf
        b = math.inf
        player_token = "blue"
        opponent_token = "orange"
        if player_id == "blue":
            player_turn = True
        elif player_id == "orange":
            player_turn = False
        else:
            print("Please enter a valid player name. Either 'blue' or 'orange'")
            sys.exit(0)
        while True:
            # if I am X, produce the first move
            try:
                if not player_turn:
                    # collect move
                    game_input = input().strip()
                else:
                    start_time = time.time()
                    # Your move logic here
                    move = self.minimax(self.board, a, b)
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    # check if move was made in time
                    if elapsed_time > 5:
                        print("Time limit exceeded")
                        sys.exit(0)

                    # check if move is valid
                    print(move, flush=True)
                    # no longer our players turn
                    player_turn = False

            except EOFError:
                break


    if __name__ == "__main__":
        main()