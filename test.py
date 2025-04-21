import pygame
import random
import time
from typing import List, Tuple, Dict, Optional
from copy import deepcopy

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 600
CARD_WIDTH = 100
CARD_HEIGHT = 150
CARD_SPACING = 30

# Colors
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

class Card:
    def __init__(self, color: str, value: str):
        self.color = color
        self.value = value
        # Placeholder for card image
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


class Player:
    def __init__(self, name: str, position: int):
        self.name = name
        self.hand = []
        self.position = position 
        
    def draw(self, deck: Deck, count: int = 1):
        for _ in range(count):
            card = deck.draw_card()
            if card:
                self.hand.append(card)
                
    def play_card(self, card_index: int):
        if 0 <= card_index < len(self.hand):
            return self.hand.pop(card_index)
        return None


class RuleBasedAI:
    """Simple rule-based AI that follows basic UNO strategy"""
    
    def choose_move(self, player, game):
        top_card = game.get_top_card()
        playable_cards = []
        
        # Find all playable cards
        for i, card in enumerate(player.hand):
            if game.is_valid_move(card):
                playable_cards.append((i, card))
        
        if not playable_cards:
            # No playable cards, draw from deck
            return None
        
        # Prioritize cards:
        # 1. Special cards (Skip, Reverse, Draw Two)
        # 2. Number cards
        # 3. Wild cards (save them for when needed)
        
        special_cards = [(i, card) for i, card in playable_cards 
                        if card.color != "wild" and card.value in ["skip", "reverse", "draw2"]]
        number_cards = [(i, card) for i, card in playable_cards 
                       if card.color != "wild" and card.value not in ["skip", "reverse", "draw2"]]
        wild_cards = [(i, card) for i, card in playable_cards if card.color == "wild"]
        
        # Choose in order of priority
        if special_cards:
            choice = random.choice(special_cards)
            return choice[0]  # Return the index
        elif number_cards:
            choice = random.choice(number_cards)
            return choice[0]  # Return the index
        elif wild_cards:
            choice = random.choice(wild_cards)
            return choice[0]  # Return the index
        
        return None  # Draw a card as fallback


