import pygame
import random
from constants import *

class Card:
    def __init__(self, color: str, value: str):
        self.color = color
        self.value = value
        self.image = None
        self.rect = pygame.Rect(0, 0, CARD_WIDTH, CARD_HEIGHT)
        
    def load_image(self):
        card_img = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        
        # Set card color
        if self.color == "red":
            card_img.fill(RED)
        elif self.color == "blue":
            card_img.fill(BLUE)
        elif self.color == "green":
            card_img.fill(GREEN)
        elif self.color == "yellow":
            card_img.fill(YELLOW)
        else:  # wild cards
            card_img.fill(BLACK)
            
        # Add a white border
        pygame.draw.rect(card_img, WHITE, (3, 3, CARD_WIDTH-6, CARD_HEIGHT-6), 2)
        
        # Add the value text
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
        
    def __str__(self):
        return f"{self.color} {self.value}"

    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return self.color == other.color and self.value == other.value

    def clone(self):
        return Card(self.color, self.value)



class Deck:
    def __init__(self):
        self.cards = []
        self.build()
        
    def build(self):
        # Create regular cards 
        for color in COLORS:
            # One zero for each color
            self.cards.append(Card(color, "0"))
            
            # Two of each other value
            for value in VALUES[1:]:
                self.cards.append(Card(color, value))
                self.cards.append(Card(color, value))
                
        # Create wild cards (4 of each type)
        for _ in range(4):
            for special in SPECIAL_CARDS:
                self.cards.append(Card("wild", special))
                
        # Shuffle the deck
        self.shuffle()
        
    def shuffle(self):
        random.shuffle(self.cards)
        
    def draw_card(self):
        if len(self.cards) > 0:
            return self.cards.pop()
        return None
