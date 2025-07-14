"""
Game Settings and Configuration
==============================
This file contains all the important settings and constants for our game.
In programming, it's good practice to keep all configuration values in one place!

Educational Concepts:
- Constants and global variables
- Dictionaries for organizing data
- Coordinate systems and positioning
- Game design parameters
"""

from pygame.math import Vector2

# =============================================================================
# SCREEN AND DISPLAY SETTINGS
# =============================================================================
# These control how big our game window is and how detailed the graphics are

SCREEN_WIDTH = 1280  # Width of game window in pixels
SCREEN_HEIGHT = 720  # Height of game window in pixels
TILE_SIZE = 64  # Size of each tile in our game world (pixels)

# =============================================================================
# USER INTERFACE POSITIONS
# =============================================================================
# These dictionaries tell us where to place UI elements on the screen

# Overlay positions for showing tools and seeds
OVERLAY_POSITIONS = {
    "tool": (40, SCREEN_HEIGHT - 15),  # Where to show current tool
    "seed": (70, SCREEN_HEIGHT - 5),  # Where to show current seed
}

# Tool positioning offsets relative to player
PLAYER_TOOL_OFFSET = {
    "left": Vector2(-50, 40),  # Tool position when facing left
    "right": Vector2(50, 40),  # Tool position when facing right
    "up": Vector2(0, -10),  # Tool position when facing up
    "down": Vector2(0, 50),  # Tool position when facing down
}

# =============================================================================
# GRAPHICS LAYERS SYSTEM
# =============================================================================
# This controls which graphics appear in front of others (like z-depth)
# Lower numbers are drawn first (in the background)

LAYERS = {
    "water": 0,  # Water is drawn first (background)
    "ground": 1,  # Ground tiles
    "soil": 2,  # Farmable soil
    "soil water": 3,  # Wet soil
    "rain floor": 4,  # Rain effects on ground
    "house bottom": 5,  # Bottom part of buildings
    "ground plant": 6,  # Plants growing on ground
    "main": 7,  # Player and main characters
    "house top": 8,  # Top part of buildings (roofs)
    "fruit": 9,  # Harvestable fruits
    "rain drops": 10,  # Rain drop effects (foreground)
}

# =============================================================================
# GAME WORLD OBJECT POSITIONS
# =============================================================================
# These dictionaries define where special objects (like apples) appear in the world

# Apple tree positions - Small and Large trees have different apple locations
APPLE_POS = {
    "Small": [
        (18, 17),
        (30, 37),
        (12, 50),
        (30, 45),
        (20, 30),
        (30, 10),
    ],  # Small tree apple spots
    "Large": [
        (30, 24),
        (60, 65),
        (50, 50),
        (16, 40),
        (45, 50),
        (42, 70),
    ],  # Large tree apple spots
}

# =============================================================================
# GAME MECHANICS AND TIMING
# =============================================================================
# These settings control how the game plays and feels

# Plant growth speeds (lower numbers = faster growth)
GROW_SPEED = {
    "corn": 0.1,  # Corn grows relatively fast
    "tomato": 0.07,  # Tomatoes grow a bit slower
}

# =============================================================================
# ECONOMIC SYSTEM - PRICES AND VALUES
# =============================================================================
# These dictionaries control the game's economy

# How much money you get for selling items
SALE_PRICES = {
    "wood": 4,  # Wood sells for 4 coins
    "apple": 2,  # Apples sell for 2 coins
    "corn": 10,  # Corn sells for 10 coins
    "tomato": 20,  # Tomatoes sell for 20 coins (most valuable!)
}

# How much it costs to buy seeds
PURCHASE_PRICES = {
    "corn": 4,  # Corn seeds cost 4 coins
    "tomato": 5,  # Tomato seeds cost 5 coins
}
