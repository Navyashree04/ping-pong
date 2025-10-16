import pygame
import random

class Ball:
    def _init_(self, x, y, width, height, screen_width, screen_height):
        self.original_x = x
        self.original_y = y
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.velocity_x = random.choice([-5, 5])
        self.velocity_y = random.choice([-3, 3])
        
        # Store previous position for continuous collision detection
        self.prev_x = x
        self.prev_y = y
        
        # Store previous velocity for sound detection
        self.prev_velocity_y = self.velocity_y

    def move(self):
        # Store position before moving
        self.prev_x = self.x
        self.prev_y = self.y
        self.prev_velocity_y = self.velocity_y
        
        # Move ball
        self.x += self.velocity_x
        self.y += self.velocity_y

        # Bounce off top and bottom walls
        if self.y <= 0 or self.y + self.height >= self.screen_height:
            self.velocity_y *= -1
            self.y = max(0, min(self.y, self.screen_height - self.height))

    def check_collision(self, player, ai):
        """
        Enhanced collision detection using continuous collision detection.
        Checks if the ball's path crossed through a paddle.
        """
        ball_rect = self.rect()
        
        # LEFT PADDLE (Player) - Check if ball crossed the paddle's right edge
        if self.velocity_x < 0:  # Ball moving left
            # Check if ball crossed paddle boundary this frame
            paddle_right_edge = player.x + player.width
            
            # Did ball cross from right side to left side of paddle?
            if self.prev_x >= paddle_right_edge and self.x <= paddle_right_edge:
                # Now check vertical overlap
                if self._check_vertical_overlap(ball_rect, player.rect()):
                    self._bounce_off_paddle(player, is_left_paddle=True)
                    return True
        
        # RIGHT PADDLE (AI) - Check if ball crossed the paddle's left edge
        elif self.velocity_x > 0:  # Ball moving right
            # Check if ball crossed paddle boundary this frame
            paddle_left_edge = ai.x
            
            # Did ball cross from left side to right side of paddle?
            if self.prev_x + self.width <= paddle_left_edge and self.x + self.width >= paddle_left_edge:
                # Now check vertical overlap
                if self._check_vertical_overlap(ball_rect, ai.rect()):
                    self._bounce_off_paddle(ai, is_left_paddle=False)
                    return True
        
        return False

    def _check_vertical_overlap(self, ball_rect, paddle_rect):
        """
        Check if ball and paddle overlap vertically.
        This prevents false collisions when ball passes paddle vertically.
        """
        ball_bottom = ball_rect.y + ball_rect.height
        ball_top = ball_rect.y
        paddle_bottom = paddle_rect.y + paddle_rect.height
        paddle_top = paddle_rect.y
        
        # Check if there's any vertical overlap
        return not (ball_bottom < paddle_top or ball_top > paddle_bottom)

    def _bounce_off_paddle(self, paddle, is_left_paddle):
        """
        Handle ball bounce with proper positioning and spin.
        """
        # Reverse horizontal velocity
        self.velocity_x *= -1
        
        # Position ball at paddle edge to prevent overlap/tunneling
        if is_left_paddle:
            self.x = paddle.x + paddle.width
        else:
            self.x = paddle.x - self.width
        
        # Add spin based on where ball hits paddle
        paddle_center = paddle.y + paddle.height / 2
        ball_center = self.y + self.height / 2
        relative_hit = (ball_center - paddle_center) / (paddle.height / 2)
        
        # Adjust vertical velocity for spin effect
        self.velocity_y += relative_hit * 2
        
        # Clamp vertical velocity
        self.velocity_y = max(-8, min(8, self.velocity_y))
        
        # Optional: Increase speed slightly on each hit
        speed_increase = 0.3
        if abs(self.velocity_x) < 12:  # Max speed cap
            if self.velocity_x > 0:
                self.velocity_x += speed_increase
            else:
                self.velocity_x -= speed_increase

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y
        self.prev_x = self.x
        self.prev_y = self.y
        self.velocity_x = random.choice([-5, 5])
        self.velocity_y = random.choice([-3, 3])
        self.prev_velocity_y = self.velocity_y

    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)