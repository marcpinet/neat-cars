# ------------------ IMPORTS ------------------


import pygame
import neat
import time
import numpy as np
from typing import Tuple, List
from ai.car_ai import CarAI
from render.car import Car
from render.colors import Color



# ------------------ CLASSES ------------------


class Track:
    
    BRUSH_LIMIT_SIZE = 25
    
    def __init__(self, width: int, height: int):
        self.surface = pygame.Surface((width, height))
        self.surface.fill(Color.WHITE)
        self.brush_size = 50
        self.last_position = None

    def draw(self, position: Tuple[int, int], color: Tuple[int, int, int]):
        if self.last_position:
            self.draw_interpolated(self.last_position, position, color)
        else:
            pygame.draw.circle(self.surface, color, position, self.brush_size)
        self.last_position = position
        
    def adjust_brush_size(self, amount: int):
        self.brush_size = max(Track.BRUSH_LIMIT_SIZE, self.brush_size + amount)

    def draw_interpolated(self, start: Tuple[int, int], end: Tuple[int, int], color: Tuple[int, int, int]):
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        distance = max(abs(dx), abs(dy))
        
        for i in range(distance):
            x = int(start[0] + float(i) / distance * dx)
            y = int(start[1] + float(i) / distance * dy)
            pygame.draw.circle(self.surface, color, (x, y), self.brush_size)

    def reset_last_position(self):
        self.last_position = None

    def get_surface(self) -> pygame.Surface:
        return self.surface


class Engine:
    WIDTH = 1900
    HEIGHT = 950
    FPS = 60
    DEFAULT_FONT = "comicsansms"

    def __init__(self, neat_config_path: str, debug: bool, max_simulations: int):
        self.neat_config_path = neat_config_path
        self.debug = debug
        self.max_simulations = max_simulations
        self.title = "Neat Cars"
        
        pygame.init()
        pygame.display.set_caption(self.title)
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock = pygame.time.Clock()
        
        self.track = Track(self.WIDTH, self.HEIGHT)
        self.car = Car([0, 0])
        self.decided_car_pos = None
        
        self.state = "drawing_track"
        self.instructions = [
            "Left click to draw a black line, right click to draw a white line. Mouse wheel to adjust brush size. Press SPACE when done.",
            "Use arrow keys to rotate. Click to place. CTRL + Z to go back. AI starts after placing."
        ]
        self.instruction_index = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit(0)
            
            if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                if self.state == "drawing_track":
                    self.state = "placing_start_point"
                    self.instruction_index = 1

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    if self.state == "placing_start_point":
                        self.state = "drawing_track"
                        self.instruction_index = 0

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    self.track.adjust_brush_size(1)
                elif event.button == 5:
                    self.track.adjust_brush_size(-1)

        return True
    
    def handle_drawing_track(self):
        if pygame.mouse.get_pressed()[0]:
            self.track.draw(pygame.mouse.get_pos(), Color.BLACK)
        elif pygame.mouse.get_pressed()[2]:
            self.track.draw(pygame.mouse.get_pos(), Color.WHITE)
        else:
            self.track.reset_last_position()

    def handle_placing_start_point(self):
        if not pygame.mouse.get_pressed()[0]:
            self.car.position = [
                pygame.mouse.get_pos()[0] - Car.CAR_SIZE_X / 2,
                pygame.mouse.get_pos()[1] - Car.CAR_SIZE_Y / 2
            ]
        else:
            self.state = "ai_running"
            self.decided_car_pos = self.car.position.copy()

    def draw(self):
        self.screen.blit(self.track.get_surface(), (0, 0))
        if self.state == "placing_start_point" or self.state == "ai_running":
            self.screen.blit(self.car.sprite, self.car.position)
        
        pygame.display.set_caption(f"{self.title} - {self.instructions[self.instruction_index]}")
        pygame.display.update()

    def start_ai(self):
        config = neat.config.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            self.neat_config_path
        )

        population = neat.Population(config)

        if self.debug:
            population.add_reporter(neat.StdOutReporter(True))
            population.add_reporter(neat.StatisticsReporter())

        population.run(self.run_simulation, self.max_simulations)

    def run_simulation(self, genomes: List[neat.DefaultGenome], config: neat.Config) -> None:
        car_ai = CarAI(genomes, config, self.decided_car_pos)
        timer = time.time()

        while True:
            if not self.handle_events():
                return

            car_ai.compute(self.track.get_surface())

            if car_ai.remaining_cars == 0 or time.time() - timer > CarAI.TIME_LIMIT:
                break

            self.screen.blit(self.track.get_surface(), (0, 0))
            for car in car_ai.cars:
                car.draw(self.screen)

            if car_ai.best_nn:
                car_ai.best_nn.draw(self.screen)

            caption = (f"{self.title} - Generation: {car_ai.TOTAL_GENERATIONS} - "
                       f"Alive: {car_ai.remaining_cars} - "
                       f"Time Left: {round(CarAI.TIME_LIMIT - (time.time() - timer), 2)}s - "
                       f"Best Fitness: {round(car_ai.best_fitness)}")
            pygame.display.set_caption(caption)

            pygame.display.update()
            self.clock.tick(self.FPS)

    def run(self):
        while True:
            if not self.handle_events():
                break

            if self.state == "drawing_track":
                self.handle_drawing_track()
            elif self.state == "placing_start_point":
                self.handle_placing_start_point()
            elif self.state == "ai_running":
                self.start_ai()
                break

            self.draw()
            self.clock.tick(self.FPS)

        pygame.quit()