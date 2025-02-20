
# **Lasker-Morris AI with Minimax, Alpha-Beta Pruning, and Local Beam Search**

**📋 Project Overview:**  
This project implements an AI capable of playing Lasker-Morris using the Minimax algorithm enhanced with Alpha-Beta pruning for efficient decision-making. Additionally, the AI integrates **local beam search** to improve move selection by exploring multiple states simultaneously, focusing on the top candidates at each depth. The AI evaluates possible moves using a heuristic evaluation function and optimizes search with a priority queue.

**🚀 Key Features:**
- **Minimax Algorithm**: Implements depth-limited search to simulate decision-making.
- **Alpha-Beta Pruning**: Reduces the number of nodes evaluated in the game tree, optimizing performance.
- **Local Beam Search**: Explores multiple states at each level, keeping track of the top candidates for further exploration.
- **Heuristic Evaluation**: Uses a custom evaluation function to intelligently prioritize moves.
- **Priority Queue**: Selects the best moves by evaluating the top 5 candidates at each level.
- **CLI Interface**: Provides an easy way for users to interact with the AI and test different scenarios.

**🛠️ Installation & Setup:**  
1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd Lasker-Morris-AI
   ```
2. Run the program:
   ```bash
   python Lebron.py 
   ```

**🧠 How It Works:**
- **Initialization**: The AI loads the game state from the provided input file.
- **Move Generation**: The AI generates all possible moves for the current state.
- **Evaluation**: Each move is scored using a heuristic function that evaluates material, strategic advantage, and potential for victory.
- **Minimax with Alpha-Beta**: Simulates future moves and chooses the optimal move based on the minimax algorithm, with Alpha-Beta pruning to reduce unnecessary evaluations.
- **Local Beam Search**: Explores multiple potential move sequences simultaneously and focuses on the most promising paths based on the heuristic evaluation.

**🧮 Evaluation Function**:  
- **Stone Count Difference**: Measures the relative advantage of pieces between players.
- **Mills Formed**: Assigns a high weight to moves that create mills, which is a critical factor for victory.
- **Board Control**: Assesses the player's positioning and control over the board.

**📈 Performance:**
- **Against Human Players**: Demonstrates competitive performance, securing wins or stalemates.
- **Self-Play Testing**: Utilized for tuning the evaluation function and improving the AI's playstyle.
- **Benchmarking**: Compared against other AI implementations to evaluate its effectiveness.

**👥 Team Members:**
- **Julian Espinal**:
- Implemented the Minimax algorithm, Alpha-Beta pruning, local beam search, and heuristic evaluation function.
- Conducted testing and analysis. Conducted extensive testing to refine the AI's performance and ensure accuracy

