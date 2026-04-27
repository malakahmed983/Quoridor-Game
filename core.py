# ================= CORE MODULE =================

# No external dependencies

from collections import deque

BOARD_SIZE = 9
MAX_WALLS = 10

PLAYER_1 = 0
PLAYER_2 = 1

HORIZONTAL = "H"
VERTICAL = "V"


# ================= CLASSES =================


class Player:
    def __init__(self, id, position):
        self.id = id
        self.position = position  # (row, col)
        self.walls_remaining = MAX_WALLS


class GameState:
    def __init__(self):
        self.players = [
            Player(PLAYER_1, (0, 4)),
            Player(PLAYER_2, (8, 4)),
        ]
        # Each wall is stored as (row, col, orientation)
        # HORIZONTAL wall at (r, c): blocks crossing between rows r and r+1
        #   for columns c and c+1 — valid r in 0..7, c in 0..7
        # VERTICAL wall at (r, c): blocks crossing between cols c and c+1
        #   for rows r and r+1 — valid r in 0..7, c in 0..7
        self.walls = []
        self.current_turn = PLAYER_1


# ================= TURN HELPERS =================


def switch_turn(game_state):
    game_state.current_turn = 1 - game_state.current_turn


def get_current_player(game_state):
    return game_state.players[game_state.current_turn]


def get_opponent(game_state):
    return game_state.players[1 - game_state.current_turn]


# ================= WIN CONDITION =================


def check_winner(game_state):
    """Return PLAYER_1, PLAYER_2, or None."""
    if game_state.players[PLAYER_1].position[0] == BOARD_SIZE - 1:
        return PLAYER_1
    if game_state.players[PLAYER_2].position[0] == 0:
        return PLAYER_2
    return None


# ================= WALL BLOCKING HELPERS =================


def _is_wall_blocking(walls, r1, c1, r2, c2):
    """Return True if any placed wall blocks the step from (r1,c1) to (r2,c2)."""
    dr = r2 - r1
    dc = c2 - c1

    for wr, wc, wo in walls:
        if dr == 1 and dc == 0:
            # Moving south: blocked by a HORIZONTAL wall at (r1,c) for c in {c1-1, c1}
            if wo == HORIZONTAL and wr == r1 and wc in (c1 - 1, c1):
                return True
        elif dr == -1 and dc == 0:
            # Moving north: blocked by a HORIZONTAL wall at (r2,c) for c in {c1-1, c1}
            if wo == HORIZONTAL and wr == r2 and wc in (c1 - 1, c1):
                return True
        elif dr == 0 and dc == 1:
            # Moving east: blocked by a VERTICAL wall at (r,c1) for r in {r1-1, r1}
            if wo == VERTICAL and wc == c1 and wr in (r1 - 1, r1):
                return True
        elif dr == 0 and dc == -1:
            # Moving west: blocked by a VERTICAL wall at (r,c2) for r in {r1-1, r1}
            if wo == VERTICAL and wc == c2 and wr in (r1 - 1, r1):
                return True
    return False


# ================= PATH VALIDATION (BFS) =================


def _has_path_to_goal(game_state, player_id):
    """Return True if player_id has at least one path to their goal row."""
    player = game_state.players[player_id]
    goal_row = BOARD_SIZE - 1 if player_id == PLAYER_1 else 0
    start = player.position
    walls = game_state.walls

    visited = set()
    queue = deque([start])
    visited.add(start)

    while queue:
        r, c = queue.popleft()
        if r == goal_row:
            return True
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                if (nr, nc) not in visited:
                    if not _is_wall_blocking(walls, r, c, nr, nc):
                        visited.add((nr, nc))
                        queue.append((nr, nc))
    return False


# ================= PAWN MOVEMENT =================


