from __future__ import annotations
from typing import Callable
from dataclasses import dataclass
import abc # Abstract base class
import random

from menu import printScroll, chooseOption, scrollSimultaneously

THIS_MOD = __import__(__name__)

VERB_BE = 0
VERB_ATTACK = 1
VERB_EAT = 2
VERB_DO = 3
VERB_EQUIP = 4
VERB_USE = 5
VERB_GO = 6
VERB_WIN = 7
VERB_KNOW = 8
VERB_DRINK = 9

VERBS_SECOND_PERSON = [
    "are", "attack", "eat", "do", "equip", "use", "go", "win", "know", "drink"
]

VERBS_THIRD_PERSON_SINGULAR = [
    "is", "attacks", "eats", "does", "equips", "uses", "goes", "wins", "knows", "drinks"
]

VERBS_THIRD_PERSON_PLURAL = [
    "are", "attack", "eat", "do", "equip", "use", "go", "win", "know", "drink"
]

VERBS_AFTER_NAME = 0
VERBS_AFTER_PRONOUN = 1
PRONOUNS = 2

CASE_SUBJ = 0
CASE_OBJ = 1
CASE_POSS = 2

CONTRACTION_BE = 3

WORDS_SECOND_PERSON = (
    VERBS_SECOND_PERSON,
    VERBS_SECOND_PERSON,
    [
        "you", "you", "your", "you're"
    ]
)

WORDS_THIRD_PERSON_MASC = (
    VERBS_THIRD_PERSON_SINGULAR,
    VERBS_THIRD_PERSON_SINGULAR,
    [
        "he", "him", "his", "he's"
    ]
)

WORDS_THIRD_PERSON_FEM = (
    VERBS_THIRD_PERSON_SINGULAR,
    VERBS_THIRD_PERSON_SINGULAR,
    [
        "she", "her", "her", "she's"
    ]
)

WORDS_THIRD_PERSON_NEUT = (
    VERBS_THIRD_PERSON_SINGULAR,
    VERBS_THIRD_PERSON_PLURAL,
    [
        "they", "them", "their", "they're"
    ]
)

def random_third_person_words():
    return random.choice([WORDS_THIRD_PERSON_FEM, WORDS_THIRD_PERSON_MASC, WORDS_THIRD_PERSON_NEUT])

class PlayerDeathExeption (Exception):
    pass

class Item:
    name: str
    description: str

    verb: int # The index into the user's verbs to use when describing the action of using the item

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def use(self, user: Combatant, opponent: Combatant):
        return NotImplementedError

class Weapon(Item):
    damage: int
    durability: int

    verb = VERB_USE

    on_break: Callable[[None], None]

    def __init__(self, damage: int, durability, on_break = None, **kwargs):
        super().__init__(**kwargs)
        self.damage = damage
        self.durability = durability
        self.on_break = on_break

    def use(self, user: Combatant, opponent: Combatant):
        shield = opponent.equipped_shield
        if shield is not None:
            if shield.name == "Holy Bible":
                printScroll("The power of Christ stopped the attack in its tracks.")
            elif min(shield.max_damage, shield.durability) > self.damage:
                printScroll(f"The attack was blocked by {opponent.possessive} {opponent.equipped_shield.name}")
            else:
                printScroll(f"The attack was partially blocked by {opponent.possessive} {opponent.equipped_shield.name}")
            dealt_damage = max(0, self.damage - shield.max_damage)
            shield.durability -= self.damage
            if shield.durability <= 0:
                printScroll(f"{opponent.possessive} {shield.name} broke!")
                opponent.equipped_shield = None
        else:
            dealt_damage = self.damage
        
        self.durability -= 1
        if self.durability == 0:
            printScroll(f"{user.possessive} {self.name} broke!")
            user.inventory.remove(self)
            if self.on_break is not None:
                self.on_break()
        
        opponent.health -= dealt_damage

class Shield(Item):
    max_damage: int # The maximum damage the shield can absorb in one hit
    durability: int # The maximum damage the shield can absorb

    def __init__(self, max_damage: int, durability: int, verb = VERB_EQUIP, **kwargs):
        super().__init__(**kwargs)
        self.max_damage = max_damage
        self.durability = durability
        self.verb = verb
    
    def use(self, user: Combatant, opponent: Combatant):
        user.inventory.remove(self)
        user.equipped_shield = self
 
class Food(Item):
    health: int # How much the food heals for
    max_health_increase: int # How much the food increases the user's max health

    def __init__(self, health: int, max_health_increase: int = 0, verb = VERB_EAT, **kwargs):
        super().__init__(**kwargs)
        self.health = health
        self.max_health_increase = max_health_increase
        self.verb = verb
    
    def use(self, user: Combatant, opponent: Combatant):
        user.max_health += self.max_health_increase
        user.health = min(user.health + self.health, user.max_health)
        user.inventory.remove(self)

class Key(Item):
    def __init__(self):
        self.name = "Golden Key"
        self.description = "The key you found in a drawer"
        self.verb = VERB_USE
    def use(self, user: Combatant, other: Combatant):
        printScroll("It's a key")
        printScroll("You can't attack someone with a key")

# Represents a move that a combatant takes
@dataclass
class Move:
    is_none: bool = False
    item_index: int = None

    @staticmethod
    def none() -> Move:
        return Move(is_none=True)
    
    @staticmethod
    def item(index: int) -> Move:
        return Move(item_index=index)


