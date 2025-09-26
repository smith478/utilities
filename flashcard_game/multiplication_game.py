import random
import time
import tkinter as tk
from tkinter import messagebox, font
import json
from datetime import datetime

DEFAULT_CHALLENGE_PROBLEMS = 5
DEFAULT_STANDARD_PROBLEMS = 5
CHALLENGE_NUMBERS = {3, 4, 6, 7, 8, 9}


class MultiplicationFlashCards:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Multiplication Flash Cards! ✨")
        self.window.geometry("800x600")
        self.window.configure(bg="#E6F3FF")  # Light blue background
        
        self.score = 0
        self.problem_count = 0
        self.max_problems = DEFAULT_CHALLENGE_PROBLEMS + DEFAULT_STANDARD_PROBLEMS
        self.current_problem = None
        self.start_time = None
        self.challenge_problems_count = 0
        self.standard_problems_count = 0
        
        # Vibrant button styles - purple theme for multiplication
        self.button_bg = "#8A2BE2"  # Blue violet
        self.button_fg = "white"    # White text
        self.button_active_bg = "#9932CC"  # Dark orchid
        
        self.setup_gui()
        self.load_leaderboard()
        self.show_start_screen()  # Show the initial start screen

    def show_start_screen(self):
        """Display the initial start screen for the game."""
        # Destroy existing widgets if they exist
        if hasattr(self, 'setup_frame'):
            self.setup_frame.destroy()
        if hasattr(self, 'name_frame'):
            self.name_frame.destroy()
        if hasattr(self, 'start_button'):
            self.start_button.destroy()
        if hasattr(self, 'leaderboard_button'):
            self.leaderboard_button.destroy()

        # Max number entry
        self.setup_frame = tk.Frame(self.window, bg="#D8BFD8", relief=tk.RIDGE, borderwidth=2)
        self.max_num_label = tk.Label(self.setup_frame, text="Highest number to multiply (1-12):", 
                 font=("Arial", 14), bg="#D8BFD8", fg="#4B0082")
        self.max_num_label.pack(side=tk.LEFT)
        self.max_num_entry = tk.Entry(self.setup_frame, font=("Arial", 14))
        self.max_num_entry.pack(side=tk.LEFT, padx=10)
        self.max_num_entry.insert(0, "9")
        
        # Name entry
        self.name_frame = tk.Frame(self.window, bg="#D8BFD8")
        self.name_label = tk.Label(self.name_frame, text="Your name:", 
                 font=("Arial", 14), bg="#D8BFD8", fg="#4B0082")
        self.name_label.pack(side=tk.LEFT)
        self.name_entry = tk.Entry(self.name_frame, font=("Arial", 14))
        self.name_entry.pack(side=tk.LEFT, padx=10)
        
        # Start button with bold, eye-catching style
        self.start_button = tk.Button(self.window, 
                                      text="Start Game!", 
                                      command=self.start_game, 
                                      font=("Arial", 16, "bold"),
                                      bg="dark turquoise", 
                                      fg="black",
                                      activebackground="turquoise",
                                      activeforeground="black",
                                      relief=tk.RAISED,
                                      borderwidth=5,
                                      padx=30, 
                                      pady=15)
        self.leaderboard_button = tk.Button(self.window, 
                                      text="Show Leaderboard", 
                                      command=self.show_leaderboard_popup, 
                                      font=("Arial", 16, "bold"),
                                      bg="dark turquoise", 
                                      fg="black",
                                      activebackground="turquoise",
                                      activeforeground="black",
                                      relief=tk.RAISED,
                                      borderwidth=5,
                                      padx=30, 
                                      pady=15)
        
        # Pack the title and start screen elements
        self.title_label.pack(pady=20)
        self.setup_frame.pack(pady=20)
        self.name_frame.pack(pady=10)
        self.start_button.pack(pady=20)
        self.leaderboard_button.pack(pady=10)

    def load_leaderboard(self):
        try:
            with open("multiplication_leaderboard.json", "r") as f:
                self.leaderboard = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.leaderboard = []

    def save_leaderboard(self):
        with open("multiplication_leaderboard.json", "w") as f:
            json.dump(self.leaderboard, f)

    def show_custom_leaderboard(self, title, leaderboard_text):
        leaderboard_window = tk.Toplevel(self.window)
        leaderboard_window.title(title)
        leaderboard_window.geometry("600x400")  # Set a fixed size for the window

        text_widget = tk.Text(leaderboard_window, wrap=tk.WORD, font=("Courier", 12))
        text_widget.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        text_widget.insert(tk.END, leaderboard_text)
        text_widget.config(state=tk.DISABLED)  # Make the text widget read-only

        close_button = tk.Button(leaderboard_window, text="Close", command=leaderboard_window.destroy)
        close_button.pack(pady=10)

    def show_end_game_dialog(self, score, correct_answers, total_time, leaderboard_text):
        dialog = tk.Toplevel(self.window)
        dialog.title("Game Over!")
        dialog.geometry("600x400")

        info_frame = tk.Frame(dialog)
        info_frame.pack(pady=10)

        tk.Label(info_frame, text=f"Final Score: {score}", font=("Arial", 14)).pack()
        tk.Label(info_frame, text=f"Correct Answers: {correct_answers}", font=("Arial", 14)).pack()
        tk.Label(info_frame, text=f"Total Time: {total_time:.1f} seconds", font=("Arial", 14)).pack()

        leaderboard_frame = tk.Frame(dialog)
        leaderboard_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        tk.Label(leaderboard_frame, text="🏆 Multiplication Leaderboard 🏆", font=("Arial", 16, "bold")).pack(pady=5)

        text_widget = tk.Text(leaderboard_frame, wrap=tk.WORD, font=("Courier", 12))
        text_widget.pack(expand=True, fill=tk.BOTH)

        text_widget.insert(tk.END, leaderboard_text)
        text_widget.config(state=tk.DISABLED)

        close_button = tk.Button(dialog, text="Close", command=dialog.destroy)
        close_button.pack(pady=10)

    def show_leaderboard_popup(self):
        """Display the leaderboard in a popup when the app starts."""
        if not self.leaderboard:
            leaderboard_text = "No high scores yet. Be the first to set one!"
        else:
            header = f"{'Rank':<5}{'Name':<15}{'Score':<10}{'Correct':<10}{'Time (s)':<10}\n{'-'*55}"
            leaderboard_entries = []
            for i, entry in enumerate(self.leaderboard):
                rank = f'{i+1}.'
                name = entry['name']
                score = entry['score']
                correct = entry.get('correct_answers', 'N/A')
                time_val = f"{entry['time']:.1f}"
                leaderboard_entries.append(f"{rank:<5}{name:<15}{score:<10}{correct:<10}{time_val:<10}")
            leaderboard_text = header + "\n" + "\n".join(leaderboard_entries)
        self.show_custom_leaderboard("Multiplication Leaderboard", leaderboard_text)

    def end_game(self):
        # Calculate total game time correctly
        total_time = time.time() - self.game_start_time
        
        # Add to leaderboard
        self.leaderboard.append({
            "name": self.player_name,
            "score": self.score,
            "correct_answers": self.correct_answers,
            "time": total_time,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        # Sort and keep top 10 scores
        self.leaderboard.sort(key=lambda x: x['score'], reverse=True)
        self.leaderboard = self.leaderboard[:10]
        self.save_leaderboard()
        
        # Build leaderboard text
        header = f"{'Rank':<5}{'Name':<15}{'Score':<10}{'Correct':<10}{'Time (s)':<10}\n{'-'*55}"
        leaderboard_entries = []
        for i, entry in enumerate(self.leaderboard):
            rank = f'{i+1}.'
            name = entry['name']
            score = entry['score']
            correct = entry.get('correct_answers', 'N/A')
            time_val = f"{entry['time']:.1f}"
            leaderboard_entries.append(f"{rank:<5}{name:<15}{score:<10}{correct:<10}{time_val:<10}")
        leaderboard_text = header + "\n" + "\n".join(leaderboard_entries)
        
        # Show results (this popup now includes the updated leaderboard)
        self.show_end_game_dialog(self.score, self.correct_answers, total_time, leaderboard_text)
        
        # Hide game elements
        self.hide_game_elements()
        # Instead of immediately repacking the start page elements, show a "New Game" button.
        if not hasattr(self, 'restart_frame'):
            self.restart_frame = tk.Frame(self.window, bg="#E6F3FF")
            self.new_game_button = tk.Button(self.restart_frame, 
                                             text="New Game", 
                                             command=self.restart_game,
                                             font=("Arial", 16, "bold"),
                                             bg="dark turquoise", 
                                             fg="black",
                                             activebackground="turquoise",
                                             activeforeground="black",
                                             relief=tk.RAISED,
                                             borderwidth=5,
                                             padx=30, 
                                             pady=15)
            self.new_game_button.pack(pady=20)
        self.restart_frame.pack(pady=20)

    def restart_game(self):
        """Hide the new game frame and show the start page to begin a new game."""
        self.restart_frame.pack_forget()
        self.show_start_screen()

    def start_game(self):
        try:
            self.max_num = int(self.max_num_entry.get())
            if self.max_num < 1 or self.max_num > 12:
                raise ValueError("Please enter a number between 1 and 12")
            self.player_name = self.name_entry.get().strip()
            if not self.player_name:
                raise ValueError("Please enter your name")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        # Hide setup elements and show game elements
        self.setup_frame.pack_forget()
        self.name_frame.pack_forget()
        self.start_button.pack_forget()
        self.leaderboard_button.pack_forget()
        self.hide_restart_frame()  # In case the restart frame is showing
        self.show_game_elements()
        # Set focus on the answer box immediately when game starts
        self.answer_entry.focus_set()

        # Initialize game state
        self.score = 0
        self.problem_count = 0
        self.correct_answers = 0
        self.challenge_problems_count = 0
        self.standard_problems_count = 0
        self.current_problem = None
        self.score_label.config(text="Score: 0")
        self.progress_label.config(text=f"Problem: 0/{self.max_problems}")
        
        # Create problem lists
        all_numbers = list(range(1, self.max_num + 1))
        challenge_numbers = list(CHALLENGE_NUMBERS)
        
        challenge_problems = []
        while len(challenge_problems) < DEFAULT_CHALLENGE_PROBLEMS:
            num1 = random.choice(challenge_numbers)
            num2 = random.choice(challenge_numbers)
            if num1 * num2 <= 100: # Optional: limit answer size
                challenge_problems.append((num1, num2))

        standard_problems = []
        while len(standard_problems) < DEFAULT_STANDARD_PROBLEMS:
            num1 = random.choice(all_numbers)
            num2 = random.choice(all_numbers)
            if not (num1 in CHALLENGE_NUMBERS and num2 in CHALLENGE_NUMBERS):
                standard_problems.append((num1, num2))

        self.problems = challenge_problems + standard_problems
        random.shuffle(self.problems)

        # Record the overall game start time
        self.game_start_time = time.time()
        self.generate_problem()

    def hide_restart_frame(self):
        """Hide the restart frame if it is visible."""
        if hasattr(self, 'restart_frame'):
            self.restart_frame.pack_forget()

    def run(self):
        self.window.mainloop()

    def setup_gui(self):
        # Title
        title_font = font.Font(family="Arial", size=24, weight="bold")
        self.title_label = tk.Label(self.window, text="Multiplication Flash Cards! ✨", 
                                    font=title_font, bg="#E6F3FF", fg="#4B0082")
        
        self.show_start_screen()
        
        # Problem display
        self.problem_label = tk.Label(self.window, text="", 
                                      font=("Arial", 36, "bold"), bg="#E6F3FF", fg="#4B0082")
        self.problem_label.pack(pady=20)
        
        
        
        # Answer entry frame and widget
        self.answer_frame = tk.Frame(self.window, bg="#E6F3FF")
        self.answer_frame.pack(pady=20)
        self.answer_entry = tk.Entry(self.answer_frame, font=("Arial", 24))
        self.answer_entry.pack(side=tk.LEFT, padx=10)
        self.answer_entry.bind('<Return>', lambda e: self.check_answer())
        
        # Feedback label
        self.feedback_label = tk.Label(self.window, text="", 
                                       font=("Arial", 18), 
                                       bg="#E6F3FF", 
                                       fg="green")
        self.feedback_label.pack(pady=10)
        
        # Submit button with bold, eye-catching style
        self.submit_btn = tk.Button(self.answer_frame, text="Submit", 
                                    command=self.check_answer, 
                                    font=("Arial", 16, "bold"),
                                    bg="dark turquoise", 
                                    fg="black",
                                    activebackground="turquoise",
                                    activeforeground="black",
                                    relief=tk.RAISED,
                                    borderwidth=5,
                                    padx=30, 
                                    pady=10)
        self.submit_btn.pack(side=tk.LEFT)
        
        # Score display
        self.score_label = tk.Label(self.window, text="Score: 0", 
                                    font=("Arial", 18), bg="#E6F3FF", fg="#4B0082")
        self.score_label.pack(pady=10)
        
        # Progress display
        self.progress_label = tk.Label(self.window, text="Problem: 0/10",
                                        font=("Arial", 14), bg="#E6F3FF", fg="#4B0082")
        self.progress_label.pack(pady=10)
        
        # Initially hide game elements
        self.hide_game_elements()

    
        
    def generate_problem(self):
        if not self.problems:
            self.end_game()
            return

        num1, num2 = self.problems.pop()
        answer = num1 * num2

        self.current_problem = {
            'num1': num1,
            'num2': num2,
            'operation': '×',
            'answer': answer
        }

        self.problem_label.config(text=f"{num1} × {num2} = ?")
        self.progress_label.config(text=f"Problem: {self.problem_count + 1}/{self.max_problems}")
        self.problem_count += 1

        # Clear and focus the answer entry immediately
        self.answer_entry.delete(0, tk.END)
        self.answer_entry.focus_set()
        self.feedback_label.config(text="")
        self.start_time = time.time()

    def hide_game_elements(self):
        self.problem_label.pack_forget()
        self.answer_frame.pack_forget()
        self.score_label.pack_forget()
        self.progress_label.pack_forget()
        self.feedback_label.pack_forget()
        
    def show_game_elements(self):
        self.problem_label.pack(pady=20)
        self.answer_frame.pack(pady=20)
        self.score_label.pack(pady=10)
        self.progress_label.pack(pady=10)
        self.feedback_label.pack(pady=10)

    def check_answer(self):
        if not self.current_problem:
            return
            
        try:
            user_answer = int(self.answer_entry.get())
            time_taken = time.time() - self.start_time
            
            if user_answer == self.current_problem['answer']:
                self.correct_answers += 1
                problem_score = 10
                time_bonus = max(0, 10 - int(time_taken))
                self.score += problem_score + time_bonus
                
                # Update feedback text
                feedback_text = f"✅ Correct! +{problem_score} points (+{time_bonus} time bonus) (Time: {time_taken:.1f} sec)"
                self.feedback_label.config(text=feedback_text, fg="green")
            else:
                # Display inline feedback in red
                self.feedback_label.config(text=f"❌ Incorrect. Right answer was {self.current_problem['answer']}", fg="red")
                
            self.score_label.config(text=f"Score: {self.score} (Correct Answers: {self.correct_answers})")
            
            # Automatically move to next problem after a short delay
            self.window.after(1500, self.generate_problem)
            
        except ValueError:
            self.feedback_label.config(text="❗ Please enter a valid number", fg="red")

if __name__ == "__main__":
    game = MultiplicationFlashCards()
    game.run()
