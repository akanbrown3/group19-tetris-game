import pygame
from typing import Tuple, Optional, Dict, List, Any, Union

# Type aliases for better readability
Color = Tuple[int, int, int]
ColorWithAlpha = Tuple[int, int, int, int]

# Modern color palette
COLORS: List[Color] = [
    (25, 25, 35),        # Dark background
    (255, 89, 94),       # Red
    (255, 202, 58),      # Yellow  
    (138, 201, 38),      # Green
    (25, 130, 196),      # Blue
    (106, 76, 147),      # Purple
    (255, 121, 63),      # Orange
    (240, 84, 122),      # Pink
    (100, 100, 100),     # Gray (for garbage)
]

# UI Colors
DARK_BG: Color = (15, 15, 25)
LIGHTER_BG: Color = (35, 35, 50)
BORDER_COLOR: Color = (60, 60, 80)
TEXT_PRIMARY: Color = (255, 255, 255)
TEXT_SECONDARY: Color = (180, 180, 200)
ACCENT_COLOR: Color = (100, 200, 255)
GRID_COLOR: Color = (45, 45, 65)
PAUSE_OVERLAY: ColorWithAlpha = (0, 0, 0, 128)

class TetrisRenderer:
    """Enhanced renderer supporting single and multiplayer modes"""
    
    def __init__(self, screen_width: int = 1000, screen_height: int = 700) -> None:
        """Initialize renderer with screen dimensions"""
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        
        # Single player layout
        self.single_board_x: int = 100
        self.single_board_y: int = 80
        self.single_panel_x: int = 450
        self.single_panel_width: int = 200
        
        # Multiplayer layout
        self.multi_board1_x: int = 50
        self.multi_board2_x: int = 550
        self.multi_board_y: int = 80
        self.multi_panel1_x: int = 350
        self.multi_panel2_x: int = 850
        self.multi_panel_width: int = 140
        
        # Block and board sizing
        self.block_size: int = 25
        self.board_width: int = 10 * self.block_size
        self.board_height: int = 20 * self.block_size
        
        # Initialize fonts
        self.fonts: Dict[str, pygame.font.Font] = {
            'title': pygame.font.Font(None, 36),
            'large': pygame.font.Font(None, 28),
            'medium': pygame.font.Font(None, 22),
            'small': pygame.font.Font(None, 18),
            'tiny': pygame.font.Font(None, 16)
        }
    
    def draw_rounded_rect(self, surface: pygame.Surface, color: Color, rect: pygame.Rect, radius: int = 10) -> None:
        """Draw a rounded rectangle"""
        pygame.draw.rect(surface, color, rect, border_radius=radius)
    
    def draw_block(self, surface: pygame.Surface, color: Color, x: int, y: int, size: Optional[int] = None, border_radius: int = 3) -> None:
        """Draw a tetris block with modern styling"""
        if size is None:
            size = self.block_size
            
        # Main block
        pygame.draw.rect(surface, color, [x, y, size-2, size-2], border_radius=border_radius)
        
        # Highlight effect
        highlight_color: Color = tuple(min(255, c + 30) for c in color)
        pygame.draw.rect(surface, highlight_color, [x, y, size-2, 4], border_radius=border_radius)
    
    def draw_board_background(self, surface: pygame.Surface, x: int, y: int, width: int, height: int) -> None:
        """Draw the game board background and grid"""
        # Board background
        board_rect: pygame.Rect = pygame.Rect(x - 10, y - 10, width + 20, height + 20)
        self.draw_rounded_rect(surface, LIGHTER_BG, board_rect, 8)
        pygame.draw.rect(surface, BORDER_COLOR, board_rect, 2, border_radius=8)
        
        # Grid lines
        for i in range(21):  # 20 rows + 1
            for j in range(11):  # 10 cols + 1
                if i < 20:
                    rect: pygame.Rect = pygame.Rect(x + self.block_size * j, y + self.block_size * i,
                                                   self.block_size, self.block_size)
                    pygame.draw.rect(surface, GRID_COLOR, rect, 1)
    
    def draw_placed_blocks(self, surface: pygame.Surface, board: Any, board_x: int, board_y: int) -> None:
        """Draw all placed blocks on the board"""
        for i in range(board.height):
            for j in range(board.width):
                if board.grid[i][j] > 0:
                    color: Color = COLORS[min(board.grid[i][j], len(COLORS)-1)]
                    self.draw_block(surface, color,
                                  board_x + self.block_size * j + 1,
                                  board_y + self.block_size * i + 1)
    
    def draw_piece(self, surface: pygame.Surface, piece: Any, board_x: int, board_y: int, alpha: int = 255) -> None:
        """Draw a piece on the board"""
        if not piece:
            return
            
        color: Color = COLORS[piece.color]
        
        for block_x, block_y in piece.get_blocks():
            if 0 <= block_x < 10 and 0 <= block_y < 20:
                x: int = board_x + self.block_size * block_x + 1
                y: int = board_y + self.block_size * block_y + 1
                
                if alpha < 255:
                    # Create surface for transparency
                    temp_surface: pygame.Surface = pygame.Surface((self.block_size-2, self.block_size-2))
                    temp_surface.set_alpha(alpha)
                    temp_surface.fill(color)
                    surface.blit(temp_surface, (x, y))
                else:
                    self.draw_block(surface, color, x, y)
    
    def draw_ghost_piece(self, surface: pygame.Surface, board: Any, board_x: int, board_y: int) -> None:
        """Draw ghost piece showing where current piece will land"""
        ghost_piece: Any = board.get_ghost_piece()
        if ghost_piece:
            for block_x, block_y in ghost_piece.get_blocks():
                if 0 <= block_x < 10 and 0 <= block_y < 20:
                    x: int = board_x + self.block_size * block_x + 2
                    y: int = board_y + self.block_size * block_y + 2
                    ghost_color: Color = tuple(c // 3 for c in COLORS[ghost_piece.color])
                    pygame.draw.rect(surface, ghost_color,
                                   [x, y, self.block_size - 4, self.block_size - 4],
                                   2, border_radius=2)
    
    def draw_piece_preview(self, surface: pygame.Surface, piece: Any, x: int, y: int, title: str, size: int = 16) -> None:
        """Draw a piece preview with title"""
        if not piece:
            return
            
        # Background panel
        panel_rect: pygame.Rect = pygame.Rect(x - 8, y - 8, 90, 80)
        self.draw_rounded_rect(surface, LIGHTER_BG, panel_rect, 6)
        pygame.draw.rect(surface, BORDER_COLOR, panel_rect, 2, border_radius=6)
        
        # Title
        text: pygame.Surface = self.fonts['small'].render(title, True, TEXT_SECONDARY)
        surface.blit(text, (x, y - 5))
        
        # Calculate piece bounds for centering
        shape: Any = piece.get_shape()
        min_x: int = 4
        min_y: int = 4
        max_x: int = -1
        max_y: int = -1
        
        for i in range(4):
            for j in range(4):
                if i * 4 + j in shape:
                    min_x = min(min_x, j)
                    max_x = max(max_x, j)
                    min_y = min(min_y, i)
                    max_y = max(max_y, i)
        
        if max_x >= 0:  # Valid piece
            piece_width: int = max_x - min_x + 1
            piece_height: int = max_y - min_y + 1
            
            # Center the piece
            offset_x: int = (4 * size - piece_width * size) // 2
            offset_y: int = (4 * size - piece_height * size) // 2
            
            # Draw piece
            for i in range(4):
                for j in range(4):
                    if i * 4 + j in shape:
                        block_x: int = x + 10 + offset_x + (j - min_x) * size
                        block_y: int = y + 15 + offset_y + (i - min_y) * size
                        self.draw_block(surface, COLORS[piece.color], block_x, block_y, size)
    
    def draw_stats_panel(self, surface: pygame.Surface, board: Any, x: int, y: int, width: int, player_name: str = "PLAYER") -> None:
        """Draw player statistics panel"""
        # Background
        panel_rect: pygame.Rect = pygame.Rect(x, y, width, 400)
        self.draw_rounded_rect(surface, LIGHTER_BG, panel_rect, 8)
        pygame.draw.rect(surface, BORDER_COLOR, panel_rect, 2, border_radius=8)
        
        # Player name
        player_text: pygame.Surface = self.fonts['medium'].render(player_name, True, ACCENT_COLOR)
        surface.blit(player_text, (x + 10, y + 10))
        
        current_y: int = y + 40
        
        # Score
        score_label: pygame.Surface = self.fonts['small'].render("SCORE", True, TEXT_SECONDARY)
        surface.blit(score_label, (x + 10, current_y))
        score_text: pygame.Surface = self.fonts['medium'].render(f"{board.score:,}", True, TEXT_PRIMARY)
        surface.blit(score_text, (x + 10, current_y + 18))
        current_y += 50
        
        # Level
        level_label: pygame.Surface = self.fonts['small'].render("LEVEL", True, TEXT_SECONDARY)
        surface.blit(level_label, (x + 10, current_y))
        level_text: pygame.Surface = self.fonts['medium'].render(str(board.level), True, TEXT_PRIMARY)
        surface.blit(level_text, (x + 10, current_y + 18))
        current_y += 50
        
        # Lines
        lines_label: pygame.Surface = self.fonts['small'].render("LINES", True, TEXT_SECONDARY)
        surface.blit(lines_label, (x + 10, current_y))
        lines_text: pygame.Surface = self.fonts['medium'].render(str(board.lines_cleared), True, TEXT_PRIMARY)
        surface.blit(lines_text, (x + 10, current_y + 18))
        current_y += 60
        
        # Next piece
        if board.next_piece:
            self.draw_piece_preview(surface, board.next_piece, x + 10, current_y, "NEXT")
        current_y += 90
        
        # Hold piece
        if board.held_piece:
            self.draw_piece_preview(surface, board.held_piece, x + 10, current_y, "HOLD")
        else:
            # Empty hold slot
            empty_rect: pygame.Rect = pygame.Rect(x + 2, current_y - 8, 90, 80)
            self.draw_rounded_rect(surface, LIGHTER_BG, empty_rect, 6)
            pygame.draw.rect(surface, BORDER_COLOR, empty_rect, 2, border_radius=6)
            text: pygame.Surface = self.fonts['small'].render("HOLD", True, TEXT_SECONDARY)
            surface.blit(text, (x + 10, current_y - 5))
    
    def draw_controls(self, surface: pygame.Surface, x: int, y: int, multiplayer: bool = False) -> None:
        """Draw control instructions"""
        controls_label: pygame.Surface = self.fonts['medium'].render("CONTROLS", True, TEXT_SECONDARY)
        surface.blit(controls_label, (x, y))
        
        current_y: int = y + 25
        
        if multiplayer:
            # Create two columns for multiplayer controls
            col1_x: int = x
            col2_x: int = x + 200
            
            # Player 1 controls (left column)
            p1_title: pygame.Surface = self.fonts['medium'].render("PLAYER 1:", True, TEXT_PRIMARY)
            surface.blit(p1_title, (col1_x, current_y))
            
            p1_controls: List[str] = [
                "↑ Rotate",
                "← → Move", 
                "↓ Soft Drop",
                "SPACE Hard Drop",
                "C Hold"
            ]
            
            control_y: int = current_y + 20
            for control in p1_controls:
                control_text: pygame.Surface = self.fonts['small'].render(control, True, TEXT_SECONDARY)
                surface.blit(control_text, (col1_x, control_y))
                control_y += 16
            
            # Player 2 controls (right column)
            p2_title: pygame.Surface = self.fonts['medium'].render("PLAYER 2:", True, TEXT_PRIMARY)
            surface.blit(p2_title, (col2_x, current_y))
            
            p2_controls: List[str] = [
                "W Rotate",
                "A D Move",
                "S Soft Drop", 
                "Q Hard Drop",
                "E Hold"
            ]
            
            control_y = current_y + 20
            for control in p2_controls:
                control_text: pygame.Surface = self.fonts['small'].render(control, True, TEXT_SECONDARY)
                surface.blit(control_text, (col2_x, control_y))
                control_y += 16
            
            # Common controls at the bottom
            common_y: int = control_y + 15
            common_text: pygame.Surface = self.fonts['small'].render("P Pause  |  ESC Menu", True, TEXT_SECONDARY)
            surface.blit(common_text, (col1_x, common_y))
            
        else:
            # Single player controls
            single_controls: List[str] = [
                "↑ Rotate",
                "← → Move",
                "↓ Soft Drop", 
                "SPACE Hard Drop",
                "C Hold Piece",
                "",
                "P Pause",
                "ESC Menu"
            ]
            
            for i, control in enumerate(single_controls):
                if control == "":
                    current_y += 10
                    continue
                font: pygame.font.Font = self.fonts['small'] if not control.endswith(":") else self.fonts['medium']
                color: Color = TEXT_PRIMARY if control.endswith(":") else TEXT_SECONDARY
                control_text: pygame.Surface = font.render(control, True, color)
                surface.blit(control_text, (x, current_y))
                current_y += 16
    
    def render_single_player(self, surface: pygame.Surface, board: Any) -> None:
        """Render single player mode"""
        # Clear screen with gradient
        for y in range(self.screen_height):
            intensity: int = int(15 + (y / self.screen_height) * 10)
            pygame.draw.line(surface, (intensity, intensity, intensity + 5), 
                           (0, y), (self.screen_width, y))
        
        # Draw board
        self.draw_board_background(surface, self.single_board_x, self.single_board_y, 
                                 self.board_width, self.board_height)
        self.draw_placed_blocks(surface, board, self.single_board_x, self.single_board_y)
        self.draw_ghost_piece(surface, board, self.single_board_x, self.single_board_y)
        self.draw_piece(surface, board.current_piece, self.single_board_x, self.single_board_y)
        
        # Draw UI panel
        self.draw_stats_panel(surface, board, self.single_panel_x, 50, self.single_panel_width)
        
        # Draw controls
        self.draw_controls(surface, self.single_panel_x + 10, 480)
        
        # Pause indicator
        if board.paused:
            pause_text: pygame.Surface = self.fonts['large'].render("PAUSED", True, (255, 255, 0))
            pause_rect: pygame.Rect = pause_text.get_rect(center=(self.single_board_x + self.board_width//2, 
                                                                 self.single_board_y + self.board_height//2))
            surface.blit(pause_text, pause_rect)
    
    def render_multiplayer(self, surface: pygame.Surface, board1: Any, board2: Any) -> None:
        """Render multiplayer mode"""
        # Clear screen with gradient
        for y in range(self.screen_height):
            intensity: int = int(15 + (y / self.screen_height) * 10)
            pygame.draw.line(surface, (intensity, intensity, intensity + 5), 
                           (0, y), (self.screen_width, y))
        
        # Draw Player 1 board
        self.draw_board_background(surface, self.multi_board1_x, self.multi_board_y, 
                                 self.board_width, self.board_height)
        self.draw_placed_blocks(surface, board1, self.multi_board1_x, self.multi_board_y)
        self.draw_ghost_piece(surface, board1, self.multi_board1_x, self.multi_board_y)
        self.draw_piece(surface, board1.current_piece, self.multi_board1_x, self.multi_board_y)
        
        # Draw Player 2 board
        self.draw_board_background(surface, self.multi_board2_x, self.multi_board_y, 
                                 self.board_width, self.board_height)
        self.draw_placed_blocks(surface, board2, self.multi_board2_x, self.multi_board_y)
        self.draw_ghost_piece(surface, board2, self.multi_board2_x, self.multi_board_y)
        self.draw_piece(surface, board2.current_piece, self.multi_board2_x, self.multi_board_y)
        
        # Draw UI panels
        self.draw_stats_panel(surface, board1, self.multi_panel1_x, 50, self.multi_panel_width, "PLAYER 1")
        self.draw_stats_panel(surface, board2, self.multi_panel2_x, 50, self.multi_panel_width, "PLAYER 2")
        
        # Draw controls - positioned at the bottom center
        self.draw_controls(surface, 300, 580, multiplayer=True)
        
        # Game over indicators
        if board1.game_over:
            overlay: pygame.Surface = pygame.Surface((self.board_width, self.board_height))
            overlay.set_alpha(128)
            overlay.fill((255, 0, 0))
            surface.blit(overlay, (self.multi_board1_x, self.multi_board_y))
            
            game_over_text: pygame.Surface = self.fonts['large'].render("GAME", True, (255, 255, 255))
            over_text: pygame.Surface = self.fonts['large'].render("OVER", True, (255, 255, 255))
            surface.blit(game_over_text, (self.multi_board1_x + 50, self.multi_board_y + 200))
            surface.blit(over_text, (self.multi_board1_x + 50, self.multi_board_y + 230))
        
        if board2.game_over:
            overlay: pygame.Surface = pygame.Surface((self.board_width, self.board_height))
            overlay.set_alpha(128)
            overlay.fill((255, 0, 0))
            surface.blit(overlay, (self.multi_board2_x, self.multi_board_y))
            
            game_over_text: pygame.Surface = self.fonts['large'].render("GAME", True, (255, 255, 255))
            over_text: pygame.Surface = self.fonts['large'].render("OVER", True, (255, 255, 255))
            surface.blit(game_over_text, (self.multi_board2_x + 50, self.multi_board_y + 200))
            surface.blit(over_text, (self.multi_board2_x + 50, self.multi_board_y + 230))
        
        # Pause indicators
        if board1.paused:
            pause_text: pygame.Surface = self.fonts['medium'].render("PAUSED", True, (255, 255, 0))
            surface.blit(pause_text, (self.multi_board1_x + 30, self.multi_board_y + 250))
        
        if board2.paused:
            pause_text: pygame.Surface = self.fonts['medium'].render("PAUSED", True, (255, 255, 0))
            surface.blit(pause_text, (self.multi_board2_x + 30, self.multi_board_y + 250))