from __future__ import annotations
from typing import Callable

from combat import *

class RoomTransition:
    to: Room
    description: str
    def __init__(self: RoomTransition, to: Room, description: str) -> None:
        self.to = to
        self.description = description

class Room:
    name: str
    description: str
    items: list[Weapon | Shield | Food]
    enemy: Enemy
    connections: list[RoomTransition]
    win: bool # Whether visiting this room wins the game
    win_message: str # The text to print if you win in this room

    visited: bool = False
    secret_found = False

    secret: Callable[[Player], None]
    on_enter: Callable[[Room], None]

    def __init__(self: Room, title: str, description: str, enemy: Enemy = None, items: list[Weapon | Shield] = None, secret = None, on_enter = None, win = False, win_message = None) -> None:
        self.name = title
        self.description = description
        self.items = items
        self.enemy = enemy
        self.connections = []
        self.items = items or []
        self.secret = secret
        self.on_enter = on_enter
        self.win = win
        self.win_message = win_message
    
    def add_connection(self, to: Room, description: str) -> None:
        self.connections.append(RoomTransition (to, description))


JAIL = Room (
    title = "The Jail", 
    description = "a dark cellar with rows of iron cages.", 
    items = [
        Shield (
            name = "Guard's Shield",
            description = "A large wooden shield used by the guards. It's mostly for show, but it'll protect you.",
            max_damage = 5,
            durability = 15
        ),
        Weapon (
            name = "Guard's Axe",
            description = "A double headed axe used by the guards. It's intimidating but unwieldy.",
            damage = 5,
            durability = 4,
        )
    ]
)

# Reveal the key
def armory_secret(player: Player):
    printScroll("You look around the rows of tables.")
    printScroll("One of them has drawers screwed into the underside.")
    printScroll("It's unlocked and empty apart from a hefty golden key.")
    player.pickUpItem(Key())

ARMORY = Room(
    title = "The Armory",
    description = "a room with many rows of swords and bows",
    items = [
        Weapon (
            name = "Iron sword",
            description = "An iron broadsword. It is powerful but will break quickly if not used with care.",
            damage = 5,
            durability = 3
        ),
        Weapon (
            name = "Training Bow",
            description = "A wooden training bow. It will not deal much damage but it is very reliable.",
            damage = 2,
            durability = 200
        )
    ],
    secret = armory_secret
)


GUARD_QUARTERS = Room (
    title = "The Guard's Quarters",
    description = "a large room with many bunk beds",
    enemy = Enemy (
        name = "Trainee Guard",
        description = "A new guard, stationed in the guards' quarters because nobody ever attacks from there",
        health = 10,
        inventory = [
            Shield (
                name = "Trainee Guard's Shield",
                description = "A flimsy wooden shield you took from the trainee guard",
                max_damage = 1,
                durability = 3,
            )
        ],
        words = random_third_person_words()
    )
)


# Reveal trapdoor to kitchen
def passage_secret(player: Player):
    printScroll("You notice a bump in the carpet in the middle of the corridor.")
    printScroll("You roll it up and find a trapdoor leading to a kitchen.")
    PASSAGE.add_connection(KITCHEN, "You slip through the trapdoor and land on top of a shelving unit")
PASSAGE = Room (
    title = "A Long Passage",
    description = "a long passage with doors every few metres, most of which are locked from the other side",
    secret = passage_secret
)


MESS_HALL = Room (
    title = "The Guards' Mess Hall",
    description = "a small, drab room with nobody in it. A few rows of tables are set up with cutlery and glasses",
    items = [
        Weapon (
            name = "Eating Knife",
            description = "A small, sharp steel knife. It's dangerous but one-use.",
            damage = 7,
            durability = 1
        )
    ]
)


# Reveal potion
def kitchen_secret(player: Player):
    printScroll("You look through all the cupboards and shelves. ")
    printScroll("At the back of a high shelf you find a small glass bottle with a cloudy green liquid labeled 'Potion of Healing'")
    player.pickUpItem(Food (
        name = "Potion of Healing",
        description = "A bottle of cloudy liquid which will heal all of your wounds, and make you stronger in the process",
        health = 100,
        max_health_increase = 5,
        verb = VERB_DRINK
    ))
# Change message from mess hall to kitchen
def guard_kitchen_on_enter(previous: Room):
    if previous == MESS_HALL:
        MESS_HALL.connections[2].description = "This time you decide to go through the door instead. It was a bit overdramatic last time and you want to avoid being noticed."
