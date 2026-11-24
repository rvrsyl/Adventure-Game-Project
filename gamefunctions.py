# gamefunctions.py
 
"""Helper functions for a simple text-based adventure game. Running this file
directly (python gamefunctions.py) calls test_functions().
 
The game's data lives in one state dictionary (see new_game_state) that is
passed to the functions that need it:
 
    state = {
        "player_name": str,
        "player_hp": int,
        "player_gold": int,
        "player_inventory": list of item dictionaries,
        "map_state": dict (see new_map_state),
        "monsters": list of WanderingMonster objects,
    }
 
Constants:
    MAX_HP: The most health the player can have.
    SLEEP_COST: Gold charged to sleep and restore all health.
    STARTING_GOLD: Gold a new player starts with.
    DEFAULT_SAVE_FILE: Save filename used when the player just presses Enter.
    SHOP_ITEMS: The items sold at the market.
    MAP_SIZE: Width and height of the square world map.
 
Functions:
    new_game_state: Create the state dictionary for a new game.
    new_map_state: Create the map part of the game state.
    spawn_monsters: Add new wandering monsters on random free squares.
    monster_at: Find the wandering monster on a given square.
    move_monsters: Let every wandering monster try to take a step.
    move_player: Move the player one square on the map (the model).
    render_map: Build the text picture of the map from the game state.
    draw_map: Print the map and its legend.
    run_map: Let the player walk around the map until town or a monster.
    explore: Run the map, fight monsters it finds, and return to town.
    save_game: Write the game state to a JSON file.
    load_game: Read and validate a game state from a JSON file.
    get_save_filename: Ask the user which save file to use.
    start_menu: Let the player start a new game or load a saved one.
    purchase_item: Buy as many items as the player can afford.
    new_random_monster: Create a random monster as a dictionary.
    print_welcome: Print a centered greeting for the player.
    print_market_menu: Print a bordered sign listing two market items.
    get_menu_choice: Prompt until the user enters a valid option.
    get_player_name: Prompt until the user enters a name.
    get_quantity: Prompt until the user enters a positive whole number.
    print_town_menu: Show the town status and menu.
    sleep: Restore the player's health for gold.
    shop: Let the player buy items from the market.
    equip_item: Let the player equip an item of a chosen type.
    get_equipped_item: Find the equipped item of a type.
    display_fight_statistics: Show the current state of a fight.
    get_user_fight_action: Ask whether to attack, run, or use a charm.
    fight_monster: Run a full fight and report the outcome.
    test_functions: Demonstrate the non-interactive functions.
 
Typical usage example:
 
  import gamefunctions
 
  state = gamefunctions.new_game_state("Jeff")
  gamefunctions.fight_monster(state)
"""
 
import copy
import json
import random

from WanderingMonster import MONSTER_TYPES, WanderingMonster
 
MAX_HP = 100
SLEEP_COST = 5
STARTING_GOLD = 50
DEFAULT_SAVE_FILE = "savegame.json"
MAP_SIZE = 10
TOWN_POSITION = [0, 0]
MOVE_KEYS = {"w": "up", "s": "down", "a": "left", "d": "right"}
DIRECTION_OFFSETS = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0),
}
 
# Template dictionaries for everything the market sells. Each purchase
# adds an independent copy of the template to the player's inventory.
SHOP_ITEMS = [
    {
        "name": "Night Blade",
        "type": "weapon",
        "price": 50,
        "damage": 15,
        "maxDurability": 10,
        "currentDurability": 10,
        "equipped": False,
    },
    {
        "name": "Cosmic Hand",
        "type": "consumable",
        "price": 250,
        "note": "Defeats any one monster without losing HP",
    },
]
 
 
def new_game_state(player_name):
    """
    Create the state dictionary for a new game.
 
    Parameters:
        player_name (str): The player's name.
 
    Returns:
        dict: The state, with keys 'player_name' (str), 'player_hp' (int),
            'player_gold' (int), 'player_inventory' (list of dict),
            'map_state' (dict, see new_map_state), and 'monsters' (list
            of WanderingMonster, starting with one).
    """
    state = {
        "player_name": player_name,
        "player_hp": MAX_HP,
        "player_gold": STARTING_GOLD,
        "player_inventory": [],
        "map_state": new_map_state(),
        "monsters": [],
    }
    spawn_monsters(state, 1)
    return state
 
 
