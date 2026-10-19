# gamefunctions.py

"""Helper functions for a simple text-based adventure game. Running this file directly (python gamefunctions.py) calls
test_functions().


Constants:
    MAX_HP: The most health the player can have.
    SLEEP_COST: Gold charged to sleep and restore all health.
    
Functions:
    purchase_item: Buy as many items as the player can afford.
    new_random_monster: Create a random monster as a dictionary.
    print_welcome: Print a centered greeting for the player.
    print_market_menu: Print a bordered sign listing two market items.
    get_menu_choice: Prompt until the user enters a valid option.
    get_player_name: Prompt until the user enters a name.
    print_town_menu: Show the town status and menu.
    sleep: Restore the player's health for gold.
    display_fight_statistics: Show the current state of a fight.
    get_user_fight_action: Ask whether to attack or run away.
    fight_monster: Run a full fight and report the outcome.
    test_functions: Demonstrate the non-interactive functions.

Typical usage example:

  import gamefunctions

  hp, gold = gamefunctions.MAX_HP, 10
  hp, gold = gamefunctions.fight_monster(hp, gold)
"""

import random

MAX_HP = 100
SLEEP_COST = 5


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
            (str), 'health' (int), 'strength' (int), and 'currency' (int).

    Example:
        >>> monster = new_random_monster()
        >>> sorted(monster.keys())
        ['currency', 'description', 'health', 'name', 'strength']
    """
    monster_types = [
        {
            "name": "Water Fowl",
            "description": "In the distance is a feathery, aquatic monster that "
                           "has frills resembling closely to those of an extinct "
                           "dinosaur. It makes a hooting sound as it slurps up "
                           "water from the polluted lake.",
            "health_range": (15, 25),
            "strength_range": (2, 5),
            "currency_range": (15, 30),
        },
        {
            "name": "Scrapken",
            "description": "You discover a huge heap of scraps sitting at the "
                           "west side of your campsite, but a creature hides "
                           "within the pile. You somehow need to stall it "
                           "before having a shot to take any resources.",
            "health_range": (30, 45),
            "strength_range": (9, 14),
            "currency_range": (50, 75),
        },
        {
            "name": "Blarg",
            "description": "A 40 foot tall abomination oozes fatal acid with "
                           "every cratering step it takes across the ghost town. "
                           "The snap of a twig instantly alerts it, crushing "
                           "everything in the way towards its target.",
            "health_range": (50, 100),
            "strength_range": (16, 23),
            "currency_range": (100, 175),
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
        >>> print_welcome("Jim", 20)
            Welcome, Jim!    
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


def print_town_menu(hp, gold):
    """
    Print the player's status and the list of town actions.

    Parameters:
        hp (int): The player's current health.
        gold (int): The player's current gold.

    Returns:
        None
    """
    print("\nYou are in Wakefield.")
    print(f"Current HP: {hp}, Current Gold: {gold}")
    print("What would you like to do?\n")
    print("1) Leave Wakefield (Fight a Monster)")
    print(f"2) Sleep (Restore HP for {SLEEP_COST} Gold)")
    print("3) Quit")


def sleep(hp, gold):
    """
    Restore the player to full health in exchange for gold.

    Prints a message and changes nothing if the player cannot
    afford it or is already at full health.

    Parameters:
        hp (int): The player's current health.
        gold (int): The player's current gold.

    Returns:
        tuple: (new hp (int), new gold (int)).
    """
    if hp >= MAX_HP:
        print("You're already at full health.")
    elif gold < SLEEP_COST:
        print(f"You need {SLEEP_COST} gold to sleep.")
    else:
        print("You sleep peacefully and wake up fully energized.")
        return MAX_HP, gold - SLEEP_COST
    return hp, gold


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


def get_user_fight_action():
    """
    Ask the user whether to keep fighting or run away.

    Parameters:
        None

    Returns:
        str: "1" to attack or "2" to run away.
    """
    print("1) Attack")
    print("2) Run Away")
    return get_menu_choice(["1", "2"])


def fight_monster(hp, gold):
    """
    Fight a random monster until someone is defeated or the user flees.

    Each round, the player and the monster hit each other for random
    damage. Defeating the monster awards its currency as gold. If the
    player passes out, they wake up back in town with 1 HP.

    Parameters:
        hp (int): The player's current health.
        gold (int): The player's current gold.

    Returns:
        tuple: (new hp (int), new gold (int)).
    """
    monster = new_random_monster()
    monster_hp = monster["health"]
    print(f"\nA wild {monster['name']} appears!")
    print(monster["description"])

    while hp > 0 and monster_hp > 0:
        display_fight_statistics(hp, monster, monster_hp)
        if get_user_fight_action() == "2":
            print("You fled the fight.")
            break
        hit = random.randint(10, 25)
        counter = random.randint(*monster["strength_range"])
        monster_hp -= hit
        hp -= counter
        print(f"\nYou hit for {hit}. {monster['name']} hits back for {counter}.")

    if hp <= 0:
        print("\nEverything goes black. You feel exhuasted in your bed.")
        hp = 1
    elif monster_hp <= 0:
        reward = monster["currency"]
        print(f"You killed {monster['name']} and got {reward} gold!")
        gold += reward
    return hp, gold


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
    
    print("\n--- town menu and sleep ---\n")
    print_town_menu(MAX_HP, 10)
    print(sleep(10, 10))
    print(sleep(10, 2))
    print(sleep(MAX_HP, 10))
    print()

if __name__ == "__main__":
    test_functions()

