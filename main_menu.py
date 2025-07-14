import pygame
from settings import *
import sys
import os
from timer import Timer
from settings_menu import SettingsMenu


class MainMenu:
    def __init__(self, start_game, camera_change_callback=None):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font("font/LycheeSoda.ttf", 50)
        self.title_font = pygame.font.Font("font/LycheeSoda.ttf", 100)
        self.start_game = start_game
        self.camera_change_callback = camera_change_callback
        self.options = ["Start Game", "Credits", "Options", "Quit"]
        self.selected_index = 0
        self.state = "main"  # main, credits, settings

        # Load the "Corn" graphic
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.corn_surf = pygame.image.load(
            os.path.join(base_path, "graphics/overlay/corn.png")
        ).convert_alpha()

        # Timer for input delay
        self.input_timer = Timer(200)
        # Settings menu
        self.settings_menu = SettingsMenu(camera_change_callback)

    def display(self):
        self.display_surface.fill("black")

        if self.state == "main":
            self.display_main_menu()
        elif self.state == "credits":
            self.display_credits()
        elif self.state == "settings":
            # Settings menu handles its own display
            result = self.settings_menu.update()
            if result == "back":
                self.state = "main"
                self.input_timer.activate()

    def display_main_menu(self):
        # display the title: "PyDew Valley: GAIC 25" with double the font size
        title_surf = self.title_font.render("PyDew Valley: GAIC 25", True, "White")
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4))
        self.display_surface.blit(title_surf, title_rect)

        for index, option in enumerate(self.options):
            color = "White" if index == self.selected_index else "Gray"
            text_surf = self.font.render(option, True, color)
            text_rect = text_surf.get_rect(
                center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + index * 60)
            )
            self.display_surface.blit(text_surf, text_rect)

            # Draw the "Corn" graphic next to the selected option
            if index == self.selected_index:
                corn_rect = self.corn_surf.get_rect(
                    midright=(text_rect.left - 10, text_rect.centery)
                )
                self.display_surface.blit(self.corn_surf, corn_rect)

    def display_credits(self):
        # Credits title
        title_surf = self.title_font.render("Credits", True, "White")
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH / 2, 100))
        self.display_surface.blit(title_surf, title_rect)

        # Credits content
        credits_text = [
            "GatorAI Camp 2025",
            "",
            "Based on PyDew Valley",
            "Base code by: Christian Koch",
            "Built with Python & Pygame",
            "",
            "Press ESC to return to main menu",
        ]

        start_y = 200
        for i, line in enumerate(credits_text):
            if line:  # Skip empty lines for spacing
                color = (
                    "Yellow"
                    if line
                    in [
                        "GatorAI Camp 2025",
                        "Game Development Team:",
                        "Special Thanks:",
                    ]
                    else "White"
                )
                font_size = (
                    self.font if line != "GatorAI Camp 2025" else self.title_font
                )
                text_surf = font_size.render(line, True, color)
                text_rect = text_surf.get_rect(
                    center=(SCREEN_WIDTH / 2, start_y + i * 40)
                )
                self.display_surface.blit(text_surf, text_rect)

    def input(self):
        keys = pygame.key.get_pressed()
        self.input_timer.update()

        if self.input_timer.active:
            return

        if self.state == "main":
            self.handle_main_input(keys)
        elif self.state == "credits":
            self.handle_credits_input(keys)
        # Settings input is handled in the display method

    def handle_main_input(self, keys):
        if keys[pygame.K_UP]:
            self.selected_index = (self.selected_index - 1) % len(self.options)
            self.input_timer.activate()
        elif keys[pygame.K_DOWN]:
            self.selected_index = (self.selected_index + 1) % len(self.options)
            self.input_timer.activate()
        elif keys[pygame.K_RETURN]:
            if self.selected_index == 0:  # Start Game
                self.start_game()
                self.state = "credits"
                self.input_timer.activate()
            elif self.selected_index == 2:  # Options
                self.state = "settings"
                self.input_timer.activate()
            elif self.selected_index == 3:  # Quit
                pygame.quit()
                sys.exit()

    def handle_credits_input(self, keys):
        if keys[pygame.K_ESCAPE]:
            self.state = "main"
            self.input_timer.activate()

    def update(self):
        self.input()
        self.display()
