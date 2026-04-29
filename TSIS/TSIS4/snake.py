import pygame
import random
import json
import os
import psycopg2
from datetime import datetime


pygame.init()
pygame.mixer.init()

WIDTH = 600
HEIGHT = 600
CELL = 30

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Advanced Snake Game")

font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)
title_font = pygame.font.SysFont(None, 64)

# Colors
colorBLACK  = (0, 0, 0)
colorWHITE  = (255, 255, 255)
colorGRAY   = (50, 50, 50)
colorRED    = (255, 0, 0)
colorDARKRED= (139, 0, 0)
colorYELLOW = (255, 255, 0)
colorGREEN  = (0, 255, 0)
colorBLUE   = (0, 0, 255)
colorPURPLE = (128, 0, 128)
colorCYAN   = (0, 255, 255)
colorORANGE = (255, 165, 0)
colorBROWN  = (139, 69, 19)


DB_CONFIG = {
    "dbname": "snake", 
    "user": "postgres",
    "password": "12345678", 
    "host": "localhost"
}
DB_AVAILABLE = False

def init_db():
    global DB_AVAILABLE
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_sessions (
                id SERIAL PRIMARY KEY,
                player_id INTEGER REFERENCES players(id),
                score INTEGER NOT NULL,
                level_reached INTEGER NOT NULL,
                played_at TIMESTAMP DEFAULT NOW()
            );
        """)
        conn.commit()
        cursor.close()
        conn.close()
        DB_AVAILABLE = True
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Database connection failed: {e}. Leaderboard disabled.")

def save_score(username, score, level):
    if not DB_AVAILABLE or not username.strip(): return
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO players (username) VALUES (%s) ON CONFLICT (username) DO NOTHING;", (username,))
        cursor.execute("SELECT id FROM players WHERE username = %s;", (username,))
        player_id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO game_sessions (player_id, score, level_reached) VALUES (%s, %s, %s);", (player_id, score, level))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Failed to save score:", e)

def get_leaderboard():
    if not DB_AVAILABLE: return []
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.username, s.score, s.level_reached, s.played_at 
            FROM game_sessions s 
            JOIN players p ON s.player_id = p.id 
            ORDER BY s.score DESC LIMIT 10;
        """)
        res = cursor.fetchall()
        cursor.close()
        conn.close()
        return res
    except:
        return []

