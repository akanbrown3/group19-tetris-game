import pytest
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.piece import Piece


class TestPiece:
    """Test cases for Tetris piece functionality"""
    
    def test_piece_initialization(self):
        """Test that piece initializes with correct default values"""
        piece = Piece()
        assert piece.x == 3
        assert piece.y == 0
        assert 0 <= piece.type <= 6  # Valid piece type
        assert 1 <= piece.color <= 7  # Valid color
        assert piece.rotation == 0
        
    def test_piece_initialization_with_position(self):
        """Test piece initialization with custom position"""
        piece = Piece(x=5, y=10)
        assert piece.x == 5
        assert piece.y == 10
        
    def test_piece_rotation_clockwise(self):
        """Test clockwise rotation functionality"""
        piece = Piece()
        original_rotation = piece.rotation
        piece.rotate_clockwise()
        
        # Check that rotation changed (unless it's O-piece which has only one rotation)
        if len(piece.SHAPES[piece.type]) > 1:
            assert piece.rotation != original_rotation
        
        # Test multiple rotations return to original
        for _ in range(len(piece.SHAPES[piece.type]) - 1):
            piece.rotate_clockwise()
        assert piece.rotation == original_rotation
        
    def test_piece_rotation_counterclockwise(self):
        """Test counterclockwise rotation functionality"""
        piece = Piece()
        original_rotation = piece.rotation
        piece.rotate_counterclockwise()
        
        # For pieces with multiple rotations, check it changed
        if len(piece.SHAPES[piece.type]) > 1:
            assert piece.rotation != original_rotation
            
    def test_piece_movement(self):
        """Test piece movement in all directions"""
        piece = Piece(x=5, y=5)
        
        # Test moving right
        piece.move(1, 0)
        assert piece.x == 6
        assert piece.y == 5
        
        # Test moving left
        piece.move(-2, 0)
        assert piece.x == 4
        assert piece.y == 5
        
        # Test moving down
        piece.move(0, 3)
        assert piece.x == 4
        assert piece.y == 8
        
        # Test moving up
        piece.move(0, -1)
        assert piece.x == 4
        assert piece.y == 7
        
    def test_piece_copy(self):
        """Test that piece copy creates independent duplicate"""
        original = Piece(x=3, y=5)
        original.type = 2
        original.color = 4
        original.rotation = 1
        
        copy = original.copy()
        
        # Check all attributes copied correctly
        assert copy.x == original.x
        assert copy.y == original.y
        assert copy.type == original.type
        assert copy.color == original.color
        assert copy.rotation == original.rotation
        
        # Check they are independent objects
        copy.move(1, 1)
        assert copy.x != original.x
        assert copy.y != original.y
        
    def test_get_blocks_returns_correct_coordinates(self):
        """Test that get_blocks returns correct block positions"""
        piece = Piece(x=0, y=0)
        piece.type = 6  # O-piece (square)
        piece.rotation = 0
        
        blocks = piece.get_blocks()
        assert len(blocks) == 4  # All tetrominoes have 4 blocks
        
        # All coordinates should be tuples of two integers
        for block in blocks:
            assert isinstance(block, tuple)
            assert len(block) == 2
            assert isinstance(block[0], int)
            assert isinstance(block[1], int)
            
    def test_get_blocks_accounts_for_position(self):
        """Test that get_blocks accounts for piece position"""
        piece1 = Piece(x=0, y=0)
        piece1.type = 0  # I-piece
        piece1.rotation = 0
        
        piece2 = Piece(x=2, y=3)
        piece2.type = 0  # I-piece  
        piece2.rotation = 0
        
        blocks1 = piece1.get_blocks()
        blocks2 = piece2.get_blocks()
        
        # Check that piece2 blocks are offset by (2, 3) from piece1
        for i, (block1, block2) in enumerate(zip(blocks1, blocks2)):
            assert block2[0] == block1[0] + 2
            assert block2[1] == block1[1] + 3
            
    def test_all_piece_types_have_valid_shapes(self):
        """Test that all piece types have valid shape definitions"""
        for piece_type in range(7):  # 0-6 for I,Z,S,T,J,L,O
            piece = Piece()
            piece.type = piece_type
            
            # Check that each piece type has at least one rotation
            assert len(piece.SHAPES[piece_type]) >= 1
            
            # Check that each rotation has exactly 4 blocks
            for rotation in range(len(piece.SHAPES[piece_type])):
                piece.rotation = rotation
                blocks = piece.get_blocks()
                assert len(blocks) == 4
                
    def test_shape_consistency(self):
        """Test that get_shape returns valid shape data"""
        piece = Piece()
        shape = piece.get_shape()
        
        # Shape should be a list of integers representing positions in 4x4 grid
        assert isinstance(shape, list)
        assert len(shape) == 4  # Should have 4 blocks
        
        # All positions should be valid (0-15 for 4x4 grid)
        for position in shape:
            assert isinstance(position, int)
            assert 0 <= position <= 15