from card import Card, Deck
from player import Player
import random

class UnoGame:
    def __init__(self):
        self.deck = Deck()
        self.discard_pile = []
        self.players = [
            Player("Player 1 (Human)", 0),  # bottom
            Player("Player 2 (Rule AI)", 1),  # left
            Player("Player 3 (Minimax AI)", 2),  # top
            Player("Player 4 (Rule AI)", 3)  # right
        ]
        self.current_player = 0
        self.direction = 1  # 1: clockwise, -1: counter-clockwise
        
        # Initialize the game
        self.setup_game()
        
    def setup_game(self):
        # Deal 7 cards to each player
        for player in self.players:
            player.draw(self.deck, 7)
            
        # Turn over the top card to start the discard pile
        first_card = self.deck.draw_card()
        
        while first_card.color == "wild":
            self.deck.cards.insert(0, first_card)  
            self.deck.shuffle()
            first_card = self.deck.draw_card()
            
        self.discard_pile.append(first_card)
        
    def get_top_card(self):
        if self.discard_pile:
            return self.discard_pile[-1]
        return None
        
    def is_valid_move(self, card: Card) -> bool:
        top_card = self.get_top_card()
        
        # Wild cards can always be played
        if card.color == "wild":
            return True
            
        # Same color or same value is valid
        if card.color == top_card.color or card.value == top_card.value:
            return True
            
        return False
        
    def play_card(self, card_index: int) -> bool:
        player = self.players[self.current_player]
        if 0 <= card_index < len(player.hand):
            card = player.hand[card_index]
            if self.is_valid_move(card):
                played_card = player.play_card(card_index)
                self.discard_pile.append(played_card)
                
                # Handle wild cards - set color based on player
                if played_card.color == "wild":
                    if self.current_player == 0:  # Human player
                        # For now, just pick a random color
                        # In a real implementation, you would display a color picker
                        played_card.color = random.choice(["red", "blue", "green", "yellow"])
                    else:  # AI players
                        # Find most common color in hand
                        colors = {"red": 0, "blue": 0, "green": 0, "yellow": 0}
                        for c in player.hand:
                            if c.color in colors:
                                colors[c.color] += 1
                        
                        chosen_color = max(colors, key=colors.get)
                        if all(count == 0 for count in colors.values()):
                            chosen_color = random.choice(["red", "blue", "green", "yellow"])
                        
                        played_card.color = chosen_color
                        print(f"{player.name} chose {chosen_color} for wild card")
                
                # Handle special cards
                self.handle_special_card(played_card)
                
                # Next player's turn
                self.next_turn()
                return True
        return False
        
    def handle_special_card(self, card: Card):
        # Skip: next player misses a turn
        if card.value == "skip":
            self.next_turn()
            
        # Reverse: change direction
        elif card.value == "reverse":
            self.direction *= -1
            
        # Draw 2: next player draws 2 cards and misses a turn
        elif card.value == "draw2":
            next_player = (self.current_player + self.direction) % 4
            self.players[next_player].draw(self.deck, 2)
            self.next_turn()
            
        # Wild Draw 4: next player draws 4 cards and misses a turn
        elif card.value == "wild_draw4":
            next_player = (self.current_player + self.direction) % 4
            self.players[next_player].draw(self.deck, 4)
            self.next_turn()
            
    def next_turn(self):
        self.current_player = (self.current_player + self.direction) % 4
        
    def draw_from_deck(self):
        player = self.players[self.current_player]
        player.draw(self.deck, 1)
        self.next_turn()