COOK_WORDS = random_third_person_words()
KITCHEN = Room (
    title = "The Kitchen",
    description = "a stone room with many pots and pans hung on hooks. In the centre of the room there is a row of cauldrons and furnaces",
    items = [
        Shield (
            name = "Pot Lid",
            description = "An iron lid for a large cooking pot.",
            max_damage = 10,
            durability = 25,
        ),
        Food (
            name = "Loaf of Bread",
            description = "A large loaf of wheat bread. There are loads here, so nobody will miss one.",
            health = 5,
        )
    ],
    enemy = Enemy (
        name = "Cook",
        description = f"The cook in the guards' kitchen. {COOK_WORDS[PRONOUNS][CONTRACTION_BE].capitalize()} a retired soldier, so {COOK_WORDS[PRONOUNS][CASE_SUBJ]} {COOK_WORDS[VERBS_AFTER_PRONOUN][VERB_KNOW]} how to use a knife.",
        words = COOK_WORDS,
        health = 5,
        inventory = [
            Weapon (
                name = "Cooking Knife",
                description = "The cooking knife you took from the cook",
                damage = 7,
                durability = 3,
            ),
            Food (
                name = "Bowl of Soup",
                description = "A bowl of pea soup which you took from the cook",
                health = 4,
            )
        ]
    ),
    secret = kitchen_secret
)


STORE_ROOM = Room (
    title = "The Store Room",
    description = "a chilly room where all the ingredients are kept for the King's meals. Many rows of shelves contain all kinds of exotic ingredients.",
    items = [
        Food (
            name = "Raw Steak",
            description = "An uncooked steak. It's not very hygienic but food poisoning is the least of your worries right now.",
            health = 20,
            max_health_increase = 5
        ),
        Food (
            name = "Chocolate Cake",
            description = "A fresh chocolate cake. It will heal you but it won't give you much nutrition.",
            health = 10
        )
    ]
)

# Reveal the dock
def servants_passage_secret(player: Player):
    printScroll("It's nearly pitch black. You run your hands along the cramped walls, and find a door handle.")
    printScroll("On the other side is a cavern, containing cove with a dock.")
    SERVANTS_PASSAGE.add_connection(DOCK, "You open the secret door, and see glorious sunlight on the ocean below.")
BUTLER_WORDS = random_third_person_words()
SERVANTS_PASSAGE = Room (
    title = "The Servants' Passage",
    description = "a narrow, dimly lit corridor. It contains many twists and turns",
    
    enemy = Enemy (
        name = "Butler",
        description = f"The King's butler. {BUTLER_WORDS[PRONOUNS][CASE_SUBJ]} {BUTLER_WORDS[VERBS_AFTER_PRONOUN][VERB_BE]} trained in martial arts.",
        health = 10,
        inventory = [
            Weapon (
                name = "Ceremonial Butler's Dagger",
                description = "An expensive ivory dagger which is a symbol of responsiblity for the butler (or it used to be, anyway)",
                damage = 8,
                durability = 5
            ),
            Shield (
                name = "Dinner Tray",
                description = "A piece of silverware which can be used to protect yourself, in a pinch",
                max_damage = 4,
                durability = 10
            )
        ],
        words = BUTLER_WORDS
    ),
    secret = servants_passage_secret
)


ROYAL_DINING_HALL = Room (
    title = "The Royal Dining Hall",
    description = "where the King and Queen eat their meals. It is a large room with many decorative suits of armour around the edges",
    items = [
        Weapon (
            name = "Decorative Mace",
            description = "A mace which one of the suits of armour is holding. It's decorative but still packs a punch.",
            damage = 15,
            durability = 4,
        ),
        Shield (
            name = "Decorative Shield",
            description = "A shield which one of the suit of armour is holding. It's made for show, but made well.",
            max_damage = 15,
            durability = 50,
        )
    ]
)


DOCK = Room (
    title = "The Dock",
    description = "a large carvern with a dock opening on a cove connected to the sea. There's a boat moored, but it has someone in it.",
)


ROWER_WORDS = random_third_person_words()
ROWBOAT = Room (
    title = "A Rowing Boat",
    description = "A wooden boat used to get supplies in and out of the complex",
    win = True,
    win_message = "You untie the boat and push off. You're not very good at rowing but nobody's coming after you. \n\nYou can finally relax.",
    enemy = Enemy (
        name = "Rower",
        description = f"A servant of the King. {ROWER_WORDS[PRONOUNS][CASE_SUBJ].title()} {ROWER_WORDS[VERBS_AFTER_PRONOUN][VERB_BE]} not very skilled but {ROWER_WORDS[VERBS_AFTER_PRONOUN][CONTRACTION_BE]} strong and fiercely loyal.",
        health = 20,
        inventory = [
            Weapon (
                name = "Wooden Oar",
                description = "",
                damage = 8,
                durability = 4,
            ),
            Food (
                name = "Lunch",
                description = "",
                health = 5,
            )
        ],
        words = ROWER_WORDS
    )
)


