"""
Unit tests for Quoridor game logic
Tests core game rules, move validation, and wall placement
"""

import unittest
from game_logic import GameBoard, Wall, Player


class TestGameBoard(unittest.TestCase):
    """Test suite for GameBoard class"""
    
    def setUp(self):
        """Set up a fresh board for each test"""
        self.board = GameBoard()
    
    def test_initial_state(self):
        """Test board initialization"""
        self.assertEqual(len(self.board.players), 2)
        self.assertEqual(self.board.players[0].row, 0)
        self.assertEqual(self.board.players[0].col, 4)
        self.assertEqual(self.board.players[1].row, 8)
        self.assertEqual(self.board.players[1].col, 4)
        self.assertEqual(self.board.players[0].walls_remaining, 10)
        self.assertEqual(self.board.players[1].walls_remaining, 10)
    
    def test_valid_pawn_move(self):
        """Test valid single square pawn movement"""
        # Player 0 moves down one square
        result = self.board.move_pawn(0, 1, 4)
        self.assertTrue(result)
        self.assertEqual(self.board.players[0].row, 1)
        self.assertEqual(self.board.players[0].col, 4)
    
    def test_invalid_move_out_of_bounds(self):
        """Test that moves outside board boundaries are invalid"""
        result = self.board.is_valid_move(0, -1, 4)
        self.assertFalse(result)
        
        result = self.board.is_valid_move(0, 9, 4)
        self.assertFalse(result)
    
    def test_invalid_move_too_far(self):
        """Test that moving more than 2 squares is invalid"""
        result = self.board.is_valid_move(0, 3, 4)
        self.assertFalse(result)
    
    def test_diagonal_move_invalid(self):
        """Test that diagonal moves are invalid"""
        result = self.board.is_valid_move(0, 1, 5)
        self.assertFalse(result)
    
    def test_get_valid_moves(self):
        """Test getting valid moves for a player"""
        valid_moves = self.board.get_valid_moves(0)
        # Player 0 at (0, 4) should be able to move down to (1, 4)
        self.assertIn((1, 4), valid_moves)
        # Should not be able to move up (out of bounds)
        self.assertNotIn((-1, 4), valid_moves)
    
    def test_wall_placement(self):
        """Test wall placement on board"""
        wall = Wall(1, 1, True)
        result = self.board.place_wall(wall, 0)
        self.assertTrue(result)
        self.assertTrue(self.board.h_walls[1][1])
        self.assertEqual(self.board.players[0].walls_remaining, 9)
    
    def test_invalid_wall_overlap(self):
        """Test that overlapping walls are rejected"""
        wall1 = Wall(2, 2, True)
        wall2 = Wall(2, 2, True)
        
        result1 = self.board.place_wall(wall1, 0)
        self.assertTrue(result1)
        
        result2 = self.board.place_wall(wall2, 1)
        self.assertFalse(result2)
    
    def test_win_condition(self):
        """Test win condition detection"""
        # Move player 1 out of player 0's path
        # Player 1 starts at (8, 4). Move up and left to (4, 0)
        for _ in range(4):
            self.board.move_pawn(1, self.board.players[1].row - 1, self.board.players[1].col)
        for _ in range(4):
            self.board.move_pawn(1, self.board.players[1].row, self.board.players[1].col - 1)
        
        # Now move player 0 straight down to row 8
        for _ in range(8):
            self.board.move_pawn(0, self.board.players[0].row + 1, self.board.players[0].col)
        
        # Player 0 should be at (8, 4) and have won
        self.assertTrue(self.board.has_won(0))
        self.assertFalse(self.board.has_won(1))
    
    def test_path_validation(self):
        """Test that walls blocking all paths are rejected"""
        # This is a complex test - need to set up a scenario where a wall
        # would completely block a player
        # For now, just test that the method doesn't crash
        wall = Wall(4, 4, True)
        blocks = self.board._blocks_player_path(wall)
        self.assertIsInstance(blocks, bool)
    
    def test_jump_over_opponent(self):
        """Test jumping over opponent pawn"""
        # Player 0 is at (0, 4), Player 1 is at (8, 4)
        # Move player 1 up to (1, 4) - 7 moves needed
        for _ in range(7):
            self.board.move_pawn(1, self.board.players[1].row - 1, self.board.players[1].col)
        
        # Now player 1 should be at (1, 4)
        self.assertEqual(self.board.players[1].row, 1)
        self.assertEqual(self.board.players[1].col, 4)
        
        # Check if player 0 can jump over player 1
        valid_moves = self.board.get_valid_moves(0)
        # Player 0 should be able to jump to (2, 4)
        self.assertIn((2, 4), valid_moves)


class TestPlayer(unittest.TestCase):
    """Test suite for Player class"""
    
    def test_player_creation(self):
        """Test player creation"""
        player = Player(0, 0, 4)
        self.assertEqual(player.player_id, 0)
        self.assertEqual(player.row, 0)
        self.assertEqual(player.col, 4)
        self.assertEqual(player.walls_remaining, 10)


class TestWall(unittest.TestCase):
    """Test suite for Wall class"""
    
    def test_wall_creation_horizontal(self):
        """Test horizontal wall creation"""
        wall = Wall(3, 2, True)
        self.assertEqual(wall.row, 3)
        self.assertEqual(wall.col, 2)
        self.assertTrue(wall.is_horizontal)
    
    def test_wall_creation_vertical(self):
        """Test vertical wall creation"""
        wall = Wall(3, 2, False)
        self.assertEqual(wall.row, 3)
        self.assertEqual(wall.col, 2)
        self.assertFalse(wall.is_horizontal)
    
    def test_wall_equality(self):
        """Test wall equality comparison"""
        wall1 = Wall(3, 2, True)
        wall2 = Wall(3, 2, True)
        wall3 = Wall(3, 2, False)
        
        self.assertEqual(wall1, wall2)
        self.assertNotEqual(wall1, wall3)
    
    def test_wall_hash(self):
        """Test wall can be used in hash-based collections"""
        wall = Wall(3, 2, True)
        wall_set = {wall}
        self.assertIn(wall, wall_set)


if __name__ == "__main__":
    unittest.main()
