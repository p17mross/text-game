from player import Player
from menu import printScroll

printScroll("You are trapped in a fortress, deep underground")
printScroll("You have escaped your cage but need to find your way out of the compound without being caught or killed.")
printScroll("Good luck")

player = Player()

player.playGame()