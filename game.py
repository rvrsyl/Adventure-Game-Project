"""Driver that imports gamefunctions.py and uses each function."""
 
import gamefunctions
 
 
def main():
    """Greet the player, visit the shop, and meet a monster."""
    name = input("What is your name? ")
    gamefunctions.print_welcome(name, 30)
 
    money = 500.0
    items = [("Camera", 5.49), ("Wrist-Rocket", 2.19)]
    gamefunctions.print_shop_menu(items[0][0], items[0][1],
                                  items[1][0], items[1][1])
    print(f"You have ${money:.2f}.")
 
    choice = input("Buy which item (1 or 2)? ")
    item_name, price = items[0] if choice == "1" else items[1]
    quantity = int(input(f"How many {item_name}s? "))
 
    bought, money = gamefunctions.purchase_item(price, money, quantity)
    print(f"You bought {bought} {item_name}(s) and have "
          f"${money:.2f} left.")
 
    monster = gamefunctions.new_random_monster()
    print(f"\nA wild {monster['name']} appears!")
    print(monster["description"])
    print(f"Health: {monster['health']}  "
          f"Strength: {monster['strength']}")
 
 
if __name__ == "__main__":
    main()
 
