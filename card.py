import pygame
import random
from constants import *

class Card:
    def __init__(self, color: str, value: str):
        # each card has a color, a number value and a rectangle image
        self.color = color
        self.value = value
        self.image = None
        self.rect = pygame.Rect(0, 0, CARD_WIDTH, CARD_HEIGHT)
        
    def load_image(self):

        # get card-width and height
        card_img = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        
        # set the colors of the images according to their color values
        if self.color == "red":
            card_img.fill(RED)
        elif self.color == "blue":
            card_img.fill(BLUE)
        elif self.color == "green":
            card_img.fill(GREEN)
        elif self.color == "yellow":
            card_img.fill(YELLOW)
        else:  # wild cards are black
            card_img.fill(BLACK)
            
        # white border
        pygame.draw.rect(card_img, WHITE, (3, 3, CARD_WIDTH-6, CARD_HEIGHT-6), 2)
        
        # print the value of the card on it
        font = pygame.font.SysFont('Arial', 30, bold=True)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    shadow = font.render(self.value, True, BLACK)
                    shadow_rect = shadow.get_rect(center=(CARD_WIDTH/2 + dx, CARD_HEIGHT/2 + dy))
                    card_img.blit(shadow, shadow_rect)
        text = font.render(self.value, True, WHITE)
        text_rect = text.get_rect(center=(CARD_WIDTH/2, CARD_HEIGHT/2))
        card_img.blit(text, text_rect)
        
        self.image = card_img
        return card_img

    # print card info
    def __str__(self):
        return f"{self.color} {self.value}"

    # check if two cards are exactly the same
    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return self.color == other.color and self.value == other.value

    # make a copy of the card
    def clone(self):
        return Card(self.color, self.value)



class Deck:
    def __init__(self):
        # the deck in the middle as an array of cards
        self.cards = []
        self.build()
        
    def build(self):
        # build the deck as having one 0 for each color + 2 of all other numbers
        for color in COLORS:
            self.cards.append(Card(color, "0"))
            
            for value in VALUES[1:]:
                self.cards.append(Card(color, value))
                self.cards.append(Card(color, value))
                
        # 4 of each type of wild cards
        for _ in range(4):
            for special in SPECIAL_CARDS:
                self.cards.append(Card("wild", special))
                
        # shuffle all values
        self.shuffle()
        
    def shuffle(self):
        random.shuffle(self.cards)
        
    def draw_card(self):
        # pop the drawn card if there is at least 1 card in the deck
        if len(self.cards) > 0:
            return self.cards.pop()
        return None
