#V3
#Add a splash screen with a more robust settings tab
#make the computer player more responsive to play against
#Move the player naming to the settings, maybe add a save function?


import tkinter as tk
import tkinter.simpledialog as simpledialog
from tkinter import colorchooser, messagebox, ttk
import random
import json
import time


single_player_mode = True  # Set to True for AI mode, and False for two-player mode
#will  move this to a pop up to select before naming happens -- maybe splash screen
# Initialize the game board
ROWS = 6
COLS = 7
board = [[' ' for _ in range(COLS)] for _ in range(ROWS)]

# Define colors for the game board
COLOR_EMPTY = '#FFFFFF'  # White
COLOR_PLAYER_1 = '#FF0000'  # Red
COLOR_PLAYER_2 = '#FFFF00'  # Yellow

# Create the GUI window
window = tk.Tk()
window.title("Connect 4")

# Making the main window responsive
window.rowconfigure(0, weight=1)
window.columnconfigure(0, weight=1)

# Ask for player names
player1_name = simpledialog.askstring("Player 1", "Enter name for Player 1:", parent=window)
player2_name = simpledialog.askstring("Player 2", "Enter name for Player 2:", parent=window)

player1_name = player1_name if player1_name else "Player 1"
player2_name = player2_name if player2_name else "Player 2"

