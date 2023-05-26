import tkinter as tk
from tkinter import colorchooser, messagebox, ttk
import random

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

# Create the notebook
notebook = ttk.Notebook(window)
notebook.pack()

# Create the game tab
game_tab = ttk.Frame(notebook)
notebook.add(game_tab, text='Game')

# Create the settings tab
settings_tab = ttk.Frame(notebook)
notebook.add(settings_tab, text='Settings')

# Create the statistics tab
stats_tab = ttk.Frame(notebook)
notebook.add(stats_tab, text='Statistics')

# Create the buttons for the game board
buttons = []
for row in range(ROWS):
    button_row = []
    for col in range(COLS):
        button = tk.Button(game_tab, bg=COLOR_EMPTY, width=5, height=2, relief='flat')
        button.grid(row=row, column=col, padx=3, pady=3)
        button.configure(command=lambda c=col: button_click(c))
        button_row.append(button)
    buttons.append(button_row)

    # Set the button to be circular
    game_tab.grid_columnconfigure(col, weight=1, uniform='group1')
    game_tab.grid_rowconfigure(row, weight=1, uniform='group1')

# Variable to store current player
current_player = '1'  # Player 1 starts

# Variable to track computer player
computer_player = True

# Variables to keep track of the number of wins for each player
player1_wins = 0
player2_wins = 0

# Variables to keep track of game statistics
total_games = 0
player1_games = 0
player2_games = 0
ties = 0

