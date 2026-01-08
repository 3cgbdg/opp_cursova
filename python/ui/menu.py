import pygame
import os
from typing import Optional, Tuple


WINDOW_SIZE = 720
BG_COLOR = (22, 24, 27)
MENU_COLOR = (40, 44, 52)
TEXT_COLOR = (255, 255, 255)
SELECTED_COLOR = (100, 149, 237)
BUTTON_HEIGHT = 60
BUTTON_SPACING = 20


class MenuUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("Reversi - Menu")
        
        self.font = pygame.font.SysFont("segoeui", 48, bold=True)
        self.button_font = pygame.font.SysFont("segoeui", 32)
        
        self.selected_option = 0
        
        # Game settings
        self.game_mode = "pvc"  # "pvp" or "pvc"
        self.difficulty = 3     # AI search depth (1, 3, 5)
        
        # Audio settings
        self.music_enabled = True
        self.music_playing = False
        self.volume = 0.7  # Volume from 0.0 to 1.0
        self.dragging_volume = False
        self.volume_slider_rect = None
        
        # Load music
        self.music_path = self._find_music_file()
        if self.music_path:
            pygame.mixer.music.load(self.music_path)
            pygame.mixer.music.set_volume(self.volume)
        
    def _find_music_file(self) -> Optional[str]:
        """Searches for the Rocky Balboa music file for the game"""
        # Possible Rocky Balboa file names
        possible_names = [
            "gonna_fly_now.mp3",
            "rocky_theme.mp3",
            "rocky.mp3",
            "rocky_balboa.mp3",
            "theme.mp3"
        ]
        
        # Search in python directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        music_dir = os.path.join(base_dir, "music")
        
        # Create directory if not exists
        if not os.path.exists(music_dir):
            os.makedirs(music_dir, exist_ok=True)
        
        # Search for files
        for name in possible_names:
            path = os.path.join(music_dir, name)
            if os.path.exists(path):
                return path
        
        # Also search in the project root directory
        project_root = os.path.dirname(os.path.dirname(base_dir))
        for name in possible_names:
            path = os.path.join(project_root, name)
            if os.path.exists(path):
                return path
        
        return None
    
    def _toggle_music(self):
        """Toggles music on/off"""
        self.music_enabled = not self.music_enabled
        
        if self.music_enabled and self.music_path:
            if not self.music_playing:
                pygame.mixer.music.set_volume(self.volume)
                pygame.mixer.music.play(-1)  # -1 = loop
                self.music_playing = True
        else:
            pygame.mixer.music.stop()
            self.music_playing = False
    
    def _update_volume(self, new_volume: float):
        """Updates the music volume"""
        self.volume = max(0.0, min(1.0, new_volume))
        pygame.mixer.music.set_volume(self.volume)
    
    def _start_music(self):
        """Starts the music if enabled"""
        if self.music_enabled and self.music_path and not self.music_playing:
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play(-1)
            self.music_playing = True
    
    def run(self) -> Tuple[bool, bool, float]:
        """
        Runs the menu
        Returns: (should_start_game, music_enabled, volume, game_mode, difficulty)
        """
        clock = pygame.time.Clock()
        running = True
        start_game = False
        
        num_options = 6  # Start, Mode, Difficulty, Music, Volume, Exit
        
        # Start music if enabled
        self._start_music()
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected_option = (self.selected_option - 1) % num_options
                        self.dragging_volume = False
                    elif event.key == pygame.K_DOWN:
                        self.selected_option = (self.selected_option + 1) % num_options
                        self.dragging_volume = False
                    elif event.key == pygame.K_LEFT:
                        if self.selected_option == 2:  # Difficulty
                            # 1 -> 5 -> 3 -> 1
                            if self.difficulty == 1: self.difficulty = 5
                            elif self.difficulty == 5: self.difficulty = 3
                            else: self.difficulty = 1
                        elif self.selected_option == 4:  # Volume
                            self._update_volume(self.volume - 0.1)
                        elif self.selected_option == 1: # Mode
                            self.game_mode = "pvp" if self.game_mode == "pvc" else "pvc"

                    elif event.key == pygame.K_RIGHT:
                        if self.selected_option == 2:  # Difficulty
                            # 1 -> 3 -> 5 -> 1
                            if self.difficulty == 1: self.difficulty = 3
                            elif self.difficulty == 3: self.difficulty = 5
                            else: self.difficulty = 1
                        elif self.selected_option == 4:  # Volume
                            self._update_volume(self.volume + 0.1)
                        elif self.selected_option == 1: # Mode
                            self.game_mode = "pvp" if self.game_mode == "pvc" else "pvc"

                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        if self.selected_option == 0:  # Start
                            start_game = True
                            running = False
                        elif self.selected_option == 1: # Mode
                             self.game_mode = "pvp" if self.game_mode == "pvc" else "pvc"
                        elif self.selected_option == 2: # Difficulty
                             if self.difficulty == 1: self.difficulty = 3
                             elif self.difficulty == 3: self.difficulty = 5
                             else: self.difficulty = 1
                        elif self.selected_option == 3:  # Music
                            self._toggle_music()
                        elif self.selected_option == 4: # Volume
                            pass
                        elif self.selected_option == 5:  # Exit
                            running = False
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging_volume and self.volume_slider_rect:
                        # Update volume during dragging
                        mouse_x = event.pos[0]
                        slider_x = self.volume_slider_rect.x
                        slider_width = self.volume_slider_rect.width
                        rel_x = max(0, min(slider_width, mouse_x - slider_x))
                        new_volume = rel_x / slider_width
                        self._update_volume(new_volume)
                    else:
                        # Determine which button the mouse is over
                        x, y = event.pos
                        BUTTON_WIDTH = 450
                        button_y_start = WINDOW_SIZE // 2 - 140
                        button_x_start = WINDOW_SIZE // 2 - BUTTON_WIDTH // 2
                        for i in range(num_options):
                            button_y = button_y_start + i * (BUTTON_HEIGHT + BUTTON_SPACING)
                            if (button_y <= y <= button_y + BUTTON_HEIGHT) and \
                               (button_x_start <= x <= button_x_start + BUTTON_WIDTH):
                                self.selected_option = i
                                break
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.volume_slider_rect and self.volume_slider_rect.collidepoint(event.pos):
                        # Started dragging the slider
                        self.dragging_volume = True
                        mouse_x = event.pos[0]
                        slider_x = self.volume_slider_rect.x
                        slider_width = self.volume_slider_rect.width
                        rel_x = max(0, min(slider_width, mouse_x - slider_x))
                        new_volume = rel_x / slider_width
                        self._update_volume(new_volume)
                    else:
                        x, y = event.pos
                        BUTTON_WIDTH = 450
                        button_y_start = WINDOW_SIZE // 2 - 140
                        button_x_start = WINDOW_SIZE // 2 - BUTTON_WIDTH // 2
                        for i in range(num_options):
                            button_y = button_y_start + i * (BUTTON_HEIGHT + BUTTON_SPACING)
                            if (button_y <= y <= button_y + BUTTON_HEIGHT) and \
                               (button_x_start <= x <= button_x_start + BUTTON_WIDTH):
                                if i == 0:  # Start
                                    start_game = True
                                    running = False
                                elif i == 1: # Mode
                                    self.game_mode = "pvp" if self.game_mode == "pvc" else "pvc"
                                elif i == 2: # Difficulty
                                    if self.difficulty == 1: self.difficulty = 3
                                    elif self.difficulty == 3: self.difficulty = 5
                                    else: self.difficulty = 1
                                elif i == 3:  # Music
                                    self._toggle_music()
                                elif i == 5:  # Exit
                                    running = False
                                break
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.dragging_volume = False
            
            self._draw()
            pygame.display.flip()
            clock.tick(60)
        
        # Music stays on when entering the game
        # Stop only when exiting the application
        if not start_game:
            pygame.mixer.music.stop()
        
        return start_game, self.music_enabled, self.volume, self.game_mode, self.difficulty
    
    def _draw(self):
        """Draws the menu"""
        self.screen.fill(BG_COLOR)
        
        # Title
        title = self.font.render("REVERSI", True, TEXT_COLOR)
        title_rect = title.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 4 - 40))
        self.screen.blit(title, title_rect)
        
        # Hints (now at the top)
        hint_font = pygame.font.SysFont("segoeui", 18)
        hints = [
            "Use ↑↓ arrows or mouse for navigation",
            "Enter or click to select, ←→ for volume"
        ]
        
        for i, hint in enumerate(hints):
            hint_text = hint_font.render(hint, True, (160, 160, 160))
            hint_rect = hint_text.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 4 + 25 + i * 25))
            self.screen.blit(hint_text, hint_rect)
        
        # Menu Buttons
        button_y_start = WINDOW_SIZE // 2 - 140
        
        diff_text = "Easy" if self.difficulty == 1 else ("Medium" if self.difficulty == 3 else "Hard")
        mode_text = "Player vs AI" if self.game_mode == 'pvc' else "Player vs Player"
        
        options = [
            "START",
            f"Mode: {mode_text}",
            f"AI Difficulty: {diff_text}",
            f"Music: {'On' if self.music_enabled else 'Off'}",
            "Volume:",
            "EXIT"
        ]
        
        BUTTON_WIDTH = 450
        SLIDER_WIDTH = 180
        SLIDER_HEIGHT = 12
        
        for i, option_text in enumerate(options):
            button_y = button_y_start + i * (BUTTON_HEIGHT + BUTTON_SPACING)
            is_selected = (i == self.selected_option)
            
            # Button and text color
            bg_color = SELECTED_COLOR if is_selected else MENU_COLOR
            border_color = (255, 255, 255) if is_selected else (80, 85, 95)
            
            # Draw button with rounded corners
            button_rect = pygame.Rect(
                WINDOW_SIZE // 2 - BUTTON_WIDTH // 2,
                button_y,
                BUTTON_WIDTH,
                BUTTON_HEIGHT
            )
            
            # Shadow effect for selected button
            if is_selected:
                shadow_rect = button_rect.copy()
                shadow_rect.inflate_ip(4, 4)
                pygame.draw.rect(self.screen, (60, 100, 200), shadow_rect, border_radius=15)

            pygame.draw.rect(self.screen, bg_color, button_rect, border_radius=12)
            pygame.draw.rect(self.screen, border_color, button_rect, 2, border_radius=12)
            
            if i == 4:  # Volume - draw slider
                # Text (left)
                text = self.button_font.render(f"Volume: {int(self.volume * 100)}%", True, TEXT_COLOR)
                text_rect = text.get_rect(left=button_rect.left + 25, centery=button_rect.centery)
                self.screen.blit(text, text_rect)
                
                # Slider (right)
                slider_x = button_rect.right - SLIDER_WIDTH - 25
                slider_y = button_rect.centery - SLIDER_HEIGHT // 2
                slider_rect = pygame.Rect(slider_x, slider_y, SLIDER_WIDTH, SLIDER_HEIGHT)
                self.volume_slider_rect = slider_rect
                
                # Slider background
                pygame.draw.rect(self.screen, (30, 33, 39), slider_rect, border_radius=6)
                
                # Slider value
                fill_width = int(SLIDER_WIDTH * self.volume)
                if fill_width > 0:
                    fill_rect = pygame.Rect(slider_x, slider_y, fill_width, SLIDER_HEIGHT)
                    pygame.draw.rect(self.screen, (255, 255, 255) if is_selected else SELECTED_COLOR, fill_rect, border_radius=6)
                
                # Slider marker
                marker_x = slider_x + fill_width
                pygame.draw.circle(self.screen, (255, 255, 255), (marker_x, slider_y + SLIDER_HEIGHT // 2), 8)
            else:
                # Button text (centered)
                text = self.button_font.render(option_text, True, TEXT_COLOR)
                text_rect = text.get_rect(center=button_rect.center)
                self.screen.blit(text, text_rect)

        
        # Music warning
        if not self.music_path:
            warning_font = pygame.font.SysFont("segoeui", 14)
            warning = warning_font.render(
                "Rocky Balboa music file not found. Place mp3 file in music/ folder",
                True,
                (255, 200, 0)
            )
            warning_rect = warning.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE - 30))
            self.screen.blit(warning, warning_rect)

