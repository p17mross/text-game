from math import log10
import time
import sys, select

DEFAULT_SCROLL_SPEED = 25

# Used to move the cursor around to scroll multiple lines of text at once.
ANSI_LEFT = "\033[D"
ANSI_RIGHT = "\033[C"
ANSI_UP = "\033[A"
ANSI_DOWN = "\033[B"

def scrollSimultaneously(lines: list[str], scrollSpeed = DEFAULT_SCROLL_SPEED):
    print("\n" * len(lines))

    to_sleep = 1 / scrollSpeed

    # Print each line one char at a time
    for i in range(max([len(line) for line in lines])):
        # Move the cursor to the right x and y positions 
        print(ANSI_RIGHT * i, end="")
        print(ANSI_UP * len(lines), end="")

        # Print each line
        for text in lines:
            # Don't try to print past the end of the string
            if i < len(text):
                print(f"{text[i]}", end=ANSI_LEFT)
            # Move to the next line
            print(ANSI_DOWN, end="")
        # Reset cursor so it is always at the left hand side during the sleep
        print(ANSI_LEFT * i, end="")

        # Wait for to_sleep seconds or until enter is pressed
        is_input, _, _ = select.select( [sys.stdin], [], [], to_sleep )
        # If enter was pressed
        if(is_input):
            # Move the cursor back up
            print(ANSI_UP, end="")
            # Read the character to stop it from being read in the next iteration of the loop
            input()
            # Set the timeout for all future iterations to 0
            to_sleep = 0
    print()


def chooseOption(prompt: str, options: list[str], scrollSpeed = DEFAULT_SCROLL_SPEED) -> int:
    lines = [prompt]

    padding = int(log10(len(options))) + 1

    for i, option in enumerate(options):
        lines.append(f"[{i+1:>{padding}}]: {option}")

    scrollSimultaneously(lines, scrollSpeed)
    
    # Loop until a valid selection is entered
    while True:
        # Parse input as an int
        try:
            printScroll("Enter your selection: ", end="")
            selection = int(input(""))
        # 'except ValueError' not just 'except' means that other exceptions (notably KeyboardInterrupt) are not caught here
        except ValueError:
            print("Not a valid selection")
            continue
        
        # Bounds check the input
        if selection <= 0 or selection > len(options):
            print(f"Selction must be between 1 and {len(options)}")
            continue
        
        # Input is 1-indexed but return value is 0-indexed, so subtract 1 from input
        return selection - 1

def printScroll(text, scrollSpeed = DEFAULT_SCROLL_SPEED, end = "\n", endPause = 0.2):
    if scrollSpeed == 0:
        print(text)
        return

    to_sleep = 1 / scrollSpeed

    for i, char in enumerate(text):
        print(char, end="")
        # Wait for to_sleep seconds or until enter is pressed
        is_input, _, _ = select.select( [sys.stdin], [], [], to_sleep )
        # If enter was pressed
        if(is_input):
            # Move the cursor back up
            print(ANSI_UP, end="")
            print(ANSI_RIGHT * (i + 1), end="")
            # Read the character to stop it from being read in the next iteration of the loop
            input()
            # Set the timeout for all future iterations to 0
            to_sleep = 0
    print(end=end)
    time.sleep(endPause)