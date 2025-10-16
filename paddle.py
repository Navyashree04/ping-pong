import pygame

class Paddle:
    def _init_(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = 7

    def move(self, dy, screen_height):
        """Move paddle with boundary checking"""
        self.y += dy
        self.y = max(0, min(self.y, screen_height - self.height))

    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def auto_track(self, ball, screen_height, difficulty=0.8):
        """
        AI paddle tracking with adjustable difficulty
        
        Args:
            ball: The ball object to track
            screen_height: Screen height for boundary checking
            difficulty: 0.0 to 1.0, where 1.0 is perfect tracking
                       Default 0.8 makes AI beatable
        """
        # Calculate the center of the paddle and ball
        paddle_center = self.y + self.height / 2
        ball_center = ball.y + ball.height / 2
        
        # Create a "dead zone" where AI doesn't move (makes it more human-like)
        dead_zone = 20
        
        # Only track the ball if it's moving toward the AI paddle
        if ball.velocity_x > 0:  # Ball moving toward AI
            # Calculate error margin based on difficulty
            # Lower difficulty = larger error margin
            error_margin = (1 - difficulty) * 50
            
            # Add some randomness to make AI less perfect
            target = ball_center + ((-1) ** (int(ball.y) % 2)) * error_margin
            
            if target < paddle_center - dead_zone:
                self.move(-self.speed * difficulty, screen_height)
            elif target > paddle_center + dead_zone:
                self.move(self.speed * difficulty, screen_height)
        else:
            # When ball is moving away, slowly return to center
            screen_center = screen_height / 2
            if paddle_center < screen_center - dead_zone:
                self.move(self.speed * 0.3, screen_height)
            elif paddle_center > screen_center + dead_zone:
                self.move(-self.speed * 0.3, screen_height)