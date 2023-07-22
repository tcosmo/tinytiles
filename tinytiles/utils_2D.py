class Position(object):
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __eq__(self, other: "Position"):
        return self.x == other.x and self.y == other.y

    def __add__(self, other: "Position"):
        return GridPosition(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Position"):
        return GridPosition(self.x - other.x, self.y - other.y)

    def __str__(self):
        return f"({self.x},{self.y})"

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash((self.x, self.y))


North = Position(0, 1)
East = Position(1, 0)
South = Position(0, -1)
West = Position(-1, 0)

DIRS = [North, East, South, West]


class GridPosition(Position):
    pass


class TilePosition(Position):
    pass
