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

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GameOfLife, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, width, height, n_cells_x, n_cells_y, initial_probability=0.2, tick_interval=1.0):
        if self._initialized:
            return
        pygame.init()
        self._initialized = True
        self.width, self.height = width, height
        self.screen = pygame.display.set_mode((width, height))
        self.n_cells_x, self.n_cells_y = n_cells_x, n_cells_y
        self.cell_width = width // n_cells_x
        self.cell_height = height // n_cells_y
        self.initial_probability = initial_probability
        self.game_state = None

        self.instructions_text = [
            "Witaj w symulacji Game of Life",
            "Instrukcje:",
            "- Kliknij przycisk 'Next Generation', aby przejść do następnej generacji.",
            "- Naciśnij spację, aby zatrzymać lub wznowić symulację.",
            "- Naciśnij 's', aby zapisać stan gry.",
            "- Naciśnij 'l', aby wczytać zapisany stan gry.",
            "-Przejdź dalej klikając enter",
        ]

        self.colors = {
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'gray': (128, 128, 128),
            'green': (0, 255, 0),
        }

        self.paused = False
        self.simulation_speed = 10
        self.clock = pygame.time.Clock()
        self.tick_interval = tick_interval
        self.last_tick_time = pygame.time.get_ticks()

        self.button_width, self.button_height = 200, 50
        self.button_x, self.button_y = (width - self.button_width) // 2, height - self.button_height - 10

        self.initialize_grid()

    def initialize_grid(self):
        self.game_state = GridInitializer.initialize_grid(self.n_cells_x, self.n_cells_y, self.initial_probability)

    def show_instructions(self):
        InstructionsDisplayer.show_instructions(self.instructions_text, self.width, self.height, self.screen)

    def draw_button(self):
        ButtonDrawer.draw_button(self.screen, self.button_x, self.button_y, self.button_width, self.button_height,
                                 self.colors['green'], self.colors['black'], "Next Generation")

    def draw_grid(self):
        GridDrawer.draw_grid(self.screen, self.width, self.height, self.cell_width, self.cell_height, self.n_cells_x, self.n_cells_y, self.colors['gray'])

    def next_generation(self):
        self.game_state = GameLogic.next_generation(self.game_state, self.n_cells_x, self.n_cells_y)

    def draw_cells(self):
        CellDrawer.draw_cells(self.screen, self.game_state, self.cell_width, self.cell_height, self.colors['black'])

    def save_game_state(self, filename):
        GameStateSaver.save_game_state(self.game_state, filename)

    def load_game_state(self, filename):
        self.game_state = GameStateLoader.load_game_state(filename)

    def handle_events(self):
        return EventHandler.handle_events(self)

    def run_simulation(self):
        SimulationRunner.run_simulation(self)

# Abstracted Components

class GridInitializer:
    @staticmethod
    def initialize_grid(n_cells_x, n_cells_y, initial_probability):
        return np.random.choice([0, 1], size=(n_cells_x, n_cells_y), p=[1 - initial_probability, initial_probability])

