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

class GameOfLife:
    def __init__(self, width, height, n_cells_x, n_cells_y, initial_probability=0.2, tick_interval=1.0):
        # Initialize Pygame
        pygame.init()
        # Will be initialized in initialize_grid
        self.game_state = None
        # Screen dimensions
        self.width, self.height = width, height
        self.screen = pygame.display.set_mode((width, height))
        # Grid dimensions
        self.n_cells_x, self.n_cells_y = n_cells_x, n_cells_y
        self.cell_width = width // n_cells_x
        self.cell_height = height // n_cells_y
        self.initial_probability = initial_probability

        self.instructions_text = [
            "Witaj w symulacji Gry w życie!",
            "Instrukcje:",
            "- Kliknij przycisk 'Next Generation', aby przejść do następnej generacji.",
            "- Naciśnij spację, aby zatrzymać lub wznowić symulację.",
            "- Naciśnij 's', aby zapisać stan gry.",
            "- Naciśnij 'l', aby wczytać zapisany stan gry.",
        ]
        # Colors
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.gray = (128, 128, 128)
        self.green = (0, 255, 0)

        # Simulation control variables
        self.paused = False
        # Adjust the speed of the simulation
        self.simulation_speed = 10

        self.clock = pygame.time.Clock()
        self.tick_interval = tick_interval
        self.last_tick_time = pygame.time.get_ticks()

        # Button dimensions
        self.button_width, self.button_height = 200, 50
        self.button_x, self.button_y = (width - self.button_width) // 2, height - self.button_height - 10
        # Initialize the grid
        self.initialize_grid()

    def initialize_grid(self):
        self.game_state = np.random.choice([0, 1], size=(self.n_cells_x, self.n_cells_y),
                                           p=[1 - self.initial_probability, self.initial_probability])

    def show_instructions(self):
        font = pygame.font.Font(None, 36)
        line_height = 40
        for i, line in enumerate(self.instructions_text):
            text = font.render(line, True, self.black)
            text_rect = text.get_rect(center=(self.width // 2, self.height // 2 + i * line_height))
            self.screen.blit(text, text_rect)

    def draw_button(self):
        pygame.draw.rect(self.screen, self.green, (self.button_x, self.button_y, self.button_width, self.button_height))
        font = pygame.font.Font(None, 36)
        text = font.render("Next Generation", True, self.black)
        text_rect = text.get_rect(
            center=(self.button_x + self.button_width // 2, self.button_y + self.button_height // 2))
        self.screen.blit(text, text_rect)

    def draw_grid(self):
        for y in range(0, self.height, self.cell_height):
            for x in range(0, self.width, self.cell_width):
                cell = pygame.Rect(x, y, self.cell_width, self.cell_height)
                pygame.draw.rect(self.screen, self.gray, cell, 1)

    def next_generation(self):
        new_state = np.copy(self.game_state)

        for y in range(self.n_cells_y):
            for x in range(self.n_cells_x):
                n_neighbors = self.game_state[(x - 1) % self.n_cells_x, (y - 1) % self.n_cells_y] + \
                              self.game_state[(x) % self.n_cells_x, (y - 1) % self.n_cells_y] + \
                              self.game_state[(x + 1) % self.n_cells_x, (y - 1) % self.n_cells_y] + \
                              self.game_state[(x - 1) % self.n_cells_x, (y) % self.n_cells_y] + \
                              self.game_state[(x + 1) % self.n_cells_x, (y) % self.n_cells_y] + \
                              self.game_state[(x - 1) % self.n_cells_x, (y + 1) % self.n_cells_y] + \
                              self.game_state[(x) % self.n_cells_x, (y + 1) % self.n_cells_y] + \
                              self.game_state[(x + 1) % self.n_cells_x, (y + 1) % self.n_cells_y]

                if self.game_state[x, y] == 1 and (n_neighbors < 2 or n_neighbors > 3):
                    new_state[x, y] = 0
                elif self.game_state[x, y] == 0 and n_neighbors == 3:
                    new_state[x, y] = 1

        self.game_state = new_state

    def draw_cells(self):
        for y in range(self.n_cells_y):
            for x in range(self.n_cells_x):
                cell = pygame.Rect(x * self.cell_width, y * self.cell_height, self.cell_width, self.cell_height)
                if self.game_state[x, y] == 1:
                    pygame.draw.rect(self.screen, self.black, cell)

    def save_game_state(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self.game_state, file)

    def load_game_state(self, filename):
        with open(filename, 'rb') as file:
            self.game_state = pickle.load(file)

    def run_simulation(self):
        running = True
        showing_instructions = True

        while running:
            self.screen.fill(self.white)

            if showing_instructions:
                self.show_instructions()
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        showing_instructions = False
            else:
                self.draw_grid()
                self.draw_cells()
                self.draw_button()
                pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.button_x <= event.pos[0] <= self.button_x + self.button_width \
                            and self.button_y <= event.pos[1] <= self.button_y + self.button_height:
                        self.next_generation()
                    else:
                        x, y = event.pos[0] // self.cell_width, event.pos[1] // self.cell_height
                        self.game_state[x, y] = not self.game_state[x, y]
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_s:
                        self.save_game_state('saved_game_state.pkl')
                    elif event.key == pygame.K_l:
                        self.load_game_state('saved_game_state.pkl')

            if not self.paused:
                current_time = pygame.time.get_ticks()
                if current_time - self.last_tick_time > self.tick_interval * 1000:
                    self.next_generation()
                    self.last_tick_time = current_time

            self.clock.tick(self.simulation_speed)

# Usage
if __name__ == "__main__":
    width, height = 900, 600
    n_cells_x, n_cells_y = 40, 30

    # Set the tick interval in seconds
    tick_interval = 0.5

    game = GameOfLife(width, height, n_cells_x, n_cells_y, tick_interval=tick_interval)
    game.run_simulation()
    pygame.quit()