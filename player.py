from card import Deck, Card
import random

class Player:
    # each player has a name, an array of cards and a position
    def __init__(self, name: str, position: int):
        self.name = name
        self.hand = []
        self.position = position 

    # player draws a card from the deck and appends it to their hand
    def draw(self, deck: Deck, count: int = 1):
        for _ in range(count):
            card = deck.draw_card()
            if card:
                self.hand.append(card)

    # if card index is valid, pop the card from the array
    def play_card(self, card_index: int):
        if 0 <= card_index < len(self.hand):
            return self.hand.pop(card_index)
        return None


class RuleBasedAI:
    """Simple rule-based AI that follows basic UNO strategy"""
    
    def choose_move(self, player, game):
        # the agent gets the top card and finds all playable cards in its hand
        top_card = game.get_top_card()
        playable_cards = []
        
        for i, card in enumerate(player.hand):
            if game.is_valid_move(card):
                playable_cards.append((i, card))
        
        if not playable_cards:
            # if there are no playable cards, it should draw from the deck
            return None

        # this agent prioritizes the cards + first gets rid of special cards (skip, reverse, draw two)  
        # + then plays the number cards + finally the wild cards
       
        
        special_cards = [(i, card) for i, card in playable_cards 
                        if card.color != "wild" and card.value in ["skip", "reverse", "draw2"]]
        number_cards = [(i, card) for i, card in playable_cards 
                       if card.color != "wild" and card.value not in ["skip", "reverse", "draw2"]]
        wild_cards = [(i, card) for i, card in playable_cards if card.value in ["wild", "wild_draw4"]]
        
        # chooses in order of priority
        if special_cards:
            choice = random.choice(special_cards)
            return choice[0]  # return the index
        elif number_cards:
            choice = random.choice(number_cards)
            return choice[0]  
        elif wild_cards:
            choice = random.choice(wild_cards)
            return choice[0] 
        
        return None  # if nothing else works, draw a card


