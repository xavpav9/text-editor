import pygame

pygame.init()

WHITE, BLACK = (255,255,255), (0,0,0)

screen = pygame.display.set_mode((700, 500))
pygame.display.set_caption("Text Editor")
clock = pygame.time.Clock()

running = True

while running:
    for evt in pygame.event.get():
        if evt.type == pygame.QUIT:
            running = False

    screen.fill(BLACK)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