def save_game(state, filename=DEFAULT_SAVE_FILE):
    """
    Write the game state to a JSON file.

    Everything in the state is saved: the player's name, HP, gold, the
    whole inventory (including each item's current durability and
    whether it is equipped), the map, and every wandering monster
    (converted with to_dict).

    Parameters:
        state (dict): The game state, as made by new_game_state.
        filename (str): The file to write. Defaults to DEFAULT_SAVE_FILE.

    Returns:
        bool: True if the game was saved, False if the file could not
            be written (the reason is printed).
    """
    # Monsters are objects, so each one is saved as a plain dictionary.
    save_state = dict(state)
    save_state["monsters"] = [monster.to_dict()
                              for monster in state["monsters"]]
    try:
        with open(filename, "w", encoding="utf-8") as save_file:
            json.dump(save_state, save_file, indent=2)
    except OSError as error:
        print(f"\nCould not save the game: {error}")
        return False
    print(f"\nGame saved to {filename}.")
    return True


def load_game(filename=DEFAULT_SAVE_FILE):
    """
    Read a game state from a JSON file and check that it is usable.

    Parameters:
        filename (str): The file to read. Defaults to DEFAULT_SAVE_FILE.

    Each saved monster is rebuilt with WanderingMonster.from_dict. If the
    save holds no monsters, new ones are spawned.

    Returns:
        dict or None: The loaded state, or None if the file is missing,
            is not valid JSON, or does not hold a valid game state (the
            reason is printed).
    """
    try:
        with open(filename, "r", encoding="utf-8") as save_file:
            state = json.load(save_file)
    except FileNotFoundError:
        print(f"\nNo save file named {filename} was found.")
        return None
    except (OSError, json.JSONDecodeError) as error:
        print(f"\nCould not read {filename}: {error}")
        return None

    if not _is_valid_state(state):
        print(f"\n{filename} is not a valid save file.")
        return None
    if "map_state" not in state:
        # Saves from before the map existed: start with a fresh map.
        state["map_state"] = new_map_state()
    # Saves from before wandering monsters kept one monster in the map.
    state["map_state"].pop("monster", None)
    if "monsters" in state:
        monsters = _monsters_from_dicts(state["monsters"])
        if monsters is None:
            print(f"\n{filename} is not a valid save file.")
            return None
        state["monsters"] = monsters
    else:
        state["monsters"] = []
    ensure_monsters(state)
    print(f"\nGame loaded from {filename}.")
    return state


def _is_valid_state(state):
    """
    Check that a loaded object has the shape new_game_state creates.

    Parameters:
        state (object): Whatever was read from a save file.

    Returns:
        bool: True if it has the expected keys and value types.
    """
    if not isinstance(state, dict):
        return False
    expected = {
        "player_name": str,
        "player_hp": int,
        "player_gold": int,
        "player_inventory": list,
    }
    for key, kind in expected.items():
        if not isinstance(state.get(key), kind):
            return False
    for item in state["player_inventory"]:
        if not isinstance(item, dict):
            return False
        if "name" not in item or "type" not in item:
            return False
        if item["type"] == "weapon":
            for key in ("damage", "maxDurability", "currentDurability"):
                if not isinstance(item.get(key), int):
                    return False
    if "map_state" in state and not _is_valid_map_state(state["map_state"]):
        return False
    return True


