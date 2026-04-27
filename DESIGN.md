# Quoridor Game Implementation - Design Decisions

## Overview

This document outlines the key design decisions made during the implementation of the Quoridor game.

## 1. Technology Stack Selection

### Why Python?

- **Accessibility**: Easy to learn and read, ideal for a game implementation project
- **Rich Libraries**: Pygame for graphics, extensive standard library for game logic
- **Rapid Development**: Faster prototyping and iteration compared to C++ or Java
- **Cross-Platform**: Runs on Windows, macOS, and Linux without modification

### Why Pygame?

- **Game Development**: Specifically designed for 2D game development in Python
- **Simple API**: Easy to learn for students, clean event handling
- **Performance**: Sufficient for a turn-based board game
- **Community**: Large community with many tutorials and examples
- **Licensing**: Free and open-source (LGPL)

Alternative considered: Tkinter (too limited for game GUI needs), PyQt (overkill for simple game)

## 2. Board Representation

### 2D Array Approach

**Chosen**: Separate arrays for horizontal and vertical walls

```python
h_walls = [[False] * (board_size - 1) for _ in range(board_size)]
v_walls = [[False] * board_size for _ in range(board_size - 1)]
```

**Advantages**:
- Clear separation between wall types
- O(1) lookup time for wall status
- Easy to visualize wall positions
- Efficient memory usage (boolean arrays)

**Alternatives considered**:
- Single 2D grid with wall objects: More complex indexing
- Sparse wall dictionary: Harder to validate wall overlaps
- Graph-based representation: Overkill for fixed 9x9 board

## 3. Game Logic Architecture

### Separation of Concerns

```
game_logic.py    - Pure game rules, no dependencies
    ↓
ai.py           - AI decision making using game logic
    ↓
gui.py          - Presentation and user interaction
    ↓
main.py         - Entry point and argument handling
```

**Benefits**:
- Easy to test game logic independently
- AI can be swapped or improved without GUI changes
- GUI can be replaced without affecting core logic
- Clear dependencies

## 4. Move Validation Strategy

### Multi-Step Validation Process

1. **Boundary Check**: Ensure target is within board
2. **Distance Check**: Max 2 squares (normal or jump)
3. **Direction Check**: Orthogonal movement only (except diagonal around opponent)
4. **Wall Check**: Verify no walls block the movement
5. **Collision Check**: Check opponent pawn collision

**Rationale**:
- Order minimizes expensive pathfinding calculations
- Clear, modular validation functions
- Easy to debug invalid moves

### Valid Moves Method

```python
def get_valid_moves(player_id: int) -> List[Tuple[int, int]]:
    - Check all 4 orthogonal neighbors
    - Check jump moves over opponent
    - Check diagonal alternatives if jump blocked
    - Return deduplicated list
```

## 5. Wall Placement Validation

### Three-Level Validation

**Level 1: Basic Validity**
- Check board boundaries
- Check overlaps with existing walls
- Check adjacency violations

**Level 2: Path Validation**
- Use BFS to ensure both players can still reach goal
- Temporary wall placement for testing
- Restore board state if invalid

**Level 3: Runtime Enforcement**
- Wall blocks movement at move time
- Prevents corner cases

### Path-Finding Algorithm: BFS

**Choice**: Breadth-First Search

```
Why BFS?
- Guaranteed shortest path in unweighted grid
- O(V + E) time complexity
- Simple to implement and debug
- Sufficient for 9x9 board (81 squares max)
```

Alternatives considered:
- Dijkstra: Unnecessary for unweighted grid
- A*: Overkill; BFS fast enough
- DFS: Doesn't guarantee shortest path

## 6. AI Architecture

### Three Difficulty Levels

**Easy: Baseline Random**
```
Select randomly from valid moves
Purpose: Beginner opponent, quick to compute
```

**Medium: Heuristic Evaluation**
```
Score = -distance_to_goal * 10 
        + opponent_proximity_bonus 
        + wall_advantage_bonus

Purpose: Competent opponent, reasonable play
```

**Hard: Minimax with Alpha-Beta Pruning**
```
max(min(opponent_moves)) with pruning
Depth: 2-3 moves
Evaluation: Combined heuristics

Purpose: Challenging opponent, strategic play
```

### Why Minimax?

- **Optimal Play**: Guarantees best move within search depth
- **Alpha-Beta Pruning**: Reduces computation significantly
- **Classic Approach**: Well-understood algorithm for game AI
- **Scalable**: Can increase depth for stronger play

