import pygame
# Initialize pygame
pygame.init()

# Constants for the game
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 600
CARD_WIDTH = 100
CARD_HEIGHT = 150
CARD_SPACING = 30

# Colors for the cards and background
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Uno Game - 4 Players")

# Card colors and values
COLORS = ["red", "blue", "green", "yellow"]
VALUES = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "skip", "reverse", "draw2"]
SPECIAL_CARDS = ["wild", "wild_draw4"]