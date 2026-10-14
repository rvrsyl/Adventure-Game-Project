# Assignment 05 - Game Functions
# ---------------------------------------------------------------------------

import random

def purchase_item(itemPrice, startingCurrency, quantityToPurchase=1):
    """
    Attempts to purchase quantityToPurchase items at itemPrice each,
    starting with startingCurrency. If the full quantity can't be afforded,
    buys as many as possible instead.

    Returns a tuple: (quantity purchased, currency remaining)
    """
    affordable_quantity = startingCurrency // itemPrice
    actual_quantity = min(affordable_quantity, quantityToPurchase)
    currency_remaining = startingCurrency - (actual_quantity * itemPrice)
    return actual_quantity, currency_remaining

def new_random_monster():
    """
    Creates a random monster as a dictionary with keys:
    name, description, health, strength, currency.

    Returns the monster dictionary.
    """
    monster_types = [
        {
            "name": "Water Fowl",
            "description": "In the distance is a feathery, aquatic monster that "
                            "has frills resembling closely to those of an extinct "
                            "dinosaur. It makes a hooting sound as it slurps up "
                            "water from the polluted lake.",
            "health_range": (20, 40),
            "strength_range": (10, 25),
            "currency_range": (10, 50),
        },
        {
            "name": "Scrapken",
            "description": "You discover a huge heap of scraps sitting at the "
                            "western edge of your campsite, but a creature hides "
                            "within the pile. You somehow need to stall it "
                            "before having a shot to take any resources.",
            "health_range": (75, 125),
            "strength_range": (5, 8),
            "currency_range": (750, 2000),
        },
        {
            "name": "Blarg",
            "description": "A 40 foot tall abomination oozes fatal acid with "
                            "every cratering step it takes across the ghost town. "
                            "The snap of a twig instantly alerts it, crushing "
                            "everything in the way towards its target.",
            "health_range": (200, 300),
            "strength_range": (50, 80),
            "currency_range": (150, 450),
        },
    ]

    chosen = random.choice(monster_types)

    monster = {
        "name": chosen["name"],
        "description": chosen["description"],
        "health": random.randint(*chosen["health_range"]),
        "strength": random.randint(*chosen["strength_range"]),
        "currency": random.randint(*chosen["currency_range"]),
    }
    return monster

if __name__ == "__main__":
    # Demonstrate purchase_item three times with different arguments

    # 1. Default quantityToPurchase (demonstrates the default value of 1)
    num_purchased, leftover_currency = purchase_item(418, 2476)
    print(f"Purchased {num_purchased} item(s), {leftover_currency} currency left.")

    # 2. Can afford the full requested quantity
    num_purchased, leftover_currency = purchase_item(184, 1250, 6)
    print(f"Purchased {num_purchased} item(s), {leftover_currency} currency left.")

    # 3. Cannot afford the full requested quantity (purchase is limited)
    num_purchased, leftover_currency = purchase_item(174, 381, 3)
    print(f"Purchased {num_purchased} item(s), {leftover_currency} currency left.")

    print()

    # Demonstrate new_random_monster three separate times
    for i in range(3):
        monster = new_random_monster()
        print(f"Monster {i + 1}: {monster['name']}")
        print(f"  Description: {monster['description']}")
        print(f"  Health: {monster['health']}")
        print(f"  Strength: {monster['strength']}")
        print(f"  Currency: {monster['currency']}")
        print()
# ===========================================================================

# Assignment 06 - Documentation and Strings
# ---------------------------------------------------------------------------

"""Helper functions for the text-based game."""

def print_welcome(name, width):
    """Prints a centered welcome message.

    Parameters:
        name (str): the name to greet.
        width (int): total width of the field the message is centered in.

    Returns:
        None
    """
    print(f"{'Hello, ' + name + '!':^{width}}")

def print_shop_menu(item1Name, item1Price, item2Name, item2Price):
    """Prints a bordered shop sign listing two items and their prices.

    Item names are left-aligned in a 12-character field. Prices are
    right-aligned in an 8-character field, shown with a dollar sign and
    exactly two decimal places.

    Parameters:
        item1Name (str): name of the first item.
        item1Price (float): price of the first item.
        item2Name (str): name of the second item.
        item2Price (float): price of the second item.

    Returns:
        None
    """
    print("/" + "-" * 22 + "\\")
    print(f"| {item1Name:<12}{'$' + format(item1Price, '.2f'):>8} |")
    print(f"| {item2Name:<12}{'$' + format(item2Price, '.2f'):>8} |")
    print("\\" + "-" * 22 + "/")
    return None

# Demonstration calls (no user input required)

print_welcome("Jack", 17)
print_welcome("June", 22)
print_welcome("Quint", 27)
print_welcome("Dirk", 32)

print_shop_menu("Camera", 5.49, "Wrist-Rocket", 2.19)
print_shop_menu("BOOMerang", 17.79, "Juice Bombs", 14.09)
print_shop_menu("Night Blade", 499.99, "Cosmic Hand", 249.99)
# ===========================================================================    
    