def chapel_secret(player: Player):
    CHAPEL.win = True
    CHAPEL.win_message = """You look around, and feel like something is off...
Why is there so much daylight? Wasn't this whole place underground?
You clamber up the walls to one of the stained glass windows, and realise that it is in the side of a cliff!
You break the window with a candle holder and stare at the ocean below
It can't be that far
And anything's better than this,
You jump...

"""
CHAPEL = Room (
    title = "The Chapel",
    description = "a very intricate space, with many rows of seats facing an altar. Light streams in from a lage stained glass window at the front.",
    items = [
        Weapon (
            name = "Spiritual Candelabra",
            description = "An elaborate candle holder. It's not designed for combat but it's got some nasty looking pointy bits on it.",
            damage = 6,
            durability = 3,
        ),
        Shield (
            name = "Holy Bible",
            description = "Just a bible. You could use it to block an attack, but only once.",
            max_damage = 2000, # A special message is printed when this shield is used
            durability = 1
        )
    ],
    secret = chapel_secret
)


def holy_sword_on_break():
    printScroll("The king stares at the remains of his sword.")
    printScroll("You see the faith leave his eyes.")
    KING.health = 0

KING = Enemy (
    name = "The King",
    description = "The man himself. He's holding a sword and a grudge, and is willing to enact judgement.",
    health = 50,
    inventory = [
        Weapon (
            name = "Holy Sword",
            description = "",
            damage = 15,
            durability = 4,
            on_break = holy_sword_on_break
        )
    ],
    words = WORDS_THIRD_PERSON_MASC
)
THRONE_ROOM = Room (
    title = "The Throne Room",
    description = "a vast, exquisitely decorated room with a long red carpet drawing the eye to an ornate throne at the back of the room. The King sits there, menacingly.",
    enemy = KING,
    win = True,
    win_message = """The King falls to his knees.
He says nothing but you see in his eyes he is begging you for mercy.
'Guards,' you shout, 'take this man away.'
You will decide what to do with him later.
You pace to the throne and take your seat. It is good to be back.
'Bring me my crown,' you order forcefully.

'Yes,' the servant reponds


Your Majesty.
"""
)


JAIL.add_connection(ARMORY, "You sneak past the sleeping guards and through a tall door.")
JAIL.add_connection(PASSAGE, "There is a wide open door, but it's guarded on the other side, so you sneak through a window instead.")

PASSAGE.add_connection(CHAPEL, "You walk through the chapel door and feel the light of God on you.")
PASSAGE.add_connection(ARMORY, "You walk through the creaky door into the armory")

CHAPEL.add_connection(PASSAGE, "You leave the chapel. It feels colder and darker in the passage than when you left it.")

ARMORY.add_connection(JAIL, "You walk back past the guards. They're out cold, so you don't even need to be quiet.")
ARMORY.add_connection(PASSAGE, "You open a creaky door. It makes a loud noise but nobody hears.")
ARMORY.add_connection(GUARD_QUARTERS, """You walk through a large doorway at the end of the corridor, hoping that nobody is in the guards' quarters.
It's the middle of the day (probably, you can't really tell) so there shouldn't be anyone, right?""")

GUARD_QUARTERS.add_connection(ARMORY, "You go through the massive arch into the armory. It feels like there should be someone in here, but there's not.")
GUARD_QUARTERS.add_connection(MESS_HALL, "You walk down a flight of wooden stairs.")

MESS_HALL.add_connection(GUARD_QUARTERS, "You walk up a wooden staircase")
MESS_HALL.add_connection(PASSAGE, "You walk up a flight of stairs and through a door, which shuts and locks behind you.")
MESS_HALL.add_connection(KITCHEN, "You hop over the counter in the serving area, knocking a plate which smashes on the floor.")

KITCHEN.add_connection(MESS_HALL, "You walk carefully through the door to the dining area.")
KITCHEN.add_connection(SERVANTS_PASSAGE, "You duck under a small archway in the back corner of the kitchen.")
KITCHEN.add_connection(STORE_ROOM, "You open a large, heavy door and are met with a gust of cold air, and the scent of meat and spices.")

STORE_ROOM.add_connection(KITCHEN, "You walk back into the kitchen, leaving the door open behind you.")

SERVANTS_PASSAGE.add_connection(KITCHEN, "You step over the butler and go back into the kitchen.")
SERVANTS_PASSAGE.add_connection(ROYAL_DINING_HALL, "You open a small door into a dining room, decorated with many books and paintings.")

# The only way to enter the dining hall is through the servant's passage, so this message is always appropriate
ROYAL_DINING_HALL.add_connection(SERVANTS_PASSAGE, """You look at the door you came in from. It's well hidden, looking like a bookshelf. 
You go through it, and take a moment for you eyes to adjust to the darkness""")
ROYAL_DINING_HALL.add_connection(PASSAGE, "You exit through the main door, which promptly swings shut behind you. There's no handle on this side.")

DOCK.add_connection(SERVANTS_PASSAGE, "You go back through the door into the tiny corridor. You wonder how they get anything through there, with so little space.")
DOCK.add_connection(ROWBOAT, "You take your chances and tiptoe over to the boat, hoping to take the rower by surprise.")


# This import is only needed for type signatures, so it is at the end to avoid circular imports
from player import *