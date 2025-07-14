"""
Player Character Class - The Heart of Our Game Character
=======================================================
This file defines the Player class, which represents the main character
that the player controls in the game.

Educational Concepts Covered:
- Object-Oriented Programming (Classes, Methods, Inheritance)
- Sprite-based graphics and animation
- Input handling and movement
- Game state management
- Inventory systems
- Timer-based actions
"""

import pygame  # Main game library
from settings import *  # Game configuration
from support import *  # Helper functions
from timer import Timer  # Custom timer class
import os  # File system operations
import game_settings  # Audio and settings management


class Player(pygame.sprite.Sprite):
    """
    Player Class - Represents Our Main Character
    ===========================================
    This class handles everything about the player character:
    - Movement and animation
    - Using tools (hoe, axe, watering can)
    - Planting and harvesting crops    - Managing inventory and money
    - Interacting with the game world

    It inherits from pygame.sprite.Sprite, which gives us built-in
    functionality for graphics and collision detection.
    """

    def __init__(
        self,
        pos,  # Starting position (x, y coordinates)
        group,  # Sprite group this player belongs to
        collision_sprites,  # Objects the player can't walk through
        tree_sprites,  # Trees the player can interact with
        interaction,  # Function to handle interactions
        soil_layer,  # Farming/soil system
        toggle_shop,  # Function to open/close shop
    ):
        """
        Initialize the Player - Set Up Our Character
        ===========================================
        This method runs when we create a new Player object.
        It sets up all the player's properties and abilities.

        Parameters explained:
        - pos: Where to place the player on the screen
        - group: Which sprite group to add this player to
        - collision_sprites: Things the player can't walk through
        - tree_sprites: Trees that can be chopped down
        - interaction: Function for interacting with objects
        - soil_layer: System for farming/planting
        - toggle_shop: Function to open the trading shop
        """
        # Call the parent class constructor (pygame.sprite.Sprite)
        super().__init__(group)

        # GRAPHICS AND ANIMATION SETUP
        self.import_assets()  # Load all animation frames
        self.status = "down_idle"  # Start facing down and not moving
        self.frame_index = 0  # Which animation frame to show

        # Set up the visual representation
        self.image = self.animations[self.status][
            self.frame_index
        ]  # Current sprite image
        self.rect = self.image.get_rect(center=pos)  # Position rectangle
        self.z = LAYERS["main"]  # Which layer to draw on

        # MOVEMENT SYSTEM
        self.direction = pygame.math.Vector2()  # Which direction player is moving
        self.pos = pygame.math.Vector2(
            self.rect.center
        )  # Precise position (can have decimals)
        self.speed = 200  # How fast the player moves (pixels per second)

        # COLLISION DETECTION
        self.hitbox = self.rect.copy().inflate((-126, -70))  # Smaller box for collision
        self.collision_sprites = collision_sprites  # Objects that block movement

        # TIMER SYSTEM - Controls how often player can do actions
        self.timers = {
            "tool use": Timer(350, self.use_tool),  # How often tools can be used
            "tool switch": Timer(200),  # Delay between switching tools
            "seed use": Timer(350, self.use_seed),  # How often seeds can be planted
            "seed switch": Timer(200),  # Delay between switching seeds
        }  # TOOL SYSTEM - Different tools for different tasks
        self.tools = ["hoe", "axe", "water"]  # Available tools
        self.tool_index = 0  # Which tool is currently selected
        self.selected_tool = self.tools[self.tool_index]  # Currently equipped tool

        # SEED SYSTEM - Different crops player can plant
        self.seeds = ["corn", "tomato"]  # Available seed types
        self.seed_index = 0  # Which seed is currently selected
        self.selected_seed = self.seeds[
            self.seed_index
        ]  # Currently selected seed type        # INVENTORY SYSTEM - What the player is carrying
        self.item_inventory = {  # Items collected from the world
            "wood": 20,  # Wood from chopping trees
            "apple": 20,  # Apples from trees
            "corn": 20,  # Harvested corn
            "tomato": 20,  # Harvested tomatoes
        }
        self.seed_inventory = {  # Seeds available for planting
            "corn": 5,  # Corn seeds
            "tomato": 5,  # Tomato seeds
        }
        self.money = 200  # Player's money/coins

        # WORLD INTERACTION SYSTEMS
        self.tree_sprites = tree_sprites  # Trees that can be chopped
        self.interaction = interaction  # Function for interacting with objects
        self.sleep = False  # Is the player sleeping?
        self.soil_layer = soil_layer  # Farming system reference
        self.toggle_shop = toggle_shop  # Function to open/close shop        # AUDIO SYSTEM - Sound effects for player actions
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.watering = pygame.mixer.Sound(os.path.join(base_path, "audio/water.mp3"))
        self.update_audio_volumes()  # Set initial volume levels
        # Register this player globally for audio updates
        game_settings.set_current_player(self)

    def update_audio_volumes(self):
        """
        Update audio volumes based on current settings

        EDUCATIONAL CONCEPTS:
        - Function definition and documentation
        - Working with external modules (game_settings)
        - Mathematical operations (multiplication)
        - Object method calls (.get(), .set_volume())

        This method demonstrates how to:
        1. Retrieve values from a settings system
        2. Perform calculations with those values
        3. Apply the results to game objects
        """
        # Get the current volume settings from the game settings module
        # This shows how functions can work with external data
        master_vol = game_settings.get("master_volume")  # Overall volume (0.0 to 1.0)
        sfx_vol = game_settings.get(
            "sfx_volume"
        )  # Sound effects volume (0.0 to 1.0)        # Apply both volume settings together (multiplication gives us the final volume)
        # This demonstrates mathematical operations in practical programming
        self.watering.set_volume(master_vol * sfx_vol)

    def use_tool(self):
        """
        Execute the currently selected tool's action

        EDUCATIONAL CONCEPTS:
        - Conditional statements (if/elif/else)
        - String comparison
        - Method calls on other objects
        - Loop iteration through sprite groups
        - Collision detection
        - Audio playback

        This method demonstrates:
        1. How to use if statements to control program flow
        2. How objects can interact with other objects
        3. How to check for collisions between game elements
        4. How to play sound effects in games
        """
        # Check which tool is currently selected and perform the appropriate action
        # This uses string comparison to determine behavior
        if self.selected_tool == "hoe":
            # The hoe tool is used for tilling soil for farming
            # We tell the soil layer to process a "hit" at the target position
            self.soil_layer.get_hit(self.target_pos)

        if self.selected_tool == "axe":
            # The axe tool is used for chopping down trees
            # We need to check if there's a tree at the target position

            # Loop through all tree sprites to see if any are at the target position
            # This demonstrates iteration and collision detection
            for tree in self.tree_sprites.sprites():
                # Check if the mouse/target position is inside the tree's rectangle
                if tree.rect.collidepoint(self.target_pos):
                    tree.damage()  # Tell the tree it has been damaged

        if self.selected_tool == "water":
            # The water tool is used for watering crops
            # First, tell the soil layer to water the target position
            self.soil_layer.water(self.target_pos)

            # Then play a watering sound effect            # Update volume settings first to ensure correct volume
            self.update_audio_volumes()
            self.watering.play()  # Play the watering sound

    def get_target_pos(self):
        """
        Calculate where the player's tool should be aimed

        EDUCATIONAL CONCEPTS:
        - Mathematical vector operations
        - String manipulation (.split())
        - Dictionary/list access
        - Coordinate systems in 2D games

        This method demonstrates:
        1. How to work with 2D coordinates
        2. How to manipulate strings to extract information
        3. How to use dictionaries for data lookup
        4. How vector addition works in games
        """
        # Calculate the target position by adding an offset to the player's center
        # self.status contains the direction (like "up_idle" or "down_hoe")
        # We split by "_" and take the first part to get just the direction
        direction = self.status.split("_")[0]  # "up", "down", "left", or "right"

        # Look up the offset for this direction in the PLAYER_TOOL_OFFSET dictionary
        # This gives us how far from the player center the tool should reach
        tool_offset = PLAYER_TOOL_OFFSET[direction]
        # Add the offset to the player's center position to get the target
        # This uses vector addition: player_center + offset = target_position
        self.target_pos = self.rect.center + tool_offset

    def use_seed(self):
        """
        Plant the currently selected seed (if available in inventory)

        EDUCATIONAL CONCEPTS:
        - Conditional statements
        - Dictionary access and modification
        - Inventory management systems
        - Decrementing values

        This method demonstrates:
        1. How to check if items are available before using them
        2. How to modify dictionary values
        3. How inventory systems work in games
        4. How to prevent negative quantities
        """
        # Check if the player has any of the selected seed type in their inventory
        # This prevents planting seeds the player doesn't have
        if self.seed_inventory[self.selected_seed] > 0:
            # Tell the soil layer to plant the seed at the target position
            self.soil_layer.plant_seed(self.target_pos, self.selected_seed)
            # Remove one seed from the player's inventory
            # This demonstrates how inventory quantities are managed
            self.seed_inventory[self.selected_seed] -= 1

    def import_assets(self):
        """
        Load all player animation images from files

        EDUCATIONAL CONCEPTS:
        - Dictionary data structure
        - File path manipulation
        - Loops and iteration
        - Working with external files
        - Game asset management

        This method demonstrates:
        1. How to organize data using dictionaries
        2. How to work with file paths in Python
        3. How to use loops to avoid repetitive code
        4. How games load and organize graphics
        """
        # Create a dictionary to store all animation sequences
        # Each key represents a different animation state
        # Each value is a list that will hold the animation frames
        self.animations = {
            # Basic movement animations
            "up": [],  # Walking up
            "down": [],  # Walking down
            "left": [],  # Walking left
            "right": [],  # Walking right
            # Idle (standing still) animations
            "right_idle": [],  # Standing still facing right
            "left_idle": [],  # Standing still facing left
            "up_idle": [],  # Standing still facing up
            "down_idle": [],  # Standing still facing down
            # Tool animations - hoe (for farming)
            "right_hoe": [],  # Using hoe while facing right
            "left_hoe": [],  # Using hoe while facing left
            "up_hoe": [],  # Using hoe while facing up
            "down_hoe": [],  # Using hoe while facing down
            # Tool animations - axe (for chopping trees)
            "right_axe": [],  # Using axe while facing right
            "left_axe": [],  # Using axe while facing left
            "up_axe": [],  # Using axe while facing up
            "down_axe": [],  # Using axe while facing down
            # Tool animations - water (for watering plants)
            "right_water": [],  # Using watering can while facing right
            "left_water": [],  # Using watering can while facing left
            "up_water": [],  # Using watering can while facing up
            "down_water": [],  # Using watering can while facing down
        }

        # Load the animation frames for each animation state
        # This loop demonstrates how to avoid writing repetitive code
        for animation in self.animations.keys():
            # Build the full path to the animation folder
            full_path = "graphics/character/" + animation
            # Use the import_folder helper function to load all images in that folder
            # This fills the empty list with the actual animation frames
            self.animations[animation] = import_folder(full_path)

    def animate(self, dt):
        """
        Update the player's animation frame

        EDUCATIONAL CONCEPTS:
        - Frame-based animation
        - Delta time for smooth animation
        - Modular arithmetic (% operator)
        - List indexing
        - Type conversion (int())

        This method demonstrates:
        1. How animations work in games
        2. How delta time creates smooth motion
        3. How to cycle through animation frames
        4. How to handle list boundaries safely
        """
        # Increase the frame index based on time passed
        # Multiplying by 4 controls animation speed (higher = faster)
        # dt (delta time) ensures animation speed is consistent regardless of framerate
        self.frame_index += 4 * dt

        # If we've gone past the last frame, reset to the beginning
        # This creates a looping animation
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0  # Get the current animation frame and display it
        # We convert frame_index to int because list indices must be integers
        # self.status tells us which animation sequence to use
        self.image = self.animations[self.status][int(self.frame_index)]

    def input(self):
        """
        Handle keyboard input from the player

        EDUCATIONAL CONCEPTS:
        - Event handling and user input
        - Conditional statements (if/elif/else)
        - Boolean logic and operators
        - State management
        - Game controls and key mapping

        This method demonstrates:
        1. How games respond to player input
        2. How to check multiple conditions
        3. How to map keys to game actions
        4. How to prevent actions during certain states
        5. How to implement game controls
        """
        # Get the current state of all keyboard keys
        # This gives us a dictionary-like object with True/False for each key
        keys = pygame.key.get_pressed()

        # Only allow player actions if they're not using a tool and not sleeping
        # This demonstrates how to prevent actions during certain game states
        if not self.timers["tool use"].active and not self.sleep:

            # MOVEMENT CONTROLS
            # Handle vertical movement (up/down)
            if keys[pygame.K_UP]:
                self.direction.y = -1  # Move up (negative Y)
                self.status = "up"  # Set animation state
            elif keys[pygame.K_DOWN]:
                self.direction.y = 1  # Move down (positive Y)
                self.status = "down"  # Set animation state
            else:
                self.direction.y = 0  # Stop vertical movement

            # Handle horizontal movement (left/right)
            if keys[pygame.K_RIGHT]:
                self.direction.x = 1  # Move right (positive X)
                self.status = "right"  # Set animation state
            elif keys[pygame.K_LEFT]:
                self.direction.x = -1  # Move left (negative X)
                self.status = "left"  # Set animation state
            else:
                self.direction.x = 0  # Stop horizontal movement

            # TOOL USAGE
            # Use the currently selected tool
            if keys[pygame.K_SPACE]:
                # Start the tool use timer to prevent spam-clicking
                self.timers["tool use"].activate()
                # Stop movement while using tool
                self.direction = pygame.math.Vector2()
                # Reset animation to start of tool animation
                self.frame_index = 0

            # TOOL SWITCHING
            # Switch to the next tool in the list
            if keys[pygame.K_q] and not self.timers["tool switch"].active:
                # Prevent rapid tool switching with timer
                self.timers["tool switch"].activate()
                # Move to next tool
                self.tool_index += 1
                # Wrap around to first tool if we've reached the end
                self.tool_index = (
                    self.tool_index if self.tool_index < len(self.tools) else 0
                )
                # Update the selected tool
                self.selected_tool = self.tools[self.tool_index]

            # SEED PLANTING
            # Plant seeds using Ctrl key
            if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                # Start the seed use timer
                self.timers["seed use"].activate()
                # Stop movement while planting
                self.direction = pygame.math.Vector2()
                # Reset animation
                self.frame_index = 0

            # SEED SWITCHING
            # Switch to the next seed type
            if keys[pygame.K_e] and not self.timers["seed switch"].active:
                # Prevent rapid seed switching
                self.timers["seed switch"].activate()
                # Move to next seed
                self.seed_index += 1
                # Wrap around to first seed if at the end
                self.seed_index = (
                    self.seed_index if self.seed_index < len(self.seeds) else 0
                )
                # Update the selected seed
                self.selected_seed = self.seeds[self.seed_index]

            # INTERACTION
            # Interact with objects like shops or beds
            if keys[pygame.K_RETURN]:
                # Check if the player is touching any interactive objects
                collided_interaction_sprite = pygame.sprite.spritecollide(
                    self, self.interaction, False
                )
                # If we found an interactive object
                if collided_interaction_sprite:
                    # Check what type of object it is
                    if collided_interaction_sprite[0].name == "Trader":
                        # Open the shop interface
                        self.toggle_shop()
                    else:  # For beds or other objects, make the player sleep
                        self.status = "left_idle"
                        self.sleep = True

    def get_status(self):
        """
        Determine the player's current animation state

        EDUCATIONAL CONCEPTS:
        - String manipulation (.split(), string concatenation)
        - Vector mathematics (.magnitude())
        - Conditional logic
        - State machines in games

        This method demonstrates:
        1. How to work with strings programmatically
        2. How to detect when objects are moving vs. stationary
        3. How animation states work in games
        4. How to combine different game states
        """
        # Check if the player is moving by looking at the direction vector's magnitude
        # magnitude() gives us the length of the vector (0 = not moving)
        if self.direction.magnitude() == 0:
            # Player is not moving, so show idle animation
            # Split the current status and take the direction part, then add "_idle"
            # Example: "right" becomes "right_idle", "up_hoe" becomes "up_idle"
            self.status = self.status.split("_")[0] + "_idle"

        # Check if the player is currently using a tool
        if self.timers["tool use"].active:
            # Player is using a tool, so show tool animation
            # Split the status to get direction, then add the current tool            # Example: if facing "right" and using "hoe", becomes "right_hoe"
            self.status = self.status.split("_")[0] + "_" + self.selected_tool

    def update_timers(self):
        """
        Update all the player's timers

        EDUCATIONAL CONCEPTS:
        - Dictionary iteration (.values())
        - Object method calls
        - Timer systems in games
        - For loops

        This method demonstrates:
        1. How to work with collections of objects
        2. How timer systems prevent spam actions in games
        3. How to call methods on multiple objects efficiently
        4. How game systems work together
        """  # Go through each timer and update it
        # .values() gives us all the Timer objects in the dictionary
        for timer in self.timers.values():
            timer.update()  # Each timer updates its own countdown

    def collision(self, direction):
        """
        Handle collisions between the player and solid objects

        EDUCATIONAL CONCEPTS:
        - Collision detection algorithms
        - Rectangle intersection
        - Conditional statements
        - Coordinate systems and positioning
        - Sprite groups and iteration

        This method demonstrates:
        1. How collision detection works in 2D games
        2. How to prevent players from walking through walls
        3. How to handle horizontal vs. vertical collisions separately
        4. How to adjust object positions based on collisions
        5. How hitboxes work differently from visual sprites
        """
        # Check collision with each solid object in the game
        for sprite in self.collision_sprites.sprites():
            # Only check sprites that have a hitbox (collision rectangle)
            if hasattr(sprite, "hitbox"):
                # Check if the player's hitbox overlaps with the sprite's hitbox
                if sprite.hitbox.colliderect(self.hitbox):

                    # Handle horizontal collisions (left/right movement)
                    if direction == "horizontal":
                        if self.direction.x > 0:  # Player is moving right
                            # Stop player at the left edge of the obstacle
                            self.hitbox.right = sprite.hitbox.left
                        if self.direction.x < 0:  # Player is moving left
                            # Stop player at the right edge of the obstacle
                            self.hitbox.left = sprite.hitbox.right

                        # Update the player's display rectangle and position
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx

                    # Handle vertical collisions (up/down movement)
                    if direction == "vertical":
                        if self.direction.y > 0:  # Player is moving down
                            # Stop player at the top edge of the obstacle
                            self.hitbox.bottom = sprite.hitbox.top
                        if self.direction.y < 0:  # Player is moving up
                            # Stop player at the bottom edge of the obstacle
                            self.hitbox.top = sprite.hitbox.bottom
                        # Update the player's display rectangle and position
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery

    def move(self, dt):
        """
        Move the player and handle collisions

        EDUCATIONAL CONCEPTS:
        - Vector normalization
        - Delta time for frame-rate independent movement
        - Coordinate system updates
        - Collision detection integration
        - Mathematical operations in games

        This method demonstrates:
        1. How smooth movement works in games
        2. How to normalize vectors for consistent speed
        3. How delta time creates frame-rate independent motion
        4. How to separate horizontal and vertical collision checking
        5. How coordinate systems work in 2D games
        """
        # Normalize the direction vector to ensure consistent movement speed
        # This prevents diagonal movement from being faster than straight movement
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

        # HORIZONTAL MOVEMENT
        # Update horizontal position based on direction, speed, and time
        # dt (delta time) ensures movement is consistent regardless of frame rate
        self.pos.x += self.direction.x * self.speed * dt

        # Update the hitbox position (used for collision detection)
        self.hitbox.centerx = round(self.pos.x)

        # Update the visual rectangle position (what the player sees)
        self.rect.centerx = self.hitbox.centerx

        # Check for horizontal collisions and adjust position if needed
        self.collision("horizontal")

        # VERTICAL MOVEMENT
        # Same process for vertical movement
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        # Check for vertical collisions separately
        self.collision("vertical")

    def update(self, dt):
        """
        Main update method called every frame

        EDUCATIONAL CONCEPTS:
        - Main game loop integration
        - Method calling and coordination
        - Game system architecture
        - Frame-based updates

        This method demonstrates:
        1. How all game systems work together
        2. The order of operations in game updates
        3. How the main game loop coordinates different systems
        4. How delta time is passed through the system
        """
        # Process player input first
        self.input()

        # Update the player's animation state based on current conditions
        self.get_status()

        # Update all timers (for preventing spam actions)
        self.update_timers()

        # Calculate where tools should be aimed
        self.get_target_pos()

        # Move the player and handle collisions
        self.move(dt)

        # Update the player's animation frame
        self.animate(dt)
