"""
PyDew Valley - Level Manager Module
==================================
This module manages the entire game world including map loading, sprite management,
and game systems coordination. This is one of the most complex files in our game!

Educational Concepts Covered:
- File I/O and map loading from external files
- Sprite group management and organization
- Camera systems for following the player
- Game state management
- Audio system integration
- Weather and environmental systems
- Collision detection systems
- Object-oriented design patterns

This file demonstrates advanced game programming concepts and shows how
different game systems work together to create a complete game experience.
"""

import pygame
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree, Interaction, Particle
from pytmx.util_pygame import load_pygame
from support import *
from transition import Transition
from soil import SoilLayer
from sky import Rain, Sky
from random import randint
from trader_menu import TraderMenu
import game_settings
import os
from dialogue_system import DialogueSystem


class Level:
    """
    Level Class - The Game World Manager
    ===================================
    This class is responsible for managing the entire game world including:
    - Loading and setting up the game map from external files
    - Managing all game objects (sprites) in organized groups
    - Handling the camera system that follows the player
    - Coordinating different game systems (weather, audio, shops, etc.)
    - Managing game state transitions (day/night, sleeping, etc.)

    EDUCATIONAL CONCEPTS:
    - Complex system architecture
    - Sprite group management
    - File loading and parsing
    - Camera and viewport systems
    - Audio system integration
    - Game state management
    - Object coordination

    This demonstrates how large game projects organize and manage complexity!
    """

    def __init__(self, emotions_deque):
        """
        Initialize the Game World
        ========================
        Sets up all the game systems, loads the map, creates sprite groups,
        and initializes audio, weather, and other game systems.

        EDUCATIONAL CONCEPTS:
        - Constructor method with complex initialization
        - Multiple system initialization
        - Dependency management between objects
        - Audio system setup
        - Random number generation for game variety
        """
        # Get the main display surface (the game window)
        self.display_surface = pygame.display.get_surface()

        # Store emotions for AI dialogue context
        self.emotions_deque = emotions_deque

        # SPRITE GROUP ORGANIZATION
        # Different sprite groups help us organize and manage game objects efficiently
        self.all_sprites = CameraGroup()  # Custom camera-following sprite group
        self.collision_sprites = pygame.sprite.Group()  # Objects that block movement
        self.tree_sprites = pygame.sprite.Group()  # Trees that can be chopped
        self.interaction_sprites = (
            pygame.sprite.Group()
        )  # Objects player can interact with

        # GAME SYSTEMS INITIALIZATION
        # Create the soil system for farming mechanics
        self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites)

        # Load the game map and create all game objects
        self.setup()

        # Create the UI overlay (shows player inventory, tools, etc.)
        self.overlay = Overlay(self.player, emotions_deque)

        # Create the day/night transition system
        self.transition = Transition(self.reset, self.player)

        # Register this level globally for audio updates
        game_settings.set_current_level(self)

        # WEATHER SYSTEM
        # Create rain and sky systems for environmental variety
        self.rain = Rain(self.all_sprites)
        self.raining = randint(0, 10) > 7  # 30% chance of rain
        self.soil_layer.raining = self.raining  # Tell soil system about rain
        self.sky = Sky()  # SHOP AND DIALOGUE SYSTEM
        # Create the trading menu system and dialogue system
        self.menu = TraderMenu(self.player, self.open_trader_menu)
        self.shop_active = False
        self.dialogue_system = DialogueSystem()

        # AUDIO SYSTEM
        # Load and set up game sounds and music
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.success = pygame.mixer.Sound(os.path.join(base_path, "audio/success.wav"))
        self.music = pygame.mixer.Sound(os.path.join(base_path, "audio/music.mp3"))

        # Apply volume settings from game settings and start background music
        self.update_audio_volumes()
        self.music.play(loops=-1)  # -1 means loop forever

    def setup(self):
        """
        Load and Set Up the Game Map
        ============================
        This method loads the game map from an external TMX file and creates
        all the game objects (sprites) based on the map data.

        EDUCATIONAL CONCEPTS:
        - File I/O and external data loading
        - Map/tilemap systems in games
        - Loops within loops (nested iteration)
        - Object creation from data
        - Coordinate system mapping
        - Layer-based rendering systems
        """
        # Load the map data from an external TMX file
        # TMX is a standard format for tile-based game maps
        tmx_data = load_pygame("data/map.tmx")

        # HOUSE LAYERS - Create house floor and furniture
        # We process different layers separately to control rendering order
        for layer in ["HouseFloor", "HouseFurnitureBottom"]:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic(
                    (
                        x * TILE_SIZE,
                        y * TILE_SIZE,
                    ),  # Convert tile coordinates to pixels
                    surf,  # The image/surface for this tile
                    self.all_sprites,  # Add to main sprite group
                    LAYERS["house bottom"],  # Set rendering layer
                )

        # House walls and top furniture (rendered above the player)
        for layer in ["HouseWalls", "HouseFurnitureTop"]:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites)

        # FENCE OBJECTS - Create fence barriers
        # These are both visual and collision objects
        for x, y, surf in tmx_data.get_layer_by_name("Fence").tiles():
            Generic(
                (x * TILE_SIZE, y * TILE_SIZE),
                surf,
                [self.all_sprites, self.collision_sprites],  # Add to multiple groups
            )

        # WATER OBJECTS - Create animated water tiles
        water_frames = import_folder("graphics/water")  # Load water animation frames
        for x, y, surf in tmx_data.get_layer_by_name("Water").tiles():
            Water((x * TILE_SIZE, y * TILE_SIZE), water_frames, self.all_sprites)

        # TREE OBJECTS - Create interactive trees
        for obj in tmx_data.get_layer_by_name("Trees"):
            Tree(
                pos=(obj.x, obj.y),
                surf=obj.image,
                groups=[self.all_sprites, self.collision_sprites, self.tree_sprites],
                name=obj.name,
                player_add=self.player_add,  # Callback for when player gets items
            )

        # DECORATIVE WILDFLOWERS
        for obj in tmx_data.get_layer_by_name("Decoration"):
            WildFlower(
                (obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites]
            )

        # INVISIBLE COLLISION TILES - Create invisible barriers
        for x, y, surf in tmx_data.get_layer_by_name("Collision").tiles():
            Generic(
                (x * TILE_SIZE, y * TILE_SIZE),
                pygame.Surface((TILE_SIZE, TILE_SIZE)),  # Invisible surface
                self.collision_sprites,
            )

        # PLAYER AND INTERACTION OBJECTS
        # Find special objects like player start position and interactive areas
        for obj in tmx_data.get_layer_by_name("Player"):
            if obj.name == "Start":
                # Create the player at the starting position
                self.player = Player(
                    pos=(obj.x, obj.y),
                    group=self.all_sprites,
                    collision_sprites=self.collision_sprites,
                    tree_sprites=self.tree_sprites,
                    interaction=self.interaction_sprites,
                    soil_layer=self.soil_layer,
                    toggle_shop=self.toggle_shop,
                )

            if obj.name == "Bed":
                # Create bed interaction area for sleeping
                Interaction(
                    (obj.x, obj.y),
                    (obj.width, obj.height),
                    self.interaction_sprites,
                    obj.name,
                )

            if obj.name == "Trader":
                # Create trader interaction area for shopping
                Interaction(
                    (obj.x, obj.y),
                    (obj.width, obj.height),
                    self.interaction_sprites,
                    obj.name,
                )

        # BACKGROUND GROUND TILE
        # Create the base ground that covers the entire map
        Generic(
            pos=(0, 0),
            surf=pygame.image.load("graphics/world/ground.png").convert_alpha(),
            groups=self.all_sprites,
            z=LAYERS["ground"],  # Put it at the bottom layer
        )

    def update_audio_volumes(self):
        """
        Update Audio Volume Levels
        ==========================
        Applies the current volume settings to all audio in this level.

        EDUCATIONAL CONCEPTS:
        - Audio system management
        - Settings application
        - Volume control calculations
        - System integration
        """
        # Get current volume settings from the game settings
        master_vol = game_settings.get("master_volume")
        music_vol = game_settings.get("music_volume")
        sfx_vol = game_settings.get("sfx_volume")

        # Apply volumes - music uses master * music volume
        self.music.set_volume(master_vol * music_vol)
        # SFX uses master * sfx volume
        self.success.set_volume(master_vol * sfx_vol)

    def player_add(self, item):
        """
        Add Item to Player Inventory
        ============================
        Called when the player collects an item (like chopping a tree).
        Adds the item to inventory and plays a success sound.

        EDUCATIONAL CONCEPTS:
        - Callback functions
        - Inventory management
        - Audio feedback for player actions
        - System integration
        """
        # Add the item to the player's inventory
        self.player.item_inventory[item] += 1

        # Update volume before playing sound
        self.update_audio_volumes()
        self.success.play()

    def toggle_shop(self):
        """
        Start Trader Dialogue
        ====================
        Initiates dialogue with the trader before opening the shop.

        EDUCATIONAL CONCEPTS:
        - Dialogue system integration
        - Callback functions
        - Game state management
        """
        # Get the most recent emotion for context-aware dialogue
        recent_emotions = (
            list(self.emotions_deque) if self.emotions_deque else ["neutral"]
        )
        current_emotion = recent_emotions[0] if recent_emotions else "neutral"

        # Debug: Print emotion information
        print(f"🎭 Emotion Debug - Emotions in deque: {recent_emotions}")
        print(f"🎭 Current emotion being sent to AI: {current_emotion}")
        print(f"💰 Player money: ${self.player.money}")

        # For testing: Add some emotions to the deque if it's empty
        if not self.emotions_deque or len(self.emotions_deque) == 0:
            print("🎭 No emotions detected, adding test emotion...")
            import random

            test_emotions = ["happy", "surprised", "neutral", "excited"]
            test_emotion = random.choice(test_emotions)
            self.emotions_deque.append(test_emotion)
            current_emotion = test_emotion
            print(f"🎭 Added test emotion: {test_emotion}")

        # Determine player context based on their money and progress
        if self.player.money > 1000:
            situation = "player has lots of money and is doing well farming"
        elif self.player.money < 100:
            situation = "player is just starting out and has limited funds"
        else:
            situation = "player is making steady progress with their farm"

        # Create context dictionary for AI dialogue generation
        player_context = {
            "npc_name": "Merchant Pete",
            "npc_role": "friendly trader",
            "situation": situation,
            "emotion": current_emotion,
            "player_money": self.player.money,
        }

        # Start dialogue with trader using new system
        self.dialogue_system.start_dialogue(
            "trader", player_context=player_context, on_finish=self.open_trader_menu
        )

    def open_trader_menu(self):
        """
        Open the Trading Menu
        ====================
        Opens the actual trading interface after dialogue completes.

        EDUCATIONAL CONCEPTS:
        - Sequential game states
        - UI transition management
        """
        self.shop_active = True

    def reset(self):
        """
        Reset Game World for New Day
        ============================
        Called when the player sleeps. Resets various game systems
        for a new day including plants, weather, and trees.

        EDUCATIONAL CONCEPTS:
        - Game state reset procedures
        - System coordination
        - Random events (weather)
        - Object lifecycle management
        """
        # Reset plant growth in the soil system
        self.soil_layer.update_plants()

        # Reset soil watering and determine new weather
        self.soil_layer.remove_water()
        self.raining = randint(0, 10) > 7  # New random weather
        self.soil_layer.raining = self.raining
        if self.raining:
            self.soil_layer.water_all()  # Rain waters all soil

        # Reset apples on trees
        for tree in self.tree_sprites.sprites():
            # Remove old apples
            for apple in tree.apple_sprites.sprites():
                apple.kill()
            # Create new apples
            tree.create_fruit()

        # Reset sky color to daylight
        self.sky.start_color = [255, 255, 255]

    def plant_collision(self):
        """
        Check for Plant Harvesting
        ==========================
        Checks if the player is touching any harvestable plants
        and automatically harvests them.

        EDUCATIONAL CONCEPTS:
        - Collision detection between different object types
        - Automatic event triggering
        - Object destruction and effects
        - Grid-based data management
        """
        # Check if there are any plants to harvest
        if self.soil_layer.plant_sprites:
            for plant in self.soil_layer.plant_sprites.sprites():
                # Check if plant is ready and player is touching it
                if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
                    # Add the plant to player's inventory
                    self.player_add(plant.plant_type)

                    # Create a visual particle effect
                    Particle(
                        plant.rect.topleft,
                        plant.image,
                        self.all_sprites,
                        z=LAYERS["main"],
                    )

                    # Remove the plant from the game
                    plant.kill()

                    # Update the soil grid data
                    self.soil_layer.grid[plant.rect.centery // TILE_SIZE][
                        plant.rect.centerx // TILE_SIZE
                    ].remove("P")

    def run(self, dt, events=None):
        """
        Main Game Loop Update
        ====================
        Called every frame to update and render the game world.

        EDUCATIONAL CONCEPTS:
        - Game loops and frame-based updates
        - Conditional rendering based on game state
        - Delta time for frame-independent movement
        - System prioritization (UI vs gameplay)
        - Event handling and input prioritization

        Parameters:
        dt (float): Delta time - time since last frame in seconds
        events (list): Pygame events for this frame
        """
        if events is None:
            events = []

        # Handle ESC key for shop closure
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and self.shop_active:
                    self.shop_active = False

        # RENDERING - Draw the world
        self.display_surface.fill("black")
        self.all_sprites.custom_draw(self.player)

        # GAME LOGIC UPDATES - Priority order is important!
        if self.dialogue_system.active:
            # If dialogue is active, only update dialogue logic and consume events
            self.dialogue_system.update(events)
            # Don't process other game logic while dialogue is active
        elif self.shop_active:
            # If shop is open, only update the shop menu
            self.menu.update()
        else:
            # Normal gameplay updates
            self.all_sprites.update(dt)
            self.plant_collision()
            self.soil_layer.update_plants(dt)

        # UI AND VISUAL EFFECTS
        self.overlay.display()

        # Note: Dialogue rendering is handled in dialogue_system.update()

        # Weather effects (only during normal gameplay)
        if self.raining and not self.shop_active and not self.dialogue_system.active:
            self.rain.update()

        # Sky color transitions (day/night cycle)
        self.sky.display(dt)

        # TRANSITION EFFECTS
        if self.player.sleep:
            self.transition.play()


