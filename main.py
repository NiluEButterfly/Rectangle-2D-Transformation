# ==========================================================
# PROJECT NAME  : RECTANGLE 2D TRANSFORMATION GAME
# AUTHOR        :
# DESCRIPTION   :
# ==========================================================

# --- LIBRARIES ---
import pygame
import math
import random
import sys

# --- INITIALIZATION ---
# Initialize Pygame Engine
pygame.mixer.pre_init(44100, -16, 2, 2048) # 2048 adalah ukuran buffer
pygame.mixer.init()
pygame.init()

# Window Settings
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rectangle 2D Transformation Game by NiluEB Development")

# --- STYLES & ASSETS ---
# Color Palette
BLACK, WHITE, RED, GREEN, DARKGRAY = (0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 255, 0), (169, 169, 169)
COLOR1 = "#202020" #Screen Fill Color
COLOR2 = "#222421" #Panel Control Color
COLOR3 = "#1A1C19" #Main Button Color
COLOR4 = "#4C1818" #Back and Quit Button Color

# Sound Settings
bg_music = "assets/bgm.ogg"
current_bgm = None
click_sound = pygame.mixer.Sound("assets/click.wav")
win_sound = pygame.mixer.Sound("assets/win.wav")
wind_sound = pygame.mixer.Sound("assets/wind.wav")

# Font Settings
font_A = pygame.font.Font(None, 60) #Title font
font_a1 = pygame.font.Font(None, 32) #Sub-Title and Button font
font_a2 = pygame.font.Font(None, 26) #Description font

# Time Setting
clock = pygame.time.Clock()

# Image Setting
logo_img = pygame.transform.scale(pygame.image.load("assets/logo.png").convert_alpha(), (250, 250))

# --- GAME DATA & LEVELS ---
# Game Input Transformation Box
input_boxes = { # Boxes to input number of transformation in game() menu
    "translate_x:": pygame.Rect(50, 170, 200, 32),
    "translate_y:": pygame.Rect(50, 220, 200, 32),
    "scale:": pygame.Rect(50, 270, 200, 32),
    "rotate (\u00B0):": pygame.Rect(50, 320, 200, 32) #\u00B0 => Degree Symbol
}
texts_ib = {key: '' for key in input_boxes.keys()} #Input Boxes label memory 

# Input Boxes State Managements
color_inactive = pygame.Color(WHITE) #Input Boxes inactive color
color_active = pygame.Color(DARKGRAY) #Input Boxes active color
active = None #Variable for Input Boxes object
selected_active = 0 #Variable for Input Boxes index

# Animation Managements
animating = False #Flag to indicate if the animation loop is currently active
animation_frames = 75 #Duration for animation of plater box
current_frame = 0 #Step counter for animation of player box until animation_frames
start_points = None #Initial coordinates of player box before animation
end_points = None #Target coordinates of player box after animation

# Game Win Management
sort_count = 0 #Counter of player for sucessfully solve one game 

# Game Difficulty Data
diff = 0
#Difficulty Easy
re_transx = [num for num in range(-7, 7) if num != 0]
re_transy = [num for num in range(-2, 2) if num != 0]
re_scale = [0.5, 2]
#Difficulty Medium
rm_transx = [num for num in range(-11, 11) if num != 0]
rm_transy = [num for num in range(-6, 6) if num != 0]
rm_scale = [0.5, 2, 4]
#Difficulty Hard
rh_transx = [num for num in range(-14, 14) if num != 0]
rh_transy = [num for num in range(-9, 9) if num != 0]
rh_scale = [0.5, 2, 4, 8]

