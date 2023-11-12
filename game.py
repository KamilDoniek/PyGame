# To create & start using python venv:
#       python -m venv venv
#       source venv/bin/activate

# Intall specific modules with pip:
# f.e.:   pip install pygame

# Requirements
# 1. Make simulation real time
# 2. Add pause / resume logic
# 3. Add save / load logic

# High-level logic
# 1. Create and init the simulation grid (Connect with tick)
# 2. Start the simulation with a tick interval of <n> seconds
# 3. At each tick:
#   3.1. Update the grid - loop over each element of the board
#   3.2. Render new generation

# General approach
# 1. Plan & write down the general workflow
#  1.1. Define Input&Output 
#  1.2. Consider adding validation
# 2. Separate the main algorithms / actors in the code. Try to abstract as much common code as possible
# 3. Define communication between the objects
# 4. List the patterns you could apply
# 5. Build PoCs (Proof of concepts). Try to separate implementation of specific steps. Prepare smaller modules
#    and combine them into a complete application
# 6. Refine if needed

# Deadline - 15th of December 2023
# Mail with: 
# 1. short screen recording demonstrating the new features
# 2. Linked code
# 3. Short description of the changes. Which design patterns you used and how you applied them. 

import pygame
import numpy as np
import pickle

instructions_text = [
    "Witaj w symulacji Gry w życie!",
    "Instrukcje:",
    "- Kliknij przycisk 'Next Generation', aby przejść do następnej generacji.",
    "- Naciśnij spację, aby zatrzymać lub wznowić symulację.",
    "- Naciśnij 's', aby zapisać stan gry.",
    "- Naciśnij 'l', aby wczytać zapisany stan gry.",
]
# Initialize Pygame
pygame.init()

# Screen dimensions
width, height = 900, 600
screen = pygame.display.set_mode((width, height))

# Grid dimensions
n_cells_x, n_cells_y = 40, 30
cell_width = width // n_cells_x
cell_height = height // n_cells_y

# Game state
game_state = np.random.choice([0, 1], size=(n_cells_x, n_cells_y), p=[0.8, 0.2])

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
gray = (128, 128, 128)
green = (0, 255, 0)

# Button dimensions
button_width, button_height = 200, 50
button_x, button_y = (width - button_width) // 2, height - button_height - 10


# Simulation control variables
paused = False
# Adjust the speed of the simulation
simulation_speed = 10

def show_instructions():
    font = pygame.font.Font(None, 36)
    line_height = 40
    for i, line in enumerate(instructions_text):
        text = font.render(line, True, black)
        text_rect = text.get_rect(center=(width // 2, height // 2 + i * line_height))
        screen.blit(text, text_rect)
def draw_button():
    pygame.draw.rect(screen, green, (button_x, button_y, button_width, button_height))
    font = pygame.font.Font(None, 36)
    text = font.render("Next Generation", True, black)
    text_rect = text.get_rect(center=(button_x + button_width // 2, button_y + button_height // 2))
    screen.blit(text, text_rect)

def draw_grid():
    for y in range(0, height, cell_height):
        for x in range(0, width, cell_width):
            cell = pygame.Rect(x, y, cell_width, cell_height)
            pygame.draw.rect(screen, gray, cell, 1)

def next_generation():
    global game_state
    new_state = np.copy(game_state)

    for y in range(n_cells_y):
        for x in range(n_cells_x):
            n_neighbors = game_state[(x - 1) % n_cells_x, (y - 1) % n_cells_y] + \
                          game_state[(x)     % n_cells_x, (y - 1) % n_cells_y] + \
                          game_state[(x + 1) % n_cells_x, (y - 1) % n_cells_y] + \
                          game_state[(x - 1) % n_cells_x, (y)     % n_cells_y] + \
                          game_state[(x + 1) % n_cells_x, (y)     % n_cells_y] + \
                          game_state[(x - 1) % n_cells_x, (y + 1) % n_cells_y] + \
                          game_state[(x)     % n_cells_x, (y + 1) % n_cells_y] + \
                          game_state[(x + 1) % n_cells_x, (y + 1) % n_cells_y]

            if game_state[x, y] == 1 and (n_neighbors < 2 or n_neighbors > 3):
                new_state[x, y] = 0
            elif game_state[x, y] == 0 and n_neighbors == 3:
                new_state[x, y] = 1

    game_state = new_state

def draw_cells():
    for y in range(n_cells_y):
        for x in range(n_cells_x):
            cell = pygame.Rect(x * cell_width, y * cell_height, cell_width, cell_height)
            if game_state[x, y] == 1:
                pygame.draw.rect(screen, black, cell)
def save_game_state(filename):
    with open(filename, 'wb') as file:
        pickle.dump(game_state, file)

def load_game_state(filename):
    global game_state
    with open(filename, 'rb') as file:
        game_state = pickle.load(file)

running = True
showing_instructions = True
clock = pygame.time.Clock()

while running:
    screen.fill(white)

    if showing_instructions:
        show_instructions()
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                showing_instructions = False
    else:
        draw_grid()
        draw_cells()
        draw_button()
        pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if button_x <= event.pos[0] <= button_x + button_width and button_y <= event.pos[1] <= button_y + button_height:
                next_generation()
            else:
                x, y = event.pos[0] // cell_width, event.pos[1] // cell_height
                game_state[x, y] = not game_state[x, y]
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key == pygame.K_s:
                save_game_state('saved_game_state.pkl')
            elif event.key == pygame.K_l:
                load_game_state('saved_game_state.pkl')

    if not paused:
        next_generation()

    clock.tick(simulation_speed)

pygame.quit()

