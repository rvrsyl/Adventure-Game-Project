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
    }
 
Constants:
    MAX_HP: The most health the player can have.
    SLEEP_COST: Gold charged to sleep and restore all health.
    STARTING_GOLD: Gold a new player starts with.
    SHOP_ITEMS: The items sold at the market.
 
Functions:
    new_game_state: Create the state dictionary for a new game.
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
import random
 
MAX_HP = 100
SLEEP_COST = 5
STARTING_GOLD = 50
 
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
            'player_gold' (int), and 'player_inventory' (list of dict).
    """
    return {
        "player_name": player_name,
        "player_hp": MAX_HP,
        "player_gold": STARTING_GOLD,
        "player_inventory": [],
    }
 
 
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
 
    One of three monster types is chosen at random, and its health,
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
    monster_types = [
        {
            "name": "Water Fowl",
            "description": "In the distance is a feathery, aquatic monster "
                           "that has frills resembling closely to those of "
                           "an extinct dinosaur. It makes a hooting sound as "
                           "it slurps up water from a polluted lake.",
            "health_range": (20, 30),
            "strength_range": (5, 8),
            "currency_range": (15, 25),
        },
        {
            "name": "Scrapken",
            "description": "You discover a huge heap of scraps sitting at "
                           "the west side of the town, but a creature hides "
                           "within the pile. You somehow need to stall it "
                           "before having a shot to take any resources.",
            "health_range": (40, 60),
            "strength_range": (11, 16),
            "currency_range": (45, 65),
        },
        {
            "name": "Blarg",
            "description": "A 40 foot tall abomination oozes fatal acid with "
                           "every cratering step it takes across the corn field. "
                           "Any slight noise can instantly alert it, crushing "
                           "everything in the way to hunt its new target.",
            "health_range": (70, 100),
            "strength_range": (19, 27),
            "currency_range": (85, 115),
        },
    ]
 
    chosen = random.choice(monster_types)
 
    monster = {
        "name": chosen["name"],
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
    print(f"\n{'Welcome, ' + name + '!':^{width}}")
 
 
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
        name = input("What is your name?\n").strip()
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
    print("\nYou are in Wakefield.")
    print(f"Current HP: {state['player_hp']}, "
          f"Current Gold: {state['player_gold']}")
    print(f"Equipped Weapon: {weapon_text}")
    print("What would you like to do?\n")
    print("1) Leave Wakefield (Fight a Monster)")
    print(f"2) Sleep (Restore HP for {SLEEP_COST} Gold)")
    print("3) Visit the Shop")
    print("4) Equip a Weapon")
    print("5) Quit")
 
 
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
 
 
def fight_monster(state):
    """
    Fight a random monster until someone is defeated or the user flees.
 
    Each round, the player and the monster hit each other for random
    damage. An equipped weapon adds its damage to each hit and loses
    1 durability per attack, breaking at 0. If the player has a
    consumable (the Cosmic Hand), they can use it to defeat the monster
    instantly without losing any HP. Defeating the monster awards its currency as
    gold. If the player passes out, they wake up back in town with 1 HP.
 
    Parameters:
        state (dict): The game state. Its 'player_hp', 'player_gold',
            and 'player_inventory' are updated.
 
    Returns:
        None
    """
    monster = new_random_monster()
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
 
    if state["player_hp"] <= 0:
        print("\nEverything goes black. You feel exhausted in your bed.")
        state["player_hp"] = 1
    elif monster_hp <= 0:
        reward = monster["currency"]
        print(f"You killed {monster['name']} and got {reward} gold!")
        state["player_gold"] += reward
 
 
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
    
