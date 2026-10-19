# game.py

"""A very basic text adventure. Run with PowerShell as: python game.py"""

import gamefunctions


def main():
    """Run the town menu loop until the player quits."""
    name = gamefunctions.get_player_name()
    gamefunctions.print_welcome(name, 30)
    hp, gold = gamefunctions.MAX_HP, 10
    while True:
        gamefunctions.print_town_menu(hp, gold)
        choice = gamefunctions.get_menu_choice(["1", "2", "3"])
        if choice == "1":
            hp, gold = gamefunctions.fight_monster(hp, gold)
        elif choice == "2":
            hp, gold = gamefunctions.sleep(hp, gold)
        else:
            print(f"\nThanks for playing {name}, see you soon! :)")
            break


if __name__ == "__main__":
    main()
