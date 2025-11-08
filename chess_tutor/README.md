# Chess Tutor

This program allows you to play a game of chess and ask for analysis and strategic advice from an AI chess tutor powered by Ollama.

## Setup

1.  **Install Ollama:** Make sure you have Ollama installed and running. You can find instructions here: [https://ollama.ai/](https://ollama.ai/)

2.  **Set up the virtual environment:** This project uses `uv` to manage the virtual environment. To set it up, run the following commands:

    ```bash
    uv venv
    source .venv/bin/activate
    uv pip install -r requirements.txt
    ```

3.  **Run the tutor:**

    ```bash
    python tutor_ollama.py [--model <ollama_model_name>]
    ```

    For example, to use the `gemma3:12b` model:
    ```bash
    python tutor_ollama.py --model gemma3:12b
    python tutor_ollama.py --model qwen3:8b
    ```

## How to Use

-   Enter moves in algebraic notation (e.g., `e4`, `Nf3`).
-   After each move, the program will provide an analysis of the position.
-   You can also ask questions directly, for example: "What is the best move for black?" or "What is the idea behind moving my knight to f3?".
-   Type `board` to see the current board position.
-   Type `reset` to start a new game.
-   Type `quit` to exit the program.