# Create labels to display win counts
player1_label = tk.Label(game_tab, text=f"Player 1 Wins: {player1_wins}")
player1_label.grid(row=ROWS + 2, column=0, columnspan=COLS // 2, sticky="W")
player2_label = tk.Label(game_tab, text=f"Player 2 Wins: {player2_wins}")
player2_label.grid(row=ROWS + 2, column=COLS // 2, columnspan=COLS // 2, sticky="E")

# Create labels to display game statistics
total_games_label = tk.Label(stats_tab, text=f"Total Games: {total_games}")
total_games_label.pack()
player1_games_label = tk.Label(stats_tab, text=f"Player 1 Games: {player1_games}")
player1_games_label.pack()
player2_games_label = tk.Label(stats_tab, text=f"Player 2 Games: {player2_games}")
player2_games_label.pack()
ties_label = tk.Label(stats_tab, text=f"Ties: {ties}")
ties_label.pack()

# Function to handle button clicks
def button_click(col):
    global current_player

    row = get_next_empty_row(col)
    if row is not None:
        # Update the game board
        board[row][col] = current_player
        button = buttons[row][col]
        color = COLOR_PLAYER_1 if current_player == '1' else COLOR_PLAYER_2
        button.config(bg=color, state='disabled')
        animate_piece(button, row, col)

        if check_winner(current_player):
            show_end_message(current_player)
            update_scores(current_player)
            update_statistics(current_player)
            disable_buttons()
        elif check_tie():
            show_end_message(None)
            update_statistics(None)
            disable_buttons()
        else:
            current_player = '2' if current_player == '1' else '1'

            if computer_player and current_player == '2':
                make_computer_move()

# Function to animate the falling of the piece
def animate_piece(button, row, col):
    y = -button.winfo_reqheight()  # Initial position above the button
    y_target = button.winfo_y()  # Target position aligned with the button
    while y < y_target:
        button.place(x=button.winfo_x(), y=y)
        window.update()
        y += 5
    button.place(x=button.winfo_x(), y=y_target)  # Ensure the final position is aligned

# Function to get the next empty row in a column
def get_next_empty_row(col):
    for row in range(ROWS - 1, -1, -1):
        if board[row][col] == ' ':
            return row
    return None

# Function to make the computer's move (Random move)
def make_random_move():
    available_cols = [col for col in range(COLS) if board[0][col] == ' ']
    if available_cols:
        col = random.choice(available_cols)
        button_click(col)

# Function to make the computer's move (Medium difficulty)
def make_medium_move():
    # Check if there is a winning move for the computer
    for col in range(COLS):
        row = get_next_empty_row(col)
        if row is not None:
            board[row][col] = '2'
            if check_winner('2'):
                button_click(col)
                return
            else:
                board[row][col] = ' '  # Reset the board position

    # Make a random move if no winning move is found
    make_random_move()

# Function to make the computer's move (Hard difficulty)
def make_hard_move():
    # Check if there is a winning move for the computer
    for col in range(COLS):
        row = get_next_empty_row(col)
        if row is not None:
            board[row][col] = '2'
            if check_winner('2'):
                button_click(col)
                return

    # Check if there is a winning move for the player and block it
    for col in range(COLS):
        row = get_next_empty_row(col)
        if row is not None:
            board[row][col] = '1'
            if check_winner('1'):
                board[row][col] = '2'  # Block the player's winning move
                button_click(col)
                return
            else:
                board[row][col] = ' '  # Reset the board position

    # Make a random move if no winning moves are found
    make_random_move()

# Function to make the computer's move
def make_computer_move():
    if computer_player:
        if difficulty_var.get() == "Easy":
            make_random_move()
        elif difficulty_var.get() == "Medium":
            make_medium_move()
        else:
            make_hard_move()

# Function to check for a win
def check_winner(player):
    # Check rows
    for row in range(ROWS):
        for col in range(COLS - 3):
            if board[row][col] == player and board[row][col + 1] == player and board[row][col + 2] == player and board[row][col + 3] == player:
                return True

    # Check columns
    for col in range(COLS):
        for row in range(ROWS - 3):
            if board[row][col] == player and board[row + 1][col] == player and board[row + 2][col] == player and board[row + 3][col] == player:
                return True

    # Check diagonals (top-left to bottom-right)
    for row in range(ROWS - 3):
        for col in range(COLS - 3):
            if board[row][col] == player and board[row + 1][col + 1] == player and board[row + 2][col + 2] == player and board[row + 3][col + 3] == player:
                return True

    # Check diagonals (bottom-left to top-right)
    for row in range(3, ROWS):
        for col in range(COLS - 3):
            if board[row][col] == player and board[row - 1][col + 1] == player and board[row - 2][col + 2] == player and board[row - 3][col + 3] == player:
                return True

    return False

# Function to check for a tie
def check_tie():
    return all(board[0][col] != ' ' for col in range(COLS))

# Function to display the end message
def show_end_message(player):
    if player:
        messagebox.showinfo("Game Over", f"Player {player} wins!")
    else:
        messagebox.showinfo("Game Over", "It's a tie!")

# Function to update the scores
def update_scores(player):
    global player1_wins, player2_wins
    if player == '1':
        player1_wins += 1
        player1_label.config(text=f"Player 1 Wins: {player1_wins}")
    elif player == '2':
        player2_wins += 1
        player2_label.config(text=f"Player 2 Wins: {player2_wins}")

# Function to update the game statistics
def update_statistics(player):
    global total_games, player1_games, player2_games, ties
    total_games += 1
    total_games_label.config(text=f"Total Games: {total_games}")
    if player == '1':
        player1_games += 1
        player1_games_label.config(text=f"Player 1 Games: {player1_games}")
    elif player == '2':
        player2_games += 1
        player2_games_label.config(text=f"Player 2 Games: {player2_games}")
    else:
        ties += 1
        ties_label.config(text=f"Ties: {ties}")

# Function to disable the buttons after the game ends
def disable_buttons():
    for row in buttons:
        for button in row:
            button.config(state='disabled')

# Create a label for the difficulty setting
difficulty_label = tk.Label(settings_tab, text="Difficulty:")
difficulty_label.pack()

# Create a variable to store the difficulty selection
difficulty_var = tk.StringVar(settings_tab)
difficulty_var.set("Easy")

# Create a dropdown menu for the difficulty setting
difficulty_dropdown = ttk.OptionMenu(settings_tab, difficulty_var, "Easy", "Easy", "Medium", "Hard")
difficulty_dropdown.pack()

# Create a checkbox for the computer player
computer_checkbox = ttk.Checkbutton(settings_tab, text="Computer Player", command=lambda: toggle_computer_player())
computer_checkbox.pack()

# Function to toggle the computer player
def toggle_computer_player():
    global computer_player
    computer_player = not computer_player

# Function to reset the game board and enable the buttons
def replay_game():
    global current_player, board
    current_player = '1'
    board = [[' ' for _ in range(COLS)] for _ in range(ROWS)]
    for row in buttons:
        for button in row:
            button.config(bg=COLOR_EMPTY, state='normal')
    window.update()

# Create a replay button
replay_button = tk.Button(game_tab, text="Replay", command=replay_game)
replay_button.grid(row=ROWS + 1, column=0, columnspan=COLS, pady=10)

# Start the game
window.mainloop()
