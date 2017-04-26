# compatibility
import mock
# 3rd party
from hypothesis import strategies as st, given, assume
import networkx as nx
# local
from bmazing import get_player_by_name, Game
from game.mazefield_attributes import Path, Finish
from game.mazefield import text_to_maze_attributes, MazeField, coordinate as Coordinate
from players.moagstar import get_coordinate


def partition(n, seq):
    args = [iter(seq)] * n
    return zip(*args)


@st.composite
def coordinates(draw, width, height):
    x = draw(st.integers(min_value=0, max_value=width-1))
    y = draw(st.integers(min_value=0, max_value=height-1))
    return Coordinate(x, y)


def findall(text, characters):
    return [i for i, ltr in enumerate(text) if ltr in characters]


@st.composite
def mazefields(draw, min_size=8, max_size=256):

    tiles = draw(st.text('#  ', min_size=min_size, max_size=max_size))
    num_tiles = len(tiles)

    width = draw(st.integers(min_value=2, max_value=num_tiles/4))
    rows = list(list(x) for x in partition(width, tiles))
    height = len(rows)

    sx, sy = start = draw(coordinates(width, height))
    ex, ey = draw(coordinates(width, height).filter(lambda x: x != start))
    rows[sy][sx] = '0'
    rows[ey][ex] = '='

    top_bottom = ['#' * (width + 2)]
    maze = top_bottom + [''.join(x).join('##') for x in rows] + top_bottom
    mazefield = MazeField(text_to_maze_attributes(maze))

    G = nx.Graph()

    def add_coordinate(coordinate):
        G.add_node(coordinate)
        x, y = coordinate
        surrounding = mazefield.get_surrounding(Coordinate(x+1, y+1))
        for neighbour, direction in zip(surrounding, surrounding._fields):
            if neighbour in [Path, Finish]:
                neighbour_coordinate = get_coordinate(direction, coordinate)
                neighbour_coordinate = Coordinate(*neighbour_coordinate)
                G.add_node(neighbour_coordinate)
                G.add_edge(coordinate, neighbour_coordinate)

    begin, target = None, None
    for y, row in enumerate(maze):
        if '=' in row:
            target = Coordinate(row.find('='), y)
            add_coordinate(target)
        if '0' in row:
            begin = Coordinate(row.find('0'), y)
            add_coordinate(begin)
        for x in findall(row, ' '):
            coordinate = Coordinate(x, y)
            add_coordinate(coordinate)

    assume(begin != target)
    assume(nx.has_path(G, begin, target))

    return mazefield


def _test_player(mazefield, name):
    with mock.patch('game.game.logger.exception') as exception:
        exception.side_effect = Exception
        player = get_player_by_name(name)
        maximum_turns = len(str(mazefield))
        current_game = Game(player=player, field=mazefield,
                            displayname=None, maximum_turns=maximum_turns)
        while current_game.play_turn() is False: pass


@given(mazefields())
def test_moagstar(mazefield):
    _test_player(mazefield, 'MoagstarPlayer')


@given(mazefields())
def test_byte_player(mazefield):
    _test_player(mazefield, 'BytePlayer')