class MinimaxAI:
    """Advanced AI using Minimax with Alpha-Beta Pruning"""
    
    def __init__(self, max_depth=2):  # Reduced depth to prevent issues
        self.max_depth = max_depth
        self.colors = ["red", "blue", "green", "yellow"]
        self.evaluation_cache = {}  # Add caching to prevent re-computation
    
    def choose_move(self, player, game):
        print(f"MinimaxAI evaluating {len(player.hand)} cards...")
        
        # Find all valid moves
        valid_moves = []
        for i, card in enumerate(player.hand):
            if game.is_valid_move(card):
                valid_moves.append(i)
                print(f"  Valid move {i}: {card.color} {card.value}")
        
        if not valid_moves:
            print("  No valid moves, will draw card")
            return None  # Draw a card
        
        # If only one valid move, play it immediately
        if len(valid_moves) == 1:
            print(f"  Only one valid move: {valid_moves[0]}")
            return valid_moves[0]
        
        # Use actual minimax algorithm to evaluate moves
        best_score = float('-inf')
        best_move = None
        
        print(f"  Running minimax evaluation...")
        
        for move in valid_moves:
            # Clone the game state for this move evaluation
            try:
                move_game = self._clone_game_state(game)
                move_player = move_game.players[game.current_player]
                
                # Handle wild card color selection in cloned game
                played_card = move_player.hand[move]
                if played_card.value in ["wild", "wild_draw4"]:
                    best_color = self._best_wild_color(move_player.hand)
                    played_card.color = best_color
                
                # Apply the move in the cloned game using silent method
                if move_game.play_card_silent(move):
                    # Calculate score with minimax
                    score = self._minimax(move_game, 0, False, float('-inf'), float('inf'))
                    print(f"    Move {move} ({player.hand[move].color} {player.hand[move].value}) minimax score: {score}")
                    
                    # Update best move if needed
                    if score > best_score:
                        best_score = score
                        best_move = move
                else:
                    print(f"    Move {move} failed in simulation")
                    
            except Exception as e:
                print(f"    Error evaluating move {move}: {e}")
                # Fall back to heuristic for this move
                card = player.hand[move]
                score = self._evaluate_move(card, player, game)
                if score > best_score:
                    best_score = score
                    best_move = move
        
        print(f"  Chosen move: {best_move} with score: {best_score}")
        return best_move
    
    def _evaluate_move(self, card, player, game):
        """Simple heuristic evaluation of a single move"""
        score = 0
        
        # Prefer special cards
        if card.value in ["skip", "reverse", "draw2"]:
            score += 20
        elif card.value in ["wild", "wild_draw4"]:
            score += 15
        
        # Prefer cards that match common colors in hand
        if card.color != "wild":
            color_count = sum(1 for c in player.hand if c.color == card.color)
            score += color_count * 5
        
        # Prefer higher value number cards
        if card.value.isdigit():
            score += int(card.value)
        
        # Small random factor to prevent deterministic play
        score += random.uniform(-2, 2)
        
        return score
    
    def _best_wild_color(self, hand):
        """Choose the most frequent color in hand for wild cards"""
        color_count = {"red": 0, "blue": 0, "green": 0, "yellow": 0}
        
        for card in hand:
            if card.color in color_count:
                color_count[card.color] += 1
        
        return max(color_count, key=color_count.get)
    
    def _clone_game_state(self, game):
        """Create a deep copy of the game state for simulation"""
        from game import UnoGame
        from copy import deepcopy
        
        # Create a completely independent copy
        clone = UnoGame.__new__(UnoGame)
        
        # Deep copy the deck
        clone.deck = Deck()
        clone.deck.cards = []
        for card in game.deck.cards:
            new_card = Card(card.color, card.value)
            clone.deck.cards.append(new_card)
        
        # Deep copy the discard pile
        clone.discard_pile = []
        for card in game.discard_pile:
            new_card = Card(card.color, card.value)
            clone.discard_pile.append(new_card)
        
        # Deep copy all players
        clone.players = []
        for player in game.players:
            new_player = Player(player.name, player.position)
            new_player.hand = []
            for card in player.hand:
                new_card = Card(card.color, card.value)
                new_player.hand.append(new_card)
            clone.players.append(new_player)
        
        # Copy game state
        clone.current_player = game.current_player
        clone.direction = game.direction
        
        return clone
    
    def _minimax(self, game, depth, maximizing_player, alpha, beta):
        """
        Minimax algorithm with alpha-beta pruning - uses silent game operations
        """
        # Terminal conditions: max depth reached or game over
        if depth >= self.max_depth or self._is_game_over(game):
            return self._evaluate_state(game)
        
        current_player = game.players[game.current_player]
        valid_moves = self._get_valid_moves(current_player, game)
        
        # If no valid moves, simulate drawing a card
        if not valid_moves:
            try:
                cloned_game = self._clone_game_state(game)
                cloned_game.draw_from_deck_silent()  # Use silent version
                return self._minimax(cloned_game, depth + 1, not maximizing_player, alpha, beta)
            except:
                # If something goes wrong, return current evaluation
                return self._evaluate_state(game)
        
        if maximizing_player:
            max_eval = float('-inf')
            
            for move in valid_moves[:3]:  # Limit to first 3 moves to prevent deep recursion
                try:
                    cloned_game = self._clone_game_state(game)
                    cloned_player = cloned_game.players[game.current_player]
                    
                    # Handle wild cards
                    if cloned_player.hand[move].value in ["wild", "wild_draw4"]:
                        cloned_player.hand[move].color = self._best_wild_color(cloned_player.hand)
                    
                    if cloned_game.play_card_silent(move):  # Use silent version
                        eval_score = self._minimax(cloned_game, depth + 1, False, alpha, beta)
                        max_eval = max(max_eval, eval_score)
                        
                        # Alpha-beta pruning
                        alpha = max(alpha, eval_score)
                        if beta <= alpha:
                            break
                except:
                    # Skip problematic moves
                    continue
                    
            return max_eval
        else:
            min_eval = float('inf')
            
            for move in valid_moves[:3]:  # Limit to first 3 moves to prevent deep recursion
                try:
                    cloned_game = self._clone_game_state(game)
                    cloned_player = cloned_game.players[game.current_player]
                    
                    # Handle wild cards
                    if cloned_player.hand[move].value in ["wild", "wild_draw4"]:
                        cloned_player.hand[move].color = self._best_wild_color(cloned_player.hand)
                    
                    if cloned_game.play_card_silent(move):  # Use silent version
                        eval_score = self._minimax(cloned_game, depth + 1, True, alpha, beta)
                        min_eval = min(min_eval, eval_score)
                        
                        # Alpha-beta pruning
                        beta = min(beta, eval_score)
                        if beta <= alpha:
                            break
                except:
                    # Skip problematic moves
                    continue
                    
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
