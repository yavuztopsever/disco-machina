#!/usr/bin/env python3
"""
Hangman Game Implementation

A terminal-based Hangman game with features like:
- Word selection from different categories
- Multiple difficulty levels
- Score tracking
- ASCII art visualization
- Save/load game functionality
"""

import os
import random
import json
import time
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any

# ASCII art for hangman stages
HANGMAN_STAGES = [
    """
    +---+
    |   |
        |
        |
        |
        |
    =========
    """,
    """
    +---+
    |   |
    O   |
        |
        |
        |
    =========
    """,
    """
    +---+
    |   |
    O   |
    |   |
        |
        |
    =========
    """,
    """
    +---+
    |   |
    O   |
   /|   |
        |
        |
    =========
    """,
    """
    +---+
    |   |
    O   |
   /|\\  |
        |
        |
    =========
    """,
    """
    +---+
    |   |
    O   |
   /|\\  |
   /    |
        |
    =========
    """,
    """
    +---+
    |   |
    O   |
   /|\\  |
   / \\  |
        |
    =========
    """
]

# Word categories
WORD_CATEGORIES = {
    "animals": [
        "elephant", "giraffe", "penguin", "kangaroo", "dolphin", 
        "tiger", "octopus", "flamingo", "crocodile", "hedgehog"
    ],
    "fruits": [
        "strawberry", "watermelon", "pineapple", "blueberry", "kiwi",
        "banana", "orange", "mango", "cherry", "apricot"
    ],
    "countries": [
        "australia", "brazil", "canada", "denmark", "egypt",
        "finland", "germany", "hungary", "iceland", "japan"
    ],
    "sports": [
        "basketball", "volleyball", "swimming", "tennis", "archery",
        "gymnastics", "football", "skiing", "cricket", "rugby"
    ],
    "programming": [
        "function", "variable", "algorithm", "boolean", "integer",
        "debugging", "framework", "database", "iteration", "parameter"
    ]
}

# Difficulty levels (affects number of allowed mistakes)
DIFFICULTY_LEVELS = {
    "easy": {"max_mistakes": 6, "points_multiplier": 1},
    "medium": {"max_mistakes": 5, "points_multiplier": 2},
    "hard": {"max_mistakes": 4, "points_multiplier": 3},
    "expert": {"max_mistakes": 3, "points_multiplier": 4}
}

