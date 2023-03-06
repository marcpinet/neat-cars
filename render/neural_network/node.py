# ------------------ IMPORTS ------------------


import pygame
from render.colors import Color
from render.car import Action


# ------------------ GLOBAL VARIABLES ------------------


pygame.font.init()


# ------------------ CLASSES AND FUNCTIONS ------------------


def decode(best_outputs: list, index: int) -> bool:
    if index == Action.TURN_LEFT and best_outputs[Action.TURN_LEFT] > best_outputs[Action.TURN_RIGHT]:
        return True
    elif index == Action.TURN_RIGHT and best_outputs[Action.TURN_RIGHT] > best_outputs[Action.TURN_LEFT]:
        return True
    elif index == Action.ACCELERATE and best_outputs[Action.ACCELERATE] > best_outputs[Action.BRAKE]:
        return True
    elif index == Action.BRAKE and best_outputs[Action.BRAKE] > best_outputs[Action.ACCELERATE]:
        return True

    return False


class NodeType:
    INPUT = 0
    HIDDEN = 1
    OUTPUT = 2


class Node:
    RADIUS = 20
    SPACING = 5
    LAYER_SPACING = 100
    CONNECTION_WIDTH = 1
    FONT = pygame.font.SysFont("comicsans", 15)

    def __init__(self, id: int, x: int, y: int, type: NodeType, colors: list[Color], label: str = "", index: int = 0):
        self.id = id
        self.x = x
        self.y = y
        self.type = type
        self.colors = colors
        self.label = label
        self.index = index
        self.best_inputs = [0, 0, 0, 0, 0]
        self.best_outputs = [0, 0, 0, 0]

    def draw(self, screen: pygame.Surface):

        color_scheme = self.get_color()

        pygame.draw.circle(
            screen, color_scheme[0], (self.x, self.y), Node.RADIUS)
        pygame.draw.circle(
            screen, color_scheme[1], (self.x, self.y), Node.RADIUS - 2)

        if self.type != NodeType.HIDDEN:
            text = Node.FONT.render(self.label, 1, Color.BLACK)
            screen.blit(text, (self.x + (self.type-1) * ((text.get_width()
                            if not self.type else 0) + Node.RADIUS + 5), self.y - text.get_height()/2))

    def get_color(self):
        if self.type == NodeType.INPUT:
            v = self.best_inputs[self.index]
            ratio = 1 - (min(v / 100, 1))
        elif self.type == NodeType.OUTPUT:
            ratio = 1 if decode(self.best_outputs, self.index) else 0
        else:
            ratio = 0

        color = [[0, 0, 0], [0, 0, 0]]
        for i in range(3):
            color[0][i] = int(ratio * (self.colors[1][i] -
                            self.colors[3][i]) + self.colors[3][i])
            color[1][i] = int(ratio * (self.colors[0][i] -
                            self.colors[2][i]) + self.colors[2][i])
        return color


class Connection:
    def __init__(self, input, output, wt):
        self.input = input
        self.output = output
        self.wt = wt

    def draw(self, screen):
        color = Color.GREEN if self.wt >= 0 else Color.RED
        width = int(abs(self.wt * Node.CONNECTION_WIDTH))
        pygame.draw.line(screen, color, (self.input.x + Node.RADIUS,
                         self.input.y), (self.output.x - Node.RADIUS, self.output.y), width)