# Function to load scores from a file
def load_scores():
    try:
        with open('scores.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {"player1_wins": 0, "player2_wins": 0, "ties": 0}

# Function to save scores to a file
def save_scores(scores):
    with open('scores.json', 'w') as file:
        json.dump(scores, file)

# Initialize scores
scores = load_scores()
player1_wins = scores["player1_wins"]
player2_wins = scores["player2_wins"]
ties = scores["ties"]

# Create the notebook
notebook = ttk.Notebook(window)
notebook.pack(expand=True, fill="both")

# Create the game tab
game_tab = ttk.Frame(notebook)
notebook.add(game_tab, text='Game')

# Create the settings tab
settings_tab = ttk.Frame(notebook)
notebook.add(settings_tab, text='Settings')

def toggle_single_player_mode():
    global single_player_mode
    single_player_mode = not single_player_mode
    mode_label.config(text="Single Player" if single_player_mode else "Two Players")

# Add a button or switch to toggle the mode
mode_label = tk.Label(settings_tab, text="Single Player" if single_player_mode else "Two Players")
mode_label.pack()

toggle_mode_button = tk.Button(settings_tab, text="Toggle Mode", command=toggle_single_player_mode)
toggle_mode_button.pack()

# Create the statistics tab
stats_tab = ttk.Frame(notebook)
notebook.add(stats_tab, text='Statistics')

# Create the buttons for the game board
buttons = []
move_stack = []  # Stack for undo feature
for row in range(ROWS):
    button_row = []
    for col in range(COLS):
        button = tk.Button(game_tab, bg=COLOR_EMPTY, width=5, height=2, relief='flat')
        button.grid(row=row, column=col, padx=3, pady=3, sticky='nsew')
        button.configure(command=lambda c=col: button_click(c))
        button_row.append(button)
    buttons.append(button_row)

    # Set the button to be circular
    game_tab.grid_columnconfigure(col, weight=1, uniform='group1')
    game_tab.grid_rowconfigure(row, weight=1, uniform='group1')

# Add button in settings tab to change board color
def change_board_color():
    color_code = colorchooser.askcolor(title="Choose color")[1]
    if color_code:
        for row in buttons:
            for button in row:
                button.config(bg=color_code)

change_color_button = tk.Button(settings_tab, text="Change Board Color", command=change_board_color)
change_color_button.pack()

# Initialize the current player (Player 1 starts)
current_player = '1'

# Add a label to display the current player's turn
turn_label = tk.Label(game_tab, text=f"Turn: {player1_name}", font=("Helvetica", 14))
turn_label.grid(row=ROWS + 1, column=0, columnspan=COLS, pady=5, sticky='nsew')

def check_tie():
    # Check for a tie (board full)
    return all(cell != ' ' for row in board for cell in row)

def animate_move(col, row, player_color):
    # Temporarily change the color of each button to simulate the disc falling
    for temp_row in range(row + 1):
        # Change the color of the current button to the player's color
        buttons[temp_row][col].config(bg=player_color)
        window.update_idletasks()  # Update the window to reflect the color change
        time.sleep(0.1)  # Delay to create the animation effect

        if temp_row < row:
            # Reset the color of the button above the current one to the original color
            buttons[temp_row][col].config(bg=COLOR_EMPTY)

    # Set the final position with the player's color
    buttons[row][col].config(bg=player_color, state='disabled')


def on_hover_enter(e, col):
    hover_color = "#f0f0f0"  # Replace with the color you want to use
    for row in range(ROWS):
        if buttons[row][col]['state'] == 'normal':  # Only change color if the button is active
            buttons[row][col].config(bg=hover_color)

def on_hover_leave(e, col):
    for row in range(ROWS):
        if buttons[row][col]['state'] == 'normal':
            buttons[row][col].config(bg=COLOR_EMPTY)  # Reset to the original color


# Binding the hover events to the buttons
for col in range(COLS):
    for row in range(ROWS):
        button = buttons[row][col]
        button.bind("<Enter>", lambda e, col=col: on_hover_enter(e, col))
        button.bind("<Leave>", lambda e, col=col: on_hover_leave(e, col))


# Function to update the turn label
def update_turn_label():
    turn_label.config(text=f"Turn: {player1_name if current_player == '1' else player2_name}")

# Function to handle button clicks
def button_click(col):
    global current_player
    # Find the lowest available row in the selected column
    row = get_next_empty_row(col)

    if row is not None:
        animate_move(col, row, COLOR_PLAYER_1 if current_player == '1' else COLOR_PLAYER_2)
        board[row][col] = current_player
        buttons[row][col].config(bg=COLOR_PLAYER_1 if current_player == '1' else COLOR_PLAYER_2, state='disabled')
        move_stack.append((row, col))  # Record the move for the undo feature

        if check_winner(current_player):
            show_end_message(current_player)
            reset_game()
        elif check_tie():
            show_end_message(None)
            reset_game()
        else:
            # Switch to the other player or AI
            current_player = '2' if current_player == '1' else '1'
            update_turn_label()
            # If it's the AI's turn, trigger the AI move after a short delay
            if current_player == '2' and single_player_mode:  # assuming you have a way to set `single_player_mode`
                window.after(500, make_ai_move)  # AI will make a move after 500ms -- might wanna decrease this


def make_ai_move():
    difficulty = difficulty_var.get()
    if difficulty == "Easy":
        make_random_move()
    elif difficulty == "Medium":
        make_medium_move()
    elif difficulty == "Hard":
        make_hard_move()

# Function to reset the game
def reset_game():
    global current_player, board
    current_player = '1'
    board = [[' ' for _ in range(COLS)] for _ in range(ROWS)]
    for row in buttons:
        for button in row:
            button.config(bg=COLOR_EMPTY, state='normal')
    update_turn_label()

# Add an Undo button
def undo_move():
    if move_stack:
        row, col = move_stack.pop()
        buttons[row][col].config(bg=COLOR_EMPTY, state='normal')
        board[row][col] = ' '
        # Switch player back
        global current_player
        current_player = '2' if current_player == '1' else '1'
        update_turn_label()

undo_button = tk.Button(game_tab, text="Undo", command=undo_move)
undo_button.grid(row=ROWS + 3, column=0, columnspan=COLS, pady=10, sticky='nsew')

# Create a variable to store the difficulty selection
difficulty_var = tk.StringVar(value="Easy")

# Create a dropdown menu for the difficulty setting
difficulty_dropdown = ttk.OptionMenu(settings_tab, difficulty_var, "Easy", "Easy", "Medium", "Hard")
difficulty_dropdown.pack()

# Function to make the computer's move based on difficulty
def make_computer_move():
    difficulty = difficulty_var.get()
    if difficulty == "Easy":
        make_random_move()
    elif difficulty == "Medium":
        make_medium_move()
    elif difficulty == "Hard":
        make_hard_move()

# Function to make a random move (used in Easy difficulty)
def make_random_move():
    available_cols = [col for col in range(COLS) if board[0][col] == ' ']
    if available_cols:
        col = random.choice(available_cols)
        button_click(col)

# Function to make a medium difficulty move
def make_medium_move():
    # Try to win
    for col in range(COLS):
        if is_winning_move(col, '2'):
            button_click(col)
            return
    # Try to block Player 1 from winning
    for col in range(COLS):
        if is_winning_move(col, '1'):
            button_click(col)
            return
    # Otherwise, make a random move
    make_random_move()

# Function to check if a move is a winning move
def is_winning_move(col, player):
    row = get_next_empty_row(col)
    if row is not None:
        board[row][col] = player
        if check_winner(player):
            board[row][col] = ' '  # Reset the board
            return True
        board[row][col] = ' '  # Reset the board
    return False

# Function to make a hard difficulty move using minimax
def make_hard_move():
    bestScore = float('-inf')
    bestCol = random.randint(0, COLS-1)
    for col in range(COLS):
        row = get_next_empty_row(col)
        if row is not None:
            board[row][col] = '2'  # AI's move
            score = minimax(board, 4, float('-inf'), float('inf'), False)  # Depth can be adjusted
            board[row][col] = ' '  # Undo the move
            if score > bestScore:
                bestScore = score
                bestCol = col
    button_click(bestCol)

# Function to display the end message
def show_end_message(player):
    if player:
        messagebox.showinfo("Game Over", f"{player1_name if player == '1' else player2_name} wins!")
    else:
        messagebox.showinfo("Game Over", "It's a tie!")

# Confirmation dialog on close
def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit the game?"):
        window.destroy()

window.protocol("WM_DELETE_WINDOW", on_closing)

# Function for finding the lowest available row in a column
def get_next_empty_row(col):
    for row in range(ROWS - 1, -1, -1):
        if board[row][col] == ' ':
            return row
    return None

# Function for minimax algorithm with alpha-beta pruning (used in hard difficulty)
def minimax(board, depth, alpha, beta, maximizingPlayer):
    # First, check if there is a winner or if it is a tie.
    winner = check_winner('1')
    if winner == '1':
        return -1  #human player and should be minimized
    winner = check_winner('2')
    if winner == '2':
        return 1   #AI player and should be maximized --incase i would wanna watch..

    if depth == 0 or check_tie():
        return 0  # A depth of 0 or a tie is considered neutral and returns 0

    if maximizingPlayer:
        maxEval = float('-inf')
        for col in range(COLS):
            row = get_next_empty_row(col)
            if row is not None:
                board[row][col] = '2'  # AI's move
                eval = minimax(board, depth - 1, alpha, beta, False)
                board[row][col] = ' '  # Undo the move
                maxEval = max(maxEval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
        return maxEval
    else:
        minEval = float('inf')
        for col in range(COLS):
            row = get_next_empty_row(col)
            if row is not None:
                board[row][col] = '1'  # Human's move
                eval = minimax(board, depth - 1, alpha, beta, True)
                board[row][col] = ' '  # Undo the move
                minEval = min(minEval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
        return minEval


# Function to check for a winning condition
#this might only be checking my wins
def check_winner(player):
    # Check horizontal
    for row in range(ROWS):
        for col in range(COLS - 3):
            if board[row][col] == board[row][col + 1] == board[row][col + 2] == board[row][col + 3] == player:
                return player

    # Check vertical
    for col in range(COLS):
        for row in range(ROWS - 3):
            if board[row][col] == board[row + 1][col] == board[row + 2][col] == board[row + 3][col] == player:
                return player

    # Check diagonals (from bottom-left to top-right)
    for row in range(3, ROWS):
        for col in range(COLS - 3):
            if board[row][col] == board[row - 1][col + 1] == board[row - 2][col + 2] == board[row - 3][col + 3] == player:
                return player

    # Check diagonals (from top-left to bottom-right)
    for row in range(ROWS - 3):
        for col in range(3, COLS):
            if board[row][col] == board[row + 1][col - 1] == board[row + 2][col - 2] == board[row + 3][col - 3] == player:
                return player

    return None


# Start the game
window.mainloop()