def get_personal_best(username):
    if not DB_AVAILABLE or not username.strip(): return 0
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT MAX(s.score) FROM game_sessions s 
            JOIN players p ON s.player_id = p.id 
            WHERE p.username = %s;
        """, (username,))
        res = cursor.fetchone()
        cursor.close()
        conn.close()
        return res[0] if res and res[0] else 0
    except:
        return 0

init_db()


SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {"snake_color": colorGREEN, "grid_on": True, "sound_on": True}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
            data["snake_color"] = tuple(data.get("snake_color", colorGREEN))
            return data
    return DEFAULT_SETTINGS.copy()

def save_settings(settings_dict):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings_dict, f)

current_settings = load_settings()


class Button:
    def __init__(self, x, y, w, h, text, color=colorGRAY, hover_color=colorWHITE):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        text_surf = font.render(self.text, True, colorBLACK if self.is_hovered else colorWHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.check_hover(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False

class TextInput:
    def __init__(self, x, y, w, h, placeholder="Enter Username"):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""
        self.placeholder = placeholder
        self.active = False

    def draw(self, surface):
        color = colorWHITE if self.active else colorGRAY
        pygame.draw.rect(surface, color, self.rect, 2)
        display_text = self.text if self.text else self.placeholder
        text_surf = font.render(display_text, True, colorWHITE if self.text else colorGRAY)
        surface.blit(text_surf, (self.rect.x + 10, self.rect.y + 10))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isprintable() and len(self.text) < 15:
                self.text += event.unicode


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def draw_grid():
    if current_settings["grid_on"]:
        for i in range(HEIGHT // CELL):
            for j in range(WIDTH // CELL):
                pygame.draw.rect(screen, colorGRAY, (i * CELL, j * CELL, CELL, CELL), 1)

class Snake:
    def __init__(self):
        self.body = [Point(10, 11), Point(10, 12), Point(10, 13)]
        self.dx = 1
        self.dy = 0
        self.shield_active = False

    def move(self, obstacles):
        for i in range(len(self.body) - 1, 0, -1):
            self.body[i].x = self.body[i - 1].x
            self.body[i].y = self.body[i - 1].y

        self.body[0].x += self.dx
        self.body[0].y += self.dy
        head = self.body[0]

        if head.x > WIDTH // CELL - 1 or head.x < 0 or head.y > HEIGHT // CELL - 1 or head.y < 0:
            if self.shield_active:
                self.shield_active = False
                self.bounce_back()
                return False
            return True

        for segment in self.body[1:]:
            if head.x == segment.x and head.y == segment.y:
                if self.shield_active:
                    self.shield_active = False
                    self.bounce_back()
                    return False
                return True
                
        for obs in obstacles:
            if head.x == obs.x and head.y == obs.y:
                if self.shield_active:
                    self.shield_active = False
                    self.bounce_back()
                    return False
                return True

        return False

    def bounce_back(self):
        self.body[0].x -= self.dx
        self.body[0].y -= self.dy
        self.dx, self.dy = 0, 0 

    def draw(self):
        head = self.body[0]
        head_color = colorCYAN if self.shield_active else colorWHITE
        pygame.draw.rect(screen, head_color, (head.x * CELL, head.y * CELL, CELL, CELL))
        
        body_color = current_settings["snake_color"]
        for segment in self.body[1:]:
            pygame.draw.rect(screen, body_color, (segment.x * CELL, segment.y * CELL, CELL, CELL))

    def check_food_collision(self, item):
        if not item or not item.active: return 0
        if self.body[0].x == item.pos.x and self.body[0].y == item.pos.y:
            return getattr(item, 'weight', 1)
        return 0

class Entity:
    def __init__(self):
        self.pos = Point(-1, -1)
        self.active = False
        self.spawn_time = 0
    
    def generate_random_pos(self, snake_body, obstacles):
        while True:
            tx = random.randint(0, WIDTH // CELL - 1)
            ty = random.randint(0, HEIGHT // CELL - 1)
            on_snake = any(s.x == tx and s.y == ty for s in snake_body)
            on_obs = any(o.x == tx and o.y == ty for o in obstacles)
            if not on_snake and not on_obs:
                self.pos.x, self.pos.y = tx, ty
                self.spawn_time = pygame.time.get_ticks()
                self.active = True
                break

class Food(Entity):
    def __init__(self):
        super().__init__()
        self.weight = 1

    def spawn(self, snake_body, obstacles):
        self.weight = random.randint(1, 3)
        self.generate_random_pos(snake_body, obstacles)

    def draw(self):
        if not self.active: return
        colors = {1: colorGREEN, 2: colorBLUE, 3: colorPURPLE}
        pygame.draw.rect(screen, colors[self.weight], (self.pos.x * CELL, self.pos.y * CELL, CELL, CELL))
        time_left_ms = 5000 - (pygame.time.get_ticks() - self.spawn_time)
        time_left_s = max(1, (time_left_ms + 999) // 1000)
        timer_text = small_font.render(str(time_left_s), True, colorWHITE)
        text_rect = timer_text.get_rect(center=(self.pos.x * CELL + CELL // 2, self.pos.y * CELL + CELL // 2))
        screen.blit(timer_text, text_rect)

class Poison(Entity):
    def draw(self):
        if not self.active: return
        pygame.draw.rect(screen, colorDARKRED, (self.pos.x * CELL, self.pos.y * CELL, CELL, CELL))
        pygame.draw.line(screen, colorBLACK, (self.pos.x*CELL, self.pos.y*CELL), (self.pos.x*CELL+CELL, self.pos.y*CELL+CELL), 3)

class PowerUp(Entity):
    def __init__(self):
        super().__init__()
        self.type = None
        self.color_map = {'SPEED': colorYELLOW, 'SLOW': colorCYAN, 'SHIELD': colorWHITE}

    def spawn(self, snake_body, obstacles):
        self.type = random.choice(['SPEED', 'SLOW', 'SHIELD'])
        self.generate_random_pos(snake_body, obstacles)

    def draw(self):
        if not self.active: return
        pygame.draw.circle(screen, self.color_map[self.type], 
                           (self.pos.x * CELL + CELL//2, self.pos.y * CELL + CELL//2), CELL//2 - 2)


def generate_obstacles(level, snake_head):
    obstacles = []
    if level < 3: return obstacles
    
    num_blocks = min((level - 2) * 5, 30) 
    for _ in range(num_blocks):
        while True:
            x = random.randint(0, WIDTH // CELL - 1)
            y = random.randint(0, HEIGHT // CELL - 1)
            if abs(x - snake_head.x) > 3 or abs(y - snake_head.y) > 3:
                obstacles.append(Point(x, y))
                break
    return obstacles

def draw_obstacles(obstacles):
    for obs in obstacles:
        pygame.draw.rect(screen, colorBROWN, (obs.x * CELL, obs.y * CELL, CELL, CELL))
        pygame.draw.rect(screen, colorBLACK, (obs.x * CELL, obs.y * CELL, CELL, CELL), 2)


clock = pygame.time.Clock()
game_state = "MENU"
username_input = TextInput(150, 200, 300, 40, "Enter Username")


btn_play = Button(200, 260, 200, 40, "Play")
btn_lb = Button(200, 320, 200, 40, "Leaderboard")
btn_settings = Button(200, 380, 200, 40, "Settings")
btn_quit = Button(200, 440, 200, 40, "Quit")

btn_retry = Button(100, 400, 180, 40, "Retry")
btn_menu = Button(320, 400, 180, 40, "Main Menu")
btn_back = Button(200, 520, 200, 40, "Back")

btn_toggle_grid = Button(200, 200, 200, 40, "Toggle Grid")
btn_toggle_sound = Button(200, 260, 200, 40, "Toggle Sound")
btn_cycle_color = Button(200, 320, 200, 40, "Change Color")
btn_save_settings = Button(200, 400, 200, 40, "Save & Back")


snake = None
food = Food()
poison = Poison()
powerup = PowerUp()
obstacles = []

score = 0
foods_eaten = 0
level = 1
base_fps = 5
current_fps = base_fps
personal_best = 0

powerup_active_type = None
powerup_end_time = 0

def reset_game():
    global snake, food, poison, powerup, score, foods_eaten, level, base_fps, current_fps, obstacles, personal_best, powerup_active_type
    snake = Snake()
    score = 0
    foods_eaten = 0
    level = 1
    base_fps = 5
    current_fps = base_fps
    obstacles = []
    powerup_active_type = None
    personal_best = get_personal_best(username_input.text)
    
    food.spawn(snake.body, obstacles)
    poison.active = False
    powerup.active = False

running = True
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    screen.fill(colorBLACK)


    if game_state == "MENU":
        title = title_font.render("SNAKE GAME", True, colorGREEN)
        screen.blit(title, (140, 80))
        
        for event in events:
            username_input.handle_event(event)
            if btn_play.handle_event(event):
                if not username_input.text: username_input.text = "Guest"
                reset_game()
                game_state = "PLAYING"
            elif btn_lb.handle_event(event):
                game_state = "LEADERBOARD"
            elif btn_settings.handle_event(event):
                game_state = "SETTINGS"
            elif btn_quit.handle_event(event):
                running = False

        username_input.draw(screen)
        btn_play.draw(screen)
        btn_lb.draw(screen)
        btn_settings.draw(screen)
        btn_quit.draw(screen)


    elif game_state == "SETTINGS":
        title = title_font.render("SETTINGS", True, colorWHITE)
        screen.blit(title, (180, 80))

        color_options = [colorGREEN, colorRED, colorBLUE, colorORANGE, colorPURPLE]

        for event in events:
            if btn_toggle_grid.handle_event(event):
                current_settings["grid_on"] = not current_settings["grid_on"]
            elif btn_toggle_sound.handle_event(event):
                current_settings["sound_on"] = not current_settings["sound_on"]
            elif btn_cycle_color.handle_event(event):
                idx = color_options.index(current_settings["snake_color"]) if current_settings["snake_color"] in color_options else 0
                current_settings["snake_color"] = color_options[(idx + 1) % len(color_options)]
            elif btn_save_settings.handle_event(event):
                save_settings(current_settings)
                game_state = "MENU"


        g_text = small_font.render(f"Grid: {'ON' if current_settings['grid_on'] else 'OFF'}", True, colorWHITE)
        s_text = small_font.render(f"Sound: {'ON' if current_settings['sound_on'] else 'OFF'}", True, colorWHITE)
        pygame.draw.rect(screen, current_settings["snake_color"], (420, 325, 30, 30))
        
        screen.blit(g_text, (420, 210))
        screen.blit(s_text, (420, 270))

        btn_toggle_grid.draw(screen)
        btn_toggle_sound.draw(screen)
        btn_cycle_color.draw(screen)
        btn_save_settings.draw(screen)


    elif game_state == "LEADERBOARD":
        title = title_font.render("TOP 10 PLAYERS", True, colorYELLOW)
        screen.blit(title, (120, 50))

        leaders = get_leaderboard()
        y_offset = 130
        if not leaders:
            txt = font.render("No data or DB disconnected.", True, colorWHITE)
            screen.blit(txt, (140, 200))
        else:
            header = small_font.render("Rank | User | Score | Lvl | Date", True, colorGRAY)
            screen.blit(header, (50, 100))
            for i, (usr, sc, lvl, dt) in enumerate(leaders):
                row = small_font.render(f"{i+1}. {usr[:10]:<10} | {sc:^5} | {lvl:^3} | {dt.strftime('%Y-%m-%d')}", True, colorWHITE)
                screen.blit(row, (50, y_offset))
                y_offset += 30

        for event in events:
            if btn_back.handle_event(event):
                game_state = "MENU"

        btn_back.draw(screen)


    elif game_state == "PLAYING":
        current_time = pygame.time.get_ticks()

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT and snake.dx == 0:
                    snake.dx, snake.dy = 1, 0
                elif event.key == pygame.K_LEFT and snake.dx == 0:
                    snake.dx, snake.dy = -1, 0
                elif event.key == pygame.K_DOWN and snake.dy == 0:
                    snake.dx, snake.dy = 0, 1
                elif event.key == pygame.K_UP and snake.dy == 0:
                    snake.dx, snake.dy = 0, -1


        if powerup_active_type and current_time > powerup_end_time:
            if powerup_active_type == 'SPEED' or powerup_active_type == 'SLOW':
                current_fps = base_fps
            elif powerup_active_type == 'SHIELD':
                snake.shield_active = False
            powerup_active_type = None

        
        if snake.move(obstacles):
            save_score(username_input.text, score, level)
            game_state = "GAME_OVER"

        
        if current_time - food.spawn_time > 5000:
            food.spawn(snake.body, obstacles)
        
        if poison.active and current_time - poison.spawn_time > 6000:
            poison.active = False
        elif not poison.active and random.randint(1, 100) < 5: 
            poison.generate_random_pos(snake.body, obstacles)

        if powerup.active and current_time - powerup.spawn_time > 8000:
            powerup.active = False
        elif not powerup.active and random.randint(1, 150) < 5: 
            powerup.spawn(snake.body, obstacles)

        
        weight_eaten = snake.check_food_collision(food)
        if weight_eaten > 0:
            score += weight_eaten
            foods_eaten += 1
            for _ in range(weight_eaten):
                snake.body.append(Point(snake.body[-1].x, snake.body[-1].y))
            food.spawn(snake.body, obstacles)

            if foods_eaten % 3 == 0:
                level += 1
                base_fps += 2
                current_fps = base_fps if not powerup_active_type else current_fps
                obstacles = generate_obstacles(level, snake.body[0])

        if poison.active and snake.check_food_collision(poison) > 0:
        
            snake.body = snake.body[:-2]
            poison.active = False
            if len(snake.body) <= 1:
                save_score(username_input.text, score, level)
                game_state = "GAME_OVER"

        if powerup.active and snake.check_food_collision(powerup) > 0:
            powerup_active_type = powerup.type
            powerup_end_time = current_time + 5000
            if powerup.type == 'SPEED':
                current_fps = base_fps + 5
            elif powerup.type == 'SLOW':
                current_fps = max(2, base_fps - 4)
            elif powerup.type == 'SHIELD':
                snake.shield_active = True
            powerup.active = False

        
        draw_grid()
        draw_obstacles(obstacles)
        snake.draw()
        food.draw()
        poison.draw()
        powerup.draw()

        
        hud_text = font.render(f"User: {username_input.text} | Score: {score} | PB: {personal_best} | Lvl: {level}", True, colorWHITE)
        screen.blit(hud_text, (10, 10))
        
        if powerup_active_type:
            p_text = small_font.render(f"ACTIVE: {powerup_active_type}", True, colorYELLOW)
            screen.blit(p_text, (10, 40))

    elif game_state == "GAME_OVER":
        go_text = title_font.render("GAME OVER", True, colorRED)
        score_text = font.render(f"Final Score: {score} | Level: {level}", True, colorWHITE)
        screen.blit(go_text, (160, 150))
        screen.blit(score_text, (160, 220))

        for event in events:
            if btn_retry.handle_event(event):
                reset_game()
                game_state = "PLAYING"
            elif btn_menu.handle_event(event):
                game_state = "MENU"

        btn_retry.draw(screen)
        btn_menu.draw(screen)

    pygame.display.flip()
    
    if game_state == "PLAYING":
        clock.tick(current_fps)
    else:
        clock.tick(30)

pygame.quit()