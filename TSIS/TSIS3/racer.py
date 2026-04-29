import pygame, sys
from pygame.locals import *
import random, time, json, os

pygame.init()

FPS = 60
FramePerSec = pygame.time.Clock()

BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY  = (150, 150, 150)
LIGHT_GRAY = (200, 200, 200)

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600


GAME_STATE = "MAIN_MENU" 
USERNAME = ""
DISTANCE_DRIVEN = 0
TOTAL_DISTANCE = 10000 
SCORE = 0
COINS_COLLECTED = 0


SOUND_ON = True
CAR_COLOR = 'blue' 
DIFFICULTY = 'normal'
BASE_SPEED = 5

ACTIVE_POWER_UP = None
POWER_UP_END_TIME = 0
HAS_SHIELD = False

font = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)
font_tiny = pygame.font.SysFont("Verdana", 14)

background = pygame.image.load("resources/AnimatedStreet.png")
 
DISPLAYSURF = pygame.display.set_mode((400,600))
pygame.display.set_caption("Racer Game")

pygame.mixer.music.load('resources/background.wav')
if SOUND_ON:
    pygame.mixer.music.play(-1)

def load_leaderboard():
    if not os.path.exists("leaderboard.json"):
        return []
    with open("leaderboard.json", "r") as f:
        return json.load(f)

def save_score(name, score, distance):
    board = load_leaderboard()
    board.append({"name": name, "score": score, "distance": int(distance)})
    board.sort(key=lambda x: x["score"], reverse=True)
    board = board[:10]
    with open("leaderboard.json", "w") as f:
        json.dump(board, f)


def draw_button(surface, text, x, y, w, h, default_color, hover_color):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    
    rect = pygame.Rect(x, y, w, h)
    is_hovered = rect.collidepoint(mouse)
    
    pygame.draw.rect(surface, hover_color if is_hovered else default_color, rect)
    pygame.draw.rect(surface, BLACK, rect, 2) 
    
    text_surf = font_small.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)
    
    return is_hovered and click[0] == 1

def draw_text_center(surface, text, font_type, color, y):
    text_surf = font_type.render(text, True, color)
    text_rect = text_surf.get_rect(center=(SCREEN_WIDTH/2, y))
    surface.blit(text_surf, text_rect)

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = pygame.image.load("resources/Enemy.png")
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40,SCREEN_WIDTH-40), 0)

    def move(self):
        self.rect.move_ip(0, current_speed)
        if (self.rect.bottom > 600):
            self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = pygame.transform.scale(pygame.image.load(f"resources/Player_{CAR_COLOR}.png").convert_alpha(), (44, 96))
        self.rect = self.image.get_rect()
        self.rect.center = (160, 520)
       
    def move(self):
        pressed_keys = pygame.key.get_pressed()
        if self.rect.left > 0 and pressed_keys[K_LEFT]:
            self.rect.move_ip(-5, 0)
        if self.rect.right < SCREEN_WIDTH and pressed_keys[K_RIGHT]:
            self.rect.move_ip(5, 0)

class Coins(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load("resources/coin.png").convert_alpha(), (50, 50))
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40,SCREEN_WIDTH-40), 0)
    def move(self):
        self.rect.move_ip(0, current_speed)
        if (self.rect.bottom > 600):
            self.kill()

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, obs_type):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load(f"resources/{obs_type}.png").convert_alpha(), (50, 50))
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40,SCREEN_WIDTH-40), -50)
    def move(self):
        self.rect.move_ip(0, current_speed)
        if (self.rect.bottom > 600):
            self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.type = random.choice(['nitro', 'shield', 'repair'])
        self.image = pygame.transform.scale(pygame.image.load(f"resources/{self.type}.png").convert_alpha(), (40, 40))
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH-40), -50)
        self.spawn_time = pygame.time.get_ticks() 

    def move(self):
        self.rect.move_ip(0, current_speed)
        if pygame.time.get_ticks() - self.spawn_time > 5000 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

def reset_game():
    global P1, enemies, coins, obstacles, powerups, all_sprites
    global DISTANCE_DRIVEN, COINS_COLLECTED, SCORE, current_speed, ACTIVE_POWER_UP, HAS_SHIELD
    
    DISTANCE_DRIVEN = 0
    COINS_COLLECTED = 0
    SCORE = 0
    ACTIVE_POWER_UP = None
    HAS_SHIELD = False
    
    if DIFFICULTY == 'easy': current_speed = 3
    elif DIFFICULTY == 'hard': current_speed = 7
    else: current_speed = 5
    
    P1 = Player()
    enemies = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(P1)

INC_SPEED = pygame.USEREVENT + 1
SPAWN_ENEMY = pygame.USEREVENT + 2
SPAWN_COIN = pygame.USEREVENT + 3
SPAWN_OBSTACLE = pygame.USEREVENT + 4
SPAWN_POWERUP = pygame.USEREVENT + 5

