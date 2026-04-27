"""
Quoridor Game - Core Game Logic and Board State
Implements the complete ruleset for a 2-player Quoridor game
"""

from typing import List, Tuple, Set, Optional
from enum import Enum
import copy


class Wall:
    """Represents a wall on the board"""
    def __init__(self, row: int, col: int, is_horizontal: bool):
        """
        Initialize a wall
        Args:
            row: Row position of the wall
            col: Column position of the wall
            is_horizontal: True if wall is horizontal, False if vertical
        """
        self.row = row
        self.col = col
        self.is_horizontal = is_horizontal

    def __eq__(self, other):
        if not isinstance(other, Wall):
            return False
        return (self.row == other.row and 
                self.col == other.col and 
                self.is_horizontal == other.is_horizontal)

    def __hash__(self):
        return hash((self.row, self.col, self.is_horizontal))

    def __repr__(self):
        direction = "H" if self.is_horizontal else "V"
        return f"Wall({self.row},{self.col},{direction})"


class Player:
    """Represents a player in the game"""
    def __init__(self, player_id: int, start_row: int, start_col: int):
        """
        Initialize a player
        Args:
            player_id: 0 or 1 (top or bottom player)
            start_row: Starting row position
            start_col: Starting column position
        """
        self.player_id = player_id
        self.row = start_row
        self.col = start_col
        self.walls_remaining = 10

    def __repr__(self):
        return f"Player{self.player_id}(pos=({self.row},{self.col}), walls={self.walls_remaining})"


