from .utils import shuffle_deck
from .models import Player
from django.utils import timezone

def get_next_player(players, current_player):
    player_list = list(players.order_by('id')) 
    try:
        current_index = player_list.index(current_player)
    except ValueError:
        return None
    next_index = (current_index + 1) % len(player_list)
    return player_list[next_index]

def start_game(room):
    players = list(Player.objects.filter(room=room))
    num_players = len(players)
    deck = shuffle_deck(num_players)
    hand_size = 4
    
    hands = []
    
    while True:
        deck = shuffle_deck(num_players)
        valid = True

        existing_hands = set()
        for i in range(num_players):
            hand = tuple(deck[i * hand_size: (i + 1) * hand_size])
            if hand in existing_hands or len(set(hand)) > 2:
                valid = False
                break
            hands.append(hand)

        if valid:
            break
    
    # Deal cards to each player
    for i, player in enumerate(players):
        # player.hand = deck[i * hand_size: (i + 1) * hand_size]
        player.hand = hands[i]
        player.is_turn = (i == 0)
        player.has_won = False
        player.save()

    table_card_count = 2 * num_players
    room.table_cards = deck[num_players * hand_size: num_players * hand_size + table_card_count]

    room.current_turn = 0
    room.status = 'playing'
    room.save()

def swap_card(player, room, hand_index, table_index):
    hand = player.hand
    table = room.table_cards

    hand[hand_index], table[table_index] = table[table_index], hand[hand_index]

    player.hand = hand
    player.is_turn = False
    player.save()

    room.table_cards = table
    players = list(Player.objects.filter(room=room))
    next_index = (room.current_turn + 1) % len(players)
    room.current_turn = next_index
    room.save()

    for i, p in enumerate(players):
        p.is_turn = (i == next_index)
        p.save()

    if check_win(player):
        player.has_won = True
        player.save()
        room.status = 'finished'
        room.save()
        return True

    return False

def check_win(player):
    return set(player.hand) == {'C', 'O', 'D', 'E'}

def reset_game(room):
    players = Player.objects.filter(room=room)
    for player in players:
        player.hand = []
        player.is_turn = False
        player.has_won = False
        player.save()
    room.table_cards = []
    room.current_turn = 0
    room.status = 'reset'
    room.save()
    
    room.delete()
