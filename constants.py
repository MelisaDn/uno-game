import pygame

pygame.init()

# set the constants for main frame
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 600
CARD_WIDTH = 100
CARD_HEIGHT = 150
CARD_SPACING = 30

# set the color values
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)

# display the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Uno Game - 4 Players")

# list out all possible colors and number values
COLORS = ["red", "blue", "green", "yellow"]
VALUES = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "skip", "reverse", "draw2"]
SPECIAL_CARDS = ["wild", "wild_draw4"]
