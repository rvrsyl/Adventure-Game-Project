# game.py

"""A very basic text adventure. Run with PowerShell as: python game.py"""
 
import gamefunctions
 
 
def main():
    """Start or load a game, then run the town menu loop until the player quits."""
    state = gamefunctions.start_menu()
    gamefunctions.print_welcome(state["player_name"], 30)
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
            # Only quit if the save worked, so progress is never lost silently.
            if gamefunctions.save_game(state, gamefunctions.get_save_filename()):
                print(f"Thanks for playing {state['player_name']}, see you soon! :)")
                break
 
 
if __name__ == "__main__":
    main()
