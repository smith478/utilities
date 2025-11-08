import chess
import requests
import json
import sys
import argparse

class ChessTutor:
    def __init__(self, ollama_model):
        self.board = chess.Board()
        self.ollama_model = ollama_model
        self.ollama_base_url = "http://localhost:11434/api/chat"
        self.message_history = []

        try:
            response = requests.get("http://localhost:11434/")
            if response.status_code != 200:
                print("Warning: Ollama does not seem to be running.")
        except requests.ConnectionError:
            print("Error: Could not connect to Ollama. Ensure it's running.")
            sys.exit(1)

    def get_llm_analysis(self, prompt):
        self.message_history.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.ollama_model,
            "messages": self.message_history,
            "stream": False,
        }

        try:
            response = requests.post(self.ollama_base_url, json=payload)
            if response.status_code == 200:
                response_json = response.json()
                llm_response = response_json['message']['content']
                self.message_history.append({"role": "assistant", "content": llm_response})
                return llm_response
            else:
                return f"Ollama Analysis Error: {response.text}"
        except Exception as e:
            return f"Error in Ollama analysis: {str(e)}"

    def run(self):
        print("Welcome to the Chess Tutor!")
        print("Enter moves in algebraic notation (e.g., e4, Nf3).")
        print("Type 'board' to see the current board.")
        print("Type 'reset' to start a new game.")
        print("Type 'quit' to exit.")

        while True:
            user_input = input("> ")

            if user_input.lower() == 'quit':
                break
            elif user_input.lower() == 'board':
                print(self.board)
                continue
            elif user_input.lower() == 'reset':
                self.board.reset()
                self.message_history = []
                print("Board reset.")
                continue

            try:
                self.board.push_san(user_input)
                print(self.board)
                prompt = f"The current board state is in FEN format: {self.board.fen()}. What are the best moves and the general strategy from this position?"
                analysis = self.get_llm_analysis(prompt)
                print(f"\nAnalysis:\n{analysis}")
            except ValueError:
                prompt = f"The current board state is in FEN format: {self.board.fen()}. The user asked the following question: {user_input}"
                analysis = self.get_llm_analysis(prompt)
                print(f"\nAnalysis:\n{analysis}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chess Tutor using Ollama LLM.")
    parser.add_argument("--model", type=str, default="gemma3:latest",
                        help="Specify the Ollama model to use (e.g., gemma3:latest)")
    args = parser.parse_args()

    tutor = ChessTutor(ollama_model=args.model)
    tutor.run()
