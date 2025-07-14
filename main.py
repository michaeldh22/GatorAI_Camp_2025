"""
PyDew Valley - Educational Game for Learning Python
==================================================
This is the main game file that starts and runs our farming simulation game.
Students will learn Python concepts through game development!

Educational Concepts Covered:
- Classes and Object-Oriented Programming
- Game loops and event handling
- Pygame library usage
- Module imports and organization
"""

# Import required modules for our game
from installer import install

# Install required packages if they're not already installed
install("pygame")  # Game development library
install("pytmx")  # Map loading library
install("kagglehub")  # Dataset library
install("requests")  # Library for web requests
install("opencv-python")  # Computer vision library
install("pytorch_lightning")
install("openai")  # AI API library for dialogue generation

import pygame  # Main game development library
import sys  # System operations
import os  # Operating system interface

# Import our custom game modules
from settings import *  # Game configuration settings
from level import Level  # Game world and gameplay
from main_menu import MainMenu  # Main menu system
from character_screen import CharacterScreen  # Player information screen
import game_settings  # Audio and game settings
from emotion_detector import EmotionDetector
from collections import deque


class Game:
    """
    Main Game Class - The Heart of Our Game
    ======================================
    This class manages the entire game, including:
    - Starting up pygame and creating the game window
    - Managing the main menu and game screens
    - Running the main game loop
    - Handling user input and events

    Think of this as the "manager" that coordinates everything!
    """

    def __init__(self):
        """
        Initialize the Game - Set Up Everything We Need
        ==============================================
        This method runs when we create a new Game object.
        It sets up pygame, creates the window, and prepares our game.
        """
        # Initialize pygame - this must be done before using pygame features
        pygame.init()
        pygame.mixer.init()  # Initialize audio system for sound effects and music

        # Create the game window with specified dimensions
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("PyDew Valley: GAIC 25")  # Set window title

        # Create a clock to control frame rate (how fast the game runs)
        self.clock = pygame.time.Clock()

        # Change to the directory where our game files are located
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        # Load game settings (like volume levels) from file
        game_settings.load_settings()

        # Initialize game components
        self.level = None  # The game world (will be created when game starts)
        self.main_menu = MainMenu(
            self.start_game, self.restart_emotion_detector
        )  # Main menu screen
        self.character_screen = None  # Player stats screen (created when game starts)
        self.show_main_menu = True  # Flag to control which screen to show

        # Emotion Detection Setup
        self.emotions_deque = deque(maxlen=5)  # Store the last 5 detected emotions
        self.emotion_detector = None
        if game_settings.get("enable_camera", True):
            self.emotion_detector = EmotionDetector(
                self.emotions_deque, show_camera_preview=False
            )
        # self.emotion_detector.start() # We will start this in the run loop

    def start_game(self):
        """
        Start the Main Game - Called When Player Clicks "Start Game"
        ==========================================================
        This method creates the game world and player character screen.
        """
        self.level = Level(self.emotions_deque)  # Create the game world
        self.character_screen = CharacterScreen(
            self.level.player
        )  # Create player info screen
        self.show_main_menu = False  # Hide main menu and show game

    def restart_emotion_detector(self):
        """Restart the emotion detector with new camera settings"""
        if self.emotion_detector and self.emotion_detector.is_alive():
            print("🔄 Restarting emotion detector with new camera settings...")
            self.emotion_detector.stop()
            self.emotion_detector.join(timeout=2.0)  # Wait for thread to stop

        # Create new emotion detector with updated settings
        self.emotion_detector = EmotionDetector(
            self.emotions_deque, show_camera_preview=False
        )
        self.emotion_detector.start()

    def run(self):
        """
        Main Game Loop - The Heart That Keeps Our Game Running
        =====================================================
        This is the main game loop that runs continuously until the player quits.
        Every frame (many times per second), this loop:
        1. Checks for player input (keyboard, mouse, window close)
        2. Updates the game world or menu
        3. Draws everything to the screen

        This is a fundamental concept in game programming!"""
        # Start the emotion detector thread once the main loop begins
        if self.emotion_detector and not self.emotion_detector.is_alive():
            self.emotion_detector.start()

        # Main game loop - runs until player quits
        while True:
            # A small delay to ensure the main thread has priority
            pygame.time.delay(10)

            # EVENT HANDLING - Check what the player is doing
            events = pygame.event.get()
            for event in events:
                # Check if player clicked the X button to close the window
                if event.type == pygame.QUIT:
                    if self.emotion_detector:
                        self.emotion_detector.stop()  # Signal the thread to stop
                    pygame.quit()  # Close pygame
                    sys.exit()  # Exit the program

                # Check if player pressed 'I' key to open inventory/character screen
                if (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_i
                    and self.character_screen
                ):
                    self.character_screen.toggle()  # Show/hide character screen

            # DELTA TIME - Calculate time since last frame (for smooth movement)
            delta_time = self.clock.tick() / 1000  # Convert milliseconds to seconds

            # UPDATE GAME STATE - Decide what to update based on current screen
            if self.show_main_menu:
                # We're showing the main menu
                self.main_menu.update()
            else:
                # We're in the main game - pass events for proper input handling
                self.level.run(delta_time, events)  # Update game world

                # If character screen is visible, update it too
                if self.character_screen and self.character_screen.visible:
                    self.character_screen.update()

            # RENDER - Draw everything to the screen
            pygame.display.update()  # Actually display what we've drawn


# PROGRAM ENTRY POINT - This runs when we start the program
if __name__ == "__main__":
    """
    This special condition checks if this file is being run directly
    (not imported as a module). If so, create and start the game!
    """
    game = Game()  # Create a new Game instance
    game.run()  # Start the main game loop
