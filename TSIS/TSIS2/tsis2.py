import pygame
import datetime

pygame.init()

WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
base_layer = pygame.Surface((WIDTH, HEIGHT))

colorRED = (255, 0, 0)
colorBLUE = (0, 0, 255)
colorWHITE = (255, 255, 255)
colorBLACK = (0, 0, 0)

pygame.font.init()
font = pygame.font.SysFont(None, 36)

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

# typing text init
text_mode = False
text_input = ""
text_pos = (0, 0)

def calculate_square(x1, y1, x2, y2):
    side = min(abs(x1 - x2), abs(y1 - y2))
    if x2 >= x1:
        rect_x = x1
    else:
        rect_x = x1 - side
    if y2 >= y1:
        rect_y = y1
    else:
        rect_y = y1 - side
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


def flood_fill(surface, start_pos, fill_color):
    fill_color_mapped = surface.map_rgb(fill_color)
    target_color = surface.get_at(start_pos)    
    if target_color == fill_color_mapped:
        return
    width, height = surface.get_size()
    queue = [start_pos]                         # implementing depth fist search
    surface.lock()
    while queue:
        x, y = queue.pop() 
        if surface.get_at((x, y)) == target_color:
            surface.set_at((x, y), fill_color_mapped)
            if x > 0 and surface.get_at((x - 1, y)) == target_color:
                queue.append((x - 1, y))
            if x < width - 1 and surface.get_at((x + 1, y)) == target_color:
                queue.append((x + 1, y))
            if y > 0 and surface.get_at((x, y - 1)) == target_color:
                queue.append((x, y - 1))
            if y < height - 1 and surface.get_at((x, y + 1)) == target_color:
                queue.append((x, y + 1))
    surface.unlock()

def draw_figure(surface, color, points):
    prevX, prevY, currX, currY = points
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
    elif selected_tool == 'line':
        pygame.draw.line(screen, color, (prevX, prevY), (currX, currY), THICKNESS)
    elif selected_tool == 'eraser':
        pygame.draw.rect(screen, colorBLACK, calculate_rect(prevX, prevY, currX, currY))

running = True


# p = brush, l = line, f = fill, a = text, e = eraser
# t = equil triangle, k = square
# 5 = small 6 = medium 7 = large
# 1 = red, 2 blue, 3 white, 4 black

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        # typing text
        if text_mode:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    txt_surface = font.render(text_input, True, selected_color)
                    base_layer.blit(txt_surface, text_pos)
                    text_mode = False
                elif event.key == pygame.K_ESCAPE:
                    text_mode = False
                elif event.key == pygame.K_BACKSPACE:
                    text_input = text_input[:-1]
                else:
                    text_input += event.unicode
            continue

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if selected_tool == 'text':
                text_mode = True
                text_input = ""
                text_pos = event.pos
            elif selected_tool == 'fill':
                flood_fill(base_layer, event.pos, selected_color)
            else:
                LMBpressed = True
                prevX = event.pos[0]
                prevY = event.pos[1]
        # color and size
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1: 
                selected_color = colorRED
            if event.key == pygame.K_2: 
                selected_color = colorBLUE
            if event.key == pygame.K_3: 
                selected_color = colorWHITE
            if event.key == pygame.K_4: 
                selected_color = colorBLACK
            if event.key == pygame.K_5: 
                THICKNESS = 2
            if event.key == pygame.K_6: 
                THICKNESS = 5
            if event.key == pygame.K_7: 
                THICKNESS = 10

            if event.key == pygame.K_EQUALS:
                THICKNESS += 1
                print(f"increased thickness: {THICKNESS}")
            if event.key == pygame.K_MINUS:
                THICKNESS = max(1, THICKNESS - 1)
                print(f"reduced thickness: {THICKNESS}")
            # selecting tools
            if event.key == pygame.K_r and event.mod and pygame.KMOD_LSHIFT:
                selected_tool = 'rectangle'
            if event.key == pygame.K_r and event.mod and pygame.KMOD_LCTRL:
                selected_tool = 'rhombus'
            if event.key == pygame.K_s:
                if event.mod & pygame.KMOD_CTRL:
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"canvas_{timestamp}.png"
                    pygame.image.save(base_layer, filename)
            if event.key == pygame.K_o:
                selected_tool = 'right triangle'
            if event.key == pygame.K_t: 
                selected_tool = 'equilateral triangle'
            if event.key == pygame.K_e: 
                selected_tool = 'eraser'
            if event.key == pygame.K_k: 
                selected_tool = 'square'
            if event.key == pygame.K_p: 
                selected_tool = 'pencil'
            if event.key == pygame.K_l: 
                selected_tool = 'line'
            if event.key == pygame.K_f: 
                selected_tool = 'fill'
            if event.key == pygame.K_a: 
                selected_tool = 'text'
        # brush
        if event.type == pygame.MOUSEMOTION:
            if LMBpressed and selected_tool == 'pencil':
                pygame.draw.line(base_layer, selected_color, (prevX, prevY), event.pos, THICKNESS)
                prevX, prevY = event.pos
            screen.blit(base_layer, (0, 0))            
            if LMBpressed and selected_tool not in ('pencil', 'fill', 'text'):
                currX = event.pos[0]
                currY = event.pos[1]
                draw_figure(screen, selected_color, (prevX, prevY, currX, currY))

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if LMBpressed:                
                LMBpressed = False
                currX = event.pos[0]
                currY = event.pos[1]
                if selected_tool not in ('pencil', 'fill', 'text'):
                    draw_figure(screen, selected_color, (prevX, prevY, currX, currY))
                    base_layer.blit(screen, (0, 0))
    # text previewing
    if text_mode:
        txt_surface = font.render(text_input, True, selected_color)
        screen.blit(txt_surface, text_pos)

    pygame.display.flip()
    clock.tick(60)