class HangmanGame:
    """Main Hangman game class."""
    
    def __init__(self):
        """Initialize the game state."""
        self.word = ""
        self.hidden_word = ""
        self.used_letters = set()
        self.mistakes = 0
        self.max_mistakes = 6
        self.points_multiplier = 1
        self.current_score = 0
        self.total_score = 0
        self.games_played = 0
        self.games_won = 0
        self.difficulty = "easy"
        self.category = "animals"
        self.save_dir = os.path.join(str(Path.home()), ".hangman")
        self.high_scores: List[Dict[str, Any]] = []
        self.load_high_scores()
    
    def setup_game(self, difficulty: str = "easy", category: str = "animals") -> None:
        """Set up a new game with the given difficulty and category.
        
        Args:
            difficulty: Game difficulty level (easy, medium, hard, expert)
            category: Word category (animals, fruits, countries, etc.)
        """
        # Set difficulty
        if difficulty in DIFFICULTY_LEVELS:
            self.difficulty = difficulty
            self.max_mistakes = DIFFICULTY_LEVELS[difficulty]["max_mistakes"]
            self.points_multiplier = DIFFICULTY_LEVELS[difficulty]["points_multiplier"]
        else:
            print(f"Invalid difficulty, defaulting to easy.")
            self.difficulty = "easy"
            self.max_mistakes = DIFFICULTY_LEVELS["easy"]["max_mistakes"]
            self.points_multiplier = DIFFICULTY_LEVELS["easy"]["points_multiplier"]
        
        # Set category and choose word
        if category in WORD_CATEGORIES:
            self.category = category
            self.word = random.choice(WORD_CATEGORIES[category]).upper()
        else:
            print(f"Invalid category, defaulting to animals.")
            self.category = "animals"
            self.word = random.choice(WORD_CATEGORIES["animals"]).upper()
        
        # Reset game state
        self.hidden_word = "_" * len(self.word)
        self.used_letters = set()
        self.mistakes = 0
        self.current_score = 0
    
    def display_game(self) -> None:
        """Display the current game state."""
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n===== HANGMAN =====")
        print(f"Category: {self.category.capitalize()}")
        print(f"Difficulty: {self.difficulty.capitalize()}")
        print(f"Mistakes: {self.mistakes}/{self.max_mistakes}")
        print(f"Score: {self.current_score}")
        print("\n" + HANGMAN_STAGES[self.mistakes])
        
        # Display word with guessed letters
        display_word = ""
        for i, char in enumerate(self.word):
            if self.hidden_word[i] != "_":
                display_word += char + " "
            else:
                display_word += "_ "
        print("\nWord:", display_word)
        
        # Display used letters
        print("\nGuessed letters:", " ".join(sorted(self.used_letters)))
    
    def make_guess(self, letter: str) -> bool:
        """Process a letter guess.
        
        Args:
            letter: The letter being guessed
            
        Returns:
            True if the guess was correct, False otherwise
        """
        letter = letter.upper()
        
        # Check if letter was already guessed
        if letter in self.used_letters:
            print("You already guessed that letter!")
            return False
        
        self.used_letters.add(letter)
        
        # Check if letter is in the word
        if letter in self.word:
            # Update hidden word
            new_hidden = list(self.hidden_word)
            for i, char in enumerate(self.word):
                if char == letter:
                    new_hidden[i] = letter
            self.hidden_word = "".join(new_hidden)
            
            # Calculate points for correct guess
            correct_count = self.word.count(letter)
            self.current_score += correct_count * 10 * self.points_multiplier
            return True
        else:
            self.mistakes += 1
            return False
    
    def is_game_over(self) -> bool:
        """Check if the game is over (either won or lost).
        
        Returns:
            True if the game is over, False otherwise
        """
        return self.mistakes >= self.max_mistakes or "_" not in self.hidden_word
    
    def is_game_won(self) -> bool:
        """Check if the game was won.
        
        Returns:
            True if the player won, False otherwise
        """
        return "_" not in self.hidden_word
    
    def update_stats(self) -> None:
        """Update game statistics after a game ends."""
        self.games_played += 1
        if self.is_game_won():
            self.games_won += 1
            # Add bonus points for winning
            remaining_lives = self.max_mistakes - self.mistakes
            win_bonus = 50 * remaining_lives * self.points_multiplier
            self.current_score += win_bonus
        
        self.total_score += self.current_score
    
    def display_game_result(self) -> None:
        """Display the result of the game."""
        self.display_game()
        if self.is_game_won():
            print("\n🎉 Congratulations! You guessed the word! 🎉")
            print(f"You earned {self.current_score} points!")
        else:
            print("\n💀 Game Over! You ran out of attempts! 💀")
            print(f"The word was: {self.word}")
        
        print(f"\nTotal Score: {self.total_score}")
        print(f"Games Played: {self.games_played}")
        print(f"Games Won: {self.games_won}")
        print(f"Win Rate: {(self.games_won / self.games_played * 100):.1f}%")
    
    def save_game(self) -> None:
        """Save the current game state."""
        # Create save directory if it doesn't exist
        os.makedirs(self.save_dir, exist_ok=True)
        
        save_data = {
            "word": self.word,
            "hidden_word": self.hidden_word,
            "used_letters": list(self.used_letters),
            "mistakes": self.mistakes,
            "max_mistakes": self.max_mistakes,
            "points_multiplier": self.points_multiplier,
            "current_score": self.current_score,
            "total_score": self.total_score,
            "games_played": self.games_played,
            "games_won": self.games_won,
            "difficulty": self.difficulty,
            "category": self.category,
            "timestamp": time.time()
        }
        
        with open(os.path.join(self.save_dir, "saved_game.json"), "w") as f:
            json.dump(save_data, f)
        
        print("\nGame saved successfully!")
    
    def load_game(self) -> bool:
        """Load a saved game if one exists.
        
        Returns:
            True if a game was loaded, False otherwise
        """
        save_file = os.path.join(self.save_dir, "saved_game.json")
        if not os.path.exists(save_file):
            print("No saved game found!")
            return False
        
        try:
            with open(save_file, "r") as f:
                save_data = json.load(f)
            
            self.word = save_data["word"]
            self.hidden_word = save_data["hidden_word"]
            self.used_letters = set(save_data["used_letters"])
            self.mistakes = save_data["mistakes"]
            self.max_mistakes = save_data["max_mistakes"]
            self.points_multiplier = save_data["points_multiplier"]
            self.current_score = save_data["current_score"]
            self.total_score = save_data["total_score"]
            self.games_played = save_data["games_played"]
            self.games_won = save_data["games_won"]
            self.difficulty = save_data["difficulty"]
            self.category = save_data["category"]
            
            # Delete the save file after loading
            os.remove(save_file)
            
            print("Game loaded successfully!")
            return True
        except Exception as e:
            print(f"Error loading game: {e}")
            return False
    
    def save_high_score(self) -> None:
        """Save current score to high scores if it qualifies."""
        # Create high scores entry
        score_entry = {
            "name": input("\nEnter your name for the high score table: "),
            "score": self.total_score,
            "difficulty": self.difficulty,
            "games_played": self.games_played,
            "games_won": self.games_won,
            "win_rate": round(self.games_won / self.games_played * 100, 1),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Add to high scores and sort
        self.high_scores.append(score_entry)
        self.high_scores.sort(key=lambda x: x["score"], reverse=True)
        
        # Keep only top 10 scores
        self.high_scores = self.high_scores[:10]
        
        # Save to file
        os.makedirs(self.save_dir, exist_ok=True)
        with open(os.path.join(self.save_dir, "high_scores.json"), "w") as f:
            json.dump(self.high_scores, f)
        
        print("High score saved!")
    
    def load_high_scores(self) -> None:
        """Load high scores from file if it exists."""
        high_scores_file = os.path.join(self.save_dir, "high_scores.json")
        if os.path.exists(high_scores_file):
            try:
                with open(high_scores_file, "r") as f:
                    self.high_scores = json.load(f)
            except Exception:
                self.high_scores = []
        else:
            self.high_scores = []
    
    def display_high_scores(self) -> None:
        """Display the high scores table."""
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n===== HIGH SCORES =====\n")
        
        if not self.high_scores:
            print("No high scores yet!")
            return
        
        print(f"{'Rank':<5}{'Name':<20}{'Score':<10}{'Difficulty':<10}{'Win Rate':<10}{'Date':<20}")
        print("-" * 75)
        
        for i, score in enumerate(self.high_scores):
            print(f"{i+1:<5}{score['name']:<20}{score['score']:<10}{score['difficulty'].capitalize():<10}{score['win_rate']}%{score['timestamp']:<20}")

def display_title_screen() -> None:
    """Display the game title screen."""
    os.system('cls' if os.name == 'nt' else 'clear')
    title = r"""
    __  __     ______     __   __     ______     __    __     ______     __   __   
   /\ \_\ \   /\  __ \   /\ "-.\ \   /\  ___\   /\ "-./  \   /\  __ \   /\ "-.\ \  
   \ \  __ \  \ \  __ \  \ \ \-.  \  \ \ \__ \  \ \ \-./\ \  \ \  __ \  \ \ \-.  \ 
    \ \_\ \_\  \ \_\ \_\  \ \_\\"\_\  \ \_____\  \ \_\ \ \_\  \ \_\ \_\  \ \_\\"\_\
     \/_/\/_/   \/_/\/_/   \/_/ \/_/   \/_____/   \/_/  \/_/   \/_/\/_/   \/_/ \/_/
    """
    print(title)
    print("\n" + " " * 30 + "by Your Name")
    print("\n" + " " * 25 + "Press any key to continue...")
    input()

def display_menu() -> str:
    """Display the main menu and get user selection.
    
    Returns:
        The user's menu choice
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n===== HANGMAN MENU =====\n")
    print("1. New Game")
    print("2. Load Game")
    print("3. High Scores")
    print("4. How to Play")
    print("5. Quit")
    
    while True:
        choice = input("\nEnter your choice (1-5): ")
        if choice in ["1", "2", "3", "4", "5"]:
            return choice
        print("Invalid choice! Please enter a number between 1 and 5.")

def select_difficulty() -> str:
    """Prompt user to select difficulty level.
    
    Returns:
        The selected difficulty level
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n===== SELECT DIFFICULTY =====\n")
    print("1. Easy (6 mistakes allowed, 1x points)")
    print("2. Medium (5 mistakes allowed, 2x points)")
    print("3. Hard (4 mistakes allowed, 3x points)")
    print("4. Expert (3 mistakes allowed, 4x points)")
    
    difficulties = {
        "1": "easy",
        "2": "medium",
        "3": "hard",
        "4": "expert"
    }
    
    while True:
        choice = input("\nEnter your choice (1-4): ")
        if choice in difficulties:
            return difficulties[choice]
        print("Invalid choice! Please enter a number between 1 and 4.")

def select_category() -> str:
    """Prompt user to select word category.
    
    Returns:
        The selected category
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n===== SELECT CATEGORY =====\n")
    print("1. Animals")
    print("2. Fruits")
    print("3. Countries")
    print("4. Sports")
    print("5. Programming")
    print("6. Random")
    
    categories = {
        "1": "animals",
        "2": "fruits",
        "3": "countries",
        "4": "sports",
        "5": "programming",
        "6": "random"
    }
    
    while True:
        choice = input("\nEnter your choice (1-6): ")
        if choice in categories:
            category = categories[choice]
            if category == "random":
                category = random.choice(list(WORD_CATEGORIES.keys()))
            return category
        print("Invalid choice! Please enter a number between 1 and 6.")

def display_how_to_play() -> None:
    """Display game instructions."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n===== HOW TO PLAY =====\n")
    print("Hangman is a classic word guessing game:")
    print("1. The computer selects a word from the chosen category.")
    print("2. You try to guess the word by suggesting letters.")
    print("3. Each incorrect guess adds a part to the hangman figure.")
    print("4. If the hangman is completed before you guess the word, you lose.")
    print("5. If you guess the word before the hangman is completed, you win!")
    print("\nSCORING:")
    print("- Each correct letter: 10 points × difficulty multiplier")
    print("- Winning bonus: 50 points × remaining lives × difficulty multiplier")
    print("\nPress any key to return to the menu...")
    input()

