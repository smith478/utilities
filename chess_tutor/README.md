# Chess Tutor

This program allows you to play a game of chess and ask for analysis and strategic advice from an AI chess tutor powered by Ollama.

## Setup

1.  **Install Ollama:** Make sure you have Ollama installed and running. You can find instructions here: [https://ollama.ai/](https://ollama.ai/)

2.  **Install Stockfish:** You need to have the Stockfish chess engine installed. You can download it from the official website: [https://stockfishchess.org/download/](https://stockfishchess.org/download/)

    On macOS, you can install it using Homebrew:
    ```bash
    brew install stockfish
    ```

3.  **Set up the virtual environment:** This project uses `uv` to manage the virtual environment. To set it up, run the following commands:

    ```bash
    uv venv
    source .venv/bin/activate
    uv pip install -r requirements.txt
    ```

4.  **Run the application:**

    ```bash
    python app.py
    ```

    Then open your web browser and go to `http://127.0.0.1:5000`.

## How to Use

-   The application will open a web-based UI.
-   You can play chess by clicking and dragging the pieces on the board.
-   After each of your moves, the computer will make a move based on Stockfish's recommendation.
-   The UI will display Stockfish's suggested move and an explanation from the LLM.
-   You can use the "Undo" button to take back your last move.

## TODO 

- Ability to ask about quality of a potential move
- Add ASR/STT components