class CameraGroup(pygame.sprite.Group):
    """
    Camera-Following Sprite Group
    ============================
    A custom sprite group that automatically centers the camera on the player
    and renders sprites in the correct order based on their screen position.

    EDUCATIONAL CONCEPTS:
    - Inheritance (extends pygame.sprite.Group)
    - Camera systems in games
    - Viewport and world coordinates
    - Sprite rendering order
    - Mathematical coordinate transformations
    """

    def __init__(self):
        """
        Initialize the Camera System
        ===========================
        Sets up the camera offset and gets the display surface.
        """
        super().__init__()  # Initialize the parent sprite group
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()  # Camera offset from world origin

    def custom_draw(self, player):
        """
        Draw All Sprites with Camera Offset
        ===================================
        Calculates camera position based on player location and draws
        all sprites with proper layering and offset.

        EDUCATIONAL CONCEPTS:
        - Camera following algorithms
        - Coordinate system transformations
        - Sprite layering and depth sorting
        - Vector mathematics in games

        Parameters:
        player: The player object to center the camera on
        """
        # CAMERA POSITIONING
        # Center the camera on the player
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

        # LAYERED RENDERING
        # Draw sprites in layer order for proper visual layering
        for layer in LAYERS.values():
            # Sort sprites by their Y position for proper depth
            for sprite in sorted(
                self.sprites(), key=lambda sprite: sprite.rect.centery
            ):
                # Only draw sprites that belong to this layer
                if sprite.z == layer:
                    # Calculate sprite position relative to camera
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset

                    # Draw the sprite at the offset position
                    self.display_surface.blit(sprite.image, offset_rect)

                    # DEBUG VISUALIZATION (commented out)
                    # Uncomment these lines to see collision boxes and tool ranges
                    # if sprite == player:
                    #     pygame.draw.rect(self.display_surface,'red',offset_rect,5)
                    #     hitbox_rect = player.hitbox.copy()
                    #     hitbox_rect.center = offset_rect.center
                    #     pygame.draw.rect(self.display_surface,'green',hitbox_rect,5)
                    #     target_pos = offset_rect.center + PLAYER_TOOL_OFFSET[player.status.split('_')[0]]
                    #     pygame.draw.circle(self.display_surface,'blue',target_pos,5)
