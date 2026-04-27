"""
Quoridor Game - Main Entry Point
CSE472: Artificial Intelligence Course - Spring 2026
Term Project Implementation
"""

import sys
import os
from gui import QuoridorGUI


def main():
    """Main entry point for the Quoridor game"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Quoridor - Abstract Strategy Board Game",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                          # Start with default settings (PvP mode)
  python main.py --mode pvc               # Play against AI
  python main.py --mode pvc --difficulty hard  # Play against hard AI
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["pvp", "pvc"],
        default="pvp",
        help="Game mode: pvp (Player vs Player) or pvc (Player vs Computer AI) (default: pvp)"
    )
    
    parser.add_argument(
        "--difficulty",
        choices=["easy", "medium", "hard"],
        default="medium",
        help="AI difficulty level (only for pvc mode) (default: medium)"
    )
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("QUORIDOR GAME")
    print("CSE472: Artificial Intelligence - Spring 2026")
    print("=" * 50)
    print(f"\nGame Mode: {'Player vs Computer' if args.mode == 'pvc' else 'Player vs Player'}")
    if args.mode == "pvc":
        print(f"AI Difficulty: {args.difficulty}")
    print("\nControls:")
    print("  Left Click: Select pawn or move pawn")
    print("  'W': Toggle wall placement mode")
    print("  'R': Rotate wall (horizontal/vertical)")
    print("  'ESC': Cancel wall placement")
    print("  'SPACE': Reset game")
    print("  'Q': Quit game")
    print("\nStarting game...\n")
    
    gui = QuoridorGUI(game_mode=args.mode, ai_difficulty=args.difficulty)
    gui.run()


if __name__ == "__main__":
    main()
