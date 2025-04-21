from card import Deck, Card
import random

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
        from game import UnoGame
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
