import random
from typing import List, Tuple

class Piece:
    """Represents a Tetris piece (tetromino)"""
    
    # Tetromino shapes represented as 4x4 grids
    SHAPES: List[List[List[int]]] = [
        [[4, 5, 6, 7], [1, 5, 9, 13]],                              # I-piece (horizontal first)
        [[4, 5, 9, 10], [2, 6, 5, 9]],                              # Z-piece
        [[6, 7, 9, 10], [1, 5, 6, 10]],                             # S-piece
        [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]], # T-piece
        [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]], # J-piece
        [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],  # L-piece
        [[1, 2, 5, 6]],                                              # O-piece
    ]
    
    def __init__(self, x: int = 3, y: int = 0) -> None:
        """Initialize a new piece at given position"""
        self.x: int = x
        self.y: int = y
        self.type: int = random.randint(0, len(self.SHAPES) - 1)
        self.color: int = random.randint(1, 7)  # Color index (excluding background color)
        self.rotation: int = 0
    
    def get_shape(self) -> List[int]:
        """Get current shape based on rotation"""
        return self.SHAPES[self.type][self.rotation]
    
    def rotate_clockwise(self) -> None:
        """Rotate piece clockwise"""
        self.rotation = (self.rotation + 1) % len(self.SHAPES[self.type])
    
    def rotate_counterclockwise(self) -> None:
        """Rotate piece counterclockwise"""
        self.rotation = (self.rotation - 1) % len(self.SHAPES[self.type])
    
    def move(self, dx: int, dy: int) -> None:
        """Move piece by given offset"""
        self.x += dx
        self.y += dy
    
    def copy(self) -> 'Piece':
        """Create a copy of this piece"""
        new_piece: Piece = Piece(self.x, self.y)
        new_piece.type = self.type
        new_piece.color = self.color
        new_piece.rotation = self.rotation
        return new_piece
    
    def get_blocks(self) -> List[Tuple[int, int]]:
        """Get list of (x, y) coordinates for all blocks in this piece"""
        blocks: List[Tuple[int, int]] = []
        shape: List[int] = self.get_shape()
        for i in range(4):
            for j in range(4):
                if i * 4 + j in shape:
                    blocks.append((self.x + j, self.y + i))
        return blocks