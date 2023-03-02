# ------------------ IMPORTS ------------------


import neat
from render.car import Car
import pygame


# ------------------ CLASSES ------------------

class CarAI:

    TOTAL_GENERATIONS = 0
    TIME_LIMIT = 10

    def __init__(self, genomes: neat.DefaultGenome, config: neat.Config, start_position: list):
        CarAI.TOTAL_GENERATIONS += 1

        self.cars = []
        self.nets = []

        # We create a neural network for every given genome
        for _, genome in genomes:
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            self.nets.append(net)
            genome.fitness = 0
            self.cars.append(Car(start_position))

        self.remaining_cars = len(self.cars)

    def compute(self, genomes: neat.DefaultGenome, track: pygame.Surface) -> None:
        """Compute the next move of every car and update their fitness

        Args:
            genomes (neat.DefaultGenome): The neat genomes
            track (pygame.Surface): The track on which the car is being drawn
            width (int): The width of the window
        """
        for car, net in zip(self.cars, self.nets):

            # Activate the neural network and get the output
            output = net.activate(car.get_data())
            # Output gets treated and the car is updated in the next lines
            choice = output.index(max(output))

            # 0: Left
            if choice == 0:
                car.angle -= Car.ANGLE_INCREMENT

            # 1: Right
            elif choice == 1:
                car.angle += Car.ANGLE_INCREMENT

            # 2: Accelerate
            elif choice == 2:
                car.speed += Car.SPEED_INCREMENT

            # 3: Brake
            elif choice == 3:
                if car.speed > Car.MINIMUM_SPEED:  # We don't want to go backwards nor going too slow
                    car.speed -= Car.SPEED_INCREMENT
                else:  # If we are going too slow, we accelerate ; that's greedy but it forces the car to maintain a constant speed
                    car.speed += Car.SPEED_INCREMENT

        # Refresh cars sprites, number of cars which are still alive and update their fitness
        self.remaining_cars = sum(1 for car in self.cars if car.alive)

        # We draw the car if it is still alive
        # We also update the fitness of every car by giving them the reward they got for their last move
        for i, car in enumerate(self.cars):
            if car.alive:
                car.update_sprite(track)
                genomes[i][1].fitness += car.get_reward()
