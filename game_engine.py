import pygame
from .paddle import Paddle
from .ball import Ball
import os
import math
import numpy as np

# Game Engine

WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)
RED = (255, 50, 50)
YELLOW = (255, 255, 0)

class SoundManager:
    """Manages game sound effects"""
    def _init_(self):
        # Initialize mixer with specific settings for better sound quality
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        self.sounds = {}
        self.enabled = True
        
        # Try to load sounds, create them if they don't exist
        self._load_or_create_sounds()
    
    def _load_or_create_sounds(self):
        """Load sound files or create them programmatically"""
        sound_dir = "sounds"
        
        # Try to load from files first
        sound_files = {
            'paddle_hit': 'paddle_hit.wav',
            'wall_bounce': 'wall_bounce.wav',
            'score': 'score.wav'
        }
        
        # Check if sound directory exists
        if os.path.exists(sound_dir):
            for sound_name, filename in sound_files.items():
                filepath = os.path.join(sound_dir, filename)
                if os.path.exists(filepath):
                    try:
                        self.sounds[sound_name] = pygame.mixer.Sound(filepath)
                        print(f"Loaded {sound_name} from file")
                        continue
                    except:
                        pass
        
        # Create sounds programmatically if not loaded
        if 'paddle_hit' not in self.sounds:
            self.sounds['paddle_hit'] = self._create_paddle_sound()
        if 'wall_bounce' not in self.sounds:
            self.sounds['wall_bounce'] = self._create_wall_sound()
        if 'score' not in self.sounds:
            self.sounds['score'] = self._create_score_sound()
    
    def _create_paddle_sound(self):
        """Create a paddle hit sound (short click)"""
        sample_rate = 22050
        duration = 0.05  # 50ms
        frequency = 440  # A note
        
        samples = int(sample_rate * duration)
        wave = np.zeros((samples, 2), dtype=np.int16)
        
        for i in range(samples):
            # Create a short beep with decay
            t = float(i) / sample_rate
            amplitude = 32767 * (1 - t / duration)  # Decay envelope
            value = int(amplitude * math.sin(2 * math.pi * frequency * t))
            wave[i] = [value, value]  # Stereo
        
        sound = pygame.sndarray.make_sound(wave)
        sound.set_volume(0.3)
        return sound
    
    def _create_wall_sound(self):
        """Create a wall bounce sound (lower pitch)"""
        sample_rate = 22050
        duration = 0.04  # 40ms
        frequency = 220  # Lower A note
        
        samples = int(sample_rate * duration)
        wave = np.zeros((samples, 2), dtype=np.int16)
        
        for i in range(samples):
            t = float(i) / sample_rate
            amplitude = 32767 * (1 - t / duration)
            value = int(amplitude * math.sin(2 * math.pi * frequency * t))
            wave[i] = [value, value]
        
        sound = pygame.sndarray.make_sound(wave)
        sound.set_volume(0.2)
        return sound
    
    def _create_score_sound(self):
        """Create a scoring sound (rising tone)"""
        sample_rate = 22050
        duration = 0.3  # 300ms
        
        samples = int(sample_rate * duration)
        wave = np.zeros((samples, 2), dtype=np.int16)
        
        for i in range(samples):
            t = float(i) / sample_rate
            # Rising frequency from 440Hz to 880Hz
            frequency = 440 + (440 * t / duration)
            amplitude = 32767 * (1 - t / duration) * 0.5
            value = int(amplitude * math.sin(2 * math.pi * frequency * t))
            wave[i] = [value, value]
        
        sound = pygame.sndarray.make_sound(wave)
        sound.set_volume(0.4)
        return sound
    
    def play(self, sound_name):
        """Play a sound by name"""
        if self.enabled and sound_name in self.sounds:
            self.sounds[sound_name].play()
    
    def toggle(self):
        """Toggle sound on/off"""
        self.enabled = not self.enabled
        return self.enabled