def _is_valid_map_state(map_state):
    """
    Check that an object has the shape new_map_state creates.

    Parameters:
        map_state (object): Whatever was read from a save file.

    Returns:
        bool: True if 'player' and 'town' are each an [x, y]
            pair of ints that lies on the map.
    """
    if not isinstance(map_state, dict):
        return False
    for key in ("player", "town"):
        position = map_state.get(key)
        if not isinstance(position, list) or len(position) != 2:
            return False
        for coordinate in position:
            if (not isinstance(coordinate, int) or isinstance(coordinate, bool)
                    or not 0 <= coordinate < MAP_SIZE):
                return False
    return True


def _monsters_from_dicts(data):
    """
    Rebuild wandering monsters from their saved dictionaries.

    Parameters:
        data (object): The 'monsters' value read from a save file.

    Returns:
        list or None: A list of WanderingMonster, or None if data is not a
            list of valid monster dictionaries on the map.
    """
    if not isinstance(data, list):
        return None
    monsters = []
    for entry in data:
        try:
            monster = WanderingMonster.from_dict(entry)
        except ValueError:
            return None
        if not (0 <= monster.x < MAP_SIZE and 0 <= monster.y < MAP_SIZE):
            return None
        monsters.append(monster)
    return monsters


def get_save_filename():
    """
    Ask the user which save file to use.

    Pressing Enter with no text uses DEFAULT_SAVE_FILE. A name with no
    extension gets ".json" added.

    Parameters:
        None

    Returns:
        str: The filename to use.
    """
    name = input(f"Save file name (press Enter for {DEFAULT_SAVE_FILE}):\n").strip()
    if not name:
        return DEFAULT_SAVE_FILE
    if "." not in name:
        name += ".json"
    return name


def start_menu():
    """
    Let the player start a new game or load a saved one.

    Loading is retried until it succeeds or the player chooses to start
    a new game instead. For a new game the player is asked for a name.

    Parameters:
        None

    Returns:
        dict: The game state to play with.
    """
    while True:
        print("\n1) New Game")
        print("2) Load Game")
        if get_menu_choice(["1", "2"]) == "1":
            return new_game_state(get_player_name())
        state = load_game(get_save_filename())
        if state is not None:
            return state
        print("Try again, or choose New Game.")


def new_map_state():
    """
    Create the map part of the game state.

    The map is a MAP_SIZE x MAP_SIZE grid. Positions are [x, y] lists,
    where x is the column and y is the row, so [0, 0] is the upper-left
    square. Lists (not tuples) are used so the state survives a round
    trip through a JSON save file unchanged. The player starts on the
    town square. Monsters are not part of the map state; they live in
    state["monsters"] as WanderingMonster objects.

    Parameters:
        None

    Returns:
        dict: The map state, with keys 'player' and 'town'.
    """
    map_state = {
        "player": list(TOWN_POSITION),
        "town": list(TOWN_POSITION),
    }
    return map_state


def spawn_monsters(state, count):
    """
    Add wandering monsters to random free squares.

    A new monster never starts on the town, on the player's square, or on
    a square another monster is on.

    Parameters:
        state (dict): The game state. Its 'monsters' list is added to.
        count (int): How many monsters to add.

    Returns:
        None
    """
    map_state = state["map_state"]
    forbidden = [tuple(map_state["town"]), tuple(map_state["player"])]
    for _ in range(count):
        occupied = [(monster.x, monster.y) for monster in state["monsters"]]
        monster = WanderingMonster.random_spawn(
            occupied, forbidden, MAP_SIZE, MAP_SIZE)
        if monster is None:
            return
        state["monsters"].append(monster)


def ensure_monsters(state):
    """
    Spawn two monsters if there are none on the map.

    Parameters:
        state (dict): The game state. Its 'monsters' list may be added to.

    Returns:
        None
    """
    if not state["monsters"]:
        spawn_monsters(state, 2)


def monster_at(state, position):
    """
    Find the wandering monster on a square.

    Parameters:
        state (dict): The game state.
        position (list): The [x, y] square to look at.

    Returns:
        WanderingMonster or None: A monster standing there, if any.
    """
    for monster in state["monsters"]:
        if (monster.x, monster.y) == tuple(position):
            return monster
    return None


