import sys
import copy
import math

class LaskerMorris:
    def __init__(self):
        self.players = {"blue": {"stone_count": 10, "stone_positions": set()},
                        "orange": {"stone_count": 10, "stone_positions": set()}}
        self.board = {key: None for key in ["a1", "a4", "a7", "b2", "b4", "b6", "c3", "c4",
                                            "c5", "d1", "d2", "d3", "d5", "d6", "d7", "e3",
                                            "e4", "e5", "f2", "f4", "f6", "g1", "g4", "g6"]}
        self.turn = "blue"



    def minimax(self, a, b):
        value, move = self.max_value(self.board, a, b)
        return move

    def max_value(self, a, b, current_turn):
        # check if game is in a terminal state, if it is then return the utility value
        if self.is_terminal(self.board):
            return self.utility(self.board), None
    
        v = -math.inf
        move = ""
    
        for action in self.actions(self.board):
            new_game = self.simulate_move(action)
            v2, a2 = self.min_value(new_game, a, b)  # Swap player
            if v2 > v:
                v, move = v2, action
                a = max(a, v)
            if v >= b:
                return v, move
        return v, move



    def min_value(self, a, b):
        # check if game is terminal, if so return utility
        if self.is_terminal(self.board):
            return self.utility(self.board), None
    
        v = math.inf
        move = ""
        for action in self.actions(self.board):
            # make copy of game with move made to not change the actual game board
            new_game = self.simulate_move(action)
            v2, a2 = self.max_value(new_game, a, b)  # Swap player
            if v2 < v:
                v, move = v2, action
                b = min(b, v)
            if v <= a:
                return v, move
        return v, move

    def make_move(self, move):
        source, target, remove = move.split()
        if not source or not target or not remove:
            print("Invalid move")
            sys.exit(0)
        if self.is_valid_move(source, target, remove):
            self.execute_move(source, target, remove)

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
        pass

    def is_terminal(self, board):
        pass

    def utility(self, board):
        pass

