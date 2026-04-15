import pygame

pygame.init()
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Red ball")

clock = pygame.time.Clock()
RADIUS = 25
STEP = 20
x, y = WIDTH // 2, HEIGHT // 2

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and y - RADIUS - STEP >= 0:
                y -= STEP
            if event.key == pygame.K_DOWN and y + RADIUS + STEP <= HEIGHT:
                y += STEP
            if event.key == pygame.K_LEFT and x - RADIUS - STEP >= 0:
                x -= STEP
            if event.key == pygame.K_RIGHT and x + RADIUS + STEP <= WIDTH:
                x += STEP

    screen.fill((255, 255, 255))
    pygame.draw.circle(screen, (255, 0, 0), (x, y), RADIUS)
    pygame.display.flip()
    clock.tick(60)
pygame.quit()