def move_monsters(state):
    """
    Let every wandering monster try to take one step.

    Monsters move one at a time, so each sees where the others are now.
    None of them can step onto the town square or the player's square
    (see WanderingMonster.move for the rest of the rules).

    Parameters:
        state (dict): The game state. The monsters are updated in place.

    Returns:
        None
    """
    map_state = state["map_state"]
    forbidden = [tuple(map_state["town"]), tuple(map_state["player"])]
    for monster in state["monsters"]:
        occupied = [(other.x, other.y) for other in state["monsters"]
                    if other is not monster]
        monster.move(occupied, forbidden, MAP_SIZE, MAP_SIZE)


def move_player(game_state, direction):
    """
    Move the player one square on the map.

    This only changes the model (game_state["map_state"]); nothing is
    drawn here. The player cannot leave the map: a move off an edge
    changes nothing.

    Parameters:
        game_state (dict): The game state. Its map_state 'player' position
            is updated in place.
        direction (str): One of 'up', 'down', 'left', or 'right'.

    Returns:
        str: "moved" for normal movement, "returned_to_town" if the player
            moved onto the town square, "monster_encounter" if the player
            moved onto a monster's square, or "blocked" if the move would
            have left the map (the player did not move).

    Raises:
        ValueError: If direction is not one of the four directions.
    """
    if direction not in DIRECTION_OFFSETS:
        raise ValueError(f"Unknown direction: {direction!r}")
    map_state = game_state["map_state"]
    step_x, step_y = DIRECTION_OFFSETS[direction]
    new_x = map_state["player"][0] + step_x
    new_y = map_state["player"][1] + step_y
    if not (0 <= new_x < MAP_SIZE and 0 <= new_y < MAP_SIZE):
        return "blocked"

    map_state["player"] = [new_x, new_y]
    if map_state["player"] == map_state["town"]:
        return "returned_to_town"
    if monster_at(game_state, map_state["player"]) is not None:
        return "monster_encounter"
    return "moved"


def render_map(state):
    """
    Build the text picture of the map from the game state.

    The picture depends only on the state. Each square is one character:
    P for the player, T for the town, the first letter of the monster's
    type for each monster in state["monsters"], and a period for anything
    else. The player is drawn over a monster when standing on one.

    Parameters:
        state (dict): The game state, as made by new_game_state.

    Returns:
        str: The map, one line per row, with no trailing newline.
    """
    map_state = state["map_state"]
    symbols = {}
    for monster in state["monsters"]:
        symbols[(monster.x, monster.y)] = monster.monster_type[0].upper()
    symbols[tuple(map_state["town"])] = "T"
    symbols[tuple(map_state["player"])] = "P"
    rows = []
    for y in range(MAP_SIZE):
        rows.append("".join(f" {symbols.get((x, y), '.')} "
                        for x in range(MAP_SIZE)))
    return "\n".join(rows)


def draw_map(state):
    """
    Print the map and a legend explaining its letters.

    Parameters:
        state (dict): The game state.

    Returns:
        None
    """
    legend = ["P = You", "T = Town"]
    legend += [f"{name[0].upper()} = {name}" for name in MONSTER_TYPES]
    print()
    print(render_map(state))
    print(", ".join(legend))


def run_map(game_state):
    """
    Let the player walk around the map until something ends the trip.

    Each turn the map is drawn, then one key is read (w = up, s = down,
    a = left, d = right) and passed to move_player. The trip ends when the
    player steps onto the town square or onto a monster. Every step the
    player takes (a blocked move does not count) is followed by each
    monster trying to move once, unless the step ended in a fight.

    Parameters:
        game_state (dict): The game state. Its map_state and monsters are
            updated in place as the player and monsters move.

    Returns:
        str: "town" if the player returned to town, or "monster" if the
            player ran into a monster.
    """
    print("\nYou leave Wakefield and look around. (w/a/s/d to move)")
    while True:
        draw_map(game_state)
        key = get_menu_choice(list(MOVE_KEYS))
        result = move_player(game_state, MOVE_KEYS[key])
        if result == "monster_encounter":
            return "monster"
        move_monsters(game_state)
        if result == "returned_to_town":
            return "town"
        if result == "blocked":
            print("You can't go any further that way.")


