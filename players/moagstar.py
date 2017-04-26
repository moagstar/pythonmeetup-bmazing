import random
from game import moves
from game.mazefield_attributes import Path, Finish, Start
from players.player import Player
import networkx as nx


NEIGHBOUR_TO_DELTA = {
    'left': (-1, 0),
    'right': (+1, 0),
    'up': (0, -1),
    'down': (0, +1),
}


DELTA_TO_NEIGHBOUR = {
    v: k
    for k, v in NEIGHBOUR_TO_DELTA.items()
}


class MazeTile:
    def __init__(self, coordinate, tile_type, visited=False):
        self.coordinate = coordinate
        self.tile_type = tile_type
        self.visited = visited


def get_coordinate(direction, coordinate):
    dx, dy = NEIGHBOUR_TO_DELTA[direction]
    x, y = coordinate
    return x + dx, y + dy


class MoagstarPlayer(Player):

    name = "moagstar"

    def __init__(self):
        self.coordinate = 0, 0
        self.maze = nx.Graph()
        self.current = None
        self.current_node = MazeTile(self.coordinate, Start, True)

    def move(self, direction):
        self.current = direction
        self.coordinate = get_coordinate(direction, self.coordinate)
        node = self.get_node(self.coordinate)
        node.visited = True
        self.current_node = node
        return direction

    def get_node(self, coordinate):
        for node in self.maze.nodes():
            if node.coordinate == coordinate:
                return node

    def get_closest_unvisited(self):
        curr = self.get_node(self.coordinate)
        min_path, min_path_len = None, 999
        for node in self.maze.nodes():
            if not node.visited:
                try:
                    path = nx.shortest_path(self.maze, source=curr, target=node)
                except Exception as e:
                    pass
                path_len = len(path)
                if path_len < min_path_len:
                    min_path = path
                    min_path_len = path_len
        x, y = min_path[0].coordinate
        xx, yy = min_path[1].coordinate
        delta = xx - x, yy - y
        return DELTA_TO_NEIGHBOUR[delta]

    def turn(self, surroundings):

        unvisited = []

        for direction in ('left', 'right', 'up', 'down'):

            tile_type = getattr(surroundings, direction)

            if tile_type == Finish:
                return getattr(moves, direction.upper())

            elif tile_type == Path:

                coordinate = get_coordinate(direction, self.coordinate)
                node = self.get_node(coordinate)

                if not node:
                    node = MazeTile(coordinate, tile_type)
                    self.maze.add_node(node)
                    self.maze.add_edge(self.current_node, node)
                    unvisited.append(direction)
                elif not node.visited:
                    unvisited.append(direction)

        if self.current in unvisited:
            return self.move(self.current)
        elif len(unvisited):
            return self.move(random.choice(unvisited))
        else:
            return self.move(self.get_closest_unvisited())