class MinimaxAI:
    """Advanced AI using Minimax with Alpha-Beta Pruning"""
    
    def __init__(self, max_depth=3):
        self.max_depth = max_depth
        self.colors = ["red", "blue", "green", "yellow"]  # For wild card color choice
    
    def choose_move(self, player, game):
        # Clone the game to avoid modifying the actual game state
        game_clone = self._clone_game_state(game)
        player_clone = game_clone.players[game.current_player]
        
        # Find all valid moves
        valid_moves = []
        for i, card in enumerate(player.hand):
            if game.is_valid_move(card):
                valid_moves.append(i)
        
        if not valid_moves:
            return None  # Draw a card
        
        # Evaluate each move using minimax
        best_score = float('-inf')
        best_move = None
        
        for move in valid_moves:
            # Clone the game state for each move evaluation
            move_game = self._clone_game_state(game)
            move_player = move_game.players[game.current_player]
            
            # Apply the move in the cloned game
            played_card = move_player.hand[move]
            if played_card.color == "wild":
                # Choose most common color in hand for wild cards
                best_color = self._best_wild_color(move_player.hand)
                played_card.color = best_color
                
            move_game.play_card(move)
            
            # Calculate score with minimax
            score = self._minimax(move_game, 0, False, float('-inf'), float('inf'))
            
            # Update best move if needed
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move
    
    def _best_wild_color(self, hand):
        """Choose the most frequent color in hand for wild cards"""
        color_count = {"red": 0, "blue": 0, "green": 0, "yellow": 0}
        
        for card in hand:
            if card.color in color_count:
                color_count[card.color] += 1
        
        return max(color_count, key=color_count.get)
    
    def _clone_game_state(self, game):
        clone = UnoGame.__new__(UnoGame)  # Create empty object without __init__
    
        clone.deck = Deck()
        clone.deck.cards = [card.clone() for card in game.deck.cards]
        
        clone.discard_pile = [card.clone() for card in game.discard_pile]
        
        clone.players = []
        for player in game.players:
            new_player = Player(player.name, player.position)
            new_player.hand = [card.clone() for card in player.hand]
            clone.players.append(new_player)
        
        clone.current_player = game.current_player
        clone.direction = game.direction
        
        return clone
    
    def _minimax(self, game, depth, maximizing_player, alpha, beta):
        """
        Minimax algorithm with alpha-beta pruning
        - game: current game state
        - depth: current search depth
        - maximizing_player: True if current player is the AI, False otherwise
        - alpha, beta: values for alpha-beta pruning
        """
        # Terminal conditions: max depth reached or game over
        if depth >= self.max_depth or self._is_game_over(game):
            return self._evaluate_state(game)
        
        if maximizing_player:
            max_eval = float('-inf')
            # Get current player's possible moves
            player = game.players[game.current_player]
            valid_moves = self._get_valid_moves(player, game)
            
            if not valid_moves:
                # Player has to draw; simulate drawing and continue
                cloned_game = self._clone_game_state(game)
                cloned_game.draw_from_deck()
                eval_score = self._minimax(cloned_game, depth + 1, False, alpha, beta)
                return eval_score
            
            for move in valid_moves:
                cloned_game = self._clone_game_state(game)
                cloned_player = cloned_game.players[game.current_player]
                cloned_game.play_card(move)
                
                eval_score = self._minimax(cloned_game, depth + 1, False, alpha, beta)
                max_eval = max(max_eval, eval_score)
                
                # Alpha-beta pruning
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
                
            return max_eval
        else:
            min_eval = float('inf')
            # Get current player's possible moves 
            player = game.players[game.current_player]
            valid_moves = self._get_valid_moves(player, game)
            
            if not valid_moves:
                # Player has to draw; simulate drawing and continue
                cloned_game = self._clone_game_state(game)
                cloned_game.draw_from_deck()
                eval_score = self._minimax(cloned_game, depth + 1, True, alpha, beta)
                return eval_score
            
            for move in valid_moves:
                cloned_game = self._clone_game_state(game)
                cloned_player = cloned_game.players[game.current_player]
                cloned_game.play_card(move)
                
                eval_score = self._minimax(cloned_game, depth + 1, True, alpha, beta)
                min_eval = min(min_eval, eval_score)
                
                # Alpha-beta pruning
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
                
            return min_eval
    
    def _get_valid_moves(self, player, game):
        """Get indices of valid moves for a player"""
        valid_moves = []
        for i, card in enumerate(player.hand):
            if game.is_valid_move(card):
                valid_moves.append(i)
        return valid_moves
    
    def _is_game_over(self, game):
        """Check if the game is over"""
        for player in game.players:
            if len(player.hand) == 0:
                return True
        return False
    
    def _evaluate_state(self, game):
        """
        Heuristic evaluation function for the game state
        Higher score is better for the AI player (Player 3)
        """
        ai_player_index = 2  # Player 3 (index 2) is our minimax AI
        ai_player = game.players[ai_player_index]
        
        # Base score: negative of number of cards (fewer cards is better)
        score = -len(ai_player.hand) * 10
        
        # Bonus for having cards that match the current top card
        top_card = game.get_top_card()
        matching_cards = 0
        special_cards = 0
        
        for card in ai_player.hand:
            if card.color == top_card.color or card.value == top_card.value:
                matching_cards += 1
            if card.value in ["skip", "reverse", "draw2"] or card.color == "wild":
                special_cards += 1
        
        score += matching_cards * 5
        score += special_cards * 3
        
        # Penalty for opponents with few cards
        for i, player in enumerate(game.players):
            if i != ai_player_index:
                if len(player.hand) <= 2:
                    score -= (3 - len(player.hand)) * 15  # Bigger penalty for opponents close to winning
        
        return score


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


