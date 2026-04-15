import pygame
import datetime
import math

FPS = 30
BODY_IMG_PATH = "images/photo_2026-04-15_16-33-47.jpg"
HOUR_HAND_IMG_PATH = "images/hour_hand_image.png"
MINUTE_HAND_IMG_PATH = "images/minute_hand_image.png"

pygame.init()
screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption("Mickey Mouse clock")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 40, bold=True)

body_img = pygame.image.load(BODY_IMG_PATH).convert_alpha()
hour_hand_img = pygame.transform.scale(pygame.image.load(HOUR_HAND_IMG_PATH).convert_alpha(), (450, 500))
minute_hand_img = pygame.transform.scale(pygame.image.load(MINUTE_HAND_IMG_PATH).convert_alpha(), (400, 500))

center = (800 // 2, 800 // 2)
body_rect = body_img.get_rect(center=center)

def draw_clock_face():
        pygame.draw.circle(screen, (0, 0, 0), center, 400, 4)
        pygame.draw.circle(screen, (0, 0, 0), center, 10)

        for num in range(1, 13):
            angle = math.radians(num * 30 - 90)
            x = center[0] + (400 - 40) * math.cos(angle)
            y = center[1] + (400 - 40) * math.sin(angle)
            text_surf = font.render(str(num), True, (0, 0, 0))
            text_rect = text_surf.get_rect(center=(x, y))
            screen.blit(text_surf, text_rect)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        now = datetime.datetime.now()
        hours = now.hour
        minutes = now.minute
        seconds = now.second

        minute_angle = -((minutes + seconds / 60) * 6)
        hour_angle = -(((hours % 12) + minutes / 60) * 30)

        rotated_minute_hand = pygame.transform.rotate(minute_hand_img, minute_angle)
        rotated_hour_hand = pygame.transform.rotate(hour_hand_img, hour_angle)

        minute_rect = rotated_minute_hand.get_rect(center=center)
        hour_rect = rotated_hour_hand.get_rect(center=center)

        screen.fill((255, 255, 255))
        draw_clock_face()
        screen.blit(body_img, body_rect)
        screen.blit(rotated_hour_hand, hour_rect)
        screen.blit(rotated_minute_hand, minute_rect)

        pygame.display.flip()
        clock.tick(FPS)

pygame.quit()