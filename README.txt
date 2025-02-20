The names of the members of your group. A detailed description of what each teammate contributed to the project.
Names: Julian Espinal and Maxwell Jeronimo
Julian Espinal:
Evaluation function
heuristic Strategy
Extensive testing
Minimax function
Max jeronimo:
Game logic
Player structure/logic
Extensive testing
Instructions on compiling and running your program.
running program: python Lebron.py
running program with referee:
cs4341-referee laskermorris -p1 "python Lebron.py" -p2 "python Lebron.py" --visual --debug --log
The utility function that your program uses.
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
        return heuristic(game)

The evaluation function that your program uses.
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

The heuristics and/or strategies that you employed to decide how to expand nodes of the minimax tree without exceeding your time limit.
- we propogate up utility values at the MAX_DEPTH
- we test our evaluation function on each leaf node, push them onto a priority queue and only pick the top 5 nodes to explore (Local Beam Search)
Results:
describe which tests you ran to try out your program. Did your program play against human players? Did your program play against itself? Did your program play against other programs? How did your program do during those games?
- The program was ran by itself fot test against the both of us playing
- Was also ran against itself using the referee
describe the strengths and the weaknesses of your program.
- Seems to make the most optimal moves for winning which is continuously making a mill and moving back and forth to keep removing opponent stones
- A weakness it would have would be against programs that can go deeper in the tree, or ones that have better evaluation functions
- Additionally, the strategy of forming the mill and continuously removing opponent stones is good, but if both players play in this way it is highly dependent on who goes first as to who wins
A discussion of why the evaluation function and the heuristic(s) you picked are good choices.
The chosen evaluation function and heuristics are effective because they:
Eval:
    Prioritizes Winning Conditions: Mills are weighted heavily to push toward victory.
    Balance Short and Long-Term Goals: Stone count and board control support both immediate and future advantages.
Efficient Node Expansion: The use of a priority queue with alpha-beta pruning ensures that the most promising moves are evaluated first,
keeping within the time limit while maximizing decision quality.