pygame.time.set_timer(INC_SPEED, 2000)
pygame.time.set_timer(SPAWN_ENEMY, 2000)
pygame.time.set_timer(SPAWN_COIN, 1500)
pygame.time.set_timer(SPAWN_OBSTACLE, 3000)
pygame.time.set_timer(SPAWN_POWERUP, 8000)

spawn_stone_next = True
current_speed = BASE_SPEED
click_cooldown = 0

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    if click_cooldown > 0:
        click_cooldown -= 1

    DISPLAYSURF.fill(WHITE)

    if GAME_STATE == "MAIN_MENU":
        draw_text_center(DISPLAYSURF, "RACER", font, BLACK, 100)
        
        if draw_button(DISPLAYSURF, "Play", 100, 200, 200, 50, GRAY, LIGHT_GRAY) and click_cooldown == 0:
            GAME_STATE = "USERNAME"
            click_cooldown = 20
        if draw_button(DISPLAYSURF, "Leaderboard", 100, 280, 200, 50, GRAY, LIGHT_GRAY) and click_cooldown == 0:
            GAME_STATE = "LEADERBOARD"
            click_cooldown = 20
        if draw_button(DISPLAYSURF, "Settings", 100, 360, 200, 50, GRAY, LIGHT_GRAY) and click_cooldown == 0:
            GAME_STATE = "SETTINGS"
            click_cooldown = 20
        if draw_button(DISPLAYSURF, "Quit", 100, 440, 200, 50, RED, (255, 100, 100)) and click_cooldown == 0:
            pygame.quit()
            sys.exit()

    elif GAME_STATE == "SETTINGS":
        draw_text_center(DISPLAYSURF, "Settings", font, BLACK, 50)
        

        sound_text = f"Sound: {'ON' if SOUND_ON else 'OFF'}"
        if draw_button(DISPLAYSURF, sound_text, 100, 150, 200, 40, GRAY, LIGHT_GRAY) and click_cooldown == 0:
            SOUND_ON = not SOUND_ON
            if SOUND_ON: pygame.mixer.music.play(-1)
            else: pygame.mixer.music.stop()
            click_cooldown = 20


        diff_text = f"Difficulty: {DIFFICULTY.capitalize()}"
        if draw_button(DISPLAYSURF, diff_text, 100, 220, 200, 40, GRAY, LIGHT_GRAY) and click_cooldown == 0:
            if DIFFICULTY == 'easy': DIFFICULTY = 'normal'
            elif DIFFICULTY == 'normal': DIFFICULTY = 'hard'
            else: DIFFICULTY = 'easy'
            click_cooldown = 20


        color_text = f"Car: {CAR_COLOR.capitalize()}"
        if draw_button(DISPLAYSURF, color_text, 100, 290, 200, 40, GRAY, LIGHT_GRAY) and click_cooldown == 0:
            if CAR_COLOR == 'red': CAR_COLOR = 'blue'
            elif CAR_COLOR == 'blue': CAR_COLOR = 'green'
            else: CAR_COLOR = 'red'
            click_cooldown = 20

        if draw_button(DISPLAYSURF, "Back", 100, 400, 200, 50, GRAY, LIGHT_GRAY) and click_cooldown == 0:
            GAME_STATE = "MAIN_MENU"
            click_cooldown = 20

    elif GAME_STATE == "USERNAME":
        draw_text_center(DISPLAYSURF, "Enter Username", font_small, BLACK, 200)
        

        for event in events:
            if event.type == KEYDOWN:
                if event.key == K_RETURN and len(USERNAME) > 0:
                    reset_game()
                    GAME_STATE = "PLAYING"
                elif event.key == K_BACKSPACE:
                    USERNAME = USERNAME[:-1]
                else:
                    if len(USERNAME) < 10:
                        USERNAME += event.unicode


        pygame.draw.rect(DISPLAYSURF, GRAY, (100, 250, 200, 40), 2)
        draw_text_center(DISPLAYSURF, USERNAME, font_small, BLACK, 270)
        draw_text_center(DISPLAYSURF, "Press ENTER to Start", font_tiny, BLACK, 320)

        if draw_button(DISPLAYSURF, "Back", 100, 400, 200, 40, GRAY, LIGHT_GRAY) and click_cooldown == 0:
            GAME_STATE = "MAIN_MENU"
            click_cooldown = 20

    elif GAME_STATE == "LEADERBOARD":
        draw_text_center(DISPLAYSURF, "Top 10", font_small, BLACK, 30)
        board = load_leaderboard()
        
        y_offset = 80
        for i, entry in enumerate(board):
            text = f"{i+1}. {entry['name']} - {entry['score']} pts - {entry['distance']}m"
            draw_text_center(DISPLAYSURF, text, font_tiny, BLACK, y_offset)
            y_offset += 30
            
        if draw_button(DISPLAYSURF, "Back", 100, 500, 200, 40, GRAY, LIGHT_GRAY) and click_cooldown == 0:
            GAME_STATE = "MAIN_MENU"
            click_cooldown = 20

    elif GAME_STATE == "PLAYING":
        for event in events:
            if event.type == INC_SPEED:
                current_speed += 0.2
            if event.type == SPAWN_ENEMY:
                e = Enemy()
                enemies.add(e)
                all_sprites.add(e)
            if event.type == SPAWN_COIN:
                c = Coins()
                coins.add(c)
                all_sprites.add(c)
            if event.type == SPAWN_OBSTACLE:
                obs = Obstacle('stone' if spawn_stone_next else 'oilspill')
                obstacles.add(obs)
                all_sprites.add(obs)
                spawn_stone_next = not spawn_stone_next
            if event.type == SPAWN_POWERUP:
                p = PowerUp()
                powerups.add(p)
                all_sprites.add(p)

        DISTANCE_DRIVEN += (current_speed / 10)
        SCORE = int((DISTANCE_DRIVEN / 10) + (COINS_COLLECTED * 10))


        if DISTANCE_DRIVEN >= TOTAL_DISTANCE:
            save_score(USERNAME, SCORE, DISTANCE_DRIVEN)
            GAME_STATE = "GAME_OVER"


        DISPLAYSURF.blit(background, (0,0))
        for entity in all_sprites:
            entity.move()
            DISPLAYSURF.blit(entity.image, entity.rect)


        dist_text = font_tiny.render(f"Dist: {int(DISTANCE_DRIVEN)}/{TOTAL_DISTANCE}m", True, BLACK)
        score_text = font_tiny.render(f"Score: {SCORE}", True, BLACK)
        coin_text = font_tiny.render(f"Coins: {COINS_COLLECTED}", True, BLACK)
        
        DISPLAYSURF.blit(dist_text, (10, 10))
        DISPLAYSURF.blit(score_text, (10, 30))
        DISPLAYSURF.blit(coin_text, (300, 10))


        curr_time = pygame.time.get_ticks()
        if ACTIVE_POWER_UP == 'nitro':
            if curr_time > POWER_UP_END_TIME:
                current_speed -= 4  
                ACTIVE_POWER_UP = None
            else:
                time_left = max(0, (POWER_UP_END_TIME - curr_time) // 1000)
                DISPLAYSURF.blit(font_small.render(f"NITRO: {time_left}s", True, RED), (10, 60))
        elif ACTIVE_POWER_UP == 'shield':
            DISPLAYSURF.blit(font_small.render("SHIELD ACTIVE", True, BLUE), (10, 60))

        if pygame.sprite.spritecollideany(P1, coins):
            c = pygame.sprite.spritecollideany(P1, coins)
            COINS_COLLECTED += random.randint(1, 3)
            c.kill()

        collected_powerup = pygame.sprite.spritecollideany(P1, powerups)
        if collected_powerup:
            if ACTIVE_POWER_UP == 'nitro': current_speed -= 4 # reset old nitro
            HAS_SHIELD = False 
            ACTIVE_POWER_UP = collected_powerup.type
            
            if ACTIVE_POWER_UP == 'nitro':
                current_speed += 4
                POWER_UP_END_TIME = curr_time + 4000
            elif ACTIVE_POWER_UP == 'shield':
                HAS_SHIELD = True
            elif ACTIVE_POWER_UP == 'repair':
                if enemies: random.choice(enemies.sprites()).kill()
                elif obstacles: random.choice(obstacles.sprites()).kill()
                ACTIVE_POWER_UP = None
            collected_powerup.kill()

        hit_enemy = pygame.sprite.spritecollideany(P1, enemies)
        hit_obs = pygame.sprite.spritecollideany(P1, obstacles)
        
        if hit_enemy or hit_obs:
            if HAS_SHIELD:
                if hit_enemy: hit_enemy.kill()
                if hit_obs: hit_obs.kill()
                HAS_SHIELD = False
                ACTIVE_POWER_UP = None
            else:
                if SOUND_ON: 
                    try:
                        pygame.mixer.Sound('resources/crash.wav').play()
                    except: pass
                save_score(USERNAME, SCORE, DISTANCE_DRIVEN)
                time.sleep(1)
                GAME_STATE = "GAME_OVER"

    elif GAME_STATE == "GAME_OVER":
        DISPLAYSURF.fill(RED)
        draw_text_center(DISPLAYSURF, "Game Over", font, BLACK, 100)
        draw_text_center(DISPLAYSURF, f"Final Score: {SCORE}", font_small, BLACK, 200)
        draw_text_center(DISPLAYSURF, f"Distance: {int(DISTANCE_DRIVEN)}m", font_small, BLACK, 250)
        draw_text_center(DISPLAYSURF, f"Coins: {COINS_COLLECTED}", font_small, BLACK, 300)

        if draw_button(DISPLAYSURF, "Retry", 100, 380, 200, 50, GRAY, LIGHT_GRAY) and click_cooldown == 0:
            reset_game()
            GAME_STATE = "PLAYING"
            click_cooldown = 20
        if draw_button(DISPLAYSURF, "Main Menu", 100, 450, 200, 50, GRAY, LIGHT_GRAY) and click_cooldown == 0:
            GAME_STATE = "MAIN_MENU"
            click_cooldown = 20

    pygame.display.update()
    FramePerSec.tick(FPS)