class GameEngine:
    def _init_(self, width, height):
        self.width = width
        self.height = height
        self.paddle_width = 10
        self.paddle_height = 100
        
        # Game states: 'menu', 'playing', 'game_over', 'series_over'
        self.state = 'menu'
        self.winner = None
        
        # Scoring system
        self.winning_score = 5  # Points per game
        self.series_mode = None  # 'best_of_3', 'best_of_5', 'best_of_7'
        self.series_target = 0   # Games needed to win series
        
        # Match tracking
        self.player_games_won = 0
        self.ai_games_won = 0
        
        # Menu selection
        self.menu_options = ['Best of 3', 'Best of 5', 'Best of 7', 'Exit']
        self.selected_option = 0
        
        # Sound manager
        self.sound_manager = SoundManager()
        
        # M key debounce
        self.m_key_pressed = False
        
        # Initialize game objects
        self._init_game_objects()
        
        # Fonts
        self.font = pygame.font.SysFont("Arial", 30)
        self.large_font = pygame.font.SysFont("Arial", 60, bold=True)
        self.medium_font = pygame.font.SysFont("Arial", 36)
        self.small_font = pygame.font.SysFont("Arial", 24)

    def _init_game_objects(self):
        """Initialize or reset game objects"""
        self.player = Paddle(10, self.height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ai = Paddle(self.width - 20, self.height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ball = Ball(self.width // 2, self.height // 2, 7, 7, self.width, self.height)
        self.player_score = 0
        self.ai_score = 0

    def handle_input(self):
        """Handle keyboard input based on game state"""
        keys = pygame.key.get_pressed()
        
        if self.state == 'menu':
            return self._handle_menu_input(keys)
        
        elif self.state == 'playing':
            # Player paddle controls
            if keys[pygame.K_w]:
                self.player.move(-10, self.height)
            if keys[pygame.K_s]:
                self.player.move(10, self.height)
            
            # Toggle sound with M key (with debounce)
            if keys[pygame.K_m]:
                if not self.m_key_pressed:
                    self.m_key_pressed = True
                    enabled = self.sound_manager.toggle()
                    print(f"Sound: {'ON' if enabled else 'OFF'}")
            else:
                self.m_key_pressed = False
        
        elif self.state == 'game_over':
            # Continue to next game in series
            if keys[pygame.K_SPACE]:
                self._next_game()
        
        elif self.state == 'series_over':
            # Return to menu or exit
            if keys[pygame.K_SPACE] or keys[pygame.K_r]:
                self._reset_series()
                self.state = 'menu'
            if keys[pygame.K_ESCAPE]:
                return 'quit'
        
        return None

    def _handle_menu_input(self, keys):
        """Handle menu navigation"""
        pass  # Will be handled by handle_menu_events

    def handle_menu_events(self, events):
        """Handle menu events (should be called from main.py)"""
        if self.state != 'menu':
            return None
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return self._select_menu_option()
                elif event.key == pygame.K_ESCAPE:
                    return 'quit'
        return None

    def _select_menu_option(self):
        """Process menu selection"""
        option = self.menu_options[self.selected_option]
        
        if option == 'Best of 3':
            self._start_series(3)
        elif option == 'Best of 5':
            self._start_series(5)
        elif option == 'Best of 7':
            self._start_series(7)
        elif option == 'Exit':
            return 'quit'
        
        return None

    def _start_series(self, best_of):
        """Start a new series"""
        self.series_mode = f'best_of_{best_of}'
        self.series_target = (best_of // 2) + 1
        self.player_games_won = 0
        self.ai_games_won = 0
        self._init_game_objects()
        self.state = 'playing'

    def _next_game(self):
        """Start next game in the series"""
        self._init_game_objects()
        self.state = 'playing'

    def _reset_series(self):
        """Reset everything for a new series"""
        self.player_games_won = 0
        self.ai_games_won = 0
        self.series_mode = None
        self.series_target = 0
        self.selected_option = 0

    def update(self):
        """Update game logic based on state"""
        if self.state == 'playing':
            # Move ball
            self.ball.move()
            
            # Check wall bounces (velocity_y changed means wall bounce)
            if self.ball.velocity_y != self.ball.prev_velocity_y:
                # Wall bounce detected
                self.sound_manager.play('wall_bounce')
            
            # Check paddle collisions
            collision = self.ball.check_collision(self.player, self.ai)
            if collision:
                # Paddle hit detected
                self.sound_manager.play('paddle_hit')

            # Check for scoring
            if self.ball.x <= 0:
                self.ai_score += 1
                self.sound_manager.play('score')
                self._check_game_winner()
                if self.state == 'playing':
                    self.ball.reset()
            elif self.ball.x >= self.width:
                self.player_score += 1
                self.sound_manager.play('score')
                self._check_game_winner()
                if self.state == 'playing':
                    self.ball.reset()

            # AI movement
            self.ai.auto_track(self.ball, self.height)

    def _check_game_winner(self):
        """Check if someone won this game"""
        if self.player_score >= self.winning_score:
            self.winner = 'player'
            self.player_games_won += 1
            self._check_series_winner()
        elif self.ai_score >= self.winning_score:
            self.winner = 'ai'
            self.ai_games_won += 1
            self._check_series_winner()

    def _check_series_winner(self):
        """Check if someone won the series"""
        if self.player_games_won >= self.series_target:
            self.state = 'series_over'
            self.winner = 'player'
        elif self.ai_games_won >= self.series_target:
            self.state = 'series_over'
            self.winner = 'ai'
        else:
            self.state = 'game_over'

    def render(self, screen):
        """Render game based on current state"""
        if self.state == 'menu':
            self._render_menu(screen)
        elif self.state == 'playing':
            self._render_game(screen)
        elif self.state == 'game_over':
            self._render_game_over(screen)
        elif self.state == 'series_over':
            self._render_series_over(screen)

    def _render_menu(self, screen):
        """Render main menu"""
        # Title
        title = self.large_font.render("PING PONG", True, WHITE)
        title_rect = title.get_rect(center=(self.width//2, 100))
        screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.small_font.render("Select Game Mode", True, GRAY)
        subtitle_rect = subtitle.get_rect(center=(self.width//2, 160))
        screen.blit(subtitle, subtitle_rect)
        
        # Menu options
        start_y = 240
        spacing = 70
        
        for i, option in enumerate(self.menu_options):
            if i == self.selected_option:
                color = YELLOW
                prefix = "> "
                font = self.medium_font
            else:
                color = WHITE
                prefix = "  "
                font = self.font
            
            option_text = font.render(prefix + option, True, color)
            option_rect = option_text.get_rect(center=(self.width//2, start_y + i * spacing))
            screen.blit(option_text, option_rect)
        
        # Instructions
        instructions = self.small_font.render("↑↓ to select | ENTER to confirm | ESC to exit", True, GRAY)
        instructions_rect = instructions.get_rect(center=(self.width//2, self.height - 40))
        screen.blit(instructions, instructions_rect)

    def _render_game(self, screen):
        """Render normal gameplay"""
        # Draw paddles
        pygame.draw.rect(screen, WHITE, self.player.rect())
        pygame.draw.rect(screen, WHITE, self.ai.rect())
        
        # Draw ball
        pygame.draw.ellipse(screen, WHITE, self.ball.rect())
        
        # Draw center line
        pygame.draw.aaline(screen, WHITE, (self.width//2, 0), (self.width//2, self.height))

        # Draw current game scores
        player_text = self.font.render(str(self.player_score), True, WHITE)
        ai_text = self.font.render(str(self.ai_score), True, WHITE)
        screen.blit(player_text, (self.width//4, 20))
        screen.blit(ai_text, (self.width * 3//4, 20))
        
        # Draw series score
        series_text = self.small_font.render(
            f"Games Won - Player: {self.player_games_won} | AI: {self.ai_games_won}", 
            True, GRAY
        )
        series_rect = series_text.get_rect(center=(self.width//2, self.height - 20))
        screen.blit(series_text, series_rect)
        
        # Sound indicator
        sound_status = "ON" if self.sound_manager.enabled else "OFF"
        sound_text = self.small_font.render(f"Sound: {sound_status} (M)", True, GRAY)
        screen.blit(sound_text, (10, self.height - 30))

    def _render_game_over(self, screen):
        """Render game over screen"""
        self._render_game(screen)
        
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        if self.winner == 'player':
            winner_text = self.large_font.render("PLAYER WINS GAME!", True, GREEN)
        else:
            winner_text = self.large_font.render("AI WINS GAME!", True, RED)
        
        winner_rect = winner_text.get_rect(center=(self.width//2, self.height//2 - 80))
        screen.blit(winner_text, winner_rect)
        
        series_text = self.medium_font.render(
            f"Series: Player {self.player_games_won} - {self.ai_games_won} AI",
            True, WHITE
        )
        series_rect = series_text.get_rect(center=(self.width//2, self.height//2))
        screen.blit(series_text, series_rect)
        
        next_text = self.font.render(f"First to {self.series_target} wins!", True, GRAY)
        next_rect = next_text.get_rect(center=(self.width//2, self.height//2 + 60))
        screen.blit(next_text, next_rect)
        
        continue_text = self.font.render("Press SPACE to continue", True, YELLOW)
        continue_rect = continue_text.get_rect(center=(self.width//2, self.height//2 + 110))
        screen.blit(continue_text, continue_rect)

    def _render_series_over(self, screen):
        """Render series over screen"""
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(220)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        if self.winner == 'player':
            winner_text = self.large_font.render("PLAYER WINS SERIES!", True, GREEN)
        else:
            winner_text = self.large_font.render("AI WINS SERIES!", True, RED)
        
        winner_rect = winner_text.get_rect(center=(self.width//2, self.height//2 - 100))
        screen.blit(winner_text, winner_rect)
        
        final_score = self.medium_font.render(
            f"Final Score: {self.player_games_won} - {self.ai_games_won}",
            True, WHITE
        )
        final_rect = final_score.get_rect(center=(self.width//2, self.height//2 - 20))
        screen.blit(final_score, final_rect)
        
        # Trophy emoji might not render on all systems, using text instead
        trophy = self.large_font.render("CHAMPION", True, YELLOW)
        trophy_rect = trophy.get_rect(center=(self.width//2, self.height//2 + 50))
        screen.blit(trophy, trophy_rect)
        
        restart_text = self.font.render("Press SPACE or R for Menu", True, GRAY)
        restart_rect = restart_text.get_rect(center=(self.width//2, self.height//2 + 130))
        screen.blit(restart_text, restart_rect)
        
        exit_text = self.font.render("Press ESC to Exit", True, GRAY)
        exit_rect = exit_text.get_rect(center=(self.width//2, self.height//2 + 170))
        screen.blit(exit_text, exit_rect)