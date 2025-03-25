import chess
import chess.engine
import subprocess
import json

class ChessOpeningTrainer:
    def __init__(self, engine_path="stockfish", ollama_model="gemma3:12b"):
        """
        Initializes the Chess Opening Trainer.

        Args:
            engine_path: Path to the Stockfish chess engine executable.
            ollama_model: The name of the Ollama model to use.
        """
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)
        except FileNotFoundError:
            print(f"Error: Chess engine not found at {engine_path}. Please provide the correct path.")
            exit()
        self.board = chess.Board()
        self.ollama_model = ollama_model

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

    def get_llm_explanation(self, board, best_move):
        """
        Gets an explanation from the LLM about the move's intuition.

        Args:
            board: The current chess board state.
            best_move: The best move suggested by the engine.

        Returns:
            A string containing the LLM's explanation.
        """
        try:
            # Convert the board to FEN notation
            fen = board.fen()

            # Construct the prompt for the LLM
            prompt = f"""You are a chess expert. Explain the intuition behind the following move in the given chess position.
            Position (FEN): {fen}
            Move: {best_move.uci()}
            Explain the strategic idea behind this move, including possible future plans and threats.  Be concise and clear.
            """

            # Run the Ollama model using subprocess
            command = f"ollama run --json {self.ollama_model} '{prompt}'"
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            try:
                response_json = json.loads(stdout.decode('utf-8'))
                llm_explanation = response_json.get('response', '')
            except json.JSONDecodeError:
                llm_explanation = f"Error decoding LLM response: {stdout.decode('utf-8')}"
                print(f"LLM Error: {llm_explanation}")
                return "Could not retrieve LLM explanation."

            return llm_explanation

        except FileNotFoundError:
            return "Error: Ollama not found. Please ensure Ollama is installed and running."
        except Exception as e:
            return f"Error communicating with LLM: {e}"

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

                        best_move, engine_explanation = self.get_best_move_with_explanation(self.board)
                        print(f"Engine Suggests: {best_move.uci()} - {engine_explanation}")

                        llm_explanation = self.get_llm_explanation(self.board, best_move)
                        print(f"LLM Explanation: {llm_explanation}")

                    except ValueError:
                        print("Invalid move format. Please use UCI format (e.g., e2e4).")
                    except Exception as e:
                        print(f"An unexpected error occurred: {e}")

            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

        self.engine.quit()


if __name__ == "__main__":
    # Ensure Ollama is installed and running before running this script.
    trainer = ChessOpeningTrainer()
    trainer.run()