import pygame
from game import UnoGame
from constants import *
from player import RuleBasedAI, MinimaxAI
from card import Card

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


