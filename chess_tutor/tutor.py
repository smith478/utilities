import chess
import chess.engine
import os
import sys

class ChessOpeningTrainer:
    def __init__(self, engine_path=None):
        """
        Initializes the Chess Opening Trainer.

        Args:
            engine_path: Path to the Stockfish chess engine executable.
        """
        # Expanded default paths including Homebrew location
        default_paths = {
            'darwin': [
                '/opt/homebrew/bin/stockfish',  # Homebrew on Apple Silicon Macs
                '/usr/local/bin/stockfish',     # Homebrew on Intel Macs
                '/Applications/Stockfish.app/Contents/MacOS/stockfish',
                os.path.expanduser('~/Downloads/stockfish'),
                os.path.expanduser('~/stockfish')
            ],
            'win32': [
                'stockfish.exe', 
                r'C:\Program Files\Stockfish\stockfish.exe',
                os.path.expanduser(r'~\Downloads\stockfish\stockfish.exe')
            ],
            'linux': [
                '/usr/local/bin/stockfish',
                '/usr/bin/stockfish',
                os.path.expanduser('~/stockfish/stockfish')
            ]
        }

        # If no path provided, try default paths
        if not engine_path:
            paths_to_try = default_paths.get(sys.platform, [])
            for path in paths_to_try:
                if os.path.exists(path):
                    engine_path = path
                    break
        
        # Validate engine path
        if not engine_path or not os.path.exists(engine_path):
            print(f"Error: Could not find Stockfish chess engine.")
            print("Possible solutions:")
            print("1. Ensure Stockfish is installed")
            print("2. Provide the correct path to the Stockfish executable")
            print("3. Install via Homebrew: 'brew install stockfish'")
            print("Download link: https://stockfishchess.org/download/")
            sys.exit(1)

        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)
            print(f"Stockfish initialized from: {engine_path}")
        except Exception as e:
            print(f"Error initializing Stockfish: {e}")
            sys.exit(1)
        
        self.board = chess.Board()
        self.player_color = None

    def get_best_move_with_explanation(self, board, color):
        """
        Gets the best move from the engine and provides a brief explanation.

        Args:
            board: The current chess board state.
            color: Color to analyze (chess.WHITE or chess.BLACK)

        Returns:
            A tuple containing the best move and a short explanation.
        """
        try:
            # Analyze from the perspective of the current player
            result = self.engine.analyse(
                board, 
                chess.engine.Limit(time=0.5, depth=15),
                game=board
            )
            
            # Get the score and move
            score = result.get("score")
            best_move = result.get("pv")[0]  # Best principal variation move
            
            # Generate explanation based on score
            if isinstance(score.relative, chess.engine.Mate):
                mate_in = score.relative.moves
                explanation = f"Forced mate in {mate_in} moves!" if mate_in > 0 else "Avoiding mate!"
            else:
                cp_score = score.relative.score()
                if abs(cp_score) > 100:
                    advantage = "significant" if cp_score > 0 else "significant disadvantage"
                    direction = "improving" if cp_score > 0 else "worsening"
                    explanation = f"Move {direction} position with a {advantage}."
                elif abs(cp_score) > 50:
                    advantage = "slight" if cp_score > 0 else "slight disadvantage"
                    direction = "improving" if cp_score > 0 else "worsening"
                    explanation = f"Move {direction} position with a {advantage}."
                else:
                    explanation = "Balanced move maintaining the current position."

            return best_move, explanation

        except Exception as e:
            print(f"Error analyzing move: {e}")
            return None, "Unable to analyze move."

    def run(self):
        """
        Runs the interactive chess opening trainer.
        """
        print("Welcome to the Chess Opening Trainer!")
        print("Type 'quit' at any time to exit.")
        print("Type 'help' for command list.")

        while True:
            try:
                color = input("Enter your color (white/black): ").lower()
                if color not in ("white", "black"):
                    print("Invalid color. Please enter 'white' or 'black'.")
                    continue

                self.player_color = chess.WHITE if color == "white" else chess.BLACK
                opponent_color = chess.BLACK if color == "white" else chess.WHITE

                print(f"Your color: {color.capitalize()}")
                print(f"Opponent's color: {opponent_color}")

                self.board.reset()  # Ensure a fresh board for each session
                
                # If playing black, prompt for first white move or suggest
                if self.player_color == chess.BLACK:
                    print("\nSuggested first move for White:")
                    best_first_move, explanation = self.get_best_move_with_explanation(self.board, chess.WHITE)
                    print(f"Stockfish suggests: {best_first_move.uci()} - {explanation}")

                print("\nEnter moves in UCI format (e.g., e2e4).")
                print("Legal moves will show board state and engine analysis.")

                while True:
                    # Print current board state
                    print("\nCurrent board:")
                    print(self.board)

                    # Determine whose turn it is
                    current_color = "White" if self.board.turn == chess.WHITE else "Black"
                    print(f"\n{current_color}'s turn:")

                    # Handle moves based on whether it's the player's turn
                    if self.board.turn == self.player_color:
                        move_str = input("Enter your move: ").lower()

                        if move_str == 'quit':
                            print("Exiting...")
                            return
                        
                        if move_str == 'help':
                            print("\nCommands:")
                            print("- Enter moves in UCI format (e.g., e2e4)")
                            print("- 'quit' to exit the program")
                            print("- 'help' to show this menu")
                            continue

                        try:
                            move = self.board.parse_uci(move_str)
                            if move not in self.board.legal_moves:
                                print("Illegal move. Please enter a valid move.")
                                continue

                            self.board.push(move)
                            
                            # Suggest opponent's best move
                            best_move, explanation = self.get_best_move_with_explanation(self.board, self.board.turn)
                            print(f"\nRecommended {current_color} move by Stockfish: {best_move.uci()} - {explanation}")

                        except ValueError:
                            print("Invalid move format. Please enter moves in UCI format (e.g., e2e4).")
                    else:
                        # If it's not the player's turn, get the opponent's best move
                        print("Waiting for opponent's move. Enter the move you want to follow.")
                        move_str = input("Enter opponent's move: ").lower()

                        try:
                            move = self.board.parse_uci(move_str)
                            if move not in self.board.legal_moves:
                                print("Illegal move. Please enter a valid move.")
                                continue

                            self.board.push(move)
                            
                            # Suggest player's best move
                            best_move, explanation = self.get_best_move_with_explanation(self.board, self.board.turn)
                            print(f"\nStockfish suggests your next move: {best_move.uci()} - {explanation}")

                        except ValueError:
                            print("Invalid move format. Please enter moves in UCI format (e.g., e2e4).")

            except KeyboardInterrupt:
                print("\nExiting...")
                break

        # Ensure engine is closed
        self.engine.quit()


if __name__ == "__main__":
    trainer = ChessOpeningTrainer()
    trainer.run()