def explore(state):
    """
    Run the map, fight any monsters found, and end back in town.

    When the player runs into a monster they fight that monster. A
    defeated monster is removed from state["monsters"]; if that leaves
    none, two new ones are spawned. After a fight the player stays on the
    monster's old square and the monsters try to move. The player leaves
    the map by walking back onto the town square, or by being knocked out
    in a fight, which also sends them to town.

    Parameters:
        state (dict): The game state.

    Returns:
        None
    """
    map_state = state["map_state"]
    while True:
        if run_map(state) == "town":
            return
        monster = monster_at(state, map_state["player"])
        outcome = fight_monster(state, monster)
        if outcome == "lost":
            map_state["player"] = list(map_state["town"])
            return
        if outcome == "won":
            state["monsters"].remove(monster)
            ensure_monsters(state)
        move_monsters(state)


def purchase_item(itemPrice, startingCurrency, quantityToPurchase=1):
    """
    Attempt to buy items, purchasing as many as can be afforded.
 
    Tries to buy quantityToPurchase items at itemPrice each. If the
    full quantity is too expensive, buys as many as possible instead.
    Nothing is printed.
 
    Parameters:
        itemPrice (int): The price of a single item.
        startingCurrency (int): The currency available.
        quantityToPurchase (int): How many items to try to buy.
            Defaults to 1.
 
    Returns:
        tuple: (quantity purchased (int), currency remaining (int)).
 
    Example:
        >>> purchase_item(123, 201, 3)
        (1, 78)
    """
    affordable_quantity = startingCurrency // itemPrice
    actual_quantity = min(affordable_quantity, quantityToPurchase)
    currency_remaining = startingCurrency - (actual_quantity * itemPrice)
    return actual_quantity, currency_remaining
 
 
def new_random_monster():
    """
    Create a random monster.
 
    One of the types in MONSTER_TYPES is chosen at random, and its health,
    strength, and currency are randomly picked from that type's range.
 
    Parameters:
        None
 
    Returns:
        dict: The monster, with keys 'name' (str), 'description'
            (str), 'health' (int), 'strength' (int), 'strength_range'
            (tuple of int), and 'currency' (int).
 
    Example:
        >>> monster = new_random_monster()
        >>> sorted(monster.keys())
        ['currency', 'description', 'health', 'name', 'strength', 'strength_range']
    """
    chosen_name, chosen = random.choice(list(MONSTER_TYPES.items()))
 
    monster = {
        "name": chosen_name,
        "description": chosen["description"],
        "health": random.randint(*chosen["health_range"]),
        "strength": random.randint(*chosen["strength_range"]),
        "strength_range": chosen["strength_range"],
        "currency": random.randint(*chosen["currency_range"]),
    }
    return monster
 
 
def print_welcome(name, width):
    """
    Print a centered welcome message.
 
    Parameters:
        name (str): The name to greet.
        width (int): Total width of the field the message is
            centered in.
 
    Returns:
        None
 
    Example:
        >>> print_welcome("Jack", 20)
            Welcome, Jack!    
    """
    print(f"\n{'Welcome to Wakefield, ' + name + '!':^{width}}")
 
 
def print_market_menu(item1Name, item1Price, item2Name, item2Price):
    r"""
    Print a bordered market sign listing two items and their prices.
 
    Item names are left-aligned in a 12-character field. Prices are
    right-aligned in an 8-character field, shown with a dollar sign
    and exactly two decimal places.
 
    Parameters:
        item1Name (str): Name of the first item.
        item1Price (float): Price of the first item.
        item2Name (str): Name of the second item.
        item2Price (float): Price of the second item.
 
    Returns:
        None
 
    Example:
        >>> print_market_menu("Burger", 31, "Donut", 1.234)
        /----------------------\
        | Burger        $31.00 |
        | Donut          $1.23 |
        \----------------------/
    """
    print("/" + "-" * 22 + "\\")
    print(f"| {item1Name:<12}{'$' + format(item1Price, '.2f'):>8} |")
    print(f"| {item2Name:<12}{'$' + format(item2Price, '.2f'):>8} |")
    print("\\" + "-" * 22 + "/")
 
 
