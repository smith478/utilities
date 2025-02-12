import random
import time
import tkinter as tk
from tkinter import messagebox, font
import json
from datetime import datetime

class MathFlashCards:
    # [Previous __init__ and setup_gui methods remain the same...]
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
        # [Previous setup_gui code remains the same...]
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
        self.max_num_entry.insert(0, "16")
        
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
        
        # Challenge indicator
        self.challenge_label = tk.Label(self.window, text="", 
                                      font=("Arial", 16, "bold"), 
                                      bg="#FFE4E1", 
                                      fg="#FF4500")  # Use the same orange-red as buttons
        self.challenge_label.pack(pady=5)
        
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

    def calculate_difficulty_bonus(self, num1, num2, operation):
        """Calculate bonus points based on problem difficulty"""
        bonus = 0
        bonus_text = ""
        is_challenge = False
        
        if operation == '+':
            # Bonus for addition with one number > 12 and other > 3
            if (num1 > 12 and num2 > 3) or (num2 > 12 and num1 > 3):
                bonus += 5
                bonus_text = "Challenge bonus (+5)"
                is_challenge = True
        elif operation == '-':
            # Bonus for subtraction with first number > 12 and second between 3 and 9
            if num1 > 12 and (3 <= num2 <= 9):
                bonus += 5
                bonus_text = "Challenge bonus (+5)"
                is_challenge = True
        
        return bonus, bonus_text, is_challenge
        
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
        
        # Check if this is a challenge problem and update the challenge label
        _, _, is_challenge = self.calculate_difficulty_bonus(num1, num2, operation)
        if is_challenge:
            self.challenge_label.config(text="🌟 CHALLENGE PROBLEM! Extra points available! 🌟")
        else:
            self.challenge_label.config(text="")
        
        self.problem_label.config(text=f"{num1} {operation} {num2} = ?")
        self.progress_label.config(text=f"Problem: {self.problem_count + 1}/{self.max_problems}")
        self.answer_entry.delete(0, tk.END)
        self.feedback_label.config(text="")
        self.start_time = time.time()
        
        self.problem_count += 1

    def hide_game_elements(self):
        self.problem_label.pack_forget()
        self.challenge_label.pack_forget()
        self.answer_frame.pack_forget()
        self.score_label.pack_forget()
        self.progress_label.pack_forget()
        self.feedback_label.pack_forget()
        
    def show_game_elements(self):
        self.problem_label.pack(pady=20)
        self.challenge_label.pack(pady=5)
        self.answer_frame.pack(pady=20)
        self.score_label.pack(pady=10)
        self.progress_label.pack(pady=10)
        self.feedback_label.pack(pady=10)

    # [Rest of the class methods remain the same...]
    def check_answer(self):
        if not self.current_problem:
            return
            
        try:
            user_answer = int(self.answer_entry.get())
            time_taken = time.time() - self.start_time
            
            if user_answer == self.current_problem['answer']:
                base_score = 10
                time_bonus = max(0, 5 - int(time_taken))
                
                # Calculate difficulty bonus
                difficulty_bonus, bonus_text, _ = self.calculate_difficulty_bonus(
                    self.current_problem['num1'],
                    self.current_problem['num2'],
                    self.current_problem['operation']
                )
                
                problem_score = base_score + time_bonus + difficulty_bonus
                self.score += problem_score
                
                # Update feedback text to include bonus information
                feedback_text = f"✅ Correct! +{problem_score} points (Time: {time_taken:.1f} sec)"
                if bonus_text:
                    feedback_text += f" {bonus_text}"
                    
                self.feedback_label.config(text=feedback_text, fg="green")
            else:
                # Display inline feedback in red
                self.feedback_label.config(text=f"❌ Incorrect. Right answer was {self.current_problem['answer']}", fg="red")
                
            self.score_label.config(text=f"Score: {self.score}")
            
            # Automatically move to next problem after a short delay
            self.window.after(1500, self.generate_problem)
            
        except ValueError:
            self.feedback_label.config(text="❗ Please enter a valid number", fg="red")

if __name__ == "__main__":
    game = MathFlashCards()
    game.run()