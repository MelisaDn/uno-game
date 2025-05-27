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
        self.last_player_turn = -1  # prevents player from doing multiple moves per turn
        
        # initialize both type of players: rule based and Minimax AI
        self.rule_based_ai = RuleBasedAI()
        self.minimax_ai = MinimaxAI(max_depth=3)
        
    def run(self):
        running = True
        while running:
            # check for the winner first, if false proceed with the rest of the loop
            winner = self.game.check_winner()
            if winner:
                self.draw_game()  # shows final state and displays winner
                self.show_winner(winner) 
                pygame.display.flip()
                pygame.time.delay(5000) 
                running = False
                continue 

            # handle other events like quitting, and clicking on the screen
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.handle_click(event.pos)

            # AI players' turn
            self.ai_play_turn()

            self.draw_game()

            # update the display 
            pygame.display.flip()
            self.clock.tick(30)

        pygame.quit()
        
    def handle_click(self, pos):
        # get the current player information
        current_player = self.game.players[self.game.current_player]
        
        # if the player is number 0(human player), then let them click on cards
        if self.game.current_player == 0:
            # the player should be clicking a card on their hand + the position should match + the move should be valid
            for i, card in enumerate(current_player.hand):
                if card.rect.collidepoint(pos):
                    if self.game.is_valid_move(current_player.hand[i]):
                        card = current_player.hand[i]
                        if card.value in ["wild", "wild_draw4"]:
                            self.selected_card_index = i  # save the card index to play later
                            self.show_color_chooser()     # prompt the color after wild card
                        else:
                            self.game.play_card(i)
                    else:
                        print(f"Invalid move: {card.color} {card.value}")
                    break
                    
            # check for when the player clicks the deck
            deck_rect = pygame.Rect(SCREEN_WIDTH//2 - CARD_WIDTH - 20, 
                                   SCREEN_HEIGHT//2 - CARD_HEIGHT//2,
                                   CARD_WIDTH, CARD_HEIGHT)
            if deck_rect.collidepoint(pos):
                self.game.draw_from_deck()
                print("Drew a card from the deck")
                
    def ai_play_turn(self):
        # allows AI to play if it's their turn and they haven't played this frame
        if (self.game.current_player != 0 and 
            self.last_player_turn != self.game.current_player):
            
            # Update last player
            self.last_player_turn = self.game.current_player
            # get the current player
            current_player = self.game.players[self.game.current_player]
            
            print(f"\n=== {current_player.name}'s Turn ===")
            
            pygame.time.delay(2000)
            
            move_index = None
            
            # AI type based on player number
            if self.game.current_player == 1:  # Player with index 1 is rule-based
                print(f"{current_player.name} thinking...")
                move_index = self.rule_based_ai.choose_move(current_player, self.game)
            elif self.game.current_player == 2:  # Player with index 2 is minimax
                print(f"{current_player.name} thinking with Minimax...")
                move_index = self.minimax_ai.choose_move(current_player, self.game)
            elif self.game.current_player == 3:  # Player with index 3 is rule-based
                print(f"{current_player.name} thinking...")
                move_index = self.rule_based_ai.choose_move(current_player, self.game)
            
            # if move is valid, make the move
            if move_index is not None and move_index < len(current_player.hand):
                card = current_player.hand[move_index]
                print(f"Attempting to play: {card.color} {card.value}")
                
                if self.game.play_card(move_index):
                    print(f"Successfully played card")
                else:
                    print(f"Invalid move by {current_player.name}: {card.color} {card.value}")
                    # in case of invalid move, draws from deck
                    self.game.draw_from_deck()
            else:
                self.game.draw_from_deck()
            
            print(f"=== End of {current_player.name}'s Turn ===")
            print(f"Next player: {self.game.players[self.game.current_player].name}\n")
            
            # display update
            self.draw_game()
            pygame.display.flip()
            
        # resetting the turn tracker if turn changes back to human or when current player changes
        if self.game.current_player == 0 or self.last_player_turn == self.game.current_player:
            if self.game.current_player != self.last_player_turn:
                self.last_player_turn = -1
        
    def draw_game(self):
        # black background + deck and discard piles in the middle + players' hands
        screen.fill(BLACK)
        
        self.draw_deck()
        self.draw_discard_pile()
      
        for player in self.game.players:
            self.draw_player_hand(player)
            
        # show current player + direction of the game
        current_player = self.game.players[self.game.current_player]
        indicator = self.font.render(f"Current Turn: {current_player.name}", True, WHITE)
        screen.blit(indicator, (20, 20))

        
        direction_text = "Direction: Clockwise" if self.game.direction == 1 else "Direction: Counter-Clockwise"
        direction_indicator = self.font.render(direction_text, True, WHITE)
        screen.blit(direction_indicator, (20, 50))
        
        # show chosen wild card color
        if self.game.last_wild_color:
            wild_color_text = self.font.render(f"Wild color chosen: {self.game.last_wild_color.upper()}", True, WHITE)
            screen.blit(wild_color_text, (SCREEN_WIDTH // 2 - wild_color_text.get_width() // 2, 10 ))
  

    def draw_deck(self):
        # black deck display in the middle
        deck_img = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        deck_img.fill(BLACK)
        pygame.draw.rect(deck_img, WHITE, (3, 3, CARD_WIDTH-6, CARD_HEIGHT-6), 2)
        
        # the UNO text
        font = pygame.font.SysFont('Arial', 30, bold=True)
        text = font.render("UNO", True, WHITE)
        text_rect = text.get_rect(center=(CARD_WIDTH/2, CARD_HEIGHT/2))
        deck_img.blit(text, text_rect)
        
        deck_rect = pygame.Rect(SCREEN_WIDTH//2 - CARD_WIDTH - 20, 
                               SCREEN_HEIGHT//2 - CARD_HEIGHT//2,
                               CARD_WIDTH, CARD_HEIGHT)
        screen.blit(deck_img, deck_rect)
        
        # shows how many card remain in the deck
        count_text = self.font.render(f"Deck: {len(self.game.deck.cards)} cards", True, WHITE)
        screen.blit(count_text, (SCREEN_WIDTH//2 - CARD_WIDTH - 20, 
                               SCREEN_HEIGHT//2 + CARD_HEIGHT//2 + 10))
        
    def draw_discard_pile(self):
        # black discard pile in the middle
        if self.game.discard_pile:
            top_card = self.game.discard_pile[-1]
            if not top_card.image:
                top_card.load_image()
                
            discard_rect = pygame.Rect(SCREEN_WIDTH//2 + 20, 
                                     SCREEN_HEIGHT//2 - CARD_HEIGHT//2,
                                     CARD_WIDTH, CARD_HEIGHT)
            screen.blit(top_card.image, discard_rect)
            
            # shows how many cards are in the discard pile
            count_text = self.font.render(f"Discard: {len(self.game.discard_pile)} cards", True, WHITE)
            screen.blit(count_text, (SCREEN_WIDTH//2 + 20, 
                                   SCREEN_HEIGHT//2 + CARD_HEIGHT//2 + 10))
        
    def draw_player_hand(self, player):
        num_cards = len(player.hand)
        
        # calculating screen positioning based on the player number
        if player.position == 0:  # bottom
            start_x = SCREEN_WIDTH//2 - (num_cards * (CARD_WIDTH - CARD_SPACING))//2
            y = SCREEN_HEIGHT - CARD_HEIGHT - 20
            rotation = 0
            face_up = True
        elif player.position == 1:  # left
            start_x = 20
            y = SCREEN_HEIGHT//2 - (num_cards * (CARD_WIDTH//3))//2
            rotation = 90
            face_up = True  # change the value to see/not see the AI cards
        elif player.position == 2:  # top
            start_x = SCREEN_WIDTH//2 - (num_cards * (CARD_WIDTH - CARD_SPACING))//2
            y = 60
            rotation = 0
            face_up = True  # change the value to see/not see the AI cards
        else:  # right
            start_x = SCREEN_WIDTH - CARD_WIDTH - 20
            y = SCREEN_HEIGHT//2 - (num_cards * (CARD_WIDTH//3))//2
            rotation = 90
            face_up = True  # change the value to see/not see the AI cards
            
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
            
        # for each card in player's hand, show card info for face-up ones, show UNO image for face-down cards
        for i, card in enumerate(player.hand):
            if face_up:
                if not card.image:
                    card.load_image()
                card_img = card.image
            else:
                
                card_img = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
                card_img.fill(BLACK)
                pygame.draw.rect(card_img, WHITE, (3, 3, CARD_WIDTH-6, CARD_HEIGHT-6), 2)
                
                font = pygame.font.SysFont('Arial', 20, bold=True)
                text = font.render("UNO", True, WHITE)
                text_rect = text.get_rect(center=(CARD_WIDTH/2, CARD_HEIGHT/2))
                card_img.blit(text, text_rect)

            # the card should face the player's position
            if player.position == 0:
                card_x = start_x + i * (CARD_WIDTH - CARD_SPACING)
                card.rect = pygame.Rect(card_x, y, CARD_WIDTH, CARD_HEIGHT)
            elif player.position == 1:
                card_x = start_x
                card_y = y + i * (CARD_WIDTH//3)
                card.rect = pygame.Rect(card_x, card_y, CARD_WIDTH, CARD_HEIGHT)
                # handling the rotating cards
            elif player.position == 2:
                card_x = start_x + i * (CARD_WIDTH - CARD_SPACING)
                card.rect = pygame.Rect(card_x, y, CARD_WIDTH, CARD_HEIGHT)
            else:
                card_x = start_x
                card_y = y + i * (CARD_WIDTH//3)
                card.rect = pygame.Rect(card_x, card_y, CARD_WIDTH, CARD_HEIGHT)

            
            if rotation == 0:
                screen.blit(card_img, (card.rect.x, card.rect.y))
            else:
                rotated_img = pygame.transform.rotate(card_img, rotation)
                if player.position == 1:
                    screen.blit(rotated_img, (card_x, card_y))
                else:
                    screen.blit(rotated_img, (card_x, card_y))


    def show_color_chooser(self):
        # function for choosing the color after a wild card
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
        player = self.game.players[0]  # because the human is always at index 0
        card = player.hand[self.selected_card_index]
        
        # stores the original value
        original_value = card.value
        
        # set the chosen color and play the card with its original value
        card.color = chosen_color
        self.game.last_wild_color = chosen_color
        
        if self.game.play_card(self.selected_card_index):
            print(f"Played {card.color} {original_value}")
        
        self.selected_card_index = -1
                        

    def show_winner(self, winner_name):
        # the function for display settings of the winner message
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        win_text = self.title_font.render(f"{winner_name} WINS!", True, YELLOW)
        text_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(win_text, text_rect)