class Combatant(abc.ABC):
    name: str
    health: int
    max_health: int
    inventory: list[Item]

    equipped_shield: Shield = None

    words: tuple[list[str], list[str], list[str]]
    possessive: str

    def __init__(self, name, health, max_health = None, inventory = None):
        self.name = name
        self.health = health
        self.max_health = max_health or health
        self.inventory = inventory or []

    # Function which determines what a combatant will do in a situation
    def take_turn(self) -> Move:
        pass

    def on_win(self, other: Combatant):
        pass

    def on_lose(self, other: Combatant):
        pass
    
    def on_stalemate(self, other: Combatant):
        pass



class Enemy(Combatant):

    description: str

    def __init__(self, description: int, words: tuple[list[str], list[str], list[str]], **kwargs):
        super().__init__(**kwargs)

        self.description = description
        self.words = words
        self.possessive = self.name + "'s"

    # Enemy AI
    def take_turn(self) -> Move:
        # If no shield is equipped, try to find the best one
        if self.equipped_shield is None:
            most_defence_shield_index: int = None
            for i, item in enumerate(self.inventory):
                # If the item is a shield
                if isinstance(item, Shield):
                    # If this is the first shield or has the highest defense so far, equip it
                    if most_defence_shield_index is None or item.max_damage > self.inventory[most_defence_shield_index].max_damage:
                        most_defence_shield_index = i
            # If a shield was found, equip it
            if most_defence_shield_index is not None:
                return Move.item(most_defence_shield_index)
        
        # If below half health, eat food
        if self.health < self.max_health / 2:
            least_health_food_index = None
            for i, item in enumerate(self.inventory):
                # If the item is food
                if isinstance(item, Food):
                    # If this is the first food or has the lowest health so far, eat it
                    if least_health_food_index is None or item.health < self.inventory[least_health_food_index].health:
                        most_defence_shield_index = i
            
            # A food was found, eat it
            if least_health_food_index is not None:
                return Move.item(least_health_food_index)

        most_damage_weapon_index = None

        # Otherwise, use the weapon with the most damage
        for i, item in enumerate(self.inventory):
                # If the item is a weapon
                if isinstance(item, Weapon):
                    # If this is the first weapon or has the highest damge so far, use it
                    if most_damage_weapon_index is None or item.damage > self.inventory[most_damage_weapon_index].damage:
                        most_damage_weapon_index = i
    
        # If a weapon was found, use it
        if most_damage_weapon_index is not None:
            return Move.item(most_damage_weapon_index)
        
        # If all checks fail, do nothing
        return Move.none()


def fightBattle(p1: Combatant, p2: Combatant):

    scrollSimultaneously([
        "=~-" * 40,
        "",
        f"{'BATTLE BEGIN':^120s}",
        "",
        "=~-" * 40
    ], 100)

    while True:

        p1_has_weapon = any([isinstance(item, Weapon) for item in p1.inventory])
        p2_has_weapon = any([isinstance(item, Weapon) for item in p2.inventory])

        if not p1_has_weapon and not p2_has_weapon:
            scrollSimultaneously([
                "=~-" * 40,
                "",
                f"{'STALEMATE - NEITHER COMBATANT HAS A WEAPON':^120s}",
                "",
                "=~-" * 40
            ], 100)
            p1.on_stalemate(p2)
            p2.on_stalemate(p1)
            return

        p1_shield_text = f"{p1.equipped_shield.name} equipped" if p1.equipped_shield is not None else "no shield equipped"
        p2_shield_text = f"{p2.equipped_shield.name} equipped" if p2.equipped_shield is not None else "no shield equipped"
        printScroll(f"{p1.name.title()}: {p1.health} / {p1.max_health} - {p1_shield_text}")
        printScroll(f"{p2.name.title()}: {p2.health} / {p2.max_health} - {p2_shield_text}")

        # Record the participants' choices
        p1choice = p1.take_turn()
        p2choice = p2.take_turn()

        # Randomise turn order
        turn_order = [(p1, p2, p1choice), (p2, p1, p2choice)]
        random.shuffle(turn_order)
        printScroll(f"{turn_order[0][0].name.title()} will go first.")

        for combatant, other, choice in turn_order:
            if choice.is_none:
                printScroll(f"{combatant.name} {combatant.words[VERBS_AFTER_NAME][VERB_DO]} nothing")
            else:
                item = combatant.inventory[choice.item_index]
                printScroll(f"{combatant.name} {combatant.words[VERBS_AFTER_NAME][item.verb]} {combatant.words[PRONOUNS][CASE_POSS]} {item.name}")
                item.use(combatant, other)
            
            # Check both combatants' health
            for combatant, other in [(p1, p2), (p2, p1)]:
                if other.health <= 0:

                    win_text = f"{combatant.name} {combatant.words[VERBS_AFTER_NAME][VERB_WIN]} the battle!".upper()
                    win_text_padded = f"{win_text:^120s}"

                    scrollSimultaneously([
                        "=~-" * 40,
                        "",
                        win_text_padded,
                        "",
                        "=~-" * 40
                    ], 100)

                    combatant.on_win(other)
                    other.on_lose(combatant)
                    return
        
            