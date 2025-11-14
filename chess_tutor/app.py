import chess
import chess.engine
import os
import sys
import ollama
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

class OllamaChessTutor:
    def __init__(self, engine_path=None, ollama_model="gemma3:270m", use_ollama=True):
        # Another good default model is "qwen3:8b", also consider a larger gemma3, or gpt-oss
        self.use_ollama = use_ollama
        default_paths = {
            'darwin': [
                '/opt/homebrew/bin/stockfish',
                '/usr/local/bin/stockfish',
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

        if not engine_path:
            paths_to_try = default_paths.get(sys.platform, [])
            for path in paths_to_try:
                if os.path.exists(path):
                    engine_path = path
                    break
        
        if not engine_path or not os.path.exists(engine_path):
            raise Exception("Could not find Stockfish chess engine.")

        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)
        except Exception as e:
            raise Exception(f"Error initializing Stockfish: {e}")
        
        self.ollama_model = ollama_model
        if self.use_ollama:
            try:
                print(f"Checking for Ollama model: {self.ollama_model}")
                ollama.show(self.ollama_model)
                print(f"Ollama model '{self.ollama_model}' is available and will be used for explanations.")
            except Exception as e:
                raise Exception(f"Error with Ollama model '{self.ollama_model}': {e}")

    def get_best_move_with_explanation(self, board):
        try:
            result = self.engine.analyse(
                board, 
                chess.engine.Limit(time=0.5, depth=15),
                game=board
            )
            
            best_move = result.get("pv")[0]

            if not self.use_ollama:
                return best_move, ""
            
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
            return None, f"Error analyzing move: {e}"

    def close_engine(self):
        self.engine.quit()

tutor = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    global tutor
    if not tutor:
        return jsonify({'error': 'Tutor not initialized'}), 500

    fen = request.json.get('fen')
    if not fen:
        return jsonify({'error': 'FEN string not provided'}), 400
        
    try:
        board = chess.Board(fen)
        best_move, explanation = tutor.get_best_move_with_explanation(board)
        
        if best_move:
            return jsonify({
                'best_move': best_move.uci(),
                'explanation': explanation
            })
        else:
            return jsonify({'error': 'Could not get analysis'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    use_ollama_flag = True
    if "--no-ollama" in sys.argv:
        use_ollama_flag = False
        print("Running without Ollama explanations.")

    try:
        tutor = OllamaChessTutor(use_ollama=use_ollama_flag)
        app.run(debug=True)
    except Exception as e:
        print(f"Failed to start the application: {e}")
    finally:
        if tutor:
            tutor.close_engine()