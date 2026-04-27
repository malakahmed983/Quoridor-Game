"""
Quoridor Game AI - Multiple difficulty levels
Implements easy, medium, and hard AI opponents using various strategies
"""

import random
from typing import List, Tuple, Optional
from game_logic import GameBoard, Wall
from collections import deque


class QuoridorAI:
    """AI player for Quoridor game"""
    
    def __init__(self, difficulty: str = "medium"):
        """
        Initialize AI player
        Args:
            difficulty: "easy", "medium", or "hard"
        """
        self.difficulty = difficulty
        assert difficulty in ["easy", "medium", "hard"]

    def get_best_move(self, board: GameBoard, player_id: int) -> Tuple[str, any]:
        """
        Get the best move for this AI
        Args:
            board: Current game board
            player_id: ID of the AI player
        Returns:
            Tuple of (move_type, move_data) where:
            - move_type: "move" or "wall"
            - move_data: (row, col) for move or Wall object for wall
        """
        if self.difficulty == "easy":
            return self._easy_move(board, player_id)
        elif self.difficulty == "medium":
            return self._medium_move(board, player_id)
        else:
            return self._hard_move(board, player_id)

    def _easy_move(self, board: GameBoard, player_id: int) -> Tuple[str, any]:
        """
        Easy AI: Random valid move
        Args:
            board: Current game board
            player_id: ID of the AI player
        Returns:
            Random move
        """
        # Get valid pawn moves
        valid_moves = board.get_valid_moves(player_id)
        
        # 70% chance to move pawn, 30% chance to place wall
        if random.random() < 0.7 or board.players[player_id].walls_remaining == 0:
            if valid_moves:
                move = random.choice(valid_moves)
                return ("move", move)
        
        # Try to place a wall
        wall = self._random_wall_placement(board, player_id)
        if wall:
            return ("wall", wall)
        
        # Fall back to pawn move
        if valid_moves:
            return ("move", random.choice(valid_moves))
        
        return ("move", random.choice(valid_moves))

    def _medium_move(self, board: GameBoard, player_id: int) -> Tuple[str, any]:
        """
        Medium AI: Uses heuristics to make decent moves
        Args:
            board: Current game board
            player_id: ID of the AI player
        Returns:
            Heuristic-based move
        """
        valid_moves = board.get_valid_moves(player_id)
        player = board.players[player_id]
        opponent = board.get_opponent(player_id)
        goal_row = 8 if player_id == 0 else 0
        
        # Score each move: prefer moves closer to goal
        best_move = None
        best_score = -float('inf')
        
        for move_row, move_col in valid_moves:
            # Distance to goal (lower is better)
            dist_to_goal = abs(move_row - goal_row)
            score = -dist_to_goal
            
            # Bonus for moving closer to opponent (blocking strategy)
            dist_to_opponent = abs(move_row - opponent.row) + abs(move_col - opponent.col)
            if dist_to_opponent < 4:
                score += 2
            
            if score > best_score:
                best_score = score
                best_move = (move_row, move_col)
        
        # Consider wall placement 40% of the time if we have walls
        if random.random() < 0.4 and player.walls_remaining > 0:
            wall = self._strategic_wall_placement(board, player_id)
            if wall:
                return ("wall", wall)
        
        if best_move:
            return ("move", best_move)
        
        return ("move", random.choice(valid_moves))

    def _hard_move(self, board: GameBoard, player_id: int) -> Tuple[str, any]:
        """
        Hard AI: Uses minimax with alpha-beta pruning
        Args:
            board: Current game board
            player_id: ID of the AI player
        Returns:
            Best move from minimax analysis
        """
        valid_moves = board.get_valid_moves(player_id)
        player = board.players[player_id]
        
        if not valid_moves:
            return ("move", random.choice(valid_moves))
        
        best_move = None
        best_score = -float('inf')
        alpha = -float('inf')
        beta = float('inf')
        
        # Evaluate pawn moves
        for move in valid_moves:
            board.move_pawn(player_id, move[0], move[1])
            score = self._minimax(board, player_id, depth=2, is_maximizing=False, alpha=alpha, beta=beta)
            board.move_pawn(player_id, player.row, player.col)
            
            if score > best_score:
                best_score = score
                best_move = move
            
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break
        
        # Consider wall placement 30% of the time
        if random.random() < 0.3 and player.walls_remaining > 1:
            wall = self._strategic_wall_placement(board, player_id)
            if wall:
                return ("wall", wall)
        
        return ("move", best_move)

    def _minimax(self, board: GameBoard, player_id: int, depth: int, 
                 is_maximizing: bool, alpha: float, beta: float) -> float:
        """
        Minimax algorithm with alpha-beta pruning
        Args:
            board: Current game board
            player_id: ID of the maximizing player
            depth: Search depth
            is_maximizing: True if maximizing, False if minimizing
            alpha: Alpha value for pruning
            beta: Beta value for pruning
        Returns:
            Evaluation score
        """
        # Terminal conditions
        if board.has_won(player_id):
            return 100 + depth
        if board.has_won(1 - player_id):
            return -100 - depth
        if depth == 0:
            return self._evaluate_position(board, player_id)
        
        current_player = player_id if is_maximizing else 1 - player_id
        valid_moves = board.get_valid_moves(current_player)
        
        if is_maximizing:
            max_eval = -float('inf')
            for move_row, move_col in valid_moves:
                board.move_pawn(current_player, move_row, move_col)
                eval_score = self._minimax(board, player_id, depth - 1, False, alpha, beta)
                board.move_pawn(current_player, board.players[current_player].row, board.players[current_player].col)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move_row, move_col in valid_moves:
                board.move_pawn(current_player, move_row, move_col)
                eval_score = self._minimax(board, player_id, depth - 1, True, alpha, beta)
                board.move_pawn(current_player, board.players[current_player].row, board.players[current_player].col)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval

    def _evaluate_position(self, board: GameBoard, player_id: int) -> float:
        """
        Evaluate a board position
        Args:
            board: Game board to evaluate
            player_id: ID of the player to evaluate for
        Returns:
            Evaluation score
        """
        player = board.players[player_id]
        opponent = board.get_opponent(player_id)
        
        goal_row = 8 if player_id == 0 else 0
        opponent_goal_row = 0 if player_id == 0 else 8
        
        # Distance to goal (negative is better)
        my_distance = abs(player.row - goal_row)
        opp_distance = abs(opponent.row - opponent_goal_row)
        
        # Score: opponent's distance - my distance
        score = (opp_distance - my_distance) * 10
        
        # Add wall advantage
        score += (player.walls_remaining - opponent.walls_remaining) * 2
        
        # Add path length consideration
        my_path_length = self._estimate_path_length(board, player_id)
        opp_path_length = self._estimate_path_length(board, 1 - player_id)
        score += (opp_path_length - my_path_length)
        
        return score

    def _estimate_path_length(self, board: GameBoard, player_id: int) -> int:
        """
        Estimate the shortest path length to goal using BFS
        Args:
            board: Game board
            player_id: Player ID
        Returns:
            Path length to goal
        """
        player = board.players[player_id]
        goal_row = 8 if player_id == 0 else 0
        
        visited = set()
        queue = deque([(player.row, player.col, 0)])
        visited.add((player.row, player.col))
        
        while queue:
            row, col, dist = queue.popleft()
            
            if row == goal_row:
                return dist
            
            for new_row, new_col in [(row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]:
                if (0 <= new_row < board.board_size and 0 <= new_col < board.board_size and
                    (new_row, new_col) not in visited):
                    
                    blocked = False
                    if new_row < row:
                        blocked = board.h_walls[row][col]
                    elif new_row > row:
                        blocked = board.h_walls[new_row][col]
                    elif new_col < col:
                        blocked = board.v_walls[row][col]
                    else:
                        blocked = board.v_walls[row][new_col]
                    
                    if not blocked:
                        visited.add((new_row, new_col))
                        queue.append((new_row, new_col, dist + 1))
        
        return 100

    def _strategic_wall_placement(self, board: GameBoard, player_id: int) -> Optional[Wall]:
        """
        Place a wall strategically to block opponent
        Args:
            board: Game board
            player_id: AI player ID
        Returns:
            Wall object or None if no valid strategic wall
        """
        opponent = board.get_opponent(player_id)
        opponent_goal_row = 0 if player_id == 0 else 8
        
        # Try to place walls near opponent's path to goal
        best_walls = []
        
        for row in range(board.board_size):
            for col in range(board.board_size - 1):
                wall = Wall(row, col, True)
                if board.is_valid_wall(wall):
                    if not board._blocks_player_path(wall):
                        # Score based on proximity to opponent
                        dist_to_opp = abs(row - opponent.row) + abs(col - opponent.col)
                        if dist_to_opp < 3:
                            best_walls.append((wall, dist_to_opp))
        
        for row in range(board.board_size - 1):
            for col in range(board.board_size):
                wall = Wall(row, col, False)
                if board.is_valid_wall(wall):
                    if not board._blocks_player_path(wall):
                        dist_to_opp = abs(row - opponent.row) + abs(col - opponent.col)
                        if dist_to_opp < 3:
                            best_walls.append((wall, dist_to_opp))
        
        if best_walls:
            best_walls.sort(key=lambda x: x[1])
            return best_walls[0][0]
        
        return self._random_wall_placement(board, player_id)

    def _random_wall_placement(self, board: GameBoard, player_id: int) -> Optional[Wall]:
        """
        Place a random valid wall
        Args:
            board: Game board
            player_id: AI player ID
        Returns:
            Wall object or None if no valid wall can be placed
        """
        valid_walls = []
        
        # Try horizontal walls
        for row in range(1, board.board_size):
            for col in range(board.board_size - 1):
                wall = Wall(row, col, True)
                if board.is_valid_wall(wall) and not board._blocks_player_path(wall):
                    valid_walls.append(wall)
        
        # Try vertical walls
        for row in range(board.board_size - 1):
            for col in range(1, board.board_size):
                wall = Wall(row, col, False)
                if board.is_valid_wall(wall) and not board._blocks_player_path(wall):
                    valid_walls.append(wall)
        
        if valid_walls:
            return random.choice(valid_walls)
        
        return None
