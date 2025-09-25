import pygame
import os
import sys
from enum import Enum
from typing import Dict, List, Tuple, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.board import Board
from src.ui import TetrisRenderer

class GameState(Enum):
    MENU = "menu"
    SINGLE_PLAYER = "single"
    MULTIPLAYER = "multiplayer"
    PAUSED = "paused"
    GAME_OVER = "game_over"

class MenuButton:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 color: Tuple[int, int, int] = (100, 200, 255), 
                 hover_color: Tuple[int, int, int] = (120, 220, 255)) -> None:
        self.rect: pygame.Rect = pygame.Rect(x, y, width, height)
        self.text: str = text
        self.color: Tuple[int, int, int] = color
        self.hover_color: Tuple[int, int, int] = hover_color
        self.is_hovered: bool = False
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        color: Tuple[int, int, int] = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 3, border_radius=10)
        
        text_surf: pygame.Surface = font.render(self.text, True, (255, 255, 255))
        text_rect: pygame.Rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

class TetrisGame:
    """Professional Tetris game with single and multiplayer modes"""
    
    def __init__(self, width: int = 1000, height: int = 700) -> None:
        """Initialize the game"""
        pygame.init()
        
        # Set up display
        self.width: int = width
        self.height: int = height
        self.screen: pygame.Surface = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Tetris Pro - Competitive Puzzle Game")
        
        # Game state
        self.state: GameState = GameState.MENU
        self.previous_game_mode: Optional[GameState] = None  # Track the last played game mode
        self.running: bool = True
        
        # Initialize game components
        self.board1: Board = Board(player_id=1)  # Player 1
        self.board2: Board = Board(player_id=2)  # Player 2 (for multiplayer)
        self.renderer: TetrisRenderer = TetrisRenderer(width, height)
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.fps: int = 60
        
        # Game timing
        self.drop_time1: int = 0
        self.drop_time2: int = 0
        
        # Input state for both players
        self.keys_pressed: Dict[str, bool] = {
            'p1_down': False, 'p1_left': False, 'p1_right': False,
            'p2_down': False, 'p2_left': False, 'p2_right': False
        }
        self.key_repeat_timers: Dict[str, int] = {
            'p1_left': 0, 'p1_right': 0,
            'p2_left': 0, 'p2_right': 0
        }
        self.key_repeat_delay: int = 150
        self.key_repeat_rate: int = 50
        
        # Menu setup
        self.setup_menu()
        
        # Fonts
        self.title_font: pygame.font.Font = pygame.font.Font(None, 72)
        self.button_font: pygame.font.Font = pygame.font.Font(None, 36)
        self.small_font: pygame.font.Font = pygame.font.Font(None, 24)
        
    def setup_menu(self) -> None:
        """Setup menu buttons"""
        button_width: int = 300
        button_height: int = 60
        button_x: int = (self.width - button_width) // 2
        start_y: int = 300
        spacing: int = 80
        
        self.menu_buttons: List[MenuButton] = [
            MenuButton(button_x, start_y, button_width, button_height, "Single Player"),
            MenuButton(button_x, start_y + spacing, button_width, button_height, "Multiplayer"),
            MenuButton(button_x, start_y + spacing * 2, button_width, button_height, "Quit Game")
        ]
        
        # Pause menu buttons
        self.pause_buttons: List[MenuButton] = [
            MenuButton(button_x, start_y, button_width, button_height, "Resume"),
            MenuButton(button_x, start_y + spacing, button_width, button_height, "Restart"),
            MenuButton(button_x, start_y + spacing * 2, button_width, button_height, "Main Menu")
        ]
        
        # Game over buttons
        self.game_over_buttons: List[MenuButton] = [
            MenuButton(button_x, start_y + spacing, button_width, button_height, "Play Again"),
            MenuButton(button_x, start_y + spacing * 2, button_width, button_height, "Main Menu")
        ]
    
    def handle_menu_input(self) -> bool:
        """Handle menu input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Handle button clicks
            for i, button in enumerate(self.menu_buttons):
                if button.handle_event(event):
                    if i == 0:  # Single Player
                        self.start_single_player()
                    elif i == 1:  # Multiplayer
                        self.start_multiplayer()
                    elif i == 2:  # Quit
                        return False
        return True
    
    def handle_pause_input(self) -> bool:
        """Handle pause menu input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                    if self.previous_game_mode == GameState.MULTIPLAYER:
                        self.state = GameState.MULTIPLAYER
                    else:
                        self.state = GameState.SINGLE_PLAYER
                    self.board1.toggle_pause()
                    if self.previous_game_mode == GameState.MULTIPLAYER:
                        self.board2.toggle_pause()
            
            # Handle button clicks
            for i, button in enumerate(self.pause_buttons):
                if button.handle_event(event):
                    if i == 0:  # Resume
                        if self.previous_game_mode == GameState.MULTIPLAYER:
                            self.state = GameState.MULTIPLAYER
                        else:
                            self.state = GameState.SINGLE_PLAYER
                        self.board1.toggle_pause()
                        if self.previous_game_mode == GameState.MULTIPLAYER:
                            self.board2.toggle_pause()
                    elif i == 1:  # Restart
                        self.restart_game()
                    elif i == 2:  # Main Menu
                        self.state = GameState.MENU
        return True
    
    def handle_game_over_input(self) -> bool:
        """Handle game over input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Handle button clicks
            for i, button in enumerate(self.game_over_buttons):
                if button.handle_event(event):
                    if i == 0:  # Play Again
                        self.restart_game()
                    elif i == 1:  # Main Menu
                        self.state = GameState.MENU
        return True
    
    def handle_single_player_input(self) -> bool:
        """Handle single player input"""
        current_time: int = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = GameState.MENU
                elif event.key == pygame.K_p:
                    self.state = GameState.PAUSED
                    self.board1.toggle_pause()
                elif event.key == pygame.K_UP:
                    self.board1.rotate_piece()
                elif event.key == pygame.K_SPACE:
                    self.board1.hard_drop()
                elif event.key == pygame.K_c:  # Hold piece
                    self.board1.hold_piece()
                elif event.key == pygame.K_DOWN:
                    self.keys_pressed['p1_down'] = True
                elif event.key == pygame.K_LEFT:
                    self.keys_pressed['p1_left'] = True
                    self.key_repeat_timers['p1_left'] = current_time + self.key_repeat_delay
                    self.board1.move_piece(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    self.keys_pressed['p1_right'] = True
                    self.key_repeat_timers['p1_right'] = current_time + self.key_repeat_delay
                    self.board1.move_piece(1, 0)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    self.keys_pressed['p1_down'] = False
                elif event.key == pygame.K_LEFT:
                    self.keys_pressed['p1_left'] = False
                elif event.key == pygame.K_RIGHT:
                    self.keys_pressed['p1_right'] = False
        
        # Handle held keys
        if not self.board1.game_over and not self.board1.paused:
            for direction in ['p1_left', 'p1_right']:
                if (self.keys_pressed[direction] and 
                    current_time >= self.key_repeat_timers[direction]):
                    dx: int = -1 if 'left' in direction else 1
                    self.board1.move_piece(dx, 0)
                    self.key_repeat_timers[direction] = current_time + self.key_repeat_rate
        
        return True
    
    def handle_multiplayer_input(self) -> bool:
        """Handle multiplayer input"""
        current_time: int = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = GameState.MENU
                elif event.key == pygame.K_p:
                    self.state = GameState.PAUSED
                    self.board1.toggle_pause()
                    self.board2.toggle_pause()
                
                # Player 1 controls (Arrow keys)
                elif event.key == pygame.K_UP:
                    self.board1.rotate_piece()
                elif event.key == pygame.K_SPACE:
                    self.board1.hard_drop()
                elif event.key == pygame.K_c:  # Fixed: Use C for Player 1 hold in multiplayer
                    self.board1.hold_piece()
                elif event.key == pygame.K_DOWN:
                    self.keys_pressed['p1_down'] = True
                elif event.key == pygame.K_LEFT:
                    self.keys_pressed['p1_left'] = True
                    self.key_repeat_timers['p1_left'] = current_time + self.key_repeat_delay
                    self.board1.move_piece(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    self.keys_pressed['p1_right'] = True
                    self.key_repeat_timers['p1_right'] = current_time + self.key_repeat_delay
                    self.board1.move_piece(1, 0)
                
                # Player 2 controls (WASD)
                elif event.key == pygame.K_w:
                    self.board2.rotate_piece()
                elif event.key == pygame.K_q:  # Q for hard drop
                    self.board2.hard_drop()
                elif event.key == pygame.K_e:  # Fixed: Use E for Player 2 hold
                    self.board2.hold_piece()
                elif event.key == pygame.K_s:
                    self.keys_pressed['p2_down'] = True
                elif event.key == pygame.K_a:
                    self.keys_pressed['p2_left'] = True
                    self.key_repeat_timers['p2_left'] = current_time + self.key_repeat_delay
                    self.board2.move_piece(-1, 0)
                elif event.key == pygame.K_d:
                    self.keys_pressed['p2_right'] = True
                    self.key_repeat_timers['p2_right'] = current_time + self.key_repeat_delay
                    self.board2.move_piece(1, 0)
                    
            elif event.type == pygame.KEYUP:
                # Player 1
                if event.key == pygame.K_DOWN:
                    self.keys_pressed['p1_down'] = False
                elif event.key == pygame.K_LEFT:
                    self.keys_pressed['p1_left'] = False
                elif event.key == pygame.K_RIGHT:
                    self.keys_pressed['p1_right'] = False
                # Player 2
                elif event.key == pygame.K_s:
                    self.keys_pressed['p2_down'] = False
                elif event.key == pygame.K_a:
                    self.keys_pressed['p2_left'] = False
                elif event.key == pygame.K_d:
                    self.keys_pressed['p2_right'] = False
        
        # Handle held keys for both players
        if not self.board1.game_over and not self.board1.paused:
            for direction in ['p1_left', 'p1_right']:
                if (self.keys_pressed[direction] and 
                    current_time >= self.key_repeat_timers[direction]):
                    dx: int = -1 if 'left' in direction else 1
                    self.board1.move_piece(dx, 0)
                    self.key_repeat_timers[direction] = current_time + self.key_repeat_rate
        
        if not self.board2.game_over and not self.board2.paused:
            for direction in ['p2_left', 'p2_right']:
                if (self.keys_pressed[direction] and 
                    current_time >= self.key_repeat_timers[direction]):
                    dx: int = -1 if 'left' in direction else 1
                    self.board2.move_piece(dx, 0)
                    self.key_repeat_timers[direction] = current_time + self.key_repeat_rate
        
        return True
    
    def update_single_player(self) -> None:
        """Update single player game logic"""
        if self.board1.game_over:
            self.state = GameState.GAME_OVER
            return
            
        if not self.board1.paused:
            current_time: int = pygame.time.get_ticks()
            drop_speed: int = self.board1.get_drop_speed() * 10  # Convert to milliseconds
            
            if self.keys_pressed['p1_down']:
                drop_speed = min(drop_speed, 50)
            
            if current_time - self.drop_time1 >= drop_speed:
                self.board1.drop_piece()
                self.drop_time1 = current_time
    
    def update_multiplayer(self) -> None:
        """Update multiplayer game logic"""
        current_time: int = pygame.time.get_ticks()
        
        # Update player 1
        if not self.board1.game_over and not self.board1.paused:
            drop_speed1: int = self.board1.get_drop_speed() * 10
            if self.keys_pressed['p1_down']:
                drop_speed1 = min(drop_speed1, 50)
            
            if current_time - self.drop_time1 >= drop_speed1:
                self.board1.drop_piece()
                self.drop_time1 = current_time
        
        # Update player 2
        if not self.board2.game_over and not self.board2.paused:
            drop_speed2: int = self.board2.get_drop_speed() * 10
            if self.keys_pressed['p2_down']:
                drop_speed2 = min(drop_speed2, 50)
            
            if current_time - self.drop_time2 >= drop_speed2:
                self.board2.drop_piece()
                self.drop_time2 = current_time
        
        # Check for game over
        if self.board1.game_over or self.board2.game_over:
            self.state = GameState.GAME_OVER
    
    def start_single_player(self) -> None:
        """Start single player mode"""
        self.state = GameState.SINGLE_PLAYER
        self.previous_game_mode = GameState.SINGLE_PLAYER  # Track the game mode
        self.board1.reset()
        self.drop_time1 = 0
        self.keys_pressed = {key: False for key in self.keys_pressed}
    
    def start_multiplayer(self) -> None:
        """Start multiplayer mode"""
        self.state = GameState.MULTIPLAYER
        self.previous_game_mode = GameState.MULTIPLAYER  # Track the game mode
        self.board1.reset()
        self.board2.reset()
        self.drop_time1 = 0
        self.drop_time2 = 0
        self.keys_pressed = {key: False for key in self.keys_pressed}
    
    def restart_game(self) -> None:
        """Restart current game mode"""
        # Fixed: Use previous_game_mode to determine what to restart
        if self.previous_game_mode == GameState.MULTIPLAYER:
            self.start_multiplayer()
        else:
            self.start_single_player()
    
    def draw_menu(self) -> None:
        """Draw main menu"""
        # Background gradient
        for y in range(self.height):
            color_intensity: int = int(15 + (y / self.height) * 20)
            pygame.draw.line(self.screen, (color_intensity, color_intensity, color_intensity + 10), 
                           (0, y), (self.width, y))
        
        # Title
        title_text: pygame.Surface = self.title_font.render("TETRIS GAME", True, (100, 200, 255))
        title_rect: pygame.Rect = title_text.get_rect(center=(self.width // 2, 150))
        self.screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text: pygame.Surface = self.small_font.render("Competitive Block Puzzle Game", True, (180, 180, 200))
        subtitle_rect: pygame.Rect = subtitle_text.get_rect(center=(self.width // 2, 200))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Draw buttons
        for button in self.menu_buttons:
            button.draw(self.screen, self.button_font)
    
    def draw_pause_menu(self) -> None:
        """Draw pause overlay"""
        # Semi-transparent overlay
        overlay: pygame.Surface = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Pause text
        pause_text: pygame.Surface = self.title_font.render("PAUSED", True, (255, 255, 255))
        pause_rect: pygame.Rect = pause_text.get_rect(center=(self.width // 2, 200))
        self.screen.blit(pause_text, pause_rect)
        
        # Draw buttons
        for button in self.pause_buttons:
            button.draw(self.screen, self.button_font)
    
    def draw_game_over_screen(self) -> None:
        """Draw game over screen"""
        # Semi-transparent overlay
        overlay: pygame.Surface = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_text: pygame.Surface = self.title_font.render("GAME OVER", True, (255, 89, 94))
        game_over_rect: pygame.Rect = game_over_text.get_rect(center=(self.width // 2, 120))
        self.screen.blit(game_over_text, game_over_rect)
        
        current_y: int = 170
        
        # Score display
        if self.previous_game_mode == GameState.MULTIPLAYER:
            # Winner announcement
            winner_text: pygame.Surface
            if self.board1.game_over and not self.board2.game_over:
                winner_text = self.button_font.render("Player 2 Wins!", True, (138, 201, 38))
            elif self.board2.game_over and not self.board1.game_over:
                winner_text = self.button_font.render("Player 1 Wins!", True, (138, 201, 38))
            else:
                winner_text = self.button_font.render("It's a Tie!", True, (255, 202, 58))
            winner_rect: pygame.Rect = winner_text.get_rect(center=(self.width // 2, current_y))
            self.screen.blit(winner_text, winner_rect)
            current_y += 40
            
            # Player 1 final scores
            p1_score_text: pygame.Surface = self.small_font.render(f"Player 1 - Score: {self.board1.score:,} | Level: {self.board1.level} | Lines: {self.board1.lines_cleared}", True, (255, 255, 255))
            p1_score_rect: pygame.Rect = p1_score_text.get_rect(center=(self.width // 2, current_y))
            self.screen.blit(p1_score_text, p1_score_rect)
            current_y += 25
            
            # Player 2 final scores  
            p2_score_text: pygame.Surface = self.small_font.render(f"Player 2 - Score: {self.board2.score:,} | Level: {self.board2.level} | Lines: {self.board2.lines_cleared}", True, (255, 255, 255))
            p2_score_rect: pygame.Rect = p2_score_text.get_rect(center=(self.width // 2, current_y))
            self.screen.blit(p2_score_text, p2_score_rect)
            
        else:
            # Single player final scores
            final_score_text: pygame.Surface = self.button_font.render(f"Final Score: {self.board1.score:,}", True, (255, 255, 255))
            score_rect: pygame.Rect = final_score_text.get_rect(center=(self.width // 2, current_y))
            self.screen.blit(final_score_text, score_rect)
            current_y += 35
            
            # Additional stats
            level_text: pygame.Surface = self.small_font.render(f"Level Reached: {self.board1.level}", True, (180, 180, 200))
            level_rect: pygame.Rect = level_text.get_rect(center=(self.width // 2, current_y))
            self.screen.blit(level_text, level_rect)
            current_y += 20
            
            lines_text: pygame.Surface = self.small_font.render(f"Lines Cleared: {self.board1.lines_cleared}", True, (180, 180, 200))
            lines_rect: pygame.Rect = lines_text.get_rect(center=(self.width // 2, current_y))
            self.screen.blit(lines_text, lines_rect)
        
        # Draw buttons
        for button in self.game_over_buttons:
            button.draw(self.screen, self.button_font)
    
    def run(self) -> None:
        """Main game loop"""
        while self.running:
            # Handle input based on current state
            if self.state == GameState.MENU:
                self.running = self.handle_menu_input()
            elif self.state == GameState.PAUSED:
                self.running = self.handle_pause_input()
            elif self.state == GameState.GAME_OVER:
                self.running = self.handle_game_over_input()
            elif self.state == GameState.SINGLE_PLAYER:
                self.running = self.handle_single_player_input()
                self.update_single_player()
            elif self.state == GameState.MULTIPLAYER:
                self.running = self.handle_multiplayer_input()
                self.update_multiplayer()
            
            # Render based on current state
            if self.state == GameState.MENU:
                self.draw_menu()
            elif self.state == GameState.SINGLE_PLAYER:
                self.renderer.render_single_player(self.screen, self.board1)
            elif self.state == GameState.MULTIPLAYER:
                self.renderer.render_multiplayer(self.screen, self.board1, self.board2)
            elif self.state == GameState.PAUSED:
                if self.previous_game_mode == GameState.MULTIPLAYER:
                    self.renderer.render_multiplayer(self.screen, self.board1, self.board2)
                else:
                    self.renderer.render_single_player(self.screen, self.board1)
                self.draw_pause_menu()
            elif self.state == GameState.GAME_OVER:
                if self.previous_game_mode == GameState.MULTIPLAYER:
                    self.renderer.render_multiplayer(self.screen, self.board1, self.board2)
                else:
                    self.renderer.render_single_player(self.screen, self.board1)
                self.draw_game_over_screen()
            
            pygame.display.flip()
            self.clock.tick(self.fps)
        
        pygame.quit()
        sys.exit()

def main() -> None:
    """Entry point of the game"""
    game: TetrisGame = TetrisGame()
    game.run()

if __name__ == "__main__":
    main()