import os
import sys
# Set the working directory to the folder where main.py is located
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

print(f"✅ Working directory set to: {os.getcwd()}")
import pygame
from pygame import mixer
from fighter import Fighter
from moviepy.editor import VideoFileClip
import numpy as np

mixer.init()
pygame.init()

# This Creates Game Window
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fighter")

# Setting FPS
clock = pygame.time.Clock()
FPS = 60

# Defining Colors
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

# Define Game Variables
intro_count = 3
last_count_update = pygame.time.get_ticks()
score = [0, 0]  # These are Player Scores
round_over = False
round_over_cd = 2000

# Defining King Variables
king_size = 162
king_scale = 4
king_offset = [72, 80]
king_data = [king_size, king_scale, king_offset]
wizard_size = 250
wizard_scale = 3
wizard_offset = [112, 140]
wizard_data = [wizard_size, wizard_scale, wizard_offset]

# Loading Music and Sounds
pygame.mixer.music.load("assets/Audio/fight.mp3")
pygame.mixer.music.set_volume(0.20)
pygame.mixer.music.play(-1, 0.0, 5000)
sword_fx = pygame.mixer.Sound("assets/Audio/sword.wav")
sword_fx.set_volume(1.00)
magic_fx = pygame.mixer.Sound("assets/Audio/magic.wav")
magic_fx.set_volume(0.60)

# Defining Number of steps in each animation
king_animation_steps = [10, 8, 1, 7, 7, 3, 7]
wizard_animation_steps = [8, 8, 2, 8, 8, 3, 7]

# Load the video as the background
clip = VideoFileClip("assets/Images/Test1.mp4")

# Loading Sprite Sheets
king_sheet = pygame.image.load("assets/King Pack/Sprites/warrior.png").convert_alpha()
wizard_sheet = pygame.image.load("assets/Wizard/Sprites/WizardTest.png")

# Load Victory Image
victory_img = pygame.image.load("assets/Images/victory.png").convert_alpha()

# Defining Font
count_font = pygame.font.Font("assets/Fonts/Street.ttf", 15)
score_font = pygame.font.Font("assets/Fonts/Street.ttf", 15)

# Function for Drawing the text
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Function for Drawing Background
def draw_bg():
    current_time = pygame.time.get_ticks() / 1000.0
    frame = clip.get_frame(current_time % clip.duration)
    frame = np.rot90(frame, 1)  # Correct the rotation
    frame = np.flipud(frame)  # Correct the flipping
    frame = pygame.surfarray.make_surface(frame)
    frame = pygame.transform.scale(frame, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(frame, (0, 0))

# Function for Health Bars
def draw_health_bar(health, x, y, player_num):
    ratio = health / 100
    bar_width = 400
    bar_height = 30
    border_width = 2
    pygame.draw.rect(screen, YELLOW, (x - border_width, y - border_width, bar_width + 2 * border_width, bar_height + 2 * border_width))
    pygame.draw.rect(screen, BLACK, (x, y, bar_width, bar_height))
    bar_color = RED if player_num == 1 else BLUE
    health_bar_width = int(bar_width * ratio)
    pygame.draw.rect(screen, bar_color, (x, y, health_bar_width, bar_height))
    


# Creating Two Fighters
GROUND_LEVEL = SCREEN_HEIGHT - 80
fighter_1 = Fighter(1, 200, GROUND_LEVEL, False, king_data, king_sheet, king_animation_steps, sword_fx)
fighter_2 = Fighter(2, 700, GROUND_LEVEL, True, wizard_data, wizard_sheet, wizard_animation_steps, magic_fx)

# Game Loop
run = True
while run:
    clock.tick(FPS)

    # Draws Background
    draw_bg()

    # Show player Stats
    draw_health_bar(fighter_1.displayed_health, 20, 20, 1)
    draw_health_bar(fighter_2.displayed_health, 580, 20, 2)
    draw_text("P1: " + str(score[0]), score_font, RED, 20, 60)
    draw_text("P2: " + str(score[1]), score_font, RED, 580, 60)

    # Updating Countdown
    if intro_count <= 0:
        # Moving Fighters
        fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_2, round_over)
        fighter_2.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_1, round_over)
    else:
        # Displaying the countdown timer
        draw_text(str(intro_count), count_font, YELLOW, SCREEN_WIDTH / 2.15, SCREEN_HEIGHT / 4)

        # Update Countdown
        if (pygame.time.get_ticks() - last_count_update) >= 1000:
            intro_count -= 1
            last_count_update = pygame.time.get_ticks()

    # Update Fighters
    fighter_1.update()
    fighter_2.update()

    # Draw Fighters
    fighter_1.draw(screen)
    fighter_2.draw(screen)

    # Checking for Player Defeat
    if not round_over:
        if not fighter_1.alive:
            score[1] += 1
            round_over = True
            round_over_time = pygame.time.get_ticks()
        elif not fighter_2.alive:
            score[0] += 1
            round_over = True
            round_over_time = pygame.time.get_ticks()
    else:
        # Displaying victory image
        screen.blit(victory_img, (360, 150))
        if pygame.time.get_ticks() - round_over_time > round_over_cd:
            round_over = False
            intro_count = 3
            fighter_1 = Fighter(1, 200, GROUND_LEVEL, False, king_data, king_sheet, king_animation_steps, sword_fx)
            fighter_2 = Fighter(2, 700, GROUND_LEVEL, True, wizard_data, wizard_sheet, wizard_animation_steps, magic_fx)
    # Event Handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # Updating Display
    pygame.display.update()

# Exiting the Game
pygame.quit()
