import tkinter as tk
import os
import random
from tkinter import messagebox
import pygame

# Word categories
def load_categories(file_name):
    categories = {}
    with open(file_name, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                category, items = line.split(':', 1)
                categories[category.strip()] = [item.strip().upper() for item in items.split(',')]
    return categories

categories = load_categories('categories.txt')

#Audio
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init()

win_sound = pygame.mixer.Sound("Winning.wav")
lose_sound = pygame.mixer.Sound("Losing.wav")
background_music = pygame.mixer.Sound("Lofi Loop.mp3")


def play_win_sound():
    win_sound.play()

def play_lose_sound():
    lose_sound.play()

def play_background_music():
    background_music.play(loops=-1)
    
def stop_background_music():
    background_music.stop()

win_sound.set_volume(0.5)
lose_sound.set_volume(0.5)
background_music.set_volume(0.3)
    
    
# Initialize main window
window = tk.Tk()
window.title("Wordopolis")
window.geometry("800x600")
window.configure(bg="white")



# Global variables
dark_mode = False
selected_category = ""
selected_difficulty = ""
selected_timer = "Off"
attempts_remaining = 0
word = ""
guessed_letters = set()
keyboard_buttons = {}
timer_running = False
timer_label = None
timer_remaining = 0

# Main menu
def update_main_menu():
    for widget in window.winfo_children():
        widget.destroy()
    
    title_label = tk.Label(window, text="Wordopolis", font=("Helvetica", 24), bg="white", fg="black")
    title_label.pack(pady=20)

    play_button = tk.Button(window, text="Play", command=open_play, bg="lightgray")
    play_button.pack(pady=10)

    settings_button = tk.Button(window, text="Settings", command=open_settings, bg="lightgray")
    settings_button.pack(pady=10)

    credits_button = tk.Button(window, text="Credits", command=open_credits, bg="lightgray")
    credits_button.pack(pady=10)

# Function to open play screen
def open_play():
    for widget in window.winfo_children():
        widget.destroy()

    title_label = tk.Label(window, text="Wordopolis - Play", font=("Helvetica", 24), bg="white", fg="black")
    title_label.pack(pady=20)

    category_label = tk.Label(window, text="Select a Category:", bg="white", fg="black")
    category_label.pack(pady=10)

    category_var = tk.StringVar()
    category_var.set(list(categories.keys())[0])  # Set default category

    category_menu = tk.OptionMenu(window, category_var, *categories.keys())
    category_menu.pack(pady=10)

    difficulty_label = tk.Label(window, text="Select Difficulty:", bg="white", fg="black")
    difficulty_label.pack(pady=10)

    difficulty_var = tk.StringVar()
    difficulty_var.set("Medium")  # Set default difficulty

    difficulty_menu = tk.OptionMenu(window, difficulty_var, "Very Easy", "Easy", "Medium", "Hard", "Impossible")
    difficulty_menu.pack(pady=10)

    # Timer select:
    timer_label = tk.Label(window, text="Select Timer Mode:", bg="white", fg="black")
    timer_label.pack(pady=10)

    timer_var = tk.StringVar()
    timer_var.set("Off")  # Set default timer

    timer_menu = tk.OptionMenu(window, timer_var, "Off", "10 seconds", "30 seconds", "1 minute")
    timer_menu.pack(pady=10)

    start_button = tk.Button(window, text="Start", command=lambda: start_game(category_var.get(), difficulty_var.get(), timer_var.get()), bg="lightgray")
    start_button.pack(pady=10)

    back_button = tk.Button(window, text="Back to Main Menu", command=update_main_menu, bg="lightgray")
    back_button.pack(pady=20)
    
# Function to start the actual game
def start_game(category, difficulty, timer_mode):
    global selected_category, selected_difficulty, selected_timer, attempts_remaining, word, guessed_letters, timer_remaining
    selected_category = category
    selected_difficulty = difficulty
    selected_timer = timer_mode

    # Set attempts based on difficulty
    if difficulty == "Very Easy":
        attempts_remaining = float("inf")
    elif difficulty == "Easy":
        attempts_remaining = 8
    elif difficulty == "Medium":
        attempts_remaining = 5
    elif difficulty == "Hard":
        attempts_remaining = 3
    elif difficulty == "Impossible":
        attempts_remaining = 1

    word = random.choice(categories[selected_category]).upper()
    guessed_letters = set()

    # Set timer
    if timer_mode == "10 seconds":
        timer_remaining = 10
    elif timer_mode == "30 seconds":
        timer_remaining = 30
    elif timer_mode == "1 minute":
        timer_remaining = 60
    else:
        timer_remaining = 0

    for widget in window.winfo_children():
        widget.destroy()

    game_title = tk.Label(window, text="Wordopolis - Guess the Word!", font=("Helvetica", 24), bg="white", fg="black")
    game_title.pack(pady=20)

    # Display selected category and difficulty on the game screen
    category_label = tk.Label(window, text=f"Category: {selected_category}", font=("Helvetica", 14), bg="white", fg="black")
    category_label.pack(side=tk.LEFT, padx=(20, 0), pady=5)

    difficulty_label = tk.Label(window, text=f"Difficulty: {selected_difficulty}", font=("Helvetica", 14), bg="white", fg="black")
    difficulty_label.pack(side=tk.RIGHT, padx=(0, 20), pady=5)

    # Timer display
    global timer_label
    if selected_timer != "Off":
        timer_label = tk.Label(window, text=f"Time Left: {timer_remaining}", font=("Helvetica", 14), bg="white", fg="black")
        timer_label.pack(pady=10)
        window.after(1000, countdown_timer)

    # Generate blanks for the word
    blanks = ' '.join(['_' if letter not in guessed_letters and letter != ' ' else letter for letter in word])
    blanks_label = tk.Label(window, text=blanks, font=("Helvetica", 24), bg="white", fg="black")
    blanks_label.pack(pady=20)

    attempts_label = tk.Label(window, text=f"Attempts Remaining: {attempts_remaining}", font=("Helvetica", 14), bg="white", fg="black")
    attempts_label.pack(pady=10)

    # Input for guessing letters
    guess_entry = tk.Entry(window, font=("Helvetica", 24))
    guess_entry.pack(pady=10)

    guess_button = tk.Button(window, text="Guess Letter", command=lambda: make_guess(guess_entry.get().upper(), blanks_label, attempts_label), bg="lightgray")
    guess_button.pack(pady=5)


     # Create keyboard for guessing
    keyboard_frame = tk.Frame(window, bg="white")
    keyboard_frame.pack(pady=20)


    # Define keyboard layout
    keyboard_layout = [
        "QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"
    ]

    for row in keyboard_layout:
        row_frame = tk.Frame(keyboard_frame, bg="white")
        row_frame.pack()

        for letter in row:
            button = tk.Button(row_frame, text=letter, command=lambda l=letter: make_guess(l, blanks_label, attempts_label), width=4, height=2, bg="lightgray")
            button.pack(side=tk.LEFT)
            keyboard_buttons[letter] = button

    
    guess_entry.bind("<Return>", lambda event: make_guess(guess_entry.get().upper(), blanks_label, attempts_label))
    guess_entry.focus()
    play_background_music()
    
def countdown_timer():
    global timer_remaining, timer_label
    if timer_remaining > 0:
        timer_remaining -= 1
        timer_label.config(text=f"Time Left: {timer_remaining}")
        window.after(1000, countdown_timer)
    else:
        play_lose_sound() 
        messagebox.showinfo("Time's up!", "The ran out of time! You lost!")      
        stop_background_music()
        update_main_menu()
# Function to handle the letter guessing
def make_guess(letter, blanks_label, attempts_label):
    global attempts_remaining
    if letter in guessed_letters or len(letter) != 1 or not letter.isalpha():
        messagebox.showinfo("Invalid Guess", "Please guess a single letter that hasn't been guessed yet.")
        return

    guessed_letters.add(letter)

    if letter not in word:
        attempts_remaining -= 1

    blanks = ' '.join([letter if letter in guessed_letters else (' ' if letter == ' ' else '_') for letter in word])
    blanks_label.config(text=blanks)
    attempts_label.config(text=f"Attempts Remaining: {attempts_remaining}")
    if "_" not in blanks:
        play_win_sound()
        messagebox.showinfo("Congratulations!", "You guessed the word correctly!")
        stop_background_music()
        update_main_menu()
    elif attempts_remaining <= 0:
        play_lose_sound()
        messagebox.showinfo("Game Over", f"You've run out of attempts! The word was: {word}")
        stop_background_music()
        update_main_menu()
        
# Function to handle the word guessing
def guess_word(guessed_word):
    global word
    if guessed_word == word:
        play_win_sound()
        messagebox.showinfo("Congratulations!", "You guessed the word correctly!")
        stop_background_music()
        update_main_menu()
    else:
        play_lose_sound()
        messagebox.showinfo("Incorrect!", f"Sorry, the correct word was: {word}")
        stop_background_music()
        update_main_menu()



# Function to open settings
def open_settings():
    for widget in window.winfo_children():
        widget.destroy()

    title_label = tk.Label(window, text="Settings", font=("Helvetica", 24), bg="white", fg="black")
    title_label.pack(pady=20)
    
    global dark_mode_button
    dark_mode_button = tk.Button(window, text="Toggle Dark Mode", command=toggle_dark_mode, bg="lightgray")
    dark_mode_button.pack(pady=10)

    back_button = tk.Button(window, text="Back to Main Menu", command=update_main_menu, bg="lightgray")
    back_button.pack(pady=10)

# Function to toggle dark mode
def toggle_dark_mode():
    global dark_mode
    dark_mode = not dark_mode
    
    #  changing background depending on light or dark mode
    if dark_mode:
        window.configure(bg="black")
        dark_mode_button.config(text="Toggle Light Mode")
    else:
        window.configure(bg="white")
        dark_mode_button.config(text="Toggle Dark Mode")

# Function to open credits
def open_credits():
    for widget in window.winfo_children():
        widget.destroy()

    title_label = tk.Label(window, text="Credits", font=("Helvetica", 24), bg="white", fg="black")
    title_label.pack(pady=20)

    credits_text = "Developed by Mohammad Reza Shafaghat\nVersion 1.1"
    credits_label = tk.Label(window, text=credits_text, font=("Helvetica", 14), bg="white", fg="black")
    credits_label.pack(pady=10)

    back_button = tk.Button(window, text="Back to Main Menu", command=update_main_menu, bg="lightgray")
    back_button.pack(pady=10)

# Start the application
update_main_menu()
window.mainloop()