**Why not Deep Learning / Neural Networks?**
- Requires extensive training data
- Beyond scope of this project
- Minimax sufficient for turn-based strategy game

### Heuristic Function Design

```python
Evaluation combines:
1. Distance to goal (primary factor)
2. Opponent distance to goal (comparison)
3. Path length (BFS-based)
4. Wall advantage (pieces remaining)
5. Opponent proximity (blocking potential)
```

## 7. GUI Design Principles

### User Interface Organization

```
Game Board (9x9 grid)
    ↓
Status Bar
    ↓
Instructions
```

**Color Scheme**:
- Blue: Player 0
- Red: Player 1
- Green: Valid moves
- Black: Walls and grid

**Feedback Mechanisms**:
- Highlighted valid moves (circles)
- Turn indicator text
- Wall count display
- Status messages

### Input Methods

**Mouse-Centric Design**:
- Intuitive click-to-move
- Click to place walls
- No complex keyboard combinations

**Keyboard Shortcuts**:
- Essential: W (wall), R (rotate), ESC (cancel)
- Convenience: SPACE (reset), Q (quit)

## 8. Game State Management

### Immutable vs. Mutable

**Approach**: Mutable state with validation

```python
board.move_pawn(player_id, row, col)  # Modifies board
if game_over:
    # Check win condition
```

**Why Mutable**:
- Simpler implementation
- Faster AI calculations
- Easier debugging
- Sufficient validation prevents corruption

**Alternative (Immutable)**:
- More testable
- More functional approach
- Higher memory usage
- Slower for AI minimax

## 9. Performance Optimizations

### Move Generation Efficiency

```
1. Pre-compute valid moves per turn
2. Cache results until board changes
3. AI uses cached results for evaluation
```

### Minimax Optimization

```
1. Alpha-Beta Pruning
2. Limited search depth (2-3 moves)
3. Heuristic ordering (try better moves first)
4. Early termination on win detection
```

## 10. Error Handling Strategy

### Validation Over Exceptions

```python
# Instead of:
try:
    board.move_pawn(...)
except InvalidMoveError:
    pass

# Use:
if board.is_valid_move(...):
    board.move_pawn(...)
```

**Rationale**:
- Clearer game logic flow
- Better user feedback (show invalid moves vs. just failing)
- Easier testing

## 11. Code Organization

### Module Responsibilities

| Module | Responsibility |
|--------|-----------------|
| `game_logic.py` | Game rules, board state, validation |
| `ai.py` | Move selection, strategy, evaluation |
| `gui.py` | Rendering, input handling, UI |
| `main.py` | Entry point, argument parsing |
| `test_game.py` | Unit tests for game logic |

### Class Design

**Minimal but Complete**:
- `GameBoard`: 200+ lines, core logic
- `Player`: 10 lines, simple state holder
- `Wall`: 20 lines, simple data class
- `QuoridorAI`: 300+ lines, decision logic
- `QuoridorGUI`: 400+ lines, rendering

## 12. Trade-offs Made

### Simplified Wall Placement UI

**Tradeoff**: Accuracy vs. Simplicity
- Current: Click on board to place wall
- Could improve: Drag to preview, click corners for precise placement
- Decision: Simpler works for project scope

### Fixed 2-Player Game

**Tradeoff**: Scope vs. Completeness
- Implemented: 2-player fully featured
- Future: 4-player support
- Decision: Focus on quality over quantity

### Hard-Coded AI Depth

**Tradeoff**: Performance vs. Strength
- Current: Search depth 2-3
- Could increase: Up to depth 5-6
- Decision: Depth 3 provides good balance

## 13. Extensibility

### Future Enhancement Points

1. **4-Player Support**:
   - Extend `Player` array to 4 elements
   - Modify winning conditions
   - Adjust AI strategies

2. **Game Persistence**:
   - Save/load board state
   - Replay functionality
   - Statistics tracking

3. **Network Play**:
   - Client-server architecture
   - Move serialization
   - Turn synchronization

4. **Improved AI**:
   - Opening book for better early moves
   - Endgame optimization
   - Machine learning integration

## 14. Testing Strategy

### Test Coverage

- Unit tests for game logic (test_game.py)
- Manual testing of AI difficulty levels
- Edge case testing (board boundaries, wall overlaps)
- Integration testing (UI with game logic)

### Testable Design

- Pure functions for game logic
- Dependency injection for AI
- Clear interfaces between modules

---

**Document Status**: Final  
**Last Updated**: April 28, 2026
