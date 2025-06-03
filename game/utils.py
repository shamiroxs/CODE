import random
import string

def generate_room_code(length=5):
    """Generate a unique room code using uppercase letters and digits."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def shuffle_deck():
    """
    Return a shuffled deck of CODE cards.
    You can adapt this if you want multiple instances of each letter, jokers, etc.
    """
    letters = ['C', 'O', 'D', 'E']
    # Example: 4 cards of each letter (16 total)
    deck = letters * 4
    random.shuffle(deck)
    return deck