# --- UI DRAWING FUNCTIONS ---
# Convert Coordinates Cartesius
def to_screen_coords(x, y):
    """
    Converting cartesian coordinates to pixel coordinates of Pygame screen
    """
    return ((WIDTH // 2) + 120 + int(x * 30)), (HEIGHT // 2 - int(y * 30))

# Draw General Texts Into Pygame Screen
def draw_text(text, font, color, screen, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    screen.blit(text_obj, text_rect)

# Draw Texts Margin Left
def draw_text_left(text, font, color, screen, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(topleft=(x, y))
    screen.blit(text_obj, text_rect)

def draw_image(image, screen, x, y):
    img_rect = image.get_rect(center=(x, y))
    screen.blit(image, img_rect)

# Draw Layout Menu (Rect)
def draw_lay_menu():
    lay_title = pygame.Rect(WIDTH // 2 - 400 , HEIGHT // 2 - 290, 800, 100)
    lay_menu = pygame.Rect(WIDTH // 2 - 400 , HEIGHT // 2 -170, 800, 450)
    pygame.draw.rect(screen, COLOR2, lay_title)
    pygame.draw.rect(screen, COLOR3, lay_title, 5)
    pygame.draw.rect(screen, COLOR2, lay_menu)
    pygame.draw.rect(screen, COLOR3, lay_menu, 5)

# Draw Coordinates Cartesius
def draw_cartesian():
    lay_cartesian = pygame.Rect(WIDTH // 2 - 330 , HEIGHT // 2 - 300, 901, 601)
    lay_minimenu = pygame.Rect(WIDTH // 2 - 610 , HEIGHT // 2 - 300, 261, 601)
    screen.fill(COLOR1)
    pygame.draw.rect(screen, COLOR2, lay_cartesian)
    pygame.draw.rect(screen, COLOR2, lay_minimenu)
    pygame.draw.line(screen, WHITE, to_screen_coords(-15, 0), to_screen_coords(15, 0), 2)
    pygame.draw.line(screen, WHITE, to_screen_coords(0, -10), to_screen_coords(0, 10), 2)
    for i in range(-9, 10):
        if i != 0:
            pygame.draw.line(screen, WHITE, to_screen_coords(-15, i), to_screen_coords(15, i), 1)
            draw_text(str(i), font_a2, WHITE, screen, WIDTH // 2 + 130, HEIGHT // 2 + 10 - int(i * 30))
    for i in range(-14, 15):
        if i != 0:
            pygame.draw.line(screen, WHITE, to_screen_coords(i, -10), to_screen_coords(i, 10), 1)
            draw_text(str(i), font_a2, WHITE, screen, WIDTH // 2 + 110 + int(i * 30), HEIGHT // 2 + 10)
    pygame.draw.rect(screen, COLOR3, lay_cartesian, 5)
    pygame.draw.rect(screen, COLOR3, lay_minimenu, 5)

# Draw Box Game (for Player and Target)
def draw_box(color, points):
    pygame.draw.polygon(screen, color, [to_screen_coords(*p) for p in points], 2)

# Draw Input Boxes Layout
def draw_input_boxes(text_box, texts):
    global active
    for label, box in text_box.items():
        color = color_active if active == box else color_inactive
        txt_surface = font_a1.render(f"{label} {texts[label]}", True, color)
        width = max(200, txt_surface.get_width() + 10)
        box.w = width
        box.x = 60 if box.x < WIDTH // 2 else WIDTH - box.w - 20
        screen.blit(txt_surface, (box.x + 5, box.y + 5))
        pygame.draw.rect(screen, color, box, 2)

# --- MATH ENGINE FUNCTIONS ---
# Translation Calculation
def translate(points, dx, dy):
    return [(x + dx, y + dy) for x, y in points]

# Scale Calculation
def scale(points, k):
    return [(x * k, y * k) for x, y in points]

# Rotate Calculation
def rotate(points, alpha):
    rad = math.radians(alpha)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    return [(x * cos_a - y * sin_a, x * sin_a + y * cos_a) for x, y in points]

# --- GAME HELPER FUNCTIONS ---
# Playing Background Music
def play_bgm(music_file):
    global current_bgm
    if current_bgm != music_file:
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.set_volume(0.2)
        if not pygame.mixer.music.get_busy(): 
            pygame.mixer.music.play(-1)  # -1 loop forever
        current_bgm = music_file

# Animating Player Box
def animate_movement(start, end):
    global current_frame, player_box, animating
    if current_frame == 0:
        wind_sound.set_volume(0.4)
        wind_sound.play()
    if current_frame <= animation_frames:
        progress = current_frame / animation_frames
        intermediate_points = [(start[i][0] + (end[i][0] - start[i][0]) * progress,
                                start[i][1] + (end[i][1] - start[i][1]) * progress)
                               for i in range(len(start))]
        player_box = intermediate_points
        current_frame += 0.5
    else:
        wind_sound.stop()
        current_frame = 0
        animating = False

# Reset Player Box Coordinates
def reset_boxes(tbox, dx=0, dy=0, k=0, angle=0):
    global player_box, target_box 
    player_box = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    if angle:
        target_box = rotate(tbox, angle)
    elif k:
        target_box = scale(tbox, k)
    else:
        target_box = translate(tbox, dx, dy)

# Handling Input Transformation in Input Boxes
def handle_input(event):
    global start_points, end_points, animating, selected_active, active
    label = next(label for label, box in input_boxes.items() if box == active)
    if event.key == pygame.K_RETURN:
        try:
            value = float(texts_ib[label])
            start_points = player_box
            if label == "translate_x:":
                end_points = translate(player_box, value, 0)
            elif label == "translate_y:":
                end_points = translate(player_box, 0, value)
            elif label == "scale:":
                end_points = scale(player_box, value)
            elif label == "rotate (\u00B0):":
                end_points = rotate(player_box, value)
            animating = True
            texts_ib[label] = ''
        except ValueError:
            pass
    elif event.key == pygame.K_BACKSPACE:
        texts_ib[label] = texts_ib[label][:-1]
    elif event.key == pygame.K_DOWN:
        selected_active = (selected_active + 1) % len(input_boxes)
        keys = list(input_boxes.keys())
        active = input_boxes[keys[selected_active]]
    elif event.key == pygame.K_UP:
        selected_active = (selected_active - 1) % len(input_boxes)
        keys = list(input_boxes.keys())
        active = input_boxes[keys[selected_active]]
    else:
        texts_ib[label] += event.unicode

# Handling Game Logic for Matching a Transformation and Winning Game
def handle_win_condition(sort_count, init_tbox):
    global running_game, diff
    if sort_count < 4:
        click_sound.play()
    sort_count += 1
    if diff == 1:
        if sort_count == 1:
            click_sound.play()
            reset_boxes(init_tbox, 0, random.choice(re_transy))
        elif sort_count == 2:
            click_sound.play()
            reset_boxes(init_tbox, k=random.choice(re_scale))
        elif sort_count == 3:
            click_sound.play()
            reset_boxes(init_tbox, angle=45)
        elif sort_count == 4:
            win_sound.play()
            condition_win()
            running_game = False 
    elif diff == 2:
        if sort_count == 1:
            click_sound.play()
            reset_boxes(init_tbox, random.choice(rm_transy), random.choice(rm_transy))
        elif sort_count == 2:
            click_sound.play()
            reset_boxes(init_tbox, k=random.choice(rm_scale))
            reset_boxes(target_box, angle=45)
        elif sort_count == 3:
            click_sound.play()
            reset_boxes(init_tbox, angle=45)
            reset_boxes(target_box, 0, random.choice(rm_transy))
        elif sort_count == 4:
            win_sound.play()
            condition_win()
            running_game = False 
    elif diff == 3:
        if sort_count == 1:
            click_sound.play()
            reset_boxes(init_tbox, k=random.choice(rh_scale))
            reset_boxes(target_box, random.choice(re_transx), random.choice(re_transy))
        elif sort_count == 2:
            click_sound.play()
            reset_boxes(init_tbox, k=random.choice(rm_scale))
            reset_boxes(target_box, random.choice(rm_transx), random.choice(rm_transy))
        elif sort_count == 3:
            click_sound.play()
            reset_boxes(init_tbox, k=random.choice(rh_scale))
            reset_boxes(target_box, angle=45)
            reset_boxes(target_box, random.choice(rm_transx), 0)
        elif sort_count == 4:
            win_sound.play()
            condition_win()
            running_game = False 
    return sort_count

# --- GAME MENU FUNCTIONS ---
# Main Menu
def main_menu():
    click = False
    while True:
        screen.fill(COLOR1)
        draw_lay_menu()
        draw_text('RECTANGLE 2D TRANSFORMATION', font_A, WHITE, screen, WIDTH // 2, HEIGHT // 6)
        
        mx, my = pygame.mouse.get_pos()
        button_start = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50)
        button_credit = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50)
        button_quit = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 90, 200, 50)
        
        if button_start.collidepoint((mx, my)) and click:
            click_sound.play()
            difficulty()
        if button_credit.collidepoint((mx, my)) and click:
            click_sound.play()
            credits()
        if button_quit.collidepoint((mx, my)) and click:
            pygame.quit()
            sys.exit()
        
        pygame.draw.rect(screen, COLOR3, button_start)
        pygame.draw.rect(screen, COLOR3, button_credit)
        pygame.draw.rect(screen, COLOR4, button_quit)
        
        draw_text('Start', font_a1, WHITE, screen, WIDTH // 2, HEIGHT // 2 - 25)
        draw_text('Credits', font_a1, WHITE, screen, WIDTH // 2, HEIGHT // 2 + 45)
        draw_text('Quit', font_a1, WHITE, screen, WIDTH // 2, HEIGHT // 2 + 115)
        
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click = True
        
        pygame.display.flip()
        clock.tick(60)

# Choose Difficulty Menu
def difficulty():
    global diff 
    running_diff = True
    click = False
    while running_diff:
        screen.fill(COLOR1)
        draw_lay_menu()
        draw_text('DIFFICULTY', font_A, WHITE, screen, WIDTH // 2, HEIGHT // 6)
        mx, my = pygame.mouse.get_pos()
        
        button_easy = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 90, 200, 50)
        button_medium = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 20, 200, 50)
        button_hard = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)
        button_back = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 180, 200, 50)

        if button_easy.collidepoint((mx, my)) and click:
            click_sound.play()
            diff = 1
            running_diff = False
        if button_medium.collidepoint((mx, my)) and click:
            click_sound.play()
            diff = 2
            running_diff = False
        if button_hard.collidepoint((mx, my)) and click:
            click_sound.play()
            diff = 3
            running_diff = False
        if button_back.collidepoint((mx, my)) and click:
            click_sound.play()
            running_diff = False
            main_menu()
        
        pygame.draw.rect(screen, COLOR3, button_easy)
        pygame.draw.rect(screen, COLOR3, button_medium)
        pygame.draw.rect(screen, COLOR3, button_hard)
        pygame.draw.rect(screen, COLOR4, button_back)

        draw_text('Easy', font_a1, WHITE, screen, WIDTH // 2, HEIGHT // 2 - 65)
        draw_text('Medium', font_a1, WHITE, screen, WIDTH // 2, HEIGHT // 2 + 5)
        draw_text('Hard', font_a1, WHITE, screen, WIDTH // 2, HEIGHT // 2 + 75)
        draw_text('Back', font_a1, WHITE, screen, WIDTH // 2, HEIGHT // 2 + 205)
        
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click = True
        
        pygame.display.flip()
        clock.tick(60)
    game()

# Credits Menu
def credits():   
    click = False
    while True:
        screen.fill(COLOR1)
        draw_lay_menu()
        draw_text('CREDITS', font_A, WHITE, screen, WIDTH // 2, HEIGHT // 6)
        mx, my = pygame.mouse.get_pos()

        draw_text('Developed by:', font_a1, WHITE, screen, WIDTH // 2, HEIGHT // 6 + 110)
        draw_image(logo_img, screen, WIDTH // 2, HEIGHT // 6 + 270)

        button_back = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 180, 200, 50)
        if button_back.collidepoint((mx, my)) and click:
            click_sound.play()
            main_menu()
        
        pygame.draw.rect(screen, COLOR4, button_back)
        draw_text('Back', font_a1, WHITE, screen, WIDTH // 2, HEIGHT // 2 + 205)
        
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click = True
        
        pygame.display.flip()
        clock.tick(60)

# Game Menu
def game():
    global player_box, target_box, animating, start_points, end_points, active, selected_active, diff
    player_box = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    init_tbox = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    button_tutorial = pygame.Rect(WIDTH // 2 - 580, HEIGHT // 2 + 90, 200, 50)
    button_reset = pygame.Rect(WIDTH // 2 - 580, HEIGHT // 2 + 150, 200, 50)
    button_back = pygame.Rect(WIDTH // 2 - 580, HEIGHT // 2 + 230, 200, 50)
    sort_count = 0
    if diff == 1:
        target_box = translate(init_tbox, random.choice(re_transx), 0)
        diff_name = 'EASY'
    elif diff == 2:
        target_box = translate(init_tbox, random.choice(rm_transx), random.choice(rm_transy))
        diff_name = 'MEDIUM'
    elif diff == 3:
        target_box = translate(rotate(init_tbox, 45), random.choice(rm_transx), random.choice(rm_transy))
        diff_name = 'HARD'
    running_game = True
    while running_game:
        draw_cartesian()
        draw_box(GREEN, player_box)
        draw_box(RED, target_box)
        draw_input_boxes(input_boxes, texts_ib)
        pygame.draw.rect(screen, COLOR3, button_tutorial)
        pygame.draw.rect(screen, COLOR3, button_reset)
        pygame.draw.rect(screen, COLOR4, button_back)
        draw_text(diff_name, font_a1, WHITE, screen, WIDTH // 2 - 480, HEIGHT // 2 - 260)
        draw_text('Tutorial', font_a1, WHITE, screen, WIDTH // 2 - 480, HEIGHT // 2 + 115)
        draw_text('Reset', font_a1, WHITE, screen, WIDTH // 2 - 480, HEIGHT // 2 + 175)
        draw_text('Main Menu', font_a1, WHITE, screen, WIDTH // 2 - 480, HEIGHT // 2 + 255)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for label, box in input_boxes.items():
                    if box.collidepoint(event.pos):
                        click_sound.play()
                        active = box
                        selected_active = list(input_boxes.values()).index(active)
                        break
                    if button_tutorial.collidepoint(event.pos):
                        click_sound.play()
                        tutorial()
                        break
                    if button_reset.collidepoint(event.pos):
                        click_sound.play()
                        player_box = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
                    if button_back.collidepoint(event.pos):
                        click_sound.play()
                        running_game = False
                        main_menu()
                else:
                    active = None
            if event.type == pygame.KEYDOWN and active:
                handle_input(event)
        if animating:
            animate_movement(start_points, end_points)
        if sorted(player_box) == sorted(target_box):
            sort_count = handle_win_condition(sort_count, init_tbox)
        pygame.display.flip()
        clock.tick(60)
        
    main_menu()

# Tutorial Menu
def tutorial():   
    click = False
    in_credits_run = True
    while in_credits_run:
        screen.fill(COLOR1)
        draw_lay_menu()
        draw_text('TUTORIAL', font_A, WHITE, screen, WIDTH // 2, HEIGHT // 6)
        mx, my = pygame.mouse.get_pos()

        draw_text_left('1. Transform the green player box to match the red box shape to complete a transformation.', font_a2, WHITE, screen, WIDTH // 2 - 370, HEIGHT // 6 + 120)
        draw_text_left('2. If the player complete three transformations, they win the game.', font_a2, WHITE, screen, WIDTH // 2 - 370, HEIGHT // 6 + 150)
        draw_text_left('3. Use translate_x to move the player box horizontally.', font_a2, WHITE, screen, WIDTH // 2 - 370, HEIGHT // 6 + 180)
        draw_text_left('4. Use translate_y to move the player box vertically.', font_a2, WHITE, screen, WIDTH // 2 - 370, HEIGHT // 6 + 210)
        draw_text_left('5. Use scale at the starting coordinates to set the player box scale.', font_a2, WHITE, screen, WIDTH // 2 - 370, HEIGHT // 6 + 240)
        draw_text_left('6. Use rotate at the starting coordinates to rotate the green box.', font_a2, WHITE, screen, WIDTH // 2 - 370, HEIGHT // 6 + 270)
        draw_text_left('7. The rotation angle used is 45\u00B0.', font_a2, WHITE, screen, WIDTH // 2 - 370, HEIGHT // 6 + 300)
        draw_text_left('8. Use the reset button to return the player box to its starting coordinates.', font_a2, WHITE, screen, WIDTH // 2 - 370, HEIGHT // 6 + 330)

        button_back = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 180, 200, 50)
        if button_back.collidepoint((mx, my)) and click:
            click_sound.play()
            in_credits_run = False
            break
        
        pygame.draw.rect(screen, COLOR4, button_back)
        draw_text('Back', font_a1, WHITE, screen, WIDTH // 2, HEIGHT // 2 + 205)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click = True
        pygame.display.flip()
        clock.tick(60)

# Winning Menu
def condition_win():
    click = False
    while True:
        screen.fill(COLOR1)        
        mx, my = pygame.mouse.get_pos()
        text_win = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50)
        button_back = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 90, 200, 50)
        
        if button_back.collidepoint((mx, my)) and click:
            click_sound.play()
            main_menu()
        
        pygame.draw.rect(screen, COLOR3, text_win)
        pygame.draw.rect(screen, COLOR4, button_back)

        draw_text('YOU WIN', font_A, WHITE, screen, WIDTH // 2, HEIGHT // 2 - 25)
        draw_text('Main Menu', font_a1, WHITE, screen, WIDTH // 2, HEIGHT // 2 + 115)
        
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click = True
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    play_bgm(bg_music)
    main_menu()
