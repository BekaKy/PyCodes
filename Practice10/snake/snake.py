import pygame
import random

colorBLACK = (0, 0, 0)
colorWHITE = (255, 255, 255)
colorGRAY = (50, 50, 50)
colorRED = (255, 0, 0)
colorYELLOW = (255, 255, 0)
colorGREEN = (0, 255, 0)

pygame.init()

WIDTH = 600
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

CELL = 30
font = pygame.font.SysFont(None, 36)

def draw_grid():
    for i in range(HEIGHT // CELL):
        for j in range(WIDTH // CELL):
            pygame.draw.rect(screen, colorGRAY, (i * CELL, j * CELL, CELL, CELL), 1)

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"{self.x}, {self.y}"

class Snake:
    def __init__(self):
        self.body = [Point(10, 11), Point(10, 12), Point(10, 13)]
        self.dx = 1
        self.dy = 0

    def move(self):
        # move the body
        for i in range(len(self.body) - 1, 0, -1):
            self.body[i].x = self.body[i - 1].x
            self.body[i].y = self.body[i - 1].y

        # Move the head
        self.body[0].x += self.dx
        self.body[0].y += self.dy

        head = self.body[0]

        # check border collision
        if head.x > WIDTH // CELL - 1 or head.x < 0 or head.y > HEIGHT // CELL - 1 or head.y < 0:
            return True

        # check collision with snake
        for segment in self.body[1:]:
            if head.x == segment.x and head.y == segment.y:
                return True

        return False

    def draw(self):
        head = self.body[0]
        pygame.draw.rect(screen, colorRED, (head.x * CELL, head.y * CELL, CELL, CELL))
        for segment in self.body[1:]:
            pygame.draw.rect(screen, colorYELLOW, (segment.x * CELL, segment.y * CELL, CELL, CELL))

    def check_collision(self, food):
        head = self.body[0]
        if head.x == food.pos.x and head.y == food.pos.y:
            self.body.append(Point(head.x, head.y))
            food.generate_random_pos(self.body)
            return True
        return False

class Food:
    def __init__(self):
        self.pos = Point(0, 0)

    def draw(self):
        pygame.draw.rect(screen, colorGREEN, (self.pos.x * CELL, self.pos.y * CELL, CELL, CELL))

    def generate_random_pos(self, snake_body):
        while True:
            self.pos.x = random.randint(0, WIDTH // CELL - 1)
            self.pos.y = random.randint(0, HEIGHT // CELL - 1)
            on_snake = any(segment.x == self.pos.x and segment.y == self.pos.y for segment in snake_body)
            if not on_snake:
                break


FPS = 5
clock = pygame.time.Clock()

snake = Snake()
food = Food()
food.generate_random_pos(snake.body)

score = 0
level = 1
FOODS_PER_LEVEL = 3

running = True
game_over = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_over:
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    running = False
            else:
                if event.key == pygame.K_RIGHT and snake.dx == 0:
                    snake.dx = 1
                    snake.dy = 0
                elif event.key == pygame.K_LEFT and snake.dx == 0:
                    snake.dx = -1
                    snake.dy = 0
                elif event.key == pygame.K_DOWN and snake.dy == 0:
                    snake.dx = 0
                    snake.dy = 1
                elif event.key == pygame.K_UP and snake.dy == 0:
                    snake.dx = 0
                    snake.dy = -1

    if not game_over:
        if snake.move():
            game_over = True
        
        # check if food was eaten
        if snake.check_collision(food):
            score += 1 
            if score % FOODS_PER_LEVEL == 0:
                level += 1
                FPS += 2

    screen.fill(colorBLACK)
    draw_grid()

    snake.draw()
    food.draw()

    score_text = font.render(f"Score: {score} | Level: {level}", True, colorWHITE)
    screen.blit(score_text, (10, 10))

    if game_over:
        go_text = font.render("GAME OVER", True, colorRED)
        text_rect = go_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(go_text, text_rect)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()