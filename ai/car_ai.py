# ------------------ IMPORTS ------------------


import neat
from render.car import Car, Action
from render.neural_network.nn import NN
import pygame


# ------------------ CLASSES ------------------

class CarAI:

    TOTAL_GENERATIONS = 0
    TIME_LIMIT = 15

    def __init__(self, genomes: neat.DefaultGenome, config: neat.Config, start_position: list):
        CarAI.TOTAL_GENERATIONS += 1
        
        self.genomes = genomes

        self.cars = []
        self.nets = []
        
        self.best_fitness = 0
        self.nns = []
        self.best_nn = None

        # We create a neural network for every given genome
        for _, genome in genomes:
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            self.nets.append(net)
            genome.fitness = 0
            self.cars.append(Car(start_position))
            self.nns.append(NN(config, genome, (60, 130)))

        self.remaining_cars = len(self.cars)
        self.best_nn = None
        self.best_input = None

    def compute(self, track: pygame.Surface) -> None:
        """Compute the next move of every car and update their fitness

        Args:
            genomes (neat.DefaultGenome): The neat genomes
            track (pygame.Surface): The track on which the car is being drawn
            width (int): The width of the window
        """
        i = 0
        for car, net in zip(self.cars, self.nets):
            
            car_data = car.get_data()

            # Activate the neural network and get the output from the car_data (input)
            output = net.activate(car_data)
            
            # Output gets treated and the car is updated in the next lines
            choice = output.index(max(output))
            
            # Refreshing nodes of all neural networks
            for node in self.nns[i].nodes:
                node.inputs = car_data
                node.output = choice

            # 0: Left
            if choice == Action.TURN_LEFT:
                car.turn_left()

            # 1: Right
            elif choice == Action.TURN_RIGHT:
                car.turn_right()

            # 2: Accelerate
            elif choice == Action.ACCELERATE:
                car.accelerate()

            # 3: Brake
            elif choice == Action.BRAKE:
                car.brake()
                
            i += 1

        # Refresh cars sprites, number of cars which are still alive and update their fitness
        self.remaining_cars = sum(1 for car in self.cars if car.alive)

        # We draw the car if it is still alive
        # We also update the fitness of every car by giving them the reward they got for their last move
        for i, car in enumerate(self.cars):
            if car.alive:
                car.update_sprite(track)
                self.genomes[i][1].fitness += car.get_reward()
                if self.genomes[i][1].fitness > self.best_fitness:
                    self.best_fitness = self.genomes[i][1].fitness
                    self.best_nn = self.nns[i]
