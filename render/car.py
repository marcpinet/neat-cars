# ------------------ IMPORTS ------------------


import pygame
import math
from render.colors import Color
import numpy as np


# ------------------ GLOBAL VARIABLES  ------------------


CAR_SPRITE_PATH = "assets/car.png"
DEAD_CAR_SPRITE_PATH = "assets/dead_car.png"


# ------------------ CLASSES ------------------


class Action:
    TURN_LEFT = 0
    TURN_RIGHT = 1
    ACCELERATE = 2
    BRAKE = 3

class Car:

    CAR_SIZE_X = 60
    CAR_SIZE_Y = 60

    MINIMUM_SPEED = 10
    ANGLE_INCREMENT = 10
    SPEED_INCREMENT = 1

    DEFAULT_SPEED = 10
    DEFAULT_ANGLE = 0

    COLLISION_SURFACE_COLOR = Color.WHITE

    DRAW_SENSORS = True
    SENSORS_DRAW_DISTANCE = 1920

    def __init__(self, start_position: list):
        # The _sprite is the untouched sprite (not rotated) while the sprite is the one which will be moved around
        self._sprite = pygame.image.load(CAR_SPRITE_PATH).convert_alpha()

        # Scale Sprite
        self._sprite = pygame.transform.scale(
            self._sprite, (Car.CAR_SIZE_X, Car.CAR_SIZE_Y)
        )

        # Assigning the current sprite to this variable sprite (the one which will be rotated) we need this to avoid out of memory errors from pygame
        self.sprite = self._sprite

        self.position = start_position.copy()

        self.angle = Car.DEFAULT_ANGLE
        self.speed = Car.DEFAULT_SPEED

        self.center = [
            self.position[0] + Car.CAR_SIZE_X / 2,
            self.position[1] + Car.CAR_SIZE_Y / 2
        ]  # Calculate Center

        self.sensors = []
        self.alive = True
        self.has_been_rendered_as_dead = False
        
        self.driven_distance = 0
        self.malus = 0

    def draw(self, track: pygame.Surface) -> None:
        """Draw the car on the track (and its sensors if enabled)

        Args:
            track (pygame.Surface): The track on which the car will be drawn
        """
        
        if self.alive:
            track.blit(self.sprite, self.position)
        else:
            # Change the sprite color of the car to a black and white one
            if not self.has_been_rendered_as_dead:
                self._sprite = pygame.image.load(DEAD_CAR_SPRITE_PATH).convert_alpha()
                self._sprite = pygame.transform.scale(
                    self._sprite, (Car.CAR_SIZE_X, Car.CAR_SIZE_Y)
                )
                self.update_center()
                self.has_been_rendered_as_dead = True
            track.blit(self.sprite, self.position)

        # Draw the car's sensors
        if Car.DRAW_SENSORS and self.alive:
            for sensor in self.sensors:
                position = sensor[0]
                pygame.draw.line(track, Color.GREEN,
                                 self.center, position, 2)
                pygame.draw.circle(track, Color.RED, position, 4)

    def check_collision(self, track: pygame.Surface) -> bool:
        """Check if the car is colliding with the track (by using a color system)

        Args:
            track (pygame.Surface): The track on which the car is being drawn
        """
        track_x = track.get_width()
        track_y = track.get_height()
        for point in self.corners:
            if point[0] < 0 or point[0] >= track_x or point[1] < 0 or point[1] >= track_y:
                self.alive = False
                return True

            elif track.get_at((int(point[0]), int(point[1]))) == Car.COLLISION_SURFACE_COLOR:
                self.alive = False
                return True

        return False

    def refresh_corners_positions(self) -> None:
        """Refresh the corners' current positions of the car (used for collision detection)"""
        length_x = 0.5 * Car.CAR_SIZE_X
        length_y = 0.5 * Car.CAR_SIZE_Y

        corner1 = math.radians(360 - (self.angle + 30))
        corner2 = math.radians(360 - (self.angle + 150))
        corner3 = math.radians(360 - (self.angle + 210))
        corner4 = math.radians(360 - (self.angle + 330))

        left_top = [
            self.center[0] + math.cos(corner1) * length_x,
            self.center[1] + math.sin(corner1) * length_y
        ]
        right_top = [
            self.center[0] + math.cos(corner2) * length_x,
            self.center[1] + math.sin(corner2) * length_y
        ]
        left_bottom = [
            self.center[0] + math.cos(corner3) * length_x,
            self.center[1] + math.sin(corner3) * length_y
        ]
        right_bottom = [
            self.center[0] + math.cos(corner4) * length_x,
            self.center[1] + math.sin(corner4) * length_y
        ]

        self.corners = [left_top, right_top, left_bottom, right_bottom]

    def check_sensor(self, degree: int, track: pygame.Surface) -> None:
        """Check the distance between the center of the car and the collision surface to create the sensors

        Args:
            degree (int): The degree (angle) of the sensor from the car's center
            track (pygame.Surface): The track on which the car is being drawn
        """

        # Convert degree to radians because math.cos and math.sin use radians
        radians = math.radians(360 - (self.angle + degree))
        cos = math.cos(radians)
        sin = math.sin(radians)
        length = 1

        x, y = int(self.center[0]), int(self.center[1])
        track_x = track.get_width()
        track_y = track.get_height()

        # While the collision surface is not reached, increment the length of the sensor
        while x < track_x and y < track_y and x > 0 and y > 0 and track.get_at((x, y)) != Car.COLLISION_SURFACE_COLOR:
            x = int(self.center[0] + cos * length)
            y = int(self.center[1] + sin * length)

            # If the max length of a sensor is reached, break the loop
            if length > Car.SENSORS_DRAW_DISTANCE:
                break

            length += 1

        # Distance calculation between the center of the car and the collision surface
        distance = int(math.hypot(x - self.center[0], y - self.center[1]))
        self.sensors.append([(x, y), distance])

    def update_center(self) -> None:
        """Update the center of the car after a rotation (when it turns left or right)"""
        sprite_as_rect = self._sprite.get_rect()
        rotated_sprite = pygame.transform.rotate(self._sprite, self.angle)
        sprite_as_rect.center = rotated_sprite.get_rect().center
        self.sprite = rotated_sprite.subsurface(sprite_as_rect)
        # Calculate New Center
        self.center = [
            int(self.position[0]) + Car.CAR_SIZE_X / 2,
            int(self.position[1]) + Car.CAR_SIZE_Y / 2
        ]

    def update_sprite(self, track: pygame.Surface) -> None:
        """Update the sprite of the car and its new informations (position, center, sensors, etc.)"""

        # Update the sprite
        self.update_center()

        # Radians, cos, sin
        radians = math.radians(360 - self.angle)
        cos = math.cos(radians)
        sin = math.sin(radians)

        # Move car to new position
        self.position[0] += cos * self.speed
        self.position[1] += sin * self.speed

        # Update the driven distance with the speed
        self.driven_distance += self.speed

        # Calculate Corners
        self.refresh_corners_positions()

        # Check collisions
        self.check_collision(track)

        # Clear radars and rewrite them (-90, -45, 0, 45, 90)
        self.sensors.clear()
        for sensor_angle in range(-90, 90 + 1, 45):
            self.check_sensor(sensor_angle, track)

    def get_data(self) -> list[int]:
        """Get the data of the car's sensors

        Returns:
            list[int]: The list of the sensors' distances
        """
        # Get distances to border
        distances = [int(sensor[1]) for sensor in self.sensors]

        # Ensure list has five elements (to correspond to)
        distances += [0] * (5 - len(distances))

        return distances

    def get_reward(self) -> float:
        """Get the reward of the car

        Returns:
            float: The decided reward
        """
        # The reward has been decided to be the driven distance so the car will try to drive as far as possible
        # Make it more human readable
        return (self.driven_distance - self.malus) / 10000
    
    def accelerate(self) -> None:
        """Accelerate the car"""
        self.speed += Car.SPEED_INCREMENT

    def brake(self) -> None:
        """Brake the car"""
        if self.speed > Car.MINIMUM_SPEED:  # We don't want to go backwards nor going too slow
            self.speed -= Car.SPEED_INCREMENT
        else:  
            self.speed = Car.MINIMUM_SPEED
            self.malus += 1  # Malus for going too slow
        
    def turn_left(self) -> None:
        """Turn the car to the left"""
        self.angle += Car.ANGLE_INCREMENT
        
    def turn_right(self) -> None:
        """Turn the car to the right"""
        self.angle -= Car.ANGLE_INCREMENT