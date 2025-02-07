import random
import time
import tkinter as tk
from tkinter import messagebox, font
import json
from datetime import datetime

class MathFlashCards:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Math Flash Cards! 🚀")
        self.window.geometry("800x600")
        self.window.configure(bg="#FFE4E1")  # Light pink background
        
        self.score = 0
        self.problem_count = 0
        self.max_problems = 10
        self.current_problem = None
        self.start_time = None
        
        # Vibrant button styles
        self.button_bg = "#FF4500"  # Bright orange-red
        self.button_fg = "red"      # Red text
        self.button_active_bg = "#FF6347"  # Slightly lighter tomato red
        
        self.setup_gui()
        self.load_leaderboard()
        
    def setup_gui(self):
        # Title
        title_font = font.Font(family="Arial", size=24, weight="bold")
        title = tk.Label(self.window, text="Math Flash Cards! 🚀", 
                        font=title_font, bg="#FFE4E1", fg="black")
        title.pack(pady=20)
        
        # Max number entry
        self.setup_frame = tk.Frame(self.window, bg="#FFE4E1")
        self.setup_frame.pack(pady=20)
        
        tk.Label(self.setup_frame, text="Highest number to use:", 
                font=("Arial", 14), bg="#FFE4E1", fg="black").pack(side=tk.LEFT)
        self.max_num_entry = tk.Entry(self.setup_frame, font=("Arial", 14))
        self.max_num_entry.pack(side=tk.LEFT, padx=10)
        self.max_num_entry.insert(0, "12")
        
        # Name entry
        self.name_frame = tk.Frame(self.window, bg="#FFE4E1")
        self.name_frame.pack(pady=10)
        tk.Label(self.name_frame, text="Your name:", 
                font=("Arial", 14), bg="#FFE4E1", fg="black").pack(side=tk.LEFT)
        self.name_entry = tk.Entry(self.name_frame, font=("Arial", 14))
        self.name_entry.pack(side=tk.LEFT, padx=10)
        
        # Start button with bold, eye-catching style
        start_button = tk.Button(self.window, text="Start Game!", 
                               command=self.start_game, 
                               font=("Arial", 16, "bold"),
                               bg=self.button_bg, 
                               fg=self.button_fg,
                               activebackground=self.button_active_bg,
                               activeforeground=self.button_fg,
                               relief=tk.RAISED,
                               borderwidth=5,
                               padx=30, 
                               pady=15)
        start_button.pack(pady=20)
        
        # Problem display
        self.problem_label = tk.Label(self.window, text="", 
                                    font=("Arial", 36, "bold"), bg="#FFE4E1", fg="black")
        self.problem_label.pack(pady=20)
        
        # Answer entry
        self.answer_frame = tk.Frame(self.window, bg="#FFE4E1")
        self.answer_frame.pack(pady=20)
        self.answer_entry = tk.Entry(self.answer_frame, font=("Arial", 24))
        self.answer_entry.pack(side=tk.LEFT, padx=10)
        self.answer_entry.bind('<Return>', lambda e: self.check_answer())
        
        # Feedback label
        self.feedback_label = tk.Label(self.window, text="", 
                                     font=("Arial", 18), 
                                     bg="#FFE4E1", 
                                     fg="green")
        self.feedback_label.pack(pady=10)
        
        # Submit button with bold, eye-catching style
        self.submit_btn = tk.Button(self.answer_frame, text="Submit", 
                                  command=self.check_answer, 
                                  font=("Arial", 16, "bold"),
                                  bg=self.button_bg, 
                                  fg=self.button_fg,
                                  activebackground=self.button_active_bg,
                                  activeforeground=self.button_fg,
                                  relief=tk.RAISED,
                                  borderwidth=5,
                                  padx=30, 
                                  pady=10)
        self.submit_btn.pack(side=tk.LEFT)
        
        # Score display
        self.score_label = tk.Label(self.window, text="Score: 0", 
                                  font=("Arial", 18), bg="#FFE4E1", fg="black")
        self.score_label.pack(pady=10)
        
        # Progress display
        self.progress_label = tk.Label(self.window, text="Problem: 0/10",
                                     font=("Arial", 14), bg="#FFE4E1", fg="black")
        self.progress_label.pack(pady=10)
        
        # Initially hide game elements
        self.hide_game_elements()
        
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
        
    def load_leaderboard(self):
        try:
            with open('math_leaderboard.json', 'r') as f:
                self.leaderboard = json.load(f)
        except FileNotFoundError:
            self.leaderboard = []
            
    def save_leaderboard(self):
        with open('math_leaderboard.json', 'w') as f:
            json.dump(self.leaderboard, f)
            
    def show_leaderboard(self):
        leaderboard_window = tk.Toplevel(self.window)
        leaderboard_window.title("🏆 Leaderboard")
        leaderboard_window.geometry("400x500")
        leaderboard_window.configure(bg="#FFE4E1")
        
        tk.Label(leaderboard_window, text="Top Scores", 
                font=("Arial", 20, "bold"), bg="#FFE4E1", fg="black").pack(pady=20)
        
        sorted_scores = sorted(self.leaderboard, key=lambda x: x['score'], reverse=True)
        for i, entry in enumerate(sorted_scores[:10], 1):
            score_text = f"{i}. {entry['name']}: {entry['score']} points ({entry['date']})"
            tk.Label(leaderboard_window, text=score_text, 
                    font=("Arial", 14), bg="#FFE4E1", fg="black").pack(pady=5)
            
    def start_game(self):
        try:
            self.max_num = int(self.max_num_entry.get())
            if self.max_num < 1:
                messagebox.showerror("Error", "Please enter a number greater than 0")
                return
            
            self.player_name = self.name_entry.get().strip()
            if not self.player_name:
                messagebox.showerror("Error", "Please enter your name")
                return
                
            self.setup_frame.pack_forget()
            self.name_frame.pack_forget()
            self.show_game_elements()
            self.score = 0
            self.problem_count = 0
            self.generate_problem()
            self.answer_entry.focus_set()  # Set focus to the answer box
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
            
    def generate_problem(self):
        if self.problem_count >= self.max_problems:
            self.end_game()
            return
            
        operation = random.choice(['+', '-'])
        if operation == '+':
            num1 = random.randint(0, self.max_num)
            num2 = random.randint(0, self.max_num)
            answer = num1 + num2
        else:
            num1 = random.randint(1, self.max_num)
            num2 = random.randint(0, num1)
            answer = num1 - num2
            
        self.current_problem = {
            'num1': num1,
            'num2': num2,
            'operation': operation,
            'answer': answer
        }
        
        self.problem_label.config(text=f"{num1} {operation} {num2} = ?")
        self.progress_label.config(text=f"Problem: {self.problem_count + 1}/{self.max_problems}")
        self.answer_entry.delete(0, tk.END)
        self.feedback_label.config(text="")  # Clear previous feedback
        self.start_time = time.time()
        
        self.problem_count += 1  # Increment the problem count
        
    def check_answer(self):
        if not self.current_problem:
            return
            
        try:
            user_answer = int(self.answer_entry.get())
            time_taken = time.time() - self.start_time
            
            if user_answer == self.current_problem['answer']:
                base_score = 10
                time_bonus = max(0, 5 - int(time_taken))
                problem_score = base_score + time_bonus
                self.score += problem_score
                
                # Display inline feedback in green
                self.feedback_label.config(text=f"✅ Correct! +{problem_score} points (Time: {time_taken:.1f} sec)", fg="green")
            else:
                # Display inline feedback in red
                self.feedback_label.config(text=f"❌ Incorrect. Right answer was {self.current_problem['answer']}", fg="red")
                
            self.score_label.config(text=f"Score: {self.score}")
            
            # Automatically move to next problem after a short delay
            self.window.after(1500, self.generate_problem)
            
        except ValueError:
            self.feedback_label.config(text="❗ Please enter a valid number", fg="red")
            
    def end_game(self):
        self.leaderboard.append({
            'name': self.player_name,
            'score': self.score,
            'date': datetime.now().strftime("%Y-%m-%d")
        })
        self.save_leaderboard()
        
        # Replace popup with in-game display
        self.problem_label.config(text="Game Over! 🎮")
        self.answer_entry.pack_forget()
        self.submit_btn.pack_forget()
        
        final_score_label = tk.Label(self.window, 
                                   text=f"Final Score: {self.score}\nThanks for playing!", 
                                   font=("Arial", 24, "bold"), 
                                   bg="#FFE4E1", 
                                   fg="black")
        final_score_label.pack(pady=20)
        
        self.show_leaderboard()
        
    def run(self):
        self.show_leaderboard()  # Show leaderboard at start
        self.window.mainloop()

if __name__ == "__main__":
    game = MathFlashCards()
    game.run()