class UnoInterface:
    def __init__(self):
        self.game = UnoGame()
        self.clock = pygame.time.Clock()
        self.selected_card_index = -1
        self.font = pygame.font.SysFont('Arial', 20)
        self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
        
        # Initialize AI players
        self.rule_based_ai = RuleBasedAI()
        self.minimax_ai = MinimaxAI(max_depth=3)
        
    def run(self):
        running = True
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Handle card selection and playing
                    if event.button == 1:  
                        self.handle_click(event.pos)
            
            # Let AI players take their turns
            self.ai_play_turn()
            
            # Draw everything
            self.draw_game()
            
            # Update the display
            pygame.display.flip()
            self.clock.tick(30)
            
        pygame.quit()
        
    def handle_click(self, pos):
        current_player = self.game.players[self.game.current_player]
        
        # Only allow human player (player 0) to click
        if self.game.current_player == 0:
            # Check if clicking on a card in hand
            for i, card in enumerate(current_player.hand):
                if card.rect.collidepoint(pos):
                    if self.game.play_card(i):
                        print(f"Played {card}")
                    else:
                        print(f"Invalid move: {card}")
                    break
                    
            # Check if clicking on the deck
            deck_rect = pygame.Rect(SCREEN_WIDTH//2 - CARD_WIDTH - 20, 
                                   SCREEN_HEIGHT//2 - CARD_HEIGHT//2,
                                   CARD_WIDTH, CARD_HEIGHT)
            if deck_rect.collidepoint(pos):
                self.game.draw_from_deck()
                print("Drew a card from the deck")
                
    def ai_play_turn(self):
        # Check if it's an AI player's turn
        if self.game.current_player != 0:  # Not the human player
            # Add a slight delay for better visualization
            pygame.time.delay(3000)
            
            current_player = self.game.players[self.game.current_player]
            move_index = None
            
            # Choose AI type based on player
            if self.game.current_player == 1:  # Player 2 (left) - Rule Based
                print(f"{current_player.name} thinking...")
                move_index = self.rule_based_ai.choose_move(current_player, self.game)
            elif self.game.current_player == 2:  # Player 3 (top) - Minimax
                print(f"{current_player.name} thinking with Minimax...")
                move_index = self.minimax_ai.choose_move(current_player, self.game)
            elif self.game.current_player == 3:  # Player 4 (right) - Rule Based
                print(f"{current_player.name} thinking...")
                move_index = self.rule_based_ai.choose_move(current_player, self.game)
            
            # Execute the move
            if move_index is not None:
                card = current_player.hand[move_index]
                
                # Play the card
                if self.game.play_card(move_index):
                    print(f"{current_player.name} played {card}")
                else:
                    print(f"Invalid move by {current_player.name}: {card}")
                    # This shouldn't happen if AI is working correctly
            else:
                # Draw a card
                self.game.draw_from_deck()
                print(f"{current_player.name} drew a card")
            
            # Update display to show AI move
            self.draw_game()
            pygame.display.flip()
        
    def draw_game(self):
        # Fill background
        screen.fill(BLACK)
        
        # Draw deck and discard pile
        self.draw_deck()
        self.draw_discard_pile()
        
        # Draw player hands
        for player in self.game.players:
            self.draw_player_hand(player)
            
        # Draw current player indicator
        current_player = self.game.players[self.game.current_player]
        indicator = self.font.render(f"Current Turn: {current_player.name}", True, WHITE)
        screen.blit(indicator, (20, 20))
        
        # Draw card count for each player
        for i, player in enumerate(self.game.players):
            if i == 0:  # Bottom player
                count_pos = (20, SCREEN_HEIGHT - 40)
            elif i == 1:  # Left player
                count_pos = (20, 60)
            elif i == 2:  # Top player
                count_pos = (SCREEN_WIDTH - 150, 60)
            else:  # Right player
                count_pos = (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 40)
            
            count_text = self.font.render(f"{player.name}: {len(player.hand)} cards", True, WHITE)
            screen.blit(count_text, count_pos)
        
    def draw_deck(self):
        # Draw the deck
        deck_img = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        deck_img.fill(BLACK)
        pygame.draw.rect(deck_img, WHITE, (3, 3, CARD_WIDTH-6, CARD_HEIGHT-6), 2)
        
        # Add "UNO" text
        font = pygame.font.SysFont('Arial', 30, bold=True)
        text = font.render("UNO", True, WHITE)
        text_rect = text.get_rect(center=(CARD_WIDTH/2, CARD_HEIGHT/2))
        deck_img.blit(text, text_rect)
        
        deck_rect = pygame.Rect(SCREEN_WIDTH//2 - CARD_WIDTH - 20, 
                               SCREEN_HEIGHT//2 - CARD_HEIGHT//2,
                               CARD_WIDTH, CARD_HEIGHT)
        screen.blit(deck_img, deck_rect)
        
        # Show remaining cards count
        count_text = self.font.render(f"Deck: {len(self.game.deck.cards)} cards", True, WHITE)
        screen.blit(count_text, (SCREEN_WIDTH//2 - CARD_WIDTH - 20, 
                               SCREEN_HEIGHT//2 + CARD_HEIGHT//2 + 10))
        
    def draw_discard_pile(self):
        if self.game.discard_pile:
            top_card = self.game.discard_pile[-1]
            if not top_card.image:
                top_card.load_image()
                
            discard_rect = pygame.Rect(SCREEN_WIDTH//2 + 20, 
                                     SCREEN_HEIGHT//2 - CARD_HEIGHT//2,
                                     CARD_WIDTH, CARD_HEIGHT)
            screen.blit(top_card.image, discard_rect)
            
            # Show discard pile count
            count_text = self.font.render(f"Discard: {len(self.game.discard_pile)} cards", True, WHITE)
            screen.blit(count_text, (SCREEN_WIDTH//2 + 20, 
                                   SCREEN_HEIGHT//2 + CARD_HEIGHT//2 + 10))
        
    def draw_player_hand(self, player):
        num_cards = len(player.hand)
        
        # Calculate position based on player position
        if player.position == 0:  # Bottom player
            start_x = SCREEN_WIDTH//2 - (num_cards * (CARD_WIDTH - CARD_SPACING))//2
            y = SCREEN_HEIGHT - CARD_HEIGHT - 20
            rotation = 0
            face_up = True
        elif player.position == 1:  # Left player
            start_x = 20
            y = SCREEN_HEIGHT//2 - (num_cards * (CARD_WIDTH//3))//2
            rotation = 90
            face_up = True  # Changed to show AI cards
        elif player.position == 2:  # Top player
            start_x = SCREEN_WIDTH//2 - (num_cards * (CARD_WIDTH - CARD_SPACING))//2
            y = 60
            rotation = 0
            face_up = True  # Changed to show AI cards
        else:  # Right player
            start_x = SCREEN_WIDTH - CARD_WIDTH - 20
            y = SCREEN_HEIGHT//2 - (num_cards * (CARD_WIDTH//3))//2
            rotation = 90
            face_up = True  # Changed to show AI cards
            
        # Draw player name
        name_text = self.font.render(player.name, True, WHITE)
        if player.position == 0:
            screen.blit(name_text, (SCREEN_WIDTH//2 - name_text.get_width()//2, y - 30))
        elif player.position == 1:
            screen.blit(name_text, (start_x, y - 30))
        elif player.position == 2:
            screen.blit(name_text, (SCREEN_WIDTH//2 - name_text.get_width()//2, y - 30))
        else:
            screen.blit(name_text, (start_x - name_text.get_width(), y - 30))
            
        # Draw cards
        for i, card in enumerate(player.hand):
            if face_up:
                if not card.image:
                    card.load_image()
                card_img = card.image
            else:
                # Face down card
                card_img = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
                card_img.fill(BLACK)
                pygame.draw.rect(card_img, WHITE, (3, 3, CARD_WIDTH-6, CARD_HEIGHT-6), 2)
                
                # Add "UNO" text for face down cards
                font = pygame.font.SysFont('Arial', 20, bold=True)
                text = font.render("UNO", True, WHITE)
                text_rect = text.get_rect(center=(CARD_WIDTH/2, CARD_HEIGHT/2))
                card_img.blit(text, text_rect)
                
            if player.position == 0:
                card_x = start_x + i * (CARD_WIDTH - CARD_SPACING)
                card.rect = pygame.Rect(card_x, y, CARD_WIDTH, CARD_HEIGHT)
            elif player.position == 1:
                card_x = start_x
                card_y = y + i * (CARD_WIDTH//3)
                card.rect = pygame.Rect(card_x, card_y, CARD_WIDTH, CARD_HEIGHT)
                # For rotated cards
            elif player.position == 2:
                card_x = start_x + i * (CARD_WIDTH - CARD_SPACING)
                card.rect = pygame.Rect(card_x, y, CARD_WIDTH, CARD_HEIGHT)
            else:
                card_x = start_x
                card_y = y + i * (CARD_WIDTH//3)
                card.rect = pygame.Rect(card_x, card_y, CARD_WIDTH, CARD_HEIGHT)
                
            # Draw the card
            if rotation == 0:
                screen.blit(card_img, (card.rect.x, card.rect.y))
            else:
                rotated_img = pygame.transform.rotate(card_img, rotation)
                if player.position == 1:
                    screen.blit(rotated_img, (card_x, card_y))
                else:
                    screen.blit(rotated_img, (card_x, card_y))


if __name__ == "__main__":
    game_interface = UnoInterface()
    game_interface.run()