def get_menu_choice(valid_options):
    """
    Prompt the user until they enter one of the valid options.
 
    Parameters:
        valid_options (list): The accepted answers, as strings.
 
    Returns:
        str: The user's valid choice.
    """
    while True:
        choice = input("> ").strip()
        if choice in valid_options:
            return choice
        print(f"Invalid choice. Please enter one of: "
              f"{', '.join(valid_options)}.")
 
 
def get_player_name():
    """
    Prompt the user until they enter a non-empty name.
 
    Parameters:
        None
 
    Returns:
        str: The player's name.
    """
    while True:
        name = input("\nWhat is your name?\n").strip()
        if name:
            return name
        print("Please enter a name.")
 
 
def get_quantity(prompt):
    """
    Prompt the user until they enter a positive whole number.
 
    Parameters:
        prompt (str): The text shown when asking for input.
 
    Returns:
        int: The quantity entered.
    """
    while True:
        text = input(prompt).strip()
        if text.isdigit() and int(text) > 0:
            return int(text)
        print("Please enter a positive whole number.")
 
 
def get_equipped_item(state, item_type):
    """
    Find the player's currently equipped item of a given type.
 
    Parameters:
        state (dict): The game state.
        item_type (str): The item type to look for, such as "weapon".
 
    Returns:
        dict or None: The equipped item, or None if there isn't one.
    """
    for item in state["player_inventory"]:
        if item["type"] == item_type and item.get("equipped"):
            return item
    return None
 
 
def print_town_menu(state):
    """
    Print the player's status and the list of town actions.
 
    Parameters:
        state (dict): The game state.
 
    Returns:
        None
    """
    weapon = get_equipped_item(state, "weapon")
    if weapon:
        weapon_text = (f"{weapon['name']} "
                       f"({weapon['currentDurability']}/"
                       f"{weapon['maxDurability']})")
    else:
        weapon_text = "None"
    print("\nYou are in the town of Joe's Pizza.")
    print(f"Current HP: {state['player_hp']}, "
          f"Current Gold: {state['player_gold']}")
    print(f"Equipped Weapon: {weapon_text}")
    print("What would you like to do?\n")
    print("1) Explore the Forest")
    print(f"2) Nap Time (Restore HP for {SLEEP_COST} Gold)")
    print("3) Visit the Shop")
    print("4) Equip a Weapon")
    print("5) Save and Quit")
 
 
def sleep(state):
    """
    Restore the player to full health in exchange for gold.
 
    Prints a message and changes nothing if the player cannot
    afford it or is already at full health.
 
    Parameters:
        state (dict): The game state. Its 'player_hp' and 'player_gold'
            are updated.
 
    Returns:
        None
    """
    if state["player_hp"] >= MAX_HP:
        print("You're already at full health.")
    elif state["player_gold"] < SLEEP_COST:
        print(f"You need {SLEEP_COST} gold to sleep.")
    else:
        print("\nYou sleep peacefully and wake up ready for battle.")
        state["player_hp"] = MAX_HP
        state["player_gold"] -= SLEEP_COST
 
 
