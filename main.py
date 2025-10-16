import pygame
from game.game_engine import GameEngine

# Initialize pygame/Start application
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ping Pong - Pygame Version")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Clock
clock = pygame.time.Clock()
FPS = 60

# Game loop
engine = GameEngine(WIDTH, HEIGHT)

def main():
    running = True
    while running:
        SCREEN.fill(BLACK)
        
        # Collect events for menu handling
        events = pygame.event.get()
        
        for event in events:
            if event.type == pygame.QUIT:
                running = False
        
        # Handle menu events (navigation)
        menu_result = engine.handle_menu_events(events)
        if menu_result == 'quit':
            running = False
        
        # Handle game input (movement and other keys)
        result = engine.handle_input()
        if result == 'quit':
            running = False
        
        # Update game state
        engine.update()
        
        # Render current state
        engine.render(SCREEN)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if _name_ == "_main_":
    main()