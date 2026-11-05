# game.py

"""A very basic text adventure. Run with PowerShell as: python game.py"""
 
import gamefunctions
 
 
def main():
    """Run the town menu loop until the player quits."""
    name = gamefunctions.get_player_name()
    gamefunctions.print_welcome(name, 30)
    state = gamefunctions.new_game_state(name)
    while True:
        gamefunctions.print_town_menu(state)
        choice = gamefunctions.get_menu_choice(["1", "2", "3", "4", "5"])
        if choice == "1":
            gamefunctions.fight_monster(state)
        elif choice == "2":
            gamefunctions.sleep(state)
        elif choice == "3":
            gamefunctions.shop(state)
        elif choice == "4":
            gamefunctions.equip_item(state, "weapon")
        else:
            print(f"\nThanks for playing {state['player_name']}, see you soon! :)")
            break
 
 
if __name__ == "__main__":
    main()