class InstructionsDisplayer:
    @staticmethod
    def show_instructions(instructions_text, width, height, screen):
        font = pygame.font.Font(None, 36)
        line_height = 40
        for i, line in enumerate(instructions_text):
            text = font.render(line, True, (0, 0, 0))
            text_rect = text.get_rect(center=(width // 2, height // 2 + i * line_height))
            screen.blit(text, text_rect)

class ButtonDrawer:
    @staticmethod
    def draw_button(screen, x, y, width, height, color, text_color, text):
        pygame.draw.rect(screen, color, (x, y, width, height))
        font = pygame.font.Font(None, 36)
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
        screen.blit(text_surface, text_rect)

class GridDrawer:
    @staticmethod
    def draw_grid(screen, width, height, cell_width, cell_height, n_cells_x, n_cells_y, color):
        for y in range(0, height, cell_height):
            for x in range(0, width, cell_width):
                cell = pygame.Rect(x, y, cell_width, cell_height)
                pygame.draw.rect(screen, color, cell, 1)

class GameLogic:
    @staticmethod
    def next_generation(game_state, n_cells_x, n_cells_y):
        new_state = np.copy(game_state)

        for y in range(n_cells_y):
            for x in range(n_cells_x):
                n_neighbors = GameLogic.get_neighbor_count(game_state, x, y, n_cells_x, n_cells_y)

                if game_state[x, y] == 1 and (n_neighbors < 2 or n_neighbors > 3):
                    new_state[x, y] = 0
                elif game_state[x, y] == 0 and n_neighbors == 3:
                    new_state[x, y] = 1

        return new_state

    @staticmethod
    def get_neighbor_count(game_state, x, y, n_cells_x, n_cells_y):
        neighbor_count = 0

        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue

                neighbor_x = (x + dx) % n_cells_x
                neighbor_y = (y + dy) % n_cells_y

                neighbor_count += game_state[neighbor_x, neighbor_y]

        return neighbor_count

class CellDrawer:
    @staticmethod
    def draw_cells(screen, game_state, cell_width, cell_height, color):
        for y in range(game_state.shape[1]):
            for x in range(game_state.shape[0]):
                cell = pygame.Rect(x * cell_width, y * cell_height, cell_width, cell_height)
                if game_state[x, y] == 1:
                    pygame.draw.rect(screen, color, cell)

class GameStateSaver:
    @staticmethod
    def save_game_state(game_state, filename):
        with open(filename, 'wb') as file:
            pickle.dump(game_state, file)

class GameStateLoader:
    @staticmethod
    def load_game_state(filename):
        with open(filename, 'rb') as file:
            return pickle.load(file)

class EventHandler:
    @staticmethod
    def handle_events(game_instance):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                EventHandler.handle_mouse_click(game_instance, event.pos)
            elif event.type == pygame.KEYDOWN:
                EventHandler.handle_key_press(game_instance, event.key)
            elif event.type == pygame.MOUSEBUTTONUP:
                EventHandler.handle_button_click(game_instance, event.pos)
        return True

    @staticmethod
    def handle_button_click(game_instance, pos):
        button_rect = pygame.Rect(game_instance.button_x, game_instance.button_y, game_instance.button_width,
                                  game_instance.button_height)
        if button_rect.collidepoint(pos):
            game_instance.next_generation()

    @staticmethod
    def handle_mouse_click(game_instance, pos):
        x, y = pos[0] // game_instance.cell_width, pos[1] // game_instance.cell_height
        game_instance.game_state[x, y] = not game_instance.game_state[x, y]

    @staticmethod
    def handle_key_press(game_instance, key):

        if key == pygame.K_SPACE:
            game_instance.paused = not game_instance.paused
        elif key == pygame.K_s:
             game_instance.save_game_state('saved_game_state.pkl')
        elif key == pygame.K_l:
            game_instance.load_game_state('saved_game_state.pkl')

class SimulationRunner:
    @staticmethod
    def run_simulation(game_instance):
        running = True
        showing_instructions = True

        while running:
            game_instance.screen.fill(game_instance.colors['white'])

            if showing_instructions:
                InstructionsDisplayer.show_instructions(game_instance.instructions_text, game_instance.width, game_instance.height, game_instance.screen)
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        showing_instructions = False
            else:
                game_instance.draw_grid()
                game_instance.draw_cells()
                game_instance.draw_button()
                pygame.display.flip()

            running = game_instance.handle_events()

            if not game_instance.paused:
                current_time = pygame.time.get_ticks()
                if current_time - game_instance.last_tick_time > game_instance.tick_interval * 1000:
                    game_instance.next_generation()
                    game_instance.last_tick_time = current_time

            game_instance.clock.tick(game_instance.simulation_speed)

        pygame.quit()


if __name__ == "__main__":
    width, height = 900, 600
    n_cells_x, n_cells_y = 40, 30
    tick_interval = 0.8

    game0 = GameOfLife(width, height, n_cells_x, n_cells_y, tick_interval=tick_interval)

    game0.run_simulation()