def shop(state):
    """
    Let the player buy items from the market.
 
    Shows the market sign, asks which item and how many, and adds a
    separate copy of the item to the inventory for each one bought.
    If the player can't afford the full quantity, as many as possible
    are bought.
 
    Parameters:
        state (dict): The game state. Its 'player_gold' and
            'player_inventory' are updated.
 
    Returns:
        None
    """
    first, second = SHOP_ITEMS
    print(f"\nWelcome to the shop! You have {state['player_gold']} gold.")
    print_market_menu(first["name"], first["price"],
                      second["name"], second["price"])
    print(f"1) Buy {first['name']}")
    print(f"2) Buy {second['name']}")
    print("3) Leave The Shop")
    choice = get_menu_choice(["1", "2", "3"])
    if choice == "3":
        return
 
    template = SHOP_ITEMS[int(choice) - 1]
    wanted = get_quantity(f"How many {template['name']}s?\n")
    bought, state["player_gold"] = purchase_item(
        template["price"], state["player_gold"], wanted)
 
    if bought == 0:
        print(f"\nYou can't afford a {template['name']}.")
        return
    for _ in range(bought):
        item = copy.deepcopy(template)
        del item["price"]
        state["player_inventory"].append(item)
    if bought < wanted:
        print(f"You could only afford {bought}.")
    print(f"\nYou bought {bought} {template['name']}(s). "
          f"Gold Left: {state['player_gold']}.")
 
 
def equip_item(state, item_type="weapon"):
    """
    Let the player equip one item of a given type.
 
    Only items of that type are listed, plus an option to cancel.
    Equipping an item unequips any other item of the same type.
 
    Parameters:
        state (dict): The game state.
        item_type (str): Which kind of item to offer. Defaults to
            "weapon".
 
    Returns:
        None
    """
    options = [item for item in state["player_inventory"]
               if item["type"] == item_type]
    if not options:
        print(f"\nYou don't have any {item_type}s to equip.")
        return
 
    print(f"\nWhich {item_type} would you like to equip?")
    for number, item in enumerate(options, start=1):
        marker = " [equipped]" if item.get("equipped") else ""
        print(f"{number}) {item['name']} "
              f"({item['currentDurability']}/{item['maxDurability']} "
              f"durability){marker}")
    print(f"{len(options) + 1}) None (cancel)")
 
    valid = [str(n) for n in range(1, len(options) + 2)]
    choice = int(get_menu_choice(valid))
    if choice == len(options) + 1:
        return
 
    for item in options:
        item["equipped"] = False
    options[choice - 1]["equipped"] = True
    print(f"\nYou equipped the {options[choice - 1]['name']}.")
 
 
def display_fight_statistics(hp, monster, monster_hp):
    """
    Print the current health of the player and the monster.
 
    Parameters:
        hp (int): The player's current health.
        monster (dict): The monster, as made by new_random_monster.
        monster_hp (int): The monster's current health.
 
    Returns:
        None
    """
    print(f"\nYou: {hp} HP  {monster['name']}: {monster_hp} HP")
 
 
def get_user_fight_action(monster, has_charm=False):
    """
    Ask the user whether to attack, run away, or use a charm.
 
    Parameters:
        monster (dict): The monster being fought, as made by
            new_random_monster.
        has_charm (bool): Whether the player has a banishing charm to
            offer as an option. Defaults to False.
 
    Returns:
        str: "1" to attack, "2" to run away, or "3" to use a charm.
    """
    print(f"1) Attack {monster['name']}")
    print("2) Escape the fight")
    options = ["1", "2"]
    if has_charm:
        print("3) Use Cosmic Hand (one-shot the monster with no HP lost)")
        options.append("3")
    return get_menu_choice(options)
 
 
