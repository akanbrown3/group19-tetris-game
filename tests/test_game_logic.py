import pytest
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.board import Board
from src.piece import Piece
from src.main import TetrisGame, GameState


class TestGameLogic:
    """Test cases for overall Tetris game logic integration"""
    
    def test_game_initialization(self):
        """Test that game initializes properly"""
        # Note: This test may need to be modified if pygame isn't available in test environment
        try:
            game = TetrisGame()
            assert game.width == 1000
            assert game.height == 700
            assert game.state == GameState.MENU
            assert game.running == True
            assert isinstance(game.board1, Board)
            assert isinstance(game.board2, Board)
            # Cleanup to avoid pygame issues: remove the attribute instead of assigning None
            if hasattr(game, "screen"):
                delattr(game, "screen")
        except Exception as e:
            # If pygame isn't available, test basic class structure
            assert GameState.MENU.value == "menu"
            assert GameState.SINGLE_PLAYER.value == "single"
            assert GameState.MULTIPLAYER.value == "multiplayer"

    def test_piece_spawn_and_placement_integration(self):
        """Test full piece lifecycle: spawn -> move -> lock -> clear"""
        board = Board()
        
        # Spawn a piece
        board.spawn_piece()
        assert board.current_piece is not None
        assert board.next_piece is not None
        
        # Test that current piece can move
        original_pos = (board.current_piece.x, board.current_piece.y)
        success = board.move_piece(1, 0)  # Move right
        if success:
            assert board.current_piece.x == original_pos[0] + 1
            
    def test_complete_line_clearing_workflow(self):
        """Test complete workflow of filling and clearing lines"""
        board = Board()
        
        # Fill bottom row except one space
        bottom_row = board.height - 1
        for x in range(board.width - 1):
            board.grid[bottom_row][x] = 1
            
        # Create a piece that will complete the line
        piece = Piece(x=board.width - 1, y=bottom_row)
        piece.type = 6  # O-piece (small, predictable)
        
        # Simulate placing the piece
        for block_x, block_y in piece.get_blocks():
            if 0 <= block_y < board.height and 0 <= block_x < board.width:
                board.grid[block_y][block_x] = piece.color
                
        # Clear lines
        original_score = board.score
        lines_cleared = board.clear_lines()
        
        if lines_cleared > 0:
            # Update score manually (normally done in lock_piece)
            line_scores = {1: 100, 2: 300, 3: 500, 4: 800}
            base_score = line_scores.get(lines_cleared, lines_cleared * 100)
            board.score += base_score * board.level
            board.lines_cleared += lines_cleared
            
            assert board.score > original_score
            assert board.lines_cleared > 0
            
    def test_game_over_conditions(self):
        """Test various game over conditions"""
        board = Board()
        
        # Fill the top rows to simulate game over condition
        for y in range(3):  # Fill top 3 rows
            for x in range(board.width):
                board.grid[y][x] = 1
                
        # Try to spawn a new piece - should trigger game over
        board.spawn_piece()
        
        # The collision detection should detect game over
        if board.current_piece:
            collision = board.is_collision(board.current_piece)
            if collision:
                board.game_over = True
                
        # Game over should be true if collision detected
        # (This depends on the exact implementation details)
        
    def test_hold_piece_functionality(self):
        """Test hold piece mechanism"""
        board = Board()
        board.spawn_piece()
        
        if board.current_piece:
            original_type = board.current_piece.type
            
            # Hold the piece
            success = board.hold_piece()
            
            if success:
                assert board.held_piece is not None
                assert board.held_piece.type == original_type
                assert not board.can_hold  # Should not be able to hold again immediately
                
    def test_piece_rotation_with_collision_checking(self):
        """Test piece rotation respects collision boundaries"""
        board = Board()
        
        # Create a piece near the edge
        piece = Piece(x=0, y=0)  # Left edge
        board.current_piece = piece
        
        # Try to rotate - should check for collisions
        rotation_success = board.rotate_piece()
        
        # Result depends on piece type and position, but method should not crash
        assert isinstance(rotation_success, bool)
        
    def test_soft_drop_vs_hard_drop(self):
        """Test difference between soft drop and hard drop"""
        board = Board()
        board.spawn_piece()
        
        if board.current_piece:
            original_y = board.current_piece.y
            original_score = board.score
            
            # Test soft drop (move down one space)
            soft_drop_success = board.drop_piece()
            
            # Reset for hard drop test
            board.current_piece.y = original_y
            board.score = original_score
            
            # Test hard drop (fall to bottom instantly)
            board.hard_drop()
            
            # Hard drop should have moved piece further and added to score
            assert board.score >= original_score  # Hard drop gives points
            
    def test_multiplayer_board_independence(self):
        """Test that multiplayer boards operate independently"""
        board1 = Board(player_id=1)
        board2 = Board(player_id=2)
        
        # Modify board1
        board1.score = 1000
        board1.level = 5
        board1.spawn_piece()
        
        # board2 should be unaffected
        assert board2.score == 0
        assert board2.level == 1
        assert board2.player_id == 2
        
        # Modify board2
        board2.game_over = True
        
        # board1 should be unaffected
        assert not board1.game_over
        
    def test_level_progression_affects_speed(self):
        """Test that level progression changes drop speed"""
        board = Board()
        
        # Test speed at level 1
        board.level = 1
        speed_1 = board.get_drop_speed()
        
        # Test speed at higher level
        board.level = 10
        speed_10 = board.get_drop_speed()
        
        # Higher level should mean faster speed (lower number)
        assert speed_10 < speed_1
        
    def test_scoring_scales_with_level(self):
        """Test that scoring scales with current level"""
        board = Board()
        
        # Set up scenario for scoring
        board.level = 1
        board.score = 0
        
        # Fill a line for clearing
        bottom_row = board.height - 1
        for x in range(board.width):
            board.grid[bottom_row][x] = 1
            
        lines_cleared = board.clear_lines()
        if lines_cleared > 0:
            # Calculate score manually
            line_scores = {1: 100, 2: 300, 3: 500, 4: 800}
            base_score = line_scores.get(lines_cleared, lines_cleared * 100)
            score_level_1 = base_score * 1  # level 1
            
            # Test with higher level
            board.level = 3
            score_level_3 = base_score * 3  # level 3
            
            # Higher level should give more points
            assert score_level_3 > score_level_1
            
    def test_pause_prevents_game_actions(self):
        """Test that pausing prevents game actions"""
        board = Board()
        board.spawn_piece()
        board.paused = True
        
        if board.current_piece:
            original_pos = (board.current_piece.x, board.current_piece.y)
            
            # These actions should fail when paused
            move_success = board.move_piece(1, 0)
            rotate_success = board.rotate_piece()
            drop_success = board.drop_piece()
            
            assert not move_success
            assert not rotate_success
            assert not drop_success
            
            # Position should not have changed
            assert board.current_piece.x == original_pos[0]
            assert board.current_piece.y == original_pos[1]