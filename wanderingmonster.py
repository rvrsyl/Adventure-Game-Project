# wanderingmonster.py
 
"""A monster that wanders around the game map.
 
A WanderingMonster holds only plain data (grid position, type, color, and
hit points), so it can be saved to JSON with to_dict() and rebuilt with
from_dict(). Nothing in this module prints or draws anything; the game
decides how to display a monster.
 
Constants:
    MONSTER_TYPES: The kinds of monster, with their color and stat ranges.
    DIRECTIONS: The four (dx, dy) steps a monster can try to take.
 
Classes:
    WanderingMonster: A monster standing on one square of the map grid.
 
Typical usage example:
 
  from WanderingMonster import WanderingMonster
 
  monster = WanderingMonster.random_spawn([], [(0, 0)], 10, 10)
  monster.move([], [(0, 0)], 10, 10)
  saved = monster.to_dict()
  same_monster = WanderingMonster.from_dict(saved)
"""
 
import random
 
# Positions are (x, y) where x is the column and y is the row, matching the
# player's [x, y] position on the map. Up is y - 1.
DIRECTIONS = [(0, -1), (0, 1), (-1, 0), (1, 0)]
 
# Everything about a kind of monster that does not change from monster to
# monster. A WanderingMonster stores only its type name, and looks the rest
# up here, so the saved data stays small.
MONSTER_TYPES = {
    "Water Fowl": {
        "color": [70, 130, 180],
        "description": "In the distance is a feathery, aquatic monster "
                       "that has frills resembling closely to those of "
                       "an extinct dinosaur. It makes a hooting sound as "
                       "it slurps up water from a polluted lake.",
        "health_range": (20, 30),
        "strength_range": (5, 8),
        "currency_range": (15, 25),
    },
    "Scrapken": {
        "color": [150, 150, 150],
        "description": "You discover a huge heap of scraps sitting at "
                       "the west side of the town, but a creature hides "
                       "within the pile. You somehow need to stall it "
                       "before having a shot to take any resources.",
        "health_range": (40, 60),
        "strength_range": (11, 16),
        "currency_range": (45, 65),
    },
    "Blarg": {
        "color": [60, 180, 75],
        "description": "A 40 foot tall abomination oozes fatal acid with "
                       "every cratering step it takes across the corn field. "
                       "Any slight noise can instantly alert it, crushing "
                       "everything in the way to hunt its new target.",
        "health_range": (70, 100),
        "strength_range": (19, 27),
        "currency_range": (85, 115),
    },
}
 
 
def _is_int(value):
    """Return True for a real int (a bool does not count)."""
    return isinstance(value, int) and not isinstance(value, bool)
 
 
class WanderingMonster:
    """
    A monster standing on one square of the map grid.
 
    Attributes:
        x (int): Grid column, counted from 0 at the left.
        y (int): Grid row, counted from 0 at the top.
        monster_type (str): The kind of monster; a key of MONSTER_TYPES.
        color (list): Three ints (red, green, blue), each 0 to 255.
        hp (int): The monster's remaining hit points.
    """
 
    def __init__(self, x, y, monster_type, color, hp):
        """
        Create a monster.
 
        Parameters:
            x (int): Grid column.
            y (int): Grid row.
            monster_type (str): The kind of monster.
            color (tuple or list): Three ints for the monster's color.
            hp (int): The monster's hit points.
        """
        self.x = x
        self.y = y
        self.monster_type = monster_type
        self.color = list(color)
        self.hp = hp
 
    def __repr__(self):
        """Return a short readable form, such as for printing a state."""
        return (f"WanderingMonster(x={self.x}, y={self.y}, "
                f"monster_type={self.monster_type!r}, "
                f"color={self.color}, hp={self.hp})")
 
    @classmethod
    def random_spawn(cls, occupied, forbidden, grid_w, grid_h, rng=random):
        """
        Create a monster of a random type on a random free square.
 
        Parameters:
            occupied (list): (x, y) squares that other monsters are on.
            forbidden (list): (x, y) squares no monster may start on,
                such as the town and the player's square.
            grid_w (int): Width of the grid; x must satisfy 0 <= x < grid_w.
            grid_h (int): Height of the grid; y must satisfy 0 <= y < grid_h.
            rng: Where the random choices come from. Defaults to the
                random module; pass a random.Random(seed) to test.
 
        Returns:
            WanderingMonster or None: The new monster, or None if every
                square on the grid is blocked.
        """
        blocked = {tuple(p) for p in occupied} | {tuple(p) for p in forbidden}
        free = [(x, y) for y in range(grid_h) for x in range(grid_w)
                if (x, y) not in blocked]
        if not free:
            return None
        x, y = rng.choice(free)
        monster_type = rng.choice(list(MONSTER_TYPES))
        info = MONSTER_TYPES[monster_type]
        return cls(x, y, monster_type, info["color"],
                   rng.randint(*info["health_range"]))
 
    @classmethod
    def from_dict(cls, data):
        """
        Rebuild a monster from the dictionary that to_dict made.
 
        Parameters:
            data (dict): The monster's saved data.
 
        Returns:
            WanderingMonster: The rebuilt monster.
 
        Raises:
            ValueError: If data is missing a field or a field is invalid.
        """
        if not isinstance(data, dict):
            raise ValueError("Monster data must be a dictionary.")
        for key in ("x", "y", "monster_type", "color", "hp"):
            if key not in data:
                raise ValueError(f"Monster data is missing {key!r}.")
        if not (_is_int(data["x"]) and _is_int(data["y"])
                and _is_int(data["hp"])):
            raise ValueError("Monster x, y, and hp must be ints.")
        if data["monster_type"] not in MONSTER_TYPES:
            raise ValueError(f"Unknown monster type: {data['monster_type']!r}")
        color = data["color"]
        if (not isinstance(color, (list, tuple)) or len(color) != 3
                or not all(_is_int(c) and 0 <= c <= 255 for c in color)):
            raise ValueError("Monster color must be three ints from 0 to 255.")
        return cls(data["x"], data["y"], data["monster_type"], color,
                   data["hp"])
 
    def to_dict(self):
        """
        Return the monster as a dictionary of JSON-safe values.
 
        Returns:
            dict: Keys 'x' (int), 'y' (int), 'monster_type' (str),
                'color' (list of 3 ints), and 'hp' (int).
        """
        return {
            "x": self.x,
            "y": self.y,
            "monster_type": self.monster_type,
            "color": list(self.color),
            "hp": self.hp,
        }
 
    def move(self, occupied, forbidden, grid_w, grid_h, rng=random):
        """
        Try to take one step in a random direction.
 
        One direction is picked at random. If that step would leave the
        grid or land on an occupied or forbidden square, the monster stays
        where it is (it does not try another direction).
 
        Parameters:
            occupied (list): (x, y) squares that other monsters are on.
            forbidden (list): (x, y) squares no monster may enter, such as
                the town and the player's square.
            grid_w (int): Width of the grid.
            grid_h (int): Height of the grid.
            rng: Where the random choice comes from. Defaults to the
                random module; pass a random.Random(seed) to test.
...  
...         Returns:
...             bool: True if the monster moved, False if it stayed put.
...         """
...         step_x, step_y = rng.choice(DIRECTIONS)
...         new_x = self.x + step_x
...         new_y = self.y + step_y
...         if not (0 <= new_x < grid_w and 0 <= new_y < grid_h):
...             return False
...         blocked = {tuple(p) for p in occupied} | {tuple(p) for p in forbidden}
...         if (new_x, new_y) in blocked:
...             return False
...         self.x = new_x
...         self.y = new_y
...         return True
...  
...     def combat_profile(self, rng=random):
...         """
...         Describe the monster for a fight.
...  
...         Parameters:
...             rng: Where the random rolls come from. Defaults to the
...                 random module.
...  
...         Returns:
...             dict: Keys 'name' (str), 'description' (str), 'health' (int,
...                 the monster's current hp), 'strength' (int),
...                 'strength_range' (tuple of int), and 'currency' (int, the
...                 gold it drops), in the same shape as new_random_monster.
...         """
...         info = MONSTER_TYPES[self.monster_type]
...         return {
...             "name": self.monster_type,
...             "description": info["description"],
...             "health": self.hp,
...             "strength": rng.randint(*info["strength_range"]),
...             "strength_range": info["strength_range"],
...             "currency": rng.randint(*info["currency_range"]),
...         }