def fight_monster(state, wandering=None):
    """
    Fight a monster until someone is defeated or the user flees.

    If a WanderingMonster is given, the fight is against it, and any
    damage it takes is kept if the player flees. Otherwise a new random
    monster is created.
 
    Each round, the player and the monster hit each other for random
    damage. An equipped weapon adds its damage to each hit and loses
    1 durability per attack, breaking at 0. If the player has a
    consumable (the Cosmic Hand), they can use it to defeat the monster
    instantly without losing any HP. Defeating the monster awards its currency as
    gold. If the player passes out, they wake up back in town with 1 HP.
 
    Parameters:
        state (dict): The game state. Its 'player_hp', 'player_gold',
            and 'player_inventory' are updated.
        wandering (WanderingMonster or None): The monster to fight.
            Its hp is updated. Defaults to None.
 
    Returns:
        str: "won" if the monster was defeated, "fled" if the player ran
            away, or "lost" if the player passed out.
    """
    if wandering is None:
        monster = new_random_monster()
    else:
        monster = wandering.combat_profile()
    monster_hp = monster["health"]
    print(f"\nA wild {monster['name']} appears!")
    print(monster["description"])
 
    while state["player_hp"] > 0 and monster_hp > 0:
        display_fight_statistics(state["player_hp"], monster, monster_hp)
        charm = next((item for item in state["player_inventory"]
                      if item["type"] == "consumable"), None)
        action = get_user_fight_action(monster, charm is not None)
 
        if action == "2":
            print("\nYou fled from another attack.")
            break
        if action == "3":
            state["player_inventory"].remove(charm)
            monster_hp = 0
            print(f"\nThe Cosmic Hand controls {monster['name']} to end its own life!")
            break
 
        hit = random.randint(7, 12)
        weapon = get_equipped_item(state, "weapon")
        if weapon:
            hit += weapon["damage"]
            weapon["currentDurability"] -= 1
        counter = random.randint(*monster["strength_range"])
        monster_hp -= hit
        state["player_hp"] -= counter
        print(f"\nYou hit for {hit}. {monster['name']} hits back for {counter}.")
        if weapon and weapon["currentDurability"] <= 0:
            print(f"Your {weapon['name']} breaks!")
            state["player_inventory"].remove(weapon)
 
    if wandering is not None:
        wandering.hp = max(monster_hp, 0)

    if state["player_hp"] <= 0:
        print("\nEverything goes black. You feel exhausted in your hammock.")
        state["player_hp"] = 1
        return "lost"
    if monster_hp <= 0:
        reward = monster["currency"]
        print(f"You killed {monster['name']} and got {reward} gold!")
        state["player_gold"] += reward
        return "won"
    return "fled"
 
 
def test_functions():
    """
    Demonstrate the non-interactive functions in this module.
 
    Each function is called three (or more) times with different
    arguments. No user input is requested.
 
    Parameters:
        None
 
    Returns:
        None
    """
    print("--- purchase_item ---\n")
    # Buys all 3 items: expect (3, 631)
    print(purchase_item(123, 1000, 3))
    # Can only afford 1 of 3: expect (1, 78)
    print(purchase_item(123, 201, 3))
    # Default quantity of 1: expect (1, 1771)
    print(purchase_item(341, 2112))
    # Cannot afford any: expect (0, 2112)
    print(purchase_item(3141, 2112))
    print()
    
    print("\n--- new_random_monster ---\n")
    for _ in range(3):
        monster = new_random_monster()
        print(f"{monster['name']} || Health: {monster['health']}, "
              f"Strength: {monster['strength']}, Currency: {monster['currency']}")
        print(monster["description"])
        print()
 
    print("\n--- print_welcome ---\n")
    print_welcome("Jack", 15)
    print_welcome("June", 20)
    print_welcome("Quint", 25)
    print_welcome("Dirk", 30)
    print()
    
    print("\n--- print_market_menu ---\n")
    print_market_menu("Pizza", 12 , "Milkshake", 8)
    print_market_menu("Juice Bombs", 47, "Wrist-Rocket", 34)
    print_market_menu("Night Blade", 500, "Cosmic Glove", 250)
    print()
    
    print("\n--- new_game_state, town menu, and sleep ---\n")
    test_state = new_game_state("Tester")
    print(test_state)
    print_town_menu(test_state)
    for hp, gold in [(10, 10), (10, 2), (MAX_HP, 10)]:
        test_state["player_hp"], test_state["player_gold"] = hp, gold
        print(f"Before: hp={hp}, gold={gold}")
        sleep(test_state)
        print(f"After:  hp={test_state['player_hp']}, "
              f"gold={test_state['player_gold']}")
    print()
 
 
if __name__ == "__main__":
    test_functions()
    
