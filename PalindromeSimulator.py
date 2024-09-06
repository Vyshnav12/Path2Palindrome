import tkinter as tk
import numpy as np
import random
from collections import Counter
from tkinter import simpledialog

# Initialize the grid
lgrid = np.full((8, 8), None)
lgrid[0] = ["r", "l", "q", "s", "t", "z", "c", "a"]
lgrid[1] = ["i", "v", "d", "z", "h", "l", "t", "p"]
lgrid[2] = ["u", "r", "o", "y", "w", "c", "a", "c"]
lgrid[3] = ["x", "r", "f", "n", "d", "p", "g", "v"]
lgrid[4] = ["h", "j", "f", "f", "k", "h", "g", "m"]
lgrid[5] = ["k", "y", "e", "x", "x", "g", "k", "i"]
lgrid[6] = ["l", "q", "e", "q", "f", "u", "e", "b"]
lgrid[7] = ["l", "s", "d", "h", "i", "k", "y", "n"]

green_position = {14, 23, 42, 51}
white_direction = {
    "top": -8, "bottom": 8, "left": -1, "right": 1,
    "top left": -9, "top right": -7,
    "bottom left": 7, "bottom right": 9
}

def is_edge_square(current):
    return current <= 8 or current >= 57 or current % 8 == 0 or current % 8 == 1

def is_green_square(current):
    return current in green_position

def move_square(current):
    if is_edge_square(current):
        next_square = random.randint(1, 64)
        return next_square
    else:
        direction = random.choice(list(white_direction.keys()))
        next_square = current + white_direction[direction]
        return next_square

def choose_whether_add(current, collection):
    letter = lgrid[(current - 1) // 8, (current - 1) % 8]
    collect_length = len(collection)
    
    if collect_length < 3:
        return True
    elif collect_length == 3:
        return letter in collection
    elif collect_length == 4:
        return can_form_palindrome(collection + [letter])

def green_events(current, green_prob, collection):
    mode = random.choices([0, 1], weights=[green_prob, 1 - green_prob])[0]
    letter = lgrid[(current - 1) // 8, (current - 1) % 8]
    
    if mode == 0:
        return ["f", "f", "h", "k"]
    else:
        if letter in collection:
            collection.remove(letter)
    return collection

def can_form_palindrome(collection):
    """Check if the collection can form a palindrome."""
    count = Counter(collection)
    odd_count = sum(1 for c in count.values() if c % 2 != 0)
    return odd_count <= 1  # At most one character can have an odd count

def get_palindromic_form(collection):
    """Convert the collection into its palindromic form."""
    count = Counter(collection)
    half_palindrome = []
    middle = None
    
    for letter, freq in count.items():
        half_palindrome.extend([letter] * (freq // 2))
        if freq % 2 != 0:
            middle = letter
    
    # Construct the palindrome
    palindrome = half_palindrome + ([middle] if middle else []) + half_palindrome[::-1]
    return "".join(palindrome)

def get_cell_name(current):
    """Convert a 1D index to a cell name (e.g., 1 -> A1, 2 -> B1, etc.)"""
    column = (current - 1) % 8
    row = (current - 1) // 8
    return f"{chr(65 + column)}{8 - row}"  # Convert to A1, B1, etc.

class GameBoard(tk.Tk):
    def __init__(self, lgrid, green_position, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Path2Palindrome")
        self.lgrid = lgrid
        self.green_position = green_position
        self.cells = {}
        self.current_pos = None
        self.palindrome_label = None
        self.steps_label = None
        self.create_board()

    def create_board(self):
        for i in range(8):
            for j in range(8):
                cell_id = i * 8 + j + 1
                cell_color = "light green" if cell_id in self.green_position else "grey"
                cell = tk.Label(self, text=lgrid[i, j], width=8, height=4, bg=cell_color, relief="ridge", borderwidth=2, font=("Roboto", 12))
                cell.grid(row=i, column=j)
                self.cells[cell_id] = cell

        # Create labels for palindrome and steps
        self.palindrome_label = tk.Label(self, text="Palindrome: ", font=("Roboto", 14))
        self.palindrome_label.grid(row=8, column=0, columnspan=8, pady=5)

        self.steps_label = tk.Label(self, text="Steps: 0", font=("Roboto", 14))
        self.steps_label.grid(row=9, column=0, columnspan=8, pady=5)

        # Create the simulate button
        simulate_button = tk.Button(self, text="Simulate", command=self.simulate, font=("Roboto", 12))
        simulate_button.grid(row=10, column=0, columnspan=4, pady=10)

        # Create the batch run button
        batch_button = tk.Button(self, text="Batch Run", command=self.batch_run, font=("Roboto", 12))
        batch_button.grid(row=10, column=4, columnspan=4, pady=10)

    def reset_board(self):
        for i in range(1, 65):
            if i in self.green_position:
                self.cells[i].config(bg="light green")
            else:
                self.cells[i].config(bg="grey")
        self.current_pos = None
        self.palindrome_label.config(text="Palindrome: ")
        self.steps_label.config(text="Steps: 0")

    def update_position(self, position):
        if self.current_pos:
            # If the current position was originally green, turn it blue; otherwise, turn it yellow
            if self.current_pos in self.green_position:
                self.cells[self.current_pos].config(bg="blue")
            else:
                self.cells[self.current_pos].config(bg="yellow")
        
        # Set the new position to red
        self.cells[position].config(bg="red")
        self.current_pos = position

    def simulate(self):
        self.reset_board()
        start_position = (4, 4)  # Example start position
        green_prob = 0.5  # Example probability for green events
        self.count_num_turns(start_position, green_prob)

    def count_num_turns(self, start_position, green_prob):
        num_turns = 0
        current = start_position[0] + (start_position[1] - 1) * 8
        collection = []
        
        while len(collection) < 5:
            self.update_position(current)
            
            if is_green_square(current):
                collection = green_events(current, green_prob, collection)
                current = move_square(current)
            else:
                if choose_whether_add(current, collection):
                    collection.append(lgrid[(current - 1) // 8, (current - 1) % 8])
                
                current = move_square(current)
            
            num_turns += 1

        # Form the palindrome and update the labels
        palindrome_str = get_palindromic_form(collection)
        self.palindrome_label.config(text=f"Palindrome: {palindrome_str}")
        self.steps_label.config(text=f"Steps: {num_turns}")

        return num_turns

    def batch_run(self):
        num_simulations = simpledialog.askinteger("Batch Run", "Enter the number of simulations:", minvalue=1)
        
        if num_simulations is None:
            # User cancelled the input
            return
        
        total_steps = 0
        
        for _ in range(num_simulations):
            start_position = (4, 4)  # Example start position
            green_prob = 0.5  # Example probability for green events
            num_turns = self.count_num_turns(start_position, green_prob)
            total_steps += num_turns

        average_steps = total_steps / num_simulations
        self.palindrome_label.config(text=f"Average steps: {average_steps:.2f}")
        self.steps_label.config(text="Steps: - ")


def main():
    app = GameBoard(lgrid, green_position)
    app.mainloop()

if __name__ == "__main__":
    main()
