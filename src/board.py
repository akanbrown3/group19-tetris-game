from typing import List, Optional, Dict, Any, Union
from .piece import Piece

class Board:
    """Tetris game board with hold piece and competitive features"""
    
    def __init__(self, width: int = 10, height: int = 20, player_id: int = 1) -> None:
        """Initialize empty board"""
        self.width: int = width
        self.height: int = height
        self.player_id: int = player_id
        self.opponent: Optional['Board'] = None
        self.grid: List[List[int]] = [[0 for _ in range(width)] for _ in range(height)]
        self.current_piece: Optional[Piece] = None
        self.next_piece: Optional[Piece] = None
        self.held_piece: Optional[Piece] = None
        self.can_hold: bool = True
        self.score: int = 0
        self.lines_cleared: int = 0
        self.level: int = 1
        self.game_over: bool = False
        self.paused: bool = False
        self.lines_sent: int = 0  # For competitive mode
        self.pending_garbage: List[int] = []  # Lines to add from opponent
        
    def toggle_pause(self) -> None:
        """Toggle pause state"""
        if not self.game_over:
            self.paused = not self.paused
    
    def hold_piece(self) -> bool:
        """Hold current piece and swap with held piece"""
        if not self.can_hold or not self.current_piece or self.paused or self.game_over:
            return False
            
        if self.held_piece is None:
            # First hold - store current piece and spawn new one
            self.held_piece = Piece()
            self.held_piece.type = self.current_piece.type
            self.held_piece.color = self.current_piece.color
            self.held_piece.rotation = 0
            self.held_piece.x = 3
            self.held_piece.y = 0
            self.spawn_piece()
        else:
            # Swap current and held pieces
            temp_type: int = self.current_piece.type
            temp_color: int = self.current_piece.color
            
            self.current_piece.type = self.held_piece.type
            self.current_piece.color = self.held_piece.color
            self.current_piece.rotation = 0
            self.current_piece.x = 3
            self.current_piece.y = 0
            
            self.held_piece.type = temp_type
            self.held_piece.color = temp_color
            self.held_piece.rotation = 0
            
            # Check if swapped piece can be placed
            if self.is_collision(self.current_piece):
                self.game_over = True
        
        self.can_hold = False
        return True
    
    def spawn_piece(self) -> None:
        """Spawn a new piece at the top of the board"""
        if self.next_piece is None:
            self.next_piece = Piece()
        
        self.current_piece = self.next_piece
        self.next_piece = Piece()
        self.can_hold = True  # Reset hold ability
        
        # Add pending garbage lines
        self.add_garbage_lines()
        
        # Check if game is over (piece can't be placed)
        if self.is_collision(self.current_piece):
            self.game_over = True
    
    def is_collision(self, piece: Piece) -> bool:
        """Check if piece collides with board boundaries or placed blocks"""
        for block_x, block_y in piece.get_blocks():
            # Check boundaries
            if (block_x < 0 or block_x >= self.width or 
                block_y >= self.height or
                (block_y >= 0 and self.grid[block_y][block_x] > 0)):
                return True
        return False
    
    def is_valid_move(self, piece: Piece, dx: int = 0, dy: int = 0) -> bool:
        """Check if moving piece by dx, dy is valid"""
        test_piece: Piece = piece.copy()
        test_piece.move(dx, dy)
        return not self.is_collision(test_piece)
    
    def is_valid_rotation(self, piece: Piece) -> bool:
        """Check if rotating piece is valid"""
        test_piece: Piece = piece.copy()
        test_piece.rotate_counterclockwise()
        return not self.is_collision(test_piece)
    
    def move_piece(self, dx: int, dy: int) -> bool:
        """Move current piece if valid"""
        if self.current_piece and not self.paused and not self.game_over and self.is_valid_move(self.current_piece, dx, dy):
            self.current_piece.move(dx, dy)
            return True
        return False
    
    def rotate_piece(self) -> bool:
        """Rotate current piece if valid"""
        if self.current_piece and not self.paused and not self.game_over and self.is_valid_rotation(self.current_piece):
            self.current_piece.rotate_counterclockwise()
            return True
        return False
    
    def drop_piece(self) -> bool:
        """Move piece down one row, lock if it can't move"""
        if not self.current_piece or self.paused or self.game_over:
            return False
            
        if self.is_valid_move(self.current_piece, 0, 1):
            self.current_piece.move(0, 1)
            return True
        else:
            self.lock_piece()
            return False
    
    def hard_drop(self) -> None:
        """Drop piece to the bottom instantly"""
        if not self.current_piece or self.paused or self.game_over:
            return
            
        drop_distance: int = 0
        while self.is_valid_move(self.current_piece, 0, 1):
            self.current_piece.move(0, 1)
            drop_distance += 1
        
        # Award points for hard drop (2 points per cell)
        self.score += drop_distance * 2
        self.lock_piece()
    
    def lock_piece(self) -> None:
        """Lock current piece to the board"""
        if not self.current_piece:
            return
            
        # Place piece on board
        for block_x, block_y in self.current_piece.get_blocks():
            if 0 <= block_y < self.height and 0 <= block_x < self.width:
                self.grid[block_y][block_x] = self.current_piece.color
        
        # Clear completed lines
        lines_cleared: int = self.clear_lines()
        
        # Update score and level
        if lines_cleared > 0:
            self.lines_cleared += lines_cleared
            # Enhanced scoring system based on modern Tetris guidelines
            line_scores: Dict[int, int] = {1: 100, 2: 300, 3: 500, 4: 800}
            base_score: int = line_scores.get(lines_cleared, lines_cleared * 100)
            self.score += base_score * self.level
            
            # Level progression: every 10 lines cleared
            new_level: int = min(15, (self.lines_cleared // 10) + 1)  # Cap at level 15
            if new_level > self.level:
                self.level = new_level
                
            # Send garbage in competitive mode (not implemented in single player)
            if hasattr(self, 'opponent') and self.opponent:
                self.send_garbage_to_opponent(lines_cleared, self.opponent)
        
        # Spawn next piece
        self.spawn_piece()
    
    def clear_lines(self) -> int:
        """Clear completed lines and return number cleared"""
        lines_to_clear: List[int] = []
        
        # Find completed lines
        for y in range(self.height):
            if all(self.grid[y][x] > 0 for x in range(self.width)):
                lines_to_clear.append(y)
        
        # Remove completed lines (process from bottom to top to maintain indices)
        for y in reversed(lines_to_clear):
            del self.grid[y]
        
        # Add new empty lines at the top
        for _ in range(len(lines_to_clear)):
            self.grid.insert(0, [0] * self.width)
        
        return len(lines_to_clear)
    
    def add_garbage_lines(self) -> None:
        """Add garbage lines from opponent"""
        while self.pending_garbage:
            # Add gray garbage line with one random hole
            hole_position: int = self.pending_garbage.pop(0)
            garbage_line: List[int] = [8] * self.width  # 8 = gray garbage color
            garbage_line[hole_position] = 0
            
            # Remove top line and add garbage at bottom
            if len(self.grid) > 0:
                self.grid.pop(0)
            self.grid.append(garbage_line)
    
    def send_garbage_to_opponent(self, lines_cleared: int, opponent_board: 'Board') -> None:
        """Send garbage lines to opponent based on lines cleared"""
        if lines_cleared <= 1:
            return  # No garbage for single lines
        
        garbage_count: int = lines_cleared - 1
        for _ in range(garbage_count):
            hole_position: int = __import__('random').randint(0, self.width - 1)
            opponent_board.pending_garbage.append(hole_position)
        
        self.lines_sent += garbage_count
    
    def get_drop_speed(self) -> int:
        """Get current drop speed based on level (returns frames between drops)"""
        # Modern Tetris speed curve - faster progression
        speed_table: Dict[int, int] = {
            1: 48, 2: 43, 3: 38, 4: 33, 5: 28, 6: 23, 7: 18, 8: 13, 9: 8, 10: 6,
            11: 5, 12: 4, 13: 3, 14: 2, 15: 1
        }
        return speed_table.get(self.level, 1)
    
    def get_ghost_piece(self) -> Optional[Piece]:
        """Get ghost piece position (where current piece would land)"""
        if not self.current_piece:
            return None
            
        ghost_piece: Piece = self.current_piece.copy()
        while self.is_valid_move(ghost_piece, 0, 1):
            ghost_piece.move(0, 1)
        
        return ghost_piece
    
    def get_held_piece_preview(self) -> Optional[Piece]:
        """Get held piece for preview display"""
        return self.held_piece
    
    def reset(self) -> None:
        """Reset board to initial state"""
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.current_piece = None
        self.next_piece = None
        self.held_piece = None
        self.can_hold = True
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.game_over = False
        self.paused = False
        self.lines_sent = 0
        self.pending_garbage = []
        self.spawn_piece()
    
    def get_stats(self) -> Dict[str, int]:
        """Get current game statistics"""
        return {
            'score': self.score,
            'level': self.level,
            'lines': self.lines_cleared,
            'lines_sent': self.lines_sent
        }