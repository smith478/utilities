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
        # Default paths for different operating systems
        default_paths = {
            'win32': [
                'stockfish.exe', 
                r'C:\Program Files\Stockfish\stockfish.exe',
                os.path.expanduser(r'~\Downloads\stockfish\stockfish.exe')
            ],
            'darwin': [
                '/Applications/Stockfish.app/Contents/MacOS/stockfish',
                '/usr/local/bin/stockfish',
                os.path.expanduser('~/Downloads/stockfish')
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
            print("Please provide the correct path to the Stockfish executable.")
            print("You can download it from: https://stockfishchess.org/download/")
            sys.exit(1)

        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)
        except Exception as e:
            print(f"Error initializing Stockfish: {e}")
            sys.exit(1)
        
        self.board = chess.Board()

    def get_best_move_with_explanation(self, board):
        """
        Gets the best move from the engine and provides a brief explanation.

        Args:
            board: The current chess board state.

        Returns:
            A tuple containing the best move and a short explanation.
        """
        try:
            # Increase time limit and add depth for more reliable analysis
            result = self.engine.play(board, chess.engine.Limit(time=0.5, depth=15))
            best_move = result.move
            
            # Get more detailed information about the move
            info = self.engine.analyse(board, chess.engine.Limit(depth=15))
            score = info.get("score", chess.engine.PovScore(chess.engine.Mate(0), chess.WHITE))
            
            # Generate a more informative explanation
            if isinstance(score.relative, chess.engine.Mate):
                mate_in = score.relative.moves
                explanation = f"Forced mate in {mate_in} moves!" if mate_in > 0 else "Avoiding mate!"
            else:
                cp_score = score.relative.score()
                if cp_score > 50:
                    explanation = "Strong move improving position significantly."
                elif cp_score > 20:
                    explanation = "Good move with a slight positional advantage."
                elif cp_score > -20:
                    explanation = "Balanced move maintaining the current position."
                elif cp_score > -50:
                    explanation = "Defensive move to minimize disadvantage."
                else:
                    explanation = "Challenging position, requires careful play."

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

                opponent_color = "white" if color == "black" else "black"
                print(f"Your color: {color.capitalize()}")
                print(f"Opponent's color: {opponent_color.capitalize()}")

                self.board.reset()  # Ensure a fresh board for each session
                if color == "black":
                    self.board.turn = chess.BLACK

                print("\nEnter moves in UCI format (e.g., e2e4).")
                print("Legal moves will show board state and engine analysis.")

                while True:
                    # Print current board state
                    print("\nCurrent board:")
                    print(self.board)

                    move_str = input("Enter move: ").lower()

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
                        
                        # Computer's response
                        best_move, explanation = self.get_best_move_with_explanation(self.board)
                        if best_move:
                            self.board.push(best_move)
                            print(f"\nEngine move: {best_move.uci()} - {explanation}")
                            print("Updated board:")
                            print(self.board)

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