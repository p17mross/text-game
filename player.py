import rooms
import combat
from combat import *
from menu import printScroll, chooseOption
import time

def printLineBreak():
    print()
    print("="*50)
    print()

class Player (Combatant):
    OPTION_PICK_UP_ITEM = 0
    OPTION_SEARCH_ROOM = 1
    OPTION_USE_ITEM = 2
    OPTION_NEXT_ROOM = 3

    # Second person verbs and pronouns
    words = WORDS_SECOND_PERSON
    possessive = "your"

    max_inventory_size: int
    current_room: rooms.Room

    new_room = True
    first_turn = True

    def __init__(self, max_inventory_size = 5, starting_room = rooms.JAIL, health = 10, **kwargs):

        super().__init__(name = "you", health = health, **kwargs)
        self.max_inventory_size = max_inventory_size
        self.current_room = starting_room

    def take_turn(self) -> Move:
        options_str = ["Nothing"]
        options = [Move.none()]
        for i, item in enumerate(self.inventory):
            options.append(Move.item(i))
            options_str.append(f"{self.words[VERBS_AFTER_PRONOUN][item.verb].capitalize()} your {item.name}")
        
        return options[chooseOption("What do you do? ", options_str)]

    def on_lose(self, other: Combatant):
        printScroll("You died", endPause=1)
        printScroll("Better luck next time", endPause=1)
        printScroll("Or not", endPause=1)
        raise PlayerDeathExeption

    def on_win(self, other: Combatant):
        # Give the player the enemy's weapons
        for item in other.inventory:
            self.pickUpItem(item)
        # Remove the enemy
        self.current_room.enemy = None
    
    def on_stalemate(self, other: Combatant):
        printScroll("You can't fight back. You are taken back to your cell and never see the light of day again.")
        raise PlayerDeathExeption

    def pickUpItem(self, item: Item):
        self.inventory.append(item)
        printScroll(f"You pick up {item.name}")

        if len(self.inventory) > self.max_inventory_size:
            discard_options = [f"{item.name} - {item.description}" for item in self.inventory]
            discard_choice = chooseOption("Your inventory is full - what will you discard? ", discard_options)
            self.inventory.pop(discard_choice)

    def chooseItemToPickUp(self):
        options = []
        for item in self.current_room.items:
            options.append(f"{item.name} - {item.description}")
        choice = chooseOption("Which item do you pick up?", options)
        self.pickUpItem(self.current_room.items.pop(choice))

        self.current_room.visited = True

    def searchRoom(self):
        if self.current_room.secret is None:
            printScroll("You looked thoroughly, but there was nothing to find")
            self.current_room.visited = True
        else:
            self.current_room.secret(self)
        
        self.current_room.secret_found = True 

    def useItem(self, item):
        if isinstance(item, Food):
            item.use(self, None)
            printScroll(f"You {self.words[VERBS_AFTER_PRONOUN][item.verb]} your {item.name}. ")
            printScroll(f"Your health is now {self.health} / {self.max_health}")
        elif isinstance(item, Key):
            if self.current_room == rooms.PASSAGE:
                printScroll("You check the key in all the locks you can find.")
                printScroll("None of them work, until you reach the biggest door at the very end or the corridor.")
                printScroll("You turn the key - Click.")
                printScroll("On the other side is the throne room, where the king sits.")
                rooms.PASSAGE.add_connection(rooms.THRONE_ROOM, "You push open the big door and walk in, putting on a brave face.")
            else:
                printScroll("You check the key in all the locks you can find, to no success.")
        elif isinstance(item, Shield):
            if self.equipped_shield is not None:
                self.inventory.append(self.equipped_shield)
            self.inventory.remove(item)
            self.equipped_shield = item

    def nextRoom(self, room_transition: rooms.RoomTransition):
        previous = self.current_room
        print()
        printScroll(room_transition.description)
        self.current_room = room_transition.to
        self.new_room = True
        # Call the new room's on_enter callback if it has one
        if self.current_room.on_enter is not None:
            self.current_room.on_enter(previous)


    def fightEnemy(self) -> bool:
        printScroll(f"You are challenged by {self.current_room.enemy.name} - {self.current_room.enemy.description}")
        fightBattle(self, self.current_room.enemy)

    def takeTurn(self) -> bool:
        printLineBreak()
        
        # Print 'still' if in a new room, but not on the first turn
        if not self.new_room and not self.first_turn:
            printScroll(f"You are still in {self.current_room.name}.")
        else:
            printScroll(f"You are in {self.current_room.name}.")
        self.first_turn = False

        # Print the room's description if in a new room
        if self.new_room:
            printScroll(f"It is {self.current_room.description}")
            self.new_room = False

        # If an enemy is present, start a battle with it
        if self.current_room.enemy is not None:
            self.fightEnemy()

        # Check for win after check for enemy so that final fights aren't skipped
        if self.current_room.win:
            for line in self.current_room.win_message.split("\n"):
                printScroll(line)
                time.sleep(0.5)
            return True


        options = []
        options_str = []
        
        # Picking up an item is only available once per room
        if not self.current_room.visited:
            if len(self.current_room.items) > 0:
                options.append([Player.OPTION_PICK_UP_ITEM])
                options_str.append("Pick up an item")

        # Can't look for secrets twice
        if not self.current_room.secret_found:
            options.append([Player.OPTION_SEARCH_ROOM])
            options_str.append("Search the room for secrets")

        for item in self.inventory:
            if isinstance(item, (Food, Key, Shield)):
                options.append([Player.OPTION_USE_ITEM, item])

                options_str.append(f"{self.words[VERBS_AFTER_PRONOUN][item.verb].capitalize()} your {item.name}")

        for connection in self.current_room.connections:
            options.append([Player.OPTION_NEXT_ROOM, connection])
            options_str.append(f"Go to {connection.to.name}")

        choice = options[chooseOption("What will you do? ", options_str)]

        match choice[0]:
            case Player.OPTION_PICK_UP_ITEM:
                self.chooseItemToPickUp()
            case Player.OPTION_SEARCH_ROOM:
                self.searchRoom()
            case Player.OPTION_USE_ITEM:
                self.useItem(choice[1])
            case Player.OPTION_NEXT_ROOM:
                self.nextRoom(choice[1])
        # Don't end game
        return False

    def playGame(self):
        endGame = False
        while not endGame:
            try:
                endGame = self.takeTurn()
            except PlayerDeathExeption:
                endGame = True