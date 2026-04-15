import pygame

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((600, 300))
font = pygame.font.SysFont("Arial", 24)
clock = pygame.time.Clock()

playlist = ["music/AoD.mp3", "music/TakeMeOut.mp3"]
current_index = 0
is_playing = False

def play_music():
    pygame.mixer.music.load(playlist[current_index])
    pygame.mixer.music.play()

running = True
while running:
    screen.fill((30, 30, 30))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                if not is_playing:
                    play_music()
                    is_playing = True
                else:
                    pygame.mixer.music.unpause()
            elif event.key == pygame.K_s:
                pygame.mixer.music.pause()
            elif event.key == pygame.K_n:
                current_index = (current_index + 1) % len(playlist)
                play_music()
                is_playing = True
            elif event.key == pygame.K_b:
                current_index = (current_index - 1) % len(playlist)
                play_music()
                is_playing = True
            elif event.key == pygame.K_q:
                running = False

    track_text = font.render(f"Track: {playlist[current_index]}", True, (255, 255, 255))
    status_text = font.render(f"Status: {'Playing' if pygame.mixer.music.get_busy() else 'Stopped'}", True, (0, 255, 0))
    pos = pygame.mixer.music.get_pos() // 1000
    progress_text = font.render(f"Position: {pos}s", True, (200, 200, 200))
    screen.blit(track_text, (50, 50))
    screen.blit(status_text, (50, 100))
    screen.blit(progress_text, (50, 150))
    
    pygame.display.flip()
    clock.tick(30)

pygame.quit()