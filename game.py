from card import Card, Deck
from player import Player
import random
from typing import Optional

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

        # Always allow wild and wild_draw4
        if card.value in ["wild", "wild_draw4"]:
            return True

        # Match by color or value
        if card.color == top_card.color or card.value == top_card.value:
            return True

        return False

        
    def play_card(self, card_index: int) -> bool:
        player = self.players[self.current_player]

        if 0 <= card_index < len(player.hand):
            card = player.hand[card_index]
            
            # Store original values before any modifications
            original_value = card.value
            original_color = card.color
            
            # Handle wild color selection
            if original_value in ["wild", "wild_draw4"] and self.current_player != 0:
                colors = {"red": 0, "blue": 0, "green": 0, "yellow": 0}
                for c in player.hand:
                    if c.color in colors:
                        colors[c.color] += 1
                
                # Choose most frequent color or random if no colored cards
                if all(count == 0 for count in colors.values()):
                    chosen_color = random.choice(["red", "blue", "green", "yellow"])
                else:
                    chosen_color = max(colors, key=colors.get)
                
                # Check if valid move with original wild card state
                valid_move = self.is_valid_move(card)
                
                # Now set the chosen color if valid move
                if valid_move:
                    card.color = chosen_color
                    print(f"{player.name} chose {chosen_color} for wild card")
                else:
                    return False
            else:
                # Normal validation for non-wild cards
                valid_move = self.is_valid_move(card)
                
            if valid_move:
                # Print debug
                print(f"{player.name} is playing: {card.color} {card.value}")

                # Remove the card from hand
                played_card = player.play_card(card_index)

                # Add to discard pile
                self.discard_pile.append(played_card)

                # Handle special cards
                if original_value in ["skip", "draw2", "wild_draw4", "reverse"]:
                    self.handle_special_card(played_card)
                else:
                    self.next_turn()

                # Print confirmation after the move is completed
                print(f"{player.name} played {card.color} {card.value}")
                
                return True  # Play succeeded
                
        return False  # Invalid or unplayable


        
    def handle_special_card(self, card: Card):
        # Skip: next player misses a turn
        if card.value == "skip":
            # Advance turn twice - once to skip next player, once to go to player after that
            self.next_turn()  # Skip to next player
            self.next_turn()  # Skip to player after next
            
        # Reverse: change direction
        elif card.value == "reverse":
            self.direction *= -1
            self.next_turn() 
            
        # Draw 2: next player draws 2 cards and misses a turn
        elif card.value == "draw2":
            next_player = (self.current_player + self.direction) % 4
            self.players[next_player].draw(self.deck, 2)
            self.next_turn()  # Skip to next player
            self.next_turn()  # Skip to player after next
            
        # Wild Draw 4: next player draws 4 cards and misses a turn
        elif card.value == "wild_draw4":
            next_player = (self.current_player + self.direction) % 4
            self.players[next_player].draw(self.deck, 4)
            self.next_turn()  # Skip to next player
            self.next_turn()  # Skip to player after next
            
    def next_turn(self):
        self.current_player = (self.current_player + self.direction) % 4
        
    def draw_from_deck(self):
        player = self.players[self.current_player]
        player.draw(self.deck, 1)
        self.next_turn()


    def check_winner(self) -> Optional[str]:
        for player in self.players:
            if len(player.hand) == 0:
                return player.name
        return None