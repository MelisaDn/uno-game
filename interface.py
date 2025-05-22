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
            # Check for winner before processing input or drawing
            winner = self.game.check_winner()
            if winner:
                self.draw_game()  # Draw final state
                self.show_winner(winner)  # Show overlay with winner message
                pygame.display.flip()
                pygame.time.delay(5000)  # Pause for 5 seconds
                running = False
                continue  # Skip the rest of the loop this cycle

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
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
                    if self.game.is_valid_move(current_player.hand[i]):
                        card = current_player.hand[i]
                        if card.value in ["wild", "wild_draw4"]:
                            self.selected_card_index = i  # Save card to play after choosing color
                            self.show_color_chooser()     # Custom method to prompt color
                        else:
                            self.game.play_card(i)
                    else:
                        print(f"Invalid move: {card.color} {card.value}")
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
            pygame.time.delay(1000)
            
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
                    # Note: The play_card method now prints confirmation
                    pass
                else:
                    print(f"Invalid move by {current_player.name}: {card.color} {card.value}")
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

        # Draw game direction indicator
        direction_text = "Direction: Clockwise" if self.game.direction == 1 else "Direction: Counter-Clockwise"
        direction_indicator = self.font.render(direction_text, True, WHITE)
        screen.blit(direction_indicator, (20, 50))
        
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
            face_up = True  # Change to show AI cards
        elif player.position == 2:  # Top player
            start_x = SCREEN_WIDTH//2 - (num_cards * (CARD_WIDTH - CARD_SPACING))//2
            y = 60
            rotation = 0
            face_up = True  # Change to show AI cards
        else:  # Right player
            start_x = SCREEN_WIDTH - CARD_WIDTH - 20
            y = SCREEN_HEIGHT//2 - (num_cards * (CARD_WIDTH//3))//2
            rotation = 90
            face_up = True  # Change to show AI cards
            
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


    def show_color_chooser(self):
        choosing = True
        color_buttons = {
            "red": pygame.Rect(200, 250, 100, 100),
            "green": pygame.Rect(350, 250, 100, 100),
            "blue": pygame.Rect(500, 250, 100, 100),
            "yellow": pygame.Rect(650, 250, 100, 100)
        }

        while choosing:
            screen.fill(BLACK)
            text = self.title_font.render("Choose a color", True, WHITE)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 150))

            for color, rect in color_buttons.items():
                pygame.draw.rect(screen, pygame.Color(color), rect)
                label = self.font.render(color.upper(), True, BLACK)
                label_rect = label.get_rect(center=rect.center)
                screen.blit(label, label_rect)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for color, rect in color_buttons.items():
                        if rect.collidepoint(event.pos):
                            self.play_selected_wild_card(color)
                            choosing = False
                            break


    def play_selected_wild_card(self, chosen_color):
        player = self.game.players[0]  # Human is always player 0
        card = player.hand[self.selected_card_index]
        
        # Store original value for reference
        original_value = card.value
        
        # Set the chosen color
        card.color = chosen_color
        
        # Play the card
        if self.game.play_card(self.selected_card_index):
            print(f"Played {card.color} {original_value}")
        
        self.selected_card_index = -1
                        

    def show_winner(self, winner_name):
        # Overlay the screen with a winner message
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        win_text = self.title_font.render(f"{winner_name} WINS!", True, YELLOW)
        text_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(win_text, text_rect)