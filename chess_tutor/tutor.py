import chess
import chess.engine

class ChessOpeningTrainer:
    def __init__(self, engine_path="stockfish"):  # Replace with your Stockfish path
        """
        Initializes the Chess Opening Trainer.

        Args:
            engine_path: Path to the Stockfish chess engine executable.
        """
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)
        except FileNotFoundError:
            print(f"Error: Chess engine not found at {engine_path}.  Please provide the correct path.")
            exit()
        self.board = chess.Board()

    def get_best_move_with_explanation(self, board):
        """
        Gets the best move from the engine and provides a brief explanation.

        Args:
            board: The current chess board state.

        Returns:
            A tuple containing the best move and a short explanation.
        """
        result = self.engine.play(board, chess.engine.Limit(time=2.0))  # Adjust time limit as needed
        best_move = result.move
        
        # Get evaluation (optional, but helpful for understanding)
        evaluator = chess.engine.Evaluator(self.engine)
        evaluation = evaluator.get_score(board)
        
        if evaluation > 0:
            explanation = "Engine suggests this move. It improves your position."
        elif evaluation < 0:
            explanation = "Engine suggests this move. It defends against opponent's threat."
        else:
            explanation = "Engine suggests this move. It maintains the position."

        return best_move, explanation

    def run(self):
        """
        Runs the interactive chess opening trainer.
        """
        print("Welcome to the Chess Opening Trainer!")

        while True:
            try:
                color = input("Enter your color (white/black): ").lower()
                if color not in ("white", "black"):
                    print("Invalid color. Please enter 'white' or 'black'.")
                    continue

                opponent_color = "white" if color == "black" else "black"
                print(f"Opponent's color: {opponent_color}")

                if color == "white":
                    self.board.turn = chess.WHITE
                else:
                    self.board.turn = chess.BLACK

                print("Enter moves in UCI format (e.g., e2e4). Type 'quit' to exit.")

                while True:
                    move_str = input("Enter move: ").lower()

                    if move_str == "quit":
                        print("Exiting...")
                        break

                    try:
                        move = self.board.parse_uci(move_str)
                        if move not in self.board.legal_moves:
                            print("Illegal move. Please enter a valid move.")
                            continue

                        self.board.push(move)
                        print(self.board)

                        best_move, explanation = self.get_best_move_with_explanation(self.board)
                        print(f"Engine suggests: {best_move.uci()} - {explanation}")
                        print()

                    except ValueError:
                        print("Invalid move format. Please enter moves in UCI format (e.g., e2e4).")
            except KeyboardInterrupt:
                print("\nExiting...")
                break

        self.engine.quit()


if __name__ == "__main__":
    # Replace "stockfish" with the actual path to your Stockfish executable
    trainer = ChessOpeningTrainer(engine_path="stockfish")
    trainer.run()