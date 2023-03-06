# ------------------ IMPORTS ------------------


import neat
import pygame
from render.neural_network.node import Node, Connection, NodeType
from render.colors import Color


# ------------------ CLASSES ------------------


class NN:
    INPUT_NEURONS = 5
    OUTPUT_NEURONS = 4

    def __init__(self, config: neat.Config, genome: neat.DefaultGenome, pos: tuple):
        self.nodes = []
        self.genome = genome
        self.pos = (int(pos[0]+Node.RADIUS), int(pos[1]))
        input_names = ["0°", "45°", "90°", "135°", "180°"]
        output_names = ["Left", "Right", "Accelerate", "Brake"]
        hidden_nodes = [n for n in genome.nodes.keys()]
        node_id_list = []

        # nodes
        h = (NN.INPUT_NEURONS-1)*(Node.RADIUS*2 + Node.SPACING)
        for i, input in enumerate(config.genome_config.input_keys):
            n = Node(input, pos[0], pos[1]+int(-h/2 + i*(Node.RADIUS*2 + Node.SPACING)), NodeType.INPUT, [
                     Color.GREEN_PALE, Color.GREEN, Color.DARK_GREEN_PALE, Color.DARK_GREEN], input_names[i], i)
            self.nodes.append(n)
            node_id_list.append(input)

        h = (NN.OUTPUT_NEURONS-1)*(Node.RADIUS*2 + Node.SPACING)
        for i, out in enumerate(config.genome_config.output_keys):
            n = Node(out+NN.INPUT_NEURONS, pos[0] + 2*(Node.LAYER_SPACING+2*Node.RADIUS), pos[1]+int(-h/2 + i*(
                Node.RADIUS*2 + Node.SPACING)), NodeType.OUTPUT, [Color.RED_PALE, Color.RED, Color.DARK_RED_PALE, Color.DARK_RED], output_names[i], i)
            self.nodes.append(n)
            hidden_nodes.remove(out)
            node_id_list.append(out)

        h = (len(hidden_nodes)-1)*(Node.RADIUS*2 + Node.SPACING)
        for i, m in enumerate(hidden_nodes):
            n = Node(m, self.pos[0] + (Node.LAYER_SPACING+2*Node.RADIUS), self.pos[1]+int(-h/2 + i*(Node.RADIUS*2 +
                     Node.SPACING)), NodeType.HIDDEN, [Color.BLUE_PALE, Color.DARK_BLUE, Color.BLUE_PALE, Color.DARK_BLUE])
            self.nodes.append(n)
            node_id_list.append(m)

        # connections
        self.connections = []
        for c in genome.connections.values():
            if c.enabled:
                input_, output = c.key
                self.connections.append(Connection(self.nodes[node_id_list.index(
                    input_)], self.nodes[node_id_list.index(output)], c.weight))

    def draw(self, screen: pygame.Surface):
        for c in self.connections:
            c.draw(screen)
        for node in self.nodes:
            node.draw(screen)