def get_valid_pawn_moves(game_state):
    """
    Return a list of valid destination positions (row, col) for the current player.

    Rules:
    - Move one step in any of the four cardinal directions if not blocked by a wall
      or the board edge.
    - If the destination is occupied by the opponent, try to jump straight over;
      if that is blocked (by a wall or board edge), jump diagonally to the sides.
    """
    current = get_current_player(game_state)
    opponent = get_opponent(game_state)
    r, c = current.position
    opp_pos = opponent.position
    walls = game_state.walls
    valid = []

    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nr, nc = r + dr, c + dc
        if not (0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE):
            continue
        if _is_wall_blocking(walls, r, c, nr, nc):
            continue

        if (nr, nc) == opp_pos:
            # Attempt straight jump
            jr, jc = nr + dr, nc + dc
            can_jump_straight = (
                0 <= jr < BOARD_SIZE
                and 0 <= jc < BOARD_SIZE
                and not _is_wall_blocking(walls, nr, nc, jr, jc)
            )
            if can_jump_straight:
                valid.append((jr, jc))
            else:
                # Diagonal jumps (perpendicular directions)
                for sdr, sdc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    if (sdr, sdc) == (dr, dc) or (sdr, sdc) == (-dr, -dc):
                        continue
                    sr, sc = nr + sdr, nc + sdc
                    if 0 <= sr < BOARD_SIZE and 0 <= sc < BOARD_SIZE:
                        if not _is_wall_blocking(walls, nr, nc, sr, sc):
                            valid.append((sr, sc))
        else:
            valid.append((nr, nc))

    return valid


def move_pawn(game_state, destination):
    """
    Move the current player's pawn to *destination*.

    Returns True on success, False if the move is invalid.
    Does NOT switch the turn — call switch_turn() separately if desired.
    """
    if destination not in get_valid_pawn_moves(game_state):
        return False
    get_current_player(game_state).position = destination
    return True


# ================= WALL PLACEMENT =================


def _walls_overlap(walls, row, col, orientation):
    """
    Return True if the new wall (row, col, orientation) overlaps with an existing wall.

    Two walls of the same orientation overlap when they share a cell segment.
    Walls of opposite orientation overlap when they cross at the centre point.
    """
    for wr, wc, wo in walls:
        if wo == orientation:
            # Same orientation: overlap when they share a segment
            if orientation == HORIZONTAL:
                # Both horizontal: rows equal and columns differ by at most 1
                if wr == row and abs(wc - col) <= 1:
                    return True
            else:
                # Both vertical: cols equal and rows differ by at most 1
                if wc == col and abs(wr - row) <= 1:
                    return True
        else:
            # Opposite orientation: overlap when they cross at the same (row, col)
            if wr == row and wc == col:
                return True
    return False


def get_valid_wall_placements(game_state):
    """
    Return a list of (row, col, orientation) tuples for all legal wall placements.
    """
    player = get_current_player(game_state)
    if player.walls_remaining == 0:
        return []

    valid = []
    for orientation in (HORIZONTAL, VERTICAL):
        for row in range(BOARD_SIZE - 1):
            for col in range(BOARD_SIZE - 1):
                if _walls_overlap(game_state.walls, row, col, orientation):
                    continue
                # Temporarily place the wall and verify both players still have a path
                game_state.walls.append((row, col, orientation))
                p1_ok = _has_path_to_goal(game_state, PLAYER_1)
                p2_ok = _has_path_to_goal(game_state, PLAYER_2)
                game_state.walls.pop()
                if p1_ok and p2_ok:
                    valid.append((row, col, orientation))
    return valid


def place_wall(game_state, row, col, orientation):
    """
    Place a wall for the current player.

    Returns True on success, False if the placement is invalid.
    Does NOT switch the turn — call switch_turn() separately if desired.
    """
    player = get_current_player(game_state)
    if player.walls_remaining == 0:
        return False
    if orientation not in (HORIZONTAL, VERTICAL):
        return False
    if not (0 <= row <= BOARD_SIZE - 2 and 0 <= col <= BOARD_SIZE - 2):
        return False
    if _walls_overlap(game_state.walls, row, col, orientation):
        return False
    # Temporarily place the wall to check path connectivity
    game_state.walls.append((row, col, orientation))
    if not _has_path_to_goal(game_state, PLAYER_1) or not _has_path_to_goal(
        game_state, PLAYER_2
    ):
        game_state.walls.pop()
        return False
    player.walls_remaining -= 1
    return True


# ================= RESET =================


def reset_game(game_state):
    new = GameState()
    game_state.players = new.players
    game_state.walls = new.walls
    game_state.current_turn = new.current_turn
