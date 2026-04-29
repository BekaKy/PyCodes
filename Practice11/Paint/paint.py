import pygame

pygame.init()

WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
base_layer = pygame.Surface((WIDTH, HEIGHT))

colorRED = (255, 0, 0)
colorBLUE = (0, 0, 255)
colorWHITE = (255, 255, 255)
colorBLACK = (0, 0, 0)

clock = pygame.time.Clock()

LMBpressed = False
THICKNESS = 5

tools = ('rectangle', 'rhombus')

selected_tool = tools[0]
selected_color = colorRED

currX = 0
currY = 0

prevX = 0
prevY = 0

def calculate_square(x1, y1, x2, y2):
    side = min(abs(x1 - x2), abs(y1 - y2))
    if x2 >= x1:
        rect_x = x1
    else:
        rect_x = x1 - side
    if y2 >= y1:
        rect_y = y1
    else:
        rect_y = y1-side
    return pygame.Rect(rect_x, rect_y, side, side)
def calculate_right_triangle(x1, y1, x2, y2):
    width  = abs(x1 - x2)
    height = abs(y1 - y2)
    left_x = min(x1, x2)
    top_y  = min(y1, y2)
    bottom_y = max(y1, y2)
    right_x = max(x1, x2)
    top_point    = (left_x - width, top_y)
    bottom_point  = (left_x - width, bottom_y)
    bottomr_point   = (right_x, bottom_y)
    return (top_point, bottom_point, bottomr_point)
def calculate_equilateral_triangle(x1, y1, x2, y2):
    width  = abs(x1 - x2)
    height = abs(y1 - y2)
    left_x = min(x1, x2)
    top_y  = min(y1, y2)

    top_point    = (left_x + width // 2, top_y)
    right_point  = (left_x + width, top_y + height // 2)
    left_point   = (left_x, top_y + height // 2)

    return (top_point, right_point, left_point)

def calculate_rect(x1, y1, x2, y2):
    return pygame.Rect(min(x1, x2), min(y1, y2), abs(x1 - x2), abs(y1 - y2))


def calculate_rhombus(x1, y1, x2, y2):
    width  = abs(x1 - x2)
    height = abs(y1 - y2)
    left_x = min(x1, x2)
    top_y  = min(y1, y2)

    top_point    = (left_x + width // 2, top_y)
    rigth_point  = (left_x + width, top_y + height // 2)
    bottom_point = (left_x + width // 2, top_y + height)
    left_point   = (left_x, top_y + height // 2)

    return (top_point, rigth_point, bottom_point, left_point)

def draw_figure(surface, color, points):
    prevX, prevY, currX, currY = points # points is a tuple
    if selected_tool == 'rectangle':
        pygame.draw.rect(screen, color, calculate_rect(prevX, prevY, currX, currY), THICKNESS)
    elif selected_tool == 'rhombus':
        pygame.draw.polygon(screen, color, calculate_rhombus(prevX, prevY, currX, currY), THICKNESS)
    elif selected_tool == 'equilateral triangle':
        pygame.draw.polygon(screen, color, calculate_equilateral_triangle(prevX, prevY, currX, currY), THICKNESS)
    elif selected_tool == 'right triangle':
        pygame.draw.polygon(screen, color, calculate_right_triangle(prevX, prevY, currX, currY), THICKNESS)
    elif selected_tool == 'square':
        pygame.draw.rect(screen, color, calculate_square(prevX, prevY, currX, currY), THICKNESS)
    elif selected_tool == 'eraser':
        pygame.draw.rect(screen, colorBLACK, calculate_rect(prevX, prevY, currX, currY))

running = True

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            print("LMB pressed!")
            LMBpressed = True
            prevX = event.pos[0]
            prevY = event.pos[1]
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                selected_color = colorRED
            if event.key == pygame.K_2:
                selected_color = colorBLUE
            if event.key == pygame.K_3:
                selected_color = colorWHITE
            if event.key == pygame.K_4:
                selected_color = colorBLACK
        
        if event.type == pygame.MOUSEMOTION:
            screen.blit(base_layer, (0, 0))
            print("Position of the mouse:", event.pos)
            if LMBpressed:
                currX = event.pos[0]
                currY = event.pos[1]
                draw_figure(screen, selected_color, (prevX, prevY, currX, currY))

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            print("LMB released!")
            LMBpressed = False
            currX = event.pos[0]
            currY = event.pos[1]
            draw_figure(screen, selected_color, (prevX, prevY, currX, currY))
            base_layer.blit(screen, (0, 0))

        if event.type == pygame.KEYDOWN: 
            if event.key == pygame.K_EQUALS:
                print("increased thickness")
                THICKNESS += 1
            if event.key == pygame.K_MINUS:
                print("reduced thickness")
                THICKNESS -= 1
            if event.key == pygame.K_r and event.mod and pygame.KMOD_LSHIFT:
                selected_tool = 'rectangle'
            if event.key == pygame.K_r and event.mod and pygame.KMOD_LCTRL:
                selected_tool = 'rhombus'
            if event.key == pygame.K_s:
                selected_tool = 'right triangle'
            if event.key == pygame.K_t:
                selected_tool = 'equilateral triangle'
            if event.key == pygame.K_e:
                selected_tool = 'eraser'
            if event.key == pygame.K_k:
                selected_tool = 'square'

    pygame.display.flip()
    clock.tick(60)