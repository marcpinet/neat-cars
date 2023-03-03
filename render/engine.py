# ------------------ IMPORTS ------------------


import pygame
import neat
from ai.car_ai import CarAI
from render.car import Car
import time
from render.colors import Color


# ------------------ CLASSES ------------------


class Engine:

    WIDTH = 1900
    HEIGHT = 950
    FPS = 60
    
    DEFAULT_FONT = "comicsansms"
    
    BRUSH_SIZE = 50

    def __init__(self, NEAT_CONFIG_PATH, DEBUG, MAX_SIMULATIONS):
        self.NEAT_CONFIG_PATH = NEAT_CONFIG_PATH
        self.DEBUG = DEBUG
        self.MAX_SIMULATIONS = MAX_SIMULATIONS
        self.title = "Neat Cars"
        pygame.display.set_caption(self.title)
        self.screen = pygame.display.set_mode((Engine.WIDTH, Engine.HEIGHT))
        self.screen.fill(Color.WHITE)  # Fill screen with white
        self.is_running = False
        self.clock = pygame.time.Clock()
        
        self.is_drawing_track = True
        self.is_placing_start_point = False
        self.ai_can_start = False
        self.instructions = [
            "Left click to draw a black line, right click to draw a white line. Once you are done drawing, press SPACE to go to the next step.",
            "Use the directional arrows to rotate. Click to place. CTRL + Z to go back to drawing. Once you've placed the start point, the AI will automatically start running.",
        ]
        self.instruction_index = 0
        self.tmp_screen = None
        self.track = None
        self.car = Car([0, 0])
        self.decided_car_pos = None
        
    def handle_drawing_track(self):
        """Handles the drawing of the track"""
        if(pygame.mouse.get_pressed()[0]):
            pygame.draw.circle(self.screen, Color.BLACK, pygame.mouse.get_pos(), Engine.BRUSH_SIZE)
        elif pygame.mouse.get_pressed()[2]:
            pygame.draw.circle(self.screen, Color.WHITE, pygame.mouse.get_pos(), Engine.BRUSH_SIZE)
            
    def draw_instructions(self):
        """Draws the instructions on the title's screen"""
        pygame.display.set_caption(self.title + " - " + self.instructions[self.instruction_index])
        
    def handle_placing_start_point(self):
        """Handles the placing of the start point"""
        # Car sprite follows mouse until left click
        if not pygame.mouse.get_pressed()[0]:
            self.car.position[0] = pygame.mouse.get_pos()[0] - Car.CAR_SIZE_X / 2
            self.car.position[1] = pygame.mouse.get_pos()[1] - Car.CAR_SIZE_Y / 2
            self.screen.blit(self.car.sprite, (self.car.position[0], self.car.position[1]))
        
        # Once left click is pressed, the car is placed and the AI can start
        else:
            self.ai_can_start = True
            self.is_placing_start_point = False
            self.track = self.screen.copy()
            self.screen.blit(self.car.sprite, (self.car.center[0], self.car.center[1]))
            self.decided_car_pos = [self.car.position[0], self.car.position[1]]
        
    def run(self) -> None:
        self.running = True
        while self.running:
            
            # Events handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                
                # Handle space bar
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        if self.instruction_index == 0:
                            self.is_drawing_track = False
                            self.is_placing_start_point = True
                            self.instruction_index += 1
                            self.tmp_screen = self.screen.copy()
                            
                # Handle CTRL + Z when placing start point
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        if self.is_placing_start_point:
                            self.is_placing_start_point = False
                            self.instruction_index -= 1
                            self.is_drawing_track = True
     
            # Draw instructions
            self.draw_instructions()
            
            # Drawing track
            if self.is_drawing_track:
                self.handle_drawing_track()
                
            if self.is_placing_start_point:
                self.handle_placing_start_point()
            
            # AI
            if self.ai_can_start:
                self.start_ai()
            
            # Update
            self.update()
            
    def start_ai(self):
        """Starts the AI"""
        
        # Load neat config file
        config = neat.config.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            self.NEAT_CONFIG_PATH
        )

        # Create population
        population = neat.Population(config)

        # Add reporters if debug is enabled
        if self.DEBUG:
            population.add_reporter(neat.StdOutReporter(True))
            population.add_reporter(neat.StatisticsReporter())

        # Run simulation for MAX_SIMULATION generations
        population.run(self.run_simulation, self.MAX_SIMULATIONS)
        

    def run_simulation(self, genomes: neat.DefaultGenome, config: neat.Config) -> None:
        """Run the simulation (evolutionarily)

        Args:
            genomes (neat.DefaultGenome): The genomes of the population
            config (neat.Config): The neat configuration
        """

        # Initialize CarAI
        car_ai = CarAI(genomes, config, self.decided_car_pos)
        
        # Start timer
        timer = time.time()

        self.is_running = True
        while self.is_running:
            # Events handler
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()

            # Compute the next generation
            car_ai.compute(genomes, self.track)

            # Break if all cars are dead
            if car_ai.remaining_cars == 0:
                break

            # Refresh counter to exit after CarAI.TIME_LIMIT seconds
            time_left = time.time() - timer
            if time_left > CarAI.TIME_LIMIT:
                break

            # Draw the track and cars which are still alive
            self.screen.blit(self.track, (0, 0))
            for car in car_ai.cars:
                car.draw(self.screen)

            # Refresh and show informations
            t = "Generation: " + str(car_ai.TOTAL_GENERATIONS)
            t2 = "Still Alive: " + str(car_ai.remaining_cars)
            t3 = "Time Left: " + str(round(CarAI.TIME_LIMIT - time_left, 2)) + "s"
            pygame.display.set_caption(self.title + " - " + t + " - " + t2 + " - " + t3)

            # Update the screen
            self.update()
            self.clock.tick(Engine.FPS)

    def update(self):
        pygame.display.update()
        if self.is_placing_start_point:
            self.screen.blit(self.tmp_screen, (0, 0))