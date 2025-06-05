import random
import string

def generate_room_code(length=5):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def shuffle_deck(num_players):
    letters = ['C', 'O', 'D', 'E']
    deck = 2 * num_players * letters
    random.shuffle(deck)
    return deck
