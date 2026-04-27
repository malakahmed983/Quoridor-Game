"""Unit tests for the Quoridor game core logic."""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core import (
    BOARD_SIZE,
    MAX_WALLS,
    PLAYER_1,
    PLAYER_2,
    HORIZONTAL,
    VERTICAL,
    Player,
    GameState,
    switch_turn,
    get_current_player,
    get_opponent,
    check_winner,
    reset_game,
    get_valid_pawn_moves,
    move_pawn,
    place_wall,
    get_valid_wall_placements,
    _is_wall_blocking,
    _has_path_to_goal,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fresh_state():
    return GameState()


# ---------------------------------------------------------------------------
# GameState initialisation
# ---------------------------------------------------------------------------

class TestGameStateInit:
    def test_initial_turn(self):
        gs = fresh_state()
        assert gs.current_turn == PLAYER_1

    def test_player_positions(self):
        gs = fresh_state()
        assert gs.players[PLAYER_1].position == (0, 4)
        assert gs.players[PLAYER_2].position == (8, 4)

    def test_walls_remaining(self):
        gs = fresh_state()
        assert gs.players[PLAYER_1].walls_remaining == MAX_WALLS
        assert gs.players[PLAYER_2].walls_remaining == MAX_WALLS

    def test_no_walls_initially(self):
        gs = fresh_state()
        assert gs.walls == []


# ---------------------------------------------------------------------------
# Turn helpers
# ---------------------------------------------------------------------------

class TestTurnHelpers:
    def test_switch_turn(self):
        gs = fresh_state()
        switch_turn(gs)
        assert gs.current_turn == PLAYER_2
        switch_turn(gs)
        assert gs.current_turn == PLAYER_1

    def test_get_current_player(self):
        gs = fresh_state()
        assert get_current_player(gs) is gs.players[PLAYER_1]

    def test_get_opponent(self):
        gs = fresh_state()
        assert get_opponent(gs) is gs.players[PLAYER_2]


# ---------------------------------------------------------------------------
# Win condition
# ---------------------------------------------------------------------------

class TestWinCondition:
    def test_no_winner_at_start(self):
        assert check_winner(fresh_state()) is None

    def test_player1_wins_at_row_8(self):
        gs = fresh_state()
        gs.players[PLAYER_1].position = (8, 4)
        assert check_winner(gs) == PLAYER_1

    def test_player2_wins_at_row_0(self):
        gs = fresh_state()
        gs.players[PLAYER_2].position = (0, 4)
        assert check_winner(gs) == PLAYER_2

    def test_player1_wins_any_col(self):
        gs = fresh_state()
        gs.players[PLAYER_1].position = (8, 0)
        assert check_winner(gs) == PLAYER_1


# ---------------------------------------------------------------------------
# Reset
# ---------------------------------------------------------------------------

class TestResetGame:
    def test_reset_restores_initial_state(self):
        gs = fresh_state()
        gs.players[PLAYER_1].position = (5, 5)
        gs.walls.append((2, 2, HORIZONTAL))
        switch_turn(gs)
        reset_game(gs)
        assert gs.players[PLAYER_1].position == (0, 4)
        assert gs.players[PLAYER_2].position == (8, 4)
        assert gs.walls == []
        assert gs.current_turn == PLAYER_1


# ---------------------------------------------------------------------------
# Wall blocking helper
# ---------------------------------------------------------------------------

class TestIsWallBlocking:
    def test_horizontal_wall_blocks_south(self):
        # Horizontal wall at (3, 4): blocks (3,4)->(4,4) and (3,5)->(4,5)
        walls = [(3, 4, HORIZONTAL)]
        assert _is_wall_blocking(walls, 3, 4, 4, 4) is True
        assert _is_wall_blocking(walls, 3, 5, 4, 5) is True

    def test_horizontal_wall_blocks_north(self):
        walls = [(3, 4, HORIZONTAL)]
        assert _is_wall_blocking(walls, 4, 4, 3, 4) is True
        assert _is_wall_blocking(walls, 4, 5, 3, 5) is True

    def test_horizontal_wall_does_not_block_east_west(self):
        walls = [(3, 4, HORIZONTAL)]
        assert _is_wall_blocking(walls, 3, 4, 3, 5) is False

    def test_vertical_wall_blocks_east(self):
        # Vertical wall at (3, 4): blocks (3,4)->(3,5) and (4,4)->(4,5)
        walls = [(3, 4, VERTICAL)]
        assert _is_wall_blocking(walls, 3, 4, 3, 5) is True
        assert _is_wall_blocking(walls, 4, 4, 4, 5) is True

    def test_vertical_wall_blocks_west(self):
        walls = [(3, 4, VERTICAL)]
        assert _is_wall_blocking(walls, 3, 5, 3, 4) is True
        assert _is_wall_blocking(walls, 4, 5, 4, 4) is True

    def test_vertical_wall_does_not_block_north_south(self):
        walls = [(3, 4, VERTICAL)]
        assert _is_wall_blocking(walls, 3, 4, 4, 4) is False

    def test_no_walls(self):
        assert _is_wall_blocking([], 0, 0, 1, 0) is False


# ---------------------------------------------------------------------------
# BFS path check
# ---------------------------------------------------------------------------

class TestHasPathToGoal:
    def test_player1_has_path_at_start(self):
        gs = fresh_state()
        assert _has_path_to_goal(gs, PLAYER_1) is True

    def test_player2_has_path_at_start(self):
        gs = fresh_state()
        assert _has_path_to_goal(gs, PLAYER_2) is True

    def test_player1_blocked_by_walls(self):
        gs = fresh_state()
        # Block the entire row 7 border for player 1 trying to reach row 8
        for c in range(0, 8):
            gs.walls.append((7, c, HORIZONTAL))
        assert _has_path_to_goal(gs, PLAYER_1) is False

    def test_player2_has_path_when_only_p1_is_blocked(self):
        # Trap P1 at corner (0,0) with two walls so it cannot escape,
        # while P2 at (8,4) still has a clear path to row 0.
        gs = fresh_state()
        gs.players[PLAYER_1].position = (0, 0)
        # H wall at (0,0): blocks south from (0,0) and (0,1)
        gs.walls.append((0, 0, HORIZONTAL))
        # V wall at (0,0): blocks east from (0,0) and (1,0)
        gs.walls.append((0, 0, VERTICAL))
        # P1 is completely surrounded (board edge covers north/west)
        assert _has_path_to_goal(gs, PLAYER_1) is False
        assert _has_path_to_goal(gs, PLAYER_2) is True


# ---------------------------------------------------------------------------
# Pawn movement
# ---------------------------------------------------------------------------

class TestPawnMovement:
    def test_player1_can_move_south_from_start(self):
        gs = fresh_state()
        moves = get_valid_pawn_moves(gs)
        assert (1, 4) in moves

    def test_player1_cannot_move_north_from_row0(self):
        gs = fresh_state()
        moves = get_valid_pawn_moves(gs)
        assert (-1, 4) not in moves

    def test_move_pawn_valid(self):
        gs = fresh_state()
        assert move_pawn(gs, (1, 4)) is True
        assert gs.players[PLAYER_1].position == (1, 4)

    def test_move_pawn_invalid(self):
        gs = fresh_state()
        assert move_pawn(gs, (5, 5)) is False
        assert gs.players[PLAYER_1].position == (0, 4)

    def test_cannot_move_through_wall(self):
        gs = fresh_state()
        # Place a horizontal wall that blocks player 1 from moving south
        gs.walls.append((0, 3, HORIZONTAL))
        moves = get_valid_pawn_moves(gs)
        assert (1, 4) not in moves

    def test_jump_over_opponent_straight(self):
        gs = fresh_state()
        gs.players[PLAYER_1].position = (7, 4)
        gs.players[PLAYER_2].position = (8, 4)
        moves = get_valid_pawn_moves(gs)
        # Straight jump north (to 6,4) is valid; south jump is over board edge
        assert (6, 4) in moves

    def test_diagonal_jump_when_straight_blocked(self):
        gs = fresh_state()
        # P1 at (3,4), P2 at (4,4); put a wall blocking straight jump south
        gs.players[PLAYER_1].position = (3, 4)
        gs.players[PLAYER_2].position = (4, 4)
        # Block the path south of (4,4) with a horizontal wall
        gs.walls.append((4, 3, HORIZONTAL))
        moves = get_valid_pawn_moves(gs)
        # Both diagonal jumps from (4,4) must be available: east (4,5) and west (4,3)
        assert (4, 3) in moves
        assert (4, 5) in moves

    def test_move_does_not_switch_turn(self):
        gs = fresh_state()
        move_pawn(gs, (1, 4))
        assert gs.current_turn == PLAYER_1


# ---------------------------------------------------------------------------
# Wall placement
# ---------------------------------------------------------------------------

class TestWallPlacement:
    def test_place_valid_horizontal_wall(self):
        gs = fresh_state()
        assert place_wall(gs, 4, 4, HORIZONTAL) is True
        assert (4, 4, HORIZONTAL) in gs.walls

    def test_place_valid_vertical_wall(self):
        gs = fresh_state()
        assert place_wall(gs, 4, 4, VERTICAL) is True
        assert (4, 4, VERTICAL) in gs.walls

    def test_wall_decrements_player_walls(self):
        gs = fresh_state()
        place_wall(gs, 4, 4, HORIZONTAL)
        assert gs.players[PLAYER_1].walls_remaining == MAX_WALLS - 1

    def test_wall_out_of_bounds(self):
        gs = fresh_state()
        assert place_wall(gs, 8, 4, HORIZONTAL) is False
        assert place_wall(gs, 4, 8, HORIZONTAL) is False

    def test_overlapping_same_orientation(self):
        gs = fresh_state()
        place_wall(gs, 4, 4, HORIZONTAL)
        assert place_wall(gs, 4, 4, HORIZONTAL) is False
        assert place_wall(gs, 4, 5, HORIZONTAL) is False
        assert place_wall(gs, 4, 3, HORIZONTAL) is False

    def test_crossing_walls_rejected(self):
        gs = fresh_state()
        place_wall(gs, 4, 4, HORIZONTAL)
        # A vertical wall at the same point crosses the horizontal one
        assert place_wall(gs, 4, 4, VERTICAL) is False

    def test_cannot_place_wall_that_blocks_all_paths(self):
        gs = fresh_state()
        # Manually fill walls to seal off player 1 completely (bypass walls_remaining)
        for c in range(0, 8):
            gs.walls.append((7, c, HORIZONTAL))
        # Now an additional wall shouldn't make things worse,
        # but place_wall should refuse when path is blocked
        gs2 = fresh_state()
        for c in range(0, 7):
            gs2.walls.append((7, c, HORIZONTAL))
        assert place_wall(gs2, 7, 7, HORIZONTAL) is False

    def test_no_walls_remaining_prevents_placement(self):
        gs = fresh_state()
        gs.players[PLAYER_1].walls_remaining = 0
        assert place_wall(gs, 4, 4, HORIZONTAL) is False

    def test_wall_placement_does_not_switch_turn(self):
        gs = fresh_state()
        place_wall(gs, 4, 4, HORIZONTAL)
        assert gs.current_turn == PLAYER_1

    def test_get_valid_wall_placements_non_empty_at_start(self):
        gs = fresh_state()
        valid = get_valid_wall_placements(gs)
        assert len(valid) > 0

    def test_get_valid_wall_placements_empty_when_no_walls(self):
        gs = fresh_state()
        gs.players[PLAYER_1].walls_remaining = 0
        assert get_valid_wall_placements(gs) == []


# ---------------------------------------------------------------------------
# Integration: full mini-game turn sequence
# ---------------------------------------------------------------------------

class TestIntegration:
    def test_alternate_turns_and_win(self):
        gs = fresh_state()
        # Move P2 to (8,0) so it is out of P1's path down column 4.
        gs.players[PLAYER_2].position = (8, 0)
        for row in range(1, 9):
            assert move_pawn(gs, (row, 4)) is True
            assert gs.players[PLAYER_1].position == (row, 4)
            switch_turn(gs)   # P2's turn — skip by switching straight back
            switch_turn(gs)
        assert check_winner(gs) == PLAYER_1

    def test_wall_then_pawn_then_switch(self):
        gs = fresh_state()
        assert place_wall(gs, 3, 3, HORIZONTAL) is True
        switch_turn(gs)
        assert gs.current_turn == PLAYER_2
        assert move_pawn(gs, (7, 4)) is True
        switch_turn(gs)
        assert gs.current_turn == PLAYER_1