class GameBoard:
    """
    Represents the Quoridor game board
    9x9 board with walls placed on edges between squares
    """
    
    BOARD_SIZE = 9
    
    def __init__(self):
        """Initialize the game board"""
        self.board_size = self.BOARD_SIZE
        # Horizontal walls: board_size x (board_size - 1)
        self.h_walls = [[False] * (self.board_size - 1) for _ in range(self.board_size)]
        # Vertical walls: (board_size - 1) x board_size
        self.v_walls = [[False] * self.board_size for _ in range(self.board_size - 1)]
        
        # Player positions
        self.players = [
            Player(0, 0, 4),      # Player 0 starts at top center
            Player(1, 8, 4)       # Player 1 starts at bottom center
        ]
        
        self.walls_placed = set()

    def is_valid_move(self, player_id: int, new_row: int, new_col: int) -> bool:
        """
        Check if a pawn move is valid
        Args:
            player_id: ID of the player moving
            new_row: Target row
            new_col: Target column
        Returns:
            True if move is valid, False otherwise
        """
        # Check board boundaries
        if not (0 <= new_row < self.board_size and 0 <= new_col < self.board_size):
            return False
        
        player = self.players[player_id]
        old_row, old_col = player.row, player.col
        
        # Can't stay in same position
        if new_row == old_row and new_col == old_col:
            return False
        
        # Only orthogonal moves (not diagonal for normal moves)
        is_orthogonal = (new_row == old_row or new_col == old_col)
        
        # Check distance
        distance = abs(new_row - old_row) + abs(new_col - old_col)
        if distance > 2:
            return False
        
        # If moving 2 squares, must be jumping over opponent
        if distance == 2:
            if new_row == old_row:  # Horizontal jump
                mid_col = (old_col + new_col) // 2
                opponent = self.get_opponent(player_id)
                if not (opponent.row == old_row and opponent.col == mid_col):
                    return False
                # Check if there's a wall blocking the jump
                if old_col < new_col:  # Moving right
                    if old_row < len(self.v_walls) and self.v_walls[old_row][mid_col]:
                        return False
                else:  # Moving left
                    if old_row < len(self.v_walls) and self.v_walls[old_row][old_col]:
                        return False
            else:  # Vertical jump
                mid_row = (old_row + new_row) // 2
                opponent = self.get_opponent(player_id)
                if not (opponent.row == mid_row and opponent.col == old_col):
                    return False
                # Check if there's a wall blocking the jump
                if old_row < new_row:  # Moving down
                    if mid_row < len(self.h_walls) and self.h_walls[mid_row][old_col]:
                        return False
                else:  # Moving up
                    if old_row < len(self.h_walls) and self.h_walls[old_row][old_col]:
                        return False
            return True
        
        # Single square move
        if not is_orthogonal:
            return False
        
        # Check for walls blocking normal movement
        if new_row == old_row:  # Horizontal movement
            if old_col < new_col:  # Moving right
                if old_row < len(self.v_walls) and self.v_walls[old_row][new_col]:
                    return False
            else:  # Moving left
                if old_row < len(self.v_walls) and self.v_walls[old_row][old_col]:
                    return False
        else:  # Vertical movement
            if old_row < new_row:  # Moving down
                if new_row < len(self.h_walls) and self.h_walls[new_row][old_col]:
                    return False
            else:  # Moving up
                if old_row < len(self.h_walls) and self.h_walls[old_row][old_col]:
                    return False
        
        # Check for blocking opponent (unless jumping)
        opponent = self.get_opponent(player_id)
        if opponent.row == new_row and opponent.col == new_col:
            return False
        
        return True

    def get_valid_moves(self, player_id: int) -> List[Tuple[int, int]]:
        """
        Get all valid moves for a player
        Args:
            player_id: ID of the player
        Returns:
            List of valid (row, col) positions
        """
        valid_moves = []
        player = self.players[player_id]
        opponent = self.get_opponent(player_id)
        
        # Check all adjacent squares
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_row, new_col = player.row + dr, player.col + dc
            if self.is_valid_move(player_id, new_row, new_col):
                valid_moves.append((new_row, new_col))
        
        # Check jump moves and diagonal alternatives
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            adj_row = player.row + dr
            adj_col = player.col + dc
            
            # Check if opponent is adjacent in this direction
            if (adj_row == opponent.row and adj_col == opponent.col and
                0 <= adj_row < self.board_size and 0 <= adj_col < self.board_size):
                
                # Try jump over opponent
                jump_row = player.row + 2 * dr
                jump_col = player.col + 2 * dc
                if self.is_valid_move(player_id, jump_row, jump_col):
                    valid_moves.append((jump_row, jump_col))
                else:
                    # Try diagonal move
                    for alt_dr, alt_dc in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                        if abs(alt_dr) + abs(alt_dc) == 1 and (alt_dr != -dr or alt_dc != -dc):
                            diag_row = adj_row + alt_dr
                            diag_col = adj_col + alt_dc
                            if self.is_valid_move(player_id, diag_row, diag_col):
                                valid_moves.append((diag_row, diag_col))
        
        return list(set(valid_moves))

    def move_pawn(self, player_id: int, new_row: int, new_col: int) -> bool:
        """
        Move a player's pawn
        Args:
            player_id: ID of the player
            new_row: Target row
            new_col: Target column
        Returns:
            True if move was successful
        """
        if self.is_valid_move(player_id, new_row, new_col):
            self.players[player_id].row = new_row
            self.players[player_id].col = new_col
            return True
        return False

    def is_valid_wall(self, wall: Wall) -> bool:
        """
        Check if a wall placement is valid
        Args:
            wall: Wall object to place
        Returns:
            True if placement is valid
        """
        if wall.is_horizontal:
            # Horizontal wall: row, col to row, col+1
            if not (0 < wall.row < self.board_size and 0 <= wall.col < self.board_size - 1):
                return False
            # Check if already occupied
            if self.h_walls[wall.row][wall.col]:
                return False
            # Check for overlaps with adjacent walls
            if wall.col > 0 and self.h_walls[wall.row][wall.col - 1]:
                return False
            if wall.col < self.board_size - 2 and self.h_walls[wall.row][wall.col + 1]:
                return False
        else:
            # Vertical wall: row to row+1, col
            if not (0 <= wall.row < self.board_size - 1 and 0 < wall.col < self.board_size):
                return False
            # Check if already occupied
            if self.v_walls[wall.row][wall.col]:
                return False
            # Check for overlaps with adjacent walls
            if wall.row > 0 and self.v_walls[wall.row - 1][wall.col]:
                return False
            if wall.row < self.board_size - 2 and self.v_walls[wall.row + 1][wall.col]:
                return False
        
        return True

    def place_wall(self, wall: Wall, player_id: int) -> bool:
        """
        Place a wall on the board
        Args:
            wall: Wall object to place
            player_id: ID of the player placing the wall
        Returns:
            True if wall was placed successfully
        """
        if not self.is_valid_wall(wall):
            return False
        
        # Check if placement blocks a player's path to goal
        if self._blocks_player_path(wall):
            return False
        
        # Place wall
        if wall.is_horizontal:
            self.h_walls[wall.row][wall.col] = True
        else:
            self.v_walls[wall.row][wall.col] = True
        
        self.walls_placed.add(wall)
        self.players[player_id].walls_remaining -= 1
        return True

    def _blocks_player_path(self, wall: Wall) -> bool:
        """
        Check if a wall placement would block any player's path to goal
        Args:
            wall: Wall to check
        Returns:
            True if wall blocks a player's path
        """
        # Temporarily place the wall
        if wall.is_horizontal:
            self.h_walls[wall.row][wall.col] = True
        else:
            self.v_walls[wall.row][wall.col] = True
        
        # Check if both players can still reach their goals
        player0_can_reach = self._can_reach_goal(0)
        player1_can_reach = self._can_reach_goal(1)
        
        # Remove the wall
        if wall.is_horizontal:
            self.h_walls[wall.row][wall.col] = False
        else:
            self.v_walls[wall.row][wall.col] = False
        
        return not (player0_can_reach and player1_can_reach)

    def _can_reach_goal(self, player_id: int) -> bool:
        """
        Check if a player can reach their goal using BFS
        Args:
            player_id: ID of the player
        Returns:
            True if player can reach goal
        """
        from collections import deque
        
        player = self.players[player_id]
        goal_row = 8 if player_id == 0 else 0
        
        visited = set()
        queue = deque([(player.row, player.col)])
        visited.add((player.row, player.col))
        
        while queue:
            row, col = queue.popleft()
            
            if row == goal_row:
                return True
            
            # Check all adjacent squares: up, down, left, right
            neighbors = []
            
            # Up
            if row > 0:
                neighbors.append((row - 1, col, 'up'))
            # Down  
            if row < self.board_size - 1:
                neighbors.append((row + 1, col, 'down'))
            # Left
            if col > 0:
                neighbors.append((row, col - 1, 'left'))
            # Right
            if col < self.board_size - 1:
                neighbors.append((row, col + 1, 'right'))
            
            for new_row, new_col, direction in neighbors:
                if (new_row, new_col) not in visited:
                    # Check if there's a wall blocking
                    blocked = False
                    try:
                        if direction == 'up':
                            if 0 <= row < len(self.h_walls) and 0 <= col < len(self.h_walls[0]):
                                blocked = self.h_walls[row][col]
                        elif direction == 'down':
                            if 0 <= new_row < len(self.h_walls) and 0 <= col < len(self.h_walls[0]):
                                blocked = self.h_walls[new_row][col]
                        elif direction == 'left':
                            if 0 <= row < len(self.v_walls) and 0 <= col < len(self.v_walls[0]):
                                blocked = self.v_walls[row][col]
                        else:  # right
                            if 0 <= row < len(self.v_walls) and 0 <= new_col < len(self.v_walls[0]):
                                blocked = self.v_walls[row][new_col]
                    except (IndexError, TypeError):
                        # Skip if wall array access fails
                        blocked = False
                    
                    if not blocked:
                        visited.add((new_row, new_col))
                        queue.append((new_row, new_col))
        
        return False

    def has_won(self, player_id: int) -> bool:
        """
        Check if a player has won
        Args:
            player_id: ID of the player
        Returns:
            True if player has reached the opposite side
        """
        player = self.players[player_id]
        if player_id == 0:
            return player.row == 8
        else:
            return player.row == 0

    def get_opponent(self, player_id: int) -> Player:
        """Get the opponent player"""
        return self.players[1 - player_id]

    def get_board_state(self) -> dict:
        """Get the current board state for serialization"""
        return {
            'players': [(p.row, p.col, p.walls_remaining) for p in self.players],
            'h_walls': self.h_walls,
            'v_walls': self.v_walls,
            'walls_placed': list(self.walls_placed)
        }