def play_game() -> None:
    """Main game loop."""
    game = HangmanGame()
    
    # Display title screen
    display_title_screen()
    
    while True:
        choice = display_menu()
        
        if choice == "1":  # New Game
            difficulty = select_difficulty()
            category = select_category()
            game.setup_game(difficulty, category)
            play_round(game)
        elif choice == "2":  # Load Game
            if game.load_game():
                play_round(game)
        elif choice == "3":  # High Scores
            game.display_high_scores()
            print("\nPress any key to return to the menu...")
            input()
        elif choice == "4":  # How to Play
            display_how_to_play()
        else:  # Quit
            print("\nThanks for playing! Goodbye!")
            break

def play_round(game: HangmanGame) -> None:
    """Play a single round of Hangman.
    
    Args:
        game: The HangmanGame instance
    """
    while not game.is_game_over():
        game.display_game()
        
        while True:
            guess = input("\nEnter a letter or '!' to save and quit: ").strip()
            if guess == "!":
                game.save_game()
                return
            elif len(guess) != 1 or not guess.isalpha():
                print("Please enter a single letter!")
            else:
                break
        
        game.make_guess(guess)
    
    # Game is over
    game.update_stats()
    game.display_game_result()
    
    # Save high score if the game was won
    if game.is_game_won() and (not game.high_scores or game.total_score > game.high_scores[-1]["score"] or len(game.high_scores) < 10):
        game.save_high_score()
    
    # Ask to play again
    while True:
        play_again = input("\nPlay again? (y/n): ").strip().lower()
        if play_again in ["y", "yes"]:
            difficulty = select_difficulty()
            category = select_category()
            game.setup_game(difficulty, category)
            return
        elif play_again in ["n", "no"]:
            return
        else:
            print("Please enter 'y' or 'n'.")

def main() -> None:
    """Entry point for the Hangman game."""
    try:
        play_game()
    except KeyboardInterrupt:
        print("\n\nGame terminated by user. Goodbye!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Sorry about that! The game will now exit.")

if __name__ == "__main__":
    main()