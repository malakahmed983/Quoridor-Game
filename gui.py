"""
Quoridor Game GUI - Pygame-based graphical interface
Handles rendering, user input, and game flow
"""

import pygame
import sys
from typing import Optional, Tuple
from game_logic import GameBoard, Wall
from ai import QuoridorAI


class Colors:
    """Color constants"""
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)
    DARK_GRAY = (64, 64, 64)
    LIGHT_GRAY = (200, 200, 200)
    BLUE = (0, 100, 255)
    RED = (255, 50, 50)
    GREEN = (50, 200, 50)
    YELLOW = (255, 255, 0)
    LIGHT_BLUE = (100, 150, 255)
    LIGHT_RED = (255, 150, 150)


class QuoridorGUI:
    """Graphical User Interface for Quoridor"""
    
    def __init__(self, game_mode: str = "pvp", ai_difficulty: str = "medium"):
        """
        Initialize the GUI
        Args:
            game_mode: "pvp" or "pvc"
            ai_difficulty: "easy", "medium", or "hard"
        """
        pygame.init()
        
        self.game_mode = game_mode
        self.ai_difficulty = ai_difficulty
        
        # Board dimensions
        self.board_size = 9
        self.cell_size = 60
        self.margin = 50
        self.wall_width = 8
        
        # Calculate screen size
        self.screen_width = self.margin * 2 + self.cell_size * self.board_size
        self.screen_height = self.margin * 2 + self.cell_size * self.board_size + 100
        
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Quoridor Game")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 20)
        
        # Game state
        self.board = GameBoard()
        self.current_player = 0  # 0 for human, 1 for AI or player 2
        self.game_over = False
        self.winner = None
        self.message = "Player 0's turn"
        self.message_time = 0
        
        # UI state
        self.selected_cell = None
        self.valid_moves = []
        self.wall_preview = None
        self.placing_wall = False
        self.wall_orientation = True  # True = horizontal
        
        # AI
        if game_mode == "pvc":
            self.ai = QuoridorAI(ai_difficulty)
        else:
            self.ai = None
        
        self.ai_thinking = False

    def handle_events(self) -> bool:
        """
        Handle pygame events
        Returns:
            False if user wants to quit
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                self.handle_key_press(event.key)
        return True

    def handle_mouse_click(self, pos: Tuple[int, int]):
        """Handle mouse click events"""
        if self.game_over:
            return
        
        # Check if human should move
        if self.game_mode == "pvc" and self.current_player == 1:
            return
        
        x, y = pos
        
        # Convert pixel position to board coordinates
        board_x = (x - self.margin) // self.cell_size
        board_y = (y - self.margin) // self.cell_size
        
        # Check if click is on the board
        if not (0 <= board_x < self.board_size and 0 <= board_y < self.board_size):
            # Check for wall placement area
            return
        
        if not self.placing_wall:
            # Pawn move mode
            if (board_x, board_y) == self.selected_cell:
                self.selected_cell = None
                self.valid_moves = []
            elif (board_x, board_y) in self.valid_moves:
                # Make move
                if self.board.move_pawn(self.current_player, board_y, board_x):
                    self.selected_cell = None
                    self.valid_moves = []
                    
                    # Check for win
                    if self.board.has_won(self.current_player):
                        self.game_over = True
                        self.winner = self.current_player
                        self.message = f"Player {self.current_player} wins!"
                    else:
                        self.current_player = 1 - self.current_player
                        self.message = f"Player {self.current_player}'s turn"
            else:
                # Select new cell
                self.selected_cell = (board_x, board_y)
                self.valid_moves = [(col, row) for row, col in 
                                   self.board.get_valid_moves(self.current_player)]
        else:
            # Wall placement mode
            self.place_wall_at_click(pos)

    def handle_key_press(self, key: int):
        """Handle keyboard events"""
        if key == pygame.K_w:
            # Toggle wall placement mode
            self.placing_wall = not self.placing_wall
            self.selected_cell = None
            self.valid_moves = []
        elif key == pygame.K_r:
            # Toggle wall orientation
            self.wall_orientation = not self.wall_orientation
        elif key == pygame.K_ESCAPE:
            # Cancel wall placement
            self.placing_wall = False
            self.wall_preview = None
        elif key == pygame.K_SPACE:
            # Reset game
            self.reset_game()
        elif key == pygame.K_q:
            # Quit
            return False

    def place_wall_at_click(self, pos: Tuple[int, int]):
        """Place a wall based on click position"""
        x, y = pos
        
        # Calculate which wall position was clicked
        rel_x = x - self.margin
        rel_y = y - self.margin
        
        # Determine cell boundaries
        cell_x = rel_x // self.cell_size
        cell_y = rel_y // self.cell_size
        
        if cell_x < 0 or cell_x >= self.board_size or cell_y < 0 or cell_y >= self.board_size:
            return
        
        # For now, place wall at the cell position
        wall = Wall(cell_y, cell_x, self.wall_orientation)
        
        if self.board.place_wall(wall, self.current_player):
            self.message = f"Wall placed by Player {self.current_player}"
            self.current_player = 1 - self.current_player
            self.placing_wall = False
            self.wall_preview = None
            
            # Check if game is still valid
            if not self.board._can_reach_goal(0) or not self.board._can_reach_goal(1):
                self.message = "Invalid wall placement!"
        else:
            self.message = "Cannot place wall there!"
        
        self.message_time = pygame.time.get_ticks()

    def update(self):
        """Update game state"""
        if self.game_over:
            return
        
        # Handle AI move
        if self.game_mode == "pvc" and self.current_player == 1 and not self.ai_thinking:
            self.ai_thinking = True
            move_type, move_data = self.ai.get_best_move(self.board, 1)
            
            if move_type == "move":
                self.board.move_pawn(1, move_data[0], move_data[1])
                self.message = f"AI moved to ({move_data[0]}, {move_data[1]})"
            else:  # wall
                self.board.place_wall(move_data, 1)
                self.message = "AI placed a wall"
            
            # Check for win
            if self.board.has_won(1):
                self.game_over = True
                self.winner = 1
                self.message = "AI wins!"
            else:
                self.current_player = 0
            
            self.message_time = pygame.time.get_ticks()
            self.ai_thinking = False

    def draw(self):
        """Draw the game board and UI"""
        self.screen.fill(Colors.WHITE)
        
        # Draw board background
        pygame.draw.rect(self.screen, Colors.LIGHT_GRAY,
                        (self.margin, self.margin,
                         self.cell_size * self.board_size,
                         self.cell_size * self.board_size))
        
        # Draw grid
        for i in range(self.board_size + 1):
            # Horizontal lines
            start_pos = (self.margin, self.margin + i * self.cell_size)
            end_pos = (self.margin + self.cell_size * self.board_size, 
                      self.margin + i * self.cell_size)
            pygame.draw.line(self.screen, Colors.BLACK, start_pos, end_pos, 2)
            
            # Vertical lines
            start_pos = (self.margin + i * self.cell_size, self.margin)
            end_pos = (self.margin + i * self.cell_size,
                      self.margin + self.cell_size * self.board_size)
            pygame.draw.line(self.screen, Colors.BLACK, start_pos, end_pos, 2)
        
        # Draw goal zones
        for col in range(self.board_size):
            # Top goal zone for Player 0
            pygame.draw.rect(self.screen, Colors.LIGHT_BLUE,
                           (self.margin + col * self.cell_size,
                            self.margin,
                            self.cell_size, self.cell_size))
            # Bottom goal zone for Player 1
            pygame.draw.rect(self.screen, Colors.LIGHT_RED,
                           (self.margin + col * self.cell_size,
                            self.margin + (self.board_size - 1) * self.cell_size,
                            self.cell_size, self.cell_size))
        
        # Draw walls
        self.draw_walls()
        
        # Draw valid moves
        for col, row in self.valid_moves:
            x = self.margin + col * self.cell_size + self.cell_size // 2
            y = self.margin + row * self.cell_size + self.cell_size // 2
            pygame.draw.circle(self.screen, Colors.GREEN, (x, y), 8)
        
        # Draw pawns
        self.draw_pawns()
        
        # Draw UI
        self.draw_ui()

    def draw_walls(self):
        """Draw walls on the board"""
        # Draw horizontal walls
        for row in range(self.board_size):
            for col in range(self.board_size - 1):
                if self.board.h_walls[row][col]:
                    x = self.margin + col * self.cell_size + self.cell_size
                    y = self.margin + row * self.cell_size
                    pygame.draw.rect(self.screen, Colors.BLACK,
                                   (x - self.wall_width // 2, y - self.wall_width // 2,
                                    self.cell_size, self.wall_width))
        
        # Draw vertical walls
        for row in range(self.board_size - 1):
            for col in range(self.board_size):
                if self.board.v_walls[row][col]:
                    x = self.margin + col * self.cell_size
                    y = self.margin + row * self.cell_size + self.cell_size
                    pygame.draw.rect(self.screen, Colors.BLACK,
                                   (x - self.wall_width // 2, y - self.wall_width // 2,
                                    self.wall_width, self.cell_size))

    def draw_pawns(self):
        """Draw player pawns"""
        for player_id, player in enumerate(self.board.players):
            x = self.margin + player.col * self.cell_size + self.cell_size // 2
            y = self.margin + player.row * self.cell_size + self.cell_size // 2
            
            color = Colors.BLUE if player_id == 0 else Colors.RED
            pygame.draw.circle(self.screen, color, (x, y), 15)
            pygame.draw.circle(self.screen, Colors.BLACK, (x, y), 15, 3)

    def draw_ui(self):
        """Draw UI elements"""
        ui_y = self.margin + self.cell_size * self.board_size + 10
        
        # Draw turn information
        turn_text = f"Current Player: {self.current_player}"
        if self.game_mode == "pvc":
            turn_text += " (CPU)" if self.current_player == 1 else " (You)"
        
        text_surface = self.font_medium.render(turn_text, True, Colors.BLACK)
        self.screen.blit(text_surface, (self.margin, ui_y))
        
        # Draw wall counts
        player0_walls = self.board.players[0].walls_remaining
        player1_walls = self.board.players[1].walls_remaining
        
        walls_text = f"Walls - P0: {player0_walls}  P1: {player1_walls}"
        text_surface = self.font_small.render(walls_text, True, Colors.BLACK)
        self.screen.blit(text_surface, (self.margin, ui_y + 40))
        
        # Draw mode information
        mode_text = "Press 'W' to place wall, 'R' to rotate, 'SPACE' to reset, 'Q' to quit"
        text_surface = self.font_small.render(mode_text, True, Colors.GRAY)
        self.screen.blit(text_surface, (self.margin, ui_y + 65))
        
        # Draw messages
        if pygame.time.get_ticks() - self.message_time < 3000:
            msg_surface = self.font_medium.render(self.message, True, Colors.BLACK)
            self.screen.blit(msg_surface, (self.margin, ui_y + 90))
        
        # Draw game over message
        if self.game_over:
            winner_text = f"Player {self.winner} Wins!"
            text_surface = self.font_large.render(winner_text, True, Colors.BLACK)
            text_rect = text_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            pygame.draw.rect(self.screen, Colors.YELLOW, text_rect.inflate(20, 20))
            self.screen.blit(text_surface, text_rect)

    def reset_game(self):
        """Reset the game"""
        self.board = GameBoard()
        self.current_player = 0
        self.game_over = False
        self.winner = None
        self.message = "Game reset. Player 0's turn"
        self.message_time = pygame.time.get_ticks()
        self.selected_cell = None
        self.valid_moves = []

    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            
            pygame.display.flip()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()
        sys.exit()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Quoridor Game")
    parser.add_argument("--mode", choices=["pvp", "pvc"], default="pvp",
                       help="Game mode: pvp (player vs player) or pvc (player vs computer)")
    parser.add_argument("--difficulty", choices=["easy", "medium", "hard"], default="medium",
                       help="AI difficulty level")
    
    args = parser.parse_args()
    
    gui = QuoridorGUI(game_mode=args.mode, ai_difficulty=args.difficulty)
    gui.run()


if __name__ == "__main__":
    main()
