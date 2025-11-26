import pygame
import sys

pygame.init()

# Set window size
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Time-Traveling Pet Adventure")

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))  # White background
    pygame.display.flip()

pygame.quit()
sys.exit()
