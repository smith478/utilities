import chess
import ollama
from tutor import ChessOpeningTrainer

class OllamaChessTutor(ChessOpeningTrainer):
    def __init__(self, engine_path=None, ollama_model="gemma3:270m"):
        """
        Initializes the Ollama Chess Tutor.

        Args:
            engine_path: Path to the Stockfish chess engine executable.
            ollama_model: The name of the Ollama model to use for explanations.
        """
        super().__init__(engine_path)
        self.ollama_model = ollama_model
        try:
            # Check if the model is available
            ollama.show(self.ollama_model)
            print(f"Ollama model '{self.ollama_model}' is available.")
        except Exception as e:
            print(f"Error with Ollama model '{self.ollama_model}': {e}")
            print("Please ensure the model is available in Ollama.")
            exit(1)

    def get_best_move_with_explanation(self, board, color):
        """
        Gets the best move from the engine and provides a detailed explanation from an LLM.

        Args:
            board: The current chess board state.
            color: Color to analyze (chess.WHITE or chess.BLACK)

        Returns:
            A tuple containing the best move and a detailed explanation.
        """
        # Get the best move from Stockfish
        best_move, stockfish_explanation = super().get_best_move_with_explanation(board, color)

        if not best_move:
            return None, "Unable to get best move from Stockfish."

        # Generate a more detailed explanation using Ollama
        try:
            move_history = " ".join([move.uci() for move in board.move_stack])
            prompt = (
                f"Given the following chess position (FEN: {board.fen()}) "
                f"and the move history ({move_history}), Stockfish suggests the move {best_move.uci()}. "
                f"Explain the strategic thinking behind this move. What is the main idea, "
                f"and what are the potential plans or tactics that this move enables? "
                f"Keep the explanation concise and focused on the strategy for a beginner."
            )

            response = ollama.generate(
                model=self.ollama_model,
                prompt=prompt
            )
            
            llm_explanation = response['response']
            return best_move, llm_explanation

        except Exception as e:
            print(f"Error getting explanation from Ollama: {e}")
            return best_move, f"Stockfish explanation: {stockfish_explanation}"

if __name__ == "__main__":
    # You can specify the model when you run the script, e.g., python tutor_ollama.py model_name
    import sys
    model_name = "gemma3:270m"
    if len(sys.argv) > 1:
        model_name = sys.argv[1]
    
    trainer = OllamaChessTutor(ollama_model=model_name)
    trainer.run()
