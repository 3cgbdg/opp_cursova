import pygame
import time
from typing import Tuple, Optional, List

from services.core import ReversiCore
from ui.animation import new_animation, is_active
from ui.eval import evaluate_move
from ui.draw import (
    draw_board, draw_discs, draw_hints, draw_hover, draw_last_move,
    draw_hud, draw_endgame
)


WINDOW_SIZE = 720
BOARD_MARGIN = 28
BG_COLOR = (22, 24, 27)


class GameUI:
    def __init__(self, core: ReversiCore, music_enabled: bool = True, volume: float = 0.7, game_mode: str = "pvp", difficulty: int = 3):
        pygame.init()
        self.core = core
        self.game_mode = game_mode
        self.difficulty = difficulty
        self.size = core.size
        self.size = core.size
        self.cell = (WINDOW_SIZE - 2 * BOARD_MARGIN) // self.size
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("Reversi (C++ core + Python GUI)")
        self.font = pygame.font.SysFont("segoeui", 20)
        self.big_font = pygame.font.SysFont("segoeui", 36, bold=True)
        
        # Music settings
        self.music_enabled = music_enabled
        self.volume = volume
        self._init_music()

        self.prev_board: Optional[List[int]] = None
        self.board: List[int] = self.core.get_board()
        self.animations = []
        self.anim_duration = 0.18
        self.last_move: Optional[Tuple[int, int]] = None
        self.hover_cell: Optional[Tuple[int, int]] = None
        self.game_over_cached: Optional[int] = None

        self.last_eval_text: Optional[str] = None
        self.last_eval_color = (255, 255, 255)
        self.last_eval_time = 0.0
        
        # Game over time for animation
        self.game_over_time: Optional[float] = None
        # Confetti particles
        self.confetti_particles: List[Dict] = []
    
    def _init_music(self):
        """Initializes music for the game"""
        if not self.music_enabled:
            return
        
        import os
        # Search for Rocky Balboa music for the game
        possible_names = [
            "gonna_fly_now.mp3",
            "rocky_theme.mp3",
            "rocky.mp3",
            "rocky_balboa.mp3",
            "theme.mp3"
        ]
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        music_dir = os.path.join(base_dir, "music")
        
        music_path = None
        for name in possible_names:
            path = os.path.join(music_dir, name)
            if os.path.exists(path):
                music_path = path
                break
        
        if music_path:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play(-1)  # Loop

    def run(self) -> bool:
        clock = pygame.time.Clock()
        running = True
        should_continue = True
        
        # Check initial state
        self._check_and_auto_pass()
        
        # Timer for AI move
        ai_timer = 0
        AI_DELAY = 1000 # ms

        while running:
            # AI Logic
            current_player = self.core.current_player() # 1: Black, -1: White
            is_ai_turn = (self.game_mode == 'pvc' and current_player == -1)
            
            # If it's AI turn
            if is_ai_turn and not self._is_game_over():
                current_time = pygame.time.get_ticks()
                if ai_timer == 0:
                    ai_timer = current_time + 500 # Slight delay before start
                
                if current_time >= ai_timer:
                    # Draw "Thinking..."
                    self._draw(thinking=True)
                    pygame.display.flip()
                    
                    # Execute move (blocking call)
                    r, c = self.core.get_best_move(self.difficulty)
                    if r != -1 and c != -1:
                        self._apply_move(r, c)
                    else:
                        # AI cannot move (though _check_and_auto_pass should have handled it)
                        pass
                    
                    ai_timer = 0
                    self._check_and_auto_pass()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    should_continue = False
                elif not is_ai_turn: # Block input if it's AI turn
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self._handle_click(event.pos)
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self._reset()
                        elif event.key == pygame.K_m:
                            running = False
                            should_continue = True
                    elif event.type == pygame.MOUSEMOTION:
                        self._handle_hover(event.pos)

            self._draw(thinking=(is_ai_turn and ai_timer != 0))
            pygame.display.flip()
            clock.tick(60)

        pygame.mixer.music.stop()
        return should_continue

    def _reset(self):
        self.core.reset()
        self.prev_board = None
        self.board = self.core.get_board()
        self.animations.clear()
        self.last_move = None
        self.game_over_cached = None
        self.game_over_time = None
        self.last_eval_text = None
        self.confetti_particles.clear()
        # Check initial state - are there moves
        self._check_and_auto_pass()

    def _handle_click(self, pos: Tuple[int, int]):
        if self._is_game_over():
            return
        x, y = pos
        col = (x - BOARD_MARGIN) // self.cell
        row = (y - BOARD_MARGIN) // self.cell
        if not (0 <= row < self.size and 0 <= col < self.size):
            return
        self._apply_move(row, col)
        
    def _apply_move(self, row, col):
        current_before = self.core.current_player()
        before = self.core.get_board()
        
        if not self.core.make_move(row, col):
            return

        after = self.core.get_board()
        self.prev_board = before
        self.board = after
        self.last_move = (row, col)
        
        for r in range(self.size):
            for c in range(self.size):
                bi = before[r * self.size + c]
                ai = after[r * self.size + c]
                if (r, c) == (row, col) and ai == current_before:
                    self.animations.append(new_animation((r, c), "place"))
                elif bi != ai and ai == current_before:
                    self.animations.append(new_animation((r, c), "flip"))
        
        # Check if the next player has moves, if not - auto pass
        self._check_and_auto_pass()
        
        self.game_over_cached = self.core.result()
        
        # Set game over time if the game just finished
        if self.game_over_cached != 0 and self.game_over_time is None:
            self.game_over_time = time.time()
            # Create confetti for victory effect
            self._create_confetti()

        score, label, color = evaluate_move(row, col, before, after, current_before, self.size)
        self.last_eval_text = f"{label} ({score:+d})"
        self.last_eval_color = color
        self.last_eval_time = time.time()
    
    def _check_and_auto_pass(self):
        """Automatically passes the turn if the current player has no valid moves"""
        # Clear cache to check current state
        self.game_over_cached = None
        
        while True:
            # Check if game is over (direct check)
            result = self.core.result()
            if result != 0:
                self.game_over_cached = result
                if self.game_over_time is None:
                    self.game_over_time = time.time()
                    # Create confetti for victory effect
                    self._create_confetti()
                break
            
            # Check if the current player has moves
            valid_moves = self.core.valid_moves()
            if len(valid_moves) > 0:
                break  # There are moves, don't pass
            
            # If no moves - pass
            self.core.pass_turn()
            self.board = self.core.get_board()
            
            # Check if game ended after pass
            result = self.core.result()
            if result != 0:
                self.game_over_cached = result
                if self.game_over_time is None:
                    self.game_over_time = time.time()
                    # Create confetti for victory effect
                    self._create_confetti()
                break

    def _handle_hover(self, pos: Tuple[int, int]):
        x, y = pos
        col = (x - BOARD_MARGIN) // self.cell
        row = (y - BOARD_MARGIN) // self.cell
        if 0 <= row < self.size and 0 <= col < self.size:
            self.hover_cell = (row, col)
        else:
            self.hover_cell = None

    def _draw(self, thinking=False):
        self.screen.fill(BG_COLOR)
        draw_board(self.screen, self.size, self.cell, BOARD_MARGIN)
        draw_discs(self.screen, self.board, self.size, self.cell, BOARD_MARGIN, self.animations, self.anim_duration)
        
        # Hints and Hover only for human turn
        is_human_turn = not (self.game_mode == 'pvc' and self.core.current_player() == -1)
        if is_human_turn:
            draw_hints(self.screen, self.core.valid_moves(), self.size, self.cell, BOARD_MARGIN)
            draw_hover(self.screen, self.hover_cell, self.core.valid_moves(), self.cell, BOARD_MARGIN)
        
        draw_last_move(self.screen, self.last_move, self.cell, BOARD_MARGIN)
        self.animations = [a for a in self.animations if is_active(a, self.anim_duration)]

        b, w = self.core.score()
        cur = self.core.current_player()
        
        move_str = "Black" if cur == 1 else "White"
        if thinking:
            move_str += " (Thinking...)"
            
        status = f"Turn: {move_str}   Score  B:{b}  W:{w}   (R: Restart  M: Menu)"
        draw_hud(self.screen, self.font, (WINDOW_SIZE, WINDOW_SIZE), BOARD_MARGIN, status)

        if self.last_eval_text:
            t = time.time() - self.last_eval_time
            if t < 1.6:
                alpha = 255 if t < 1.2 else int(255 * max(0.0, 1.0 - (t - 1.2) / 0.4))
                msg = self.font.render(self.last_eval_text, True, self.last_eval_color)
                surf = pygame.Surface(msg.get_size(), pygame.SRCALPHA)
                surf.blit(msg, (0, 0))
                arr = pygame.surfarray.pixels_alpha(surf)
                arr[:, :] = alpha
                del arr
                pos = (WINDOW_SIZE - BOARD_MARGIN - msg.get_width(), WINDOW_SIZE - BOARD_MARGIN - 24)
                self.screen.blit(surf, pos)
            else:
                self.last_eval_text = None

        # Update and draw confetti
        if self.confetti_particles:
            import random
            import math
            import pygame as pg
            for particle in self.confetti_particles[:]:
                particle['x'] += particle['vx']
                particle['y'] += particle['vy']
                particle['vy'] += 0.15  # Gravity
                particle['rotation'] += particle['rotation_speed']
                if particle['y'] > WINDOW_SIZE or particle['x'] < -10 or particle['x'] > WINDOW_SIZE + 10:
                    self.confetti_particles.remove(particle)
            
            # Draw confetti
            for particle in self.confetti_particles:
                # Draw various confetti shapes
                shape_type = particle.get('shape', 'rect')
                if shape_type == 'rect':
                    # Square
                    pg.draw.rect(self.screen, particle['color'], 
                                (int(particle['x']), int(particle['y']), 
                                 particle['size'], particle['size']))
                elif shape_type == 'circle':
                    # Circle
                    pg.draw.circle(self.screen, particle['color'], 
                                  (int(particle['x']), int(particle['y'])), 
                                  particle['size'] // 2)
                else:
                    # Triangle
                    points = [
                        (int(particle['x']), int(particle['y'])),
                        (int(particle['x'] + particle['size']), int(particle['y'])),
                        (int(particle['x'] + particle['size'] // 2), int(particle['y'] + particle['size']))
                    ]
                    pg.draw.polygon(self.screen, particle['color'], points)
        
        if self._is_game_over():
            # Pass time for animation (0.0 if time not set)
            time_offset = self.game_over_time if self.game_over_time is not None else time.time()
            b, w = self.core.score()
            draw_endgame(self.screen, WINDOW_SIZE, self.big_font, self.font, self.core.result(), time_offset, self.confetti_particles, b, w)

    def _create_confetti(self):
        """Creates confetti for victory effect"""
        import random
        for _ in range(200):  # 200 confetti particles
            self.confetti_particles.append({
                'x': random.randint(0, WINDOW_SIZE),
                'y': random.randint(-50, 0),
                'vx': random.uniform(-3, 3),
                'vy': random.uniform(2, 6),
                'color': random.choice([
                    (255, 215, 0),  # Gold
                    (255, 0, 0),    # Red
                    (0, 255, 0),    # Green
                    (0, 0, 255),    # Blue
                    (255, 165, 0),  # Orange
                    (255, 192, 203), # Pink
                    (138, 43, 226),  # Purple
                    (255, 255, 255), # White
                    (0, 0, 0),       # Black
                ]),
                'size': random.randint(5, 12),
                'rotation': random.uniform(0, 360),
                'rotation_speed': random.uniform(-8, 8),
                'shape': random.choice(['rect', 'circle', 'triangle'])
            })
    
    def _is_game_over(self) -> bool:
        res = self.core.result() if self.game_over_cached is None else self.game_over_cached
        # Set game over time if the game just finished
        if res != 0 and self.game_over_time is None:
            self.game_over_time = time.time()
            self._create_confetti()
        return res != 0


