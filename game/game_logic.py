from .utils import shuffle_deck
from .models import Player, GameLog
from django.utils import timezone

def start_game(room):
    deck = shuffle_deck()
    players = list(Player.objects.filter(room=room))
    num_players = len(players)
    hand_size = 4
    
    # Deal cards to each player
    for i, player in enumerate(players):
        player.hand = deck[i * hand_size: (i + 1) * hand_size]
        player.is_turn = (i == 0)
        player.has_won = False
        player.save()

    room.table_cards = deck[num_players * hand_size: num_players * hand_size + 4]
    room.current_turn = 0
    room.status = 'playing'
    room.save()

    GameLog.objects.create(room=room, action="Game started.", timestamp=timezone.now())

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

    GameLog.objects.create(room=room, action=f"{player.user.username} swapped cards.", timestamp=timezone.now())

    if check_win(player):
        player.has_won = True
        player.save()
        room.status = 'finished'
        room.save()
        GameLog.objects.create(room=room, action=f"{player.user.username} won the game!", timestamp=timezone.now())
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
    room.status = 'waiting'
    room.save()
    GameLog.objects.create(room=room, action="Game reset.", timestamp=timezone.now())
