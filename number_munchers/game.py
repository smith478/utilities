import tkinter as tk
from tkinter import messagebox, font
import random
import time

class NumberMunchers:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Number Munchers! 🔢")
        self.window.geometry("800x700")
        self.window.configure(bg="#000080")  # Classic blue background
        self.window.resizable(False, False)
        
        # Game state
        self.grid_size = 5
        self.player_row = 2
        self.player_col = 2
        self.score = 0
        self.lives = 3
        self.level = 1
        self.game_active = False
        self.numbers_to_munch = set()
        self.munched_positions = set()
        self.grid_values = []
        self.monsters = []
        self.monster_move_delay = 2000  # milliseconds
        self.last_monster_move = 0
        
        # Game modes
        self.game_modes = [
            "Multiples of 3",
            "Multiples of 4", 
            "Multiples of 5",
            "Even Numbers",
            "Odd Numbers",
            "Prime Numbers",
            "Numbers > 25",
            "Numbers < 15"
        ]
        self.current_mode = "Multiples of 3"
        
        self.setup_gui()
        self.bind_keys()
        
    def setup_gui(self):
        # Title
        title_font = font.Font(family="Courier", size=20, weight="bold")
        self.title_label = tk.Label(self.window, text="NUMBER MUNCHERS", 
                                   font=title_font, bg="#000080", fg="yellow")
        self.title_label.pack(pady=10)
        
        # Game info frame
        info_frame = tk.Frame(self.window, bg="#000080")
        info_frame.pack(pady=5)
        
        info_font = font.Font(family="Courier", size=12, weight="bold")
        self.score_label = tk.Label(info_frame, text="SCORE: 0", 
                                   font=info_font, bg="#000080", fg="white")
        self.score_label.pack(side=tk.LEFT, padx=20)
        
        self.lives_label = tk.Label(info_frame, text="LIVES: ♥♥♥", 
                                   font=info_font, bg="#000080", fg="red")
        self.lives_label.pack(side=tk.LEFT, padx=20)
        
        self.level_label = tk.Label(info_frame, text="LEVEL: 1", 
                                   font=info_font, bg="#000080", fg="white")
        self.level_label.pack(side=tk.LEFT, padx=20)
        
        # Current challenge label
        self.challenge_label = tk.Label(self.window, text="MUNCH: Multiples of 3", 
                                       font=info_font, bg="#000080", fg="cyan")
        self.challenge_label.pack(pady=5)
        
        # Game grid frame
        self.grid_frame = tk.Frame(self.window, bg="#000080")
        self.grid_frame.pack(pady=20)
        
        # Create grid
        self.grid_buttons = []
        button_font = font.Font(family="Courier", size=16, weight="bold")
        
        for row in range(self.grid_size):
            button_row = []
            for col in range(self.grid_size):
                btn = tk.Button(self.grid_frame, text="", width=6, height=3,
                               font=button_font, bg="white", fg="black",
                               relief=tk.RAISED, borderwidth=2)
                btn.grid(row=row, column=col, padx=2, pady=2)
                button_row.append(btn)
            self.grid_buttons.append(button_row)
        
        # Control instructions
        controls_frame = tk.Frame(self.window, bg="#000080")
        controls_frame.pack(pady=10)
        
        control_font = font.Font(family="Courier", size=10)
        controls_text = "ARROW KEYS: Move  |  SPACE: Munch  |  N: New Game  |  ESC: Quit"
        tk.Label(controls_frame, text=controls_text, font=control_font, 
                bg="#000080", fg="yellow").pack()
        
        # Start screen
        self.show_start_screen()
        
    def bind_keys(self):
        self.window.bind('<Key>', self.on_key_press)
        self.window.focus_set()
        
    def on_key_press(self, event):
        if not self.game_active:
            if event.keysym == 'n' or event.keysym == 'N':
                self.start_new_game()
            elif event.keysym == 'Escape':
                self.window.quit()
            return
            
        if event.keysym == 'Up':
            self.move_player(-1, 0)
        elif event.keysym == 'Down':
            self.move_player(1, 0)
        elif event.keysym == 'Left':
            self.move_player(0, -1)
        elif event.keysym == 'Right':
            self.move_player(0, 1)
        elif event.keysym == 'space':
            self.munch_number()
        elif event.keysym == 'n' or event.keysym == 'N':
            self.start_new_game()
        elif event.keysym == 'Escape':
            self.end_game()
            
    def show_start_screen(self):
        self.game_active = False
        self.clear_grid()
        
        # Show welcome message in center
        center_row = self.grid_size // 2
        center_col = self.grid_size // 2
        
        self.grid_buttons[center_row-1][center_col].config(text="NUMBER", bg="yellow", fg="blue")
        self.grid_buttons[center_row][center_col].config(text="MUNCHERS", bg="yellow", fg="blue")
        self.grid_buttons[center_row+1][center_col].config(text="Press N", bg="cyan", fg="black")
        
    def start_new_game(self):
        self.game_active = True
        self.score = 0
        self.lives = 3
        self.level = 1
        self.player_row = 2
        self.player_col = 2
        self.monsters = []
        self.munched_positions = set()
        
        # Select random game mode
        self.current_mode = random.choice(self.game_modes)
        self.challenge_label.config(text=f"MUNCH: {self.current_mode}")
        
        self.update_display()
        self.generate_grid()
        self.spawn_monsters()
        self.game_loop()
        
    def generate_grid(self):
        self.grid_values = []
        self.numbers_to_munch = set()
        
        # Generate numbers for the grid
        for row in range(self.grid_size):
            grid_row = []
            for col in range(self.grid_size):
                if self.current_mode.startswith("Multiples of"):
                    multiple = int(self.current_mode.split()[-1])
                    if random.random() < 0.4:  # 40% chance of correct answer
                        num = multiple * random.randint(1, 12)
                        self.numbers_to_munch.add((row, col))
                    else:
                        num = random.randint(1, 50)
                        while num % multiple == 0:  # Ensure it's NOT a multiple
                            num = random.randint(1, 50)
                
                elif self.current_mode == "Even Numbers":
                    if random.random() < 0.4:
                        num = random.randint(1, 25) * 2  # Even number
                        self.numbers_to_munch.add((row, col))
                    else:
                        num = random.randint(1, 25) * 2 - 1  # Odd number
                
                elif self.current_mode == "Odd Numbers":
                    if random.random() < 0.4:
                        num = random.randint(1, 25) * 2 - 1  # Odd number
                        self.numbers_to_munch.add((row, col))
                    else:
                        num = random.randint(1, 25) * 2  # Even number
                
                elif self.current_mode == "Prime Numbers":
                    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
                    if random.random() < 0.3:
                        num = random.choice(primes)
                        self.numbers_to_munch.add((row, col))
                    else:
                        num = random.randint(4, 50)
                        while self.is_prime(num):
                            num = random.randint(4, 50)
                
                elif self.current_mode.startswith("Numbers >"):
                    threshold = int(self.current_mode.split()[-1])
                    if random.random() < 0.4:
                        num = random.randint(threshold + 1, threshold + 25)
                        self.numbers_to_munch.add((row, col))
                    else:
                        num = random.randint(1, threshold)
                
                elif self.current_mode.startswith("Numbers <"):
                    threshold = int(self.current_mode.split()[-1])
                    if random.random() < 0.4:
                        num = random.randint(1, threshold - 1)
                        self.numbers_to_munch.add((row, col))
                    else:
                        num = random.randint(threshold, threshold + 25)
                
                grid_row.append(num)
            self.grid_values.append(grid_row)
        
        self.update_grid_display()
        
    def is_prime(self, n):
        if n < 2:
            return False
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                return False
        return True
        
    def update_grid_display(self):
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                btn = self.grid_buttons[row][col]
                
                # First, set the background based on the space state
                if (row, col) in self.munched_positions:
                    btn.config(text="", bg="#404040", fg="white")
                else:
                    num = self.grid_values[row][col]
                    if (row, col) in self.numbers_to_munch:
                        btn.config(text=str(num), bg="lightblue", fg="black")
                    else:
                        btn.config(text=str(num), bg="white", fg="black")
                
                # Then, override with characters (player and monsters on top)
                if row == self.player_row and col == self.player_col:
                    btn.config(text="🔢", bg="lime", fg="black")
                elif (row, col) in self.monsters:
                    btn.config(text="👾", bg="red", fg="white")
                        
    def move_player(self, dr, dc):
        new_row = self.player_row + dr
        new_col = self.player_col + dc
        
        if 0 <= new_row < self.grid_size and 0 <= new_col < self.grid_size:
            self.player_row = new_row
            self.player_col = new_col
            self.update_grid_display()
            
            # Check if player hit a monster
            if (self.player_row, self.player_col) in self.monsters:
                self.player_hit_monster()
                
    def munch_number(self):
        pos = (self.player_row, self.player_col)
        
        if pos in self.munched_positions:
            return  # Already munched
            
        if pos in self.numbers_to_munch:
            # Correct munch!
            self.score += 10 * self.level
            self.munched_positions.add(pos)
            self.numbers_to_munch.remove(pos)
            
            # Check if level complete
            if not self.numbers_to_munch:
                self.level_complete()
        else:
            # Wrong munch!
            self.lives -= 1
            if self.lives <= 0:
                self.game_over()
            else:
                messagebox.showwarning("Wrong!", "That's not a correct number!")
        
        self.update_display()
        self.update_grid_display()
        
    def spawn_monsters(self):
        self.monsters = []
        num_monsters = min(self.level, 3)  # Max 3 monsters
        
        for _ in range(num_monsters):
            attempts = 0
            while attempts < 50:  # Prevent infinite loop
                row = random.randint(0, self.grid_size - 1)
                col = random.randint(0, self.grid_size - 1)
                # Make sure monster doesn't spawn on player or too close (at least 2 squares away)
                distance = abs(row - self.player_row) + abs(col - self.player_col)
                if distance >= 2 and (row, col) not in self.monsters:
                    self.monsters.append((row, col))
                    break
                attempts += 1
                    
    def move_monsters(self):
        new_monsters = []
        for monster_row, monster_col in self.monsters:
            # Simple AI: move towards player
            if monster_row < self.player_row:
                new_row = monster_row + 1
            elif monster_row > self.player_row:
                new_row = monster_row - 1
            else:
                new_row = monster_row
                
            if monster_col < self.player_col:
                new_col = monster_col + 1
            elif monster_col > self.player_col:
                new_col = monster_col - 1
            else:
                new_col = monster_col
                
            # Keep monster in bounds
            new_row = max(0, min(self.grid_size - 1, new_row))
            new_col = max(0, min(self.grid_size - 1, new_col))
            
            new_monsters.append((new_row, new_col))
            
        self.monsters = new_monsters
        
        # Check if any monster caught the player
        if (self.player_row, self.player_col) in self.monsters:
            self.player_hit_monster()
        
        self.update_grid_display()
        
    def player_hit_monster(self):
        self.lives -= 1
        if self.lives <= 0:
            self.game_over()
        else:
            # Respawn player at center
            self.player_row = 2
            self.player_col = 2
            messagebox.showwarning("Caught!", "A monster caught you!")
        
        self.update_display()
        
    def level_complete(self):
        self.level += 1
        bonus = 100 * self.level
        self.score += bonus
        
        messagebox.showinfo("Level Complete!", 
                          f"Great job! Level {self.level-1} complete!\n"
                          f"Bonus: {bonus} points")
        
        # New level setup
        self.current_mode = random.choice(self.game_modes)
        self.challenge_label.config(text=f"MUNCH: {self.current_mode}")
        self.munched_positions = set()
        self.player_row = 2
        self.player_col = 2
        
        self.update_display()
        self.generate_grid()
        self.spawn_monsters()
        
    def game_over(self):
        self.game_active = False
        messagebox.showinfo("Game Over!", 
                          f"Game Over!\n"
                          f"Final Score: {self.score}\n"
                          f"Level Reached: {self.level}\n\n"
                          f"Press N for a new game!")
        self.show_start_screen()
        
    def end_game(self):
        self.game_active = False
        self.show_start_screen()
        
    def update_display(self):
        self.score_label.config(text=f"SCORE: {self.score}")
        hearts = "♥" * self.lives
        self.lives_label.config(text=f"LIVES: {hearts}")
        self.level_label.config(text=f"LEVEL: {self.level}")
        
    def clear_grid(self):
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                self.grid_buttons[row][col].config(text="", bg="white", fg="black")
                
    def game_loop(self):
        if not self.game_active:
            return
            
        current_time = time.time() * 1000  # Convert to milliseconds
        if current_time - self.last_monster_move > self.monster_move_delay:
            self.move_monsters()
            self.last_monster_move = current_time
            
        # Schedule next game loop iteration
        self.window.after(100, self.game_loop)
        
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    game = NumberMunchers()
    game.run()