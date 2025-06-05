import random
import string
import time
import json

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse

from .models import Room, Player
from .game_logic import start_game, swap_card, reset_game, get_next_player


def generate_room_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def home(request):
    return render(request, 'home.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"].strip()
        password = request.POST["password"]

        if not username or not password:
            return render(request, "login.html", {
                "message": "Name and password are required."
            })

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('home')
        else:
            try:
                existing_user = User.objects.get(username=username)
                return render(request, "login.html", {
                    "message": "That name is already taken and Invalid password."
                })
            except User.DoesNotExist:
                # Username does not exist: create new user
                try:
                    new_user = User.objects.create_user(username=username, password=password)
                    new_user.save()
                    login(request, new_user)
                    next_url = request.GET.get('next') or request.POST.get('next')
                    if next_url:
                        return redirect(next_url)
                    return redirect('home')
                except IntegrityError:
                    return render(request, "login.html", {
                        "message": "Could not create user. Try a different name."
                    })
    else:
        return render(request, "login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("home"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"].strip()
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        if not username or not password:
            return render(request, "register.html", {
                "message": "Name and password are required."
            })

        if password != confirmation:
            return render(request, "register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(username=username, password=password)
            user.save()
        except IntegrityError:
            return render(request, "register.html", {
                "message": "That name is already taken. Please choose another."
            })

        login(request, user)
        return HttpResponseRedirect(reverse("game"))
    else:
        return render(request, "register.html")
        
@login_required
def create_room(request):
    if request.method == 'POST':
        existing_room = Room.objects.filter(host=request.user).first()
        if existing_room:
            return redirect('join_room', code=existing_room.code)

        #reate a new room
        code = generate_room_code()
        room = Room.objects.create(code=code, host=request.user)
        Player.objects.create(user=request.user, room=room)
        return redirect('join_room', code=code)
        
    return render(request, 'create.html')

@login_required
def join_room(request, code):
    room = get_object_or_404(Room, code=code)

    if not Player.objects.filter(user=request.user, room=room).exists():
        Player.objects.create(user=request.user, room=room)

    is_host = room.host == request.user
    players = Player.objects.filter(room=room)
    return render(request, 'join.html', {'code': code, 'players': players, 'is_host': is_host})

@login_required
def game_view(request, code):

    try:
        room = Room.objects.get(code=code)
    except Room.DoesNotExist:
        return HttpResponseRedirect(reverse("home"))
        
    room = get_object_or_404(Room, code=code)
    players = Player.objects.filter(room=room)
    is_host = room.host == request.user
    
    current_player = players[room.current_turn % len(players)] if players else None
    
    try:
        player = Player.objects.get(user=request.user, room=room)
    except Player.DoesNotExist:
        return render(request, 'join.html', {'code': code, 'players': players, 'is_host': is_host})

    return render(request, 'game.html', {
        'room': room,
        'players': players,
        'player': player,
        'current_player': current_player,
        'is_host': is_host
    })

@login_required
def start_game_view(request, code):
    room = get_object_or_404(Room, code=code)
    start_game(room)
    return JsonResponse({'status': 'started'})

@login_required
def get_status(request, code):
    room = get_object_or_404(Room, code=code)
    players = Player.objects.filter(room=room)  
    
    player = players.get(user=request.user)
    player.last_seen = timezone.now()
    player.save(update_fields=['last_seen'])
    
    data = {}
    
    data['redirect'] = False
    data['redirect_url'] = f'/game/{room.code}/'
    
    if room.status == "waiting":
    	timeout_threshold = now() - timedelta(seconds=30)
    	inactive_players = players.exclude(last_seen__gte=timeout_threshold)
    	
    	for p in inactive_players:
            p.delete()    
    
    current_turn_player = players.filter(is_turn=True).first()
    if current_turn_player:
        time_diff = timezone.now() - current_turn_player.last_seen
        if time_diff > timedelta(seconds=30):
            current_turn_player.is_turn = False
            current_turn_player.save(update_fields=['is_turn'])
            
            next_player = get_next_player(players, current_turn_player)
            if next_player:
                next_player.is_turn = True
                next_player.save(update_fields=['is_turn'])
    
    winner = players.filter(has_won=True).first()
    if winner:
        room.status = "waiting"
        room.table_cards = []
        room.save(update_fields=['status', 'table_cards'])
        
        data['winner_username'] = winner.user.username
    else:
        data['winner_username'] = None
        
    active_threshold = now() - timedelta(seconds=30)
    active_players = players.filter(last_seen__gte=active_threshold)
    
    if active_players.count() < 2:
        room.status = 'waiting'
        room.table_cards = []
        room.save(update_fields=['status', 'table_cards'])

        data['redirect'] = True
        data['redirect_url'] = f'/join/{room.code}/'

      
    data.update({
        'room_status': room.status,
        'table_cards': room.table_cards,
        'players': [
            {
                'username': p.user.username,
                'hand': p.hand if p.user == request.user else ["?"] * len(p.hand),
                'is_turn': p.is_turn,
                'has_won': p.has_won
            } for p in players
        ],
        'your_turn': player.is_turn,
        'current_user': request.user.username
    })
    return JsonResponse(data)
   
@csrf_exempt
@login_required
def swap_card_view(request, code):
    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid method.")

    try:
        data = json.loads(request.body)
        hand_index = data.get('hand_index')
        table_index = data.get('table_index')

    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'error': 'Invalid JSON.'}, status=400)

    room = get_object_or_404(Room, code=code)
    player = get_object_or_404(Player, user=request.user, room=room)

    result = swap_card(player, room, hand_index, table_index)
    
    return JsonResponse({'success': result})    
  
def timeout_turn(request, room_code):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    try:
        user = request.user
        room = Room.objects.get(code=room_code)
        player = Player.objects.get(user=user, room=room)

        if not player.is_turn:
            return JsonResponse({'error': 'Not your turn'}, status=403)

        player.is_turn = False
        player.save()

        players = list(Player.objects.filter(room=room).order_by('id'))

        current_index = players.index(player)
        next_index = (current_index + 1) % len(players)
        room.current_turn = next_index
        room.save()

        for i, p in enumerate(players):
            p.is_turn = (i == next_index)
            p.save()

        return JsonResponse({'success': True})

    except Player.DoesNotExist:
        return JsonResponse({'error': 'Player not found'}, status=404)
    except Room.DoesNotExist:
        return JsonResponse({'error': 'Room not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
 
@login_required
def reset_game_view(request, code):
    room = get_object_or_404(Room, code=code)
    reset_game(room)
    return HttpResponseRedirect(reverse("home"))

@login_required
def game_end(request, code):
    room = get_object_or_404(Room, code=code)
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
    
    is_host = room.host == request.user
    return render(request, 'join.html', {'code': code, 'players': players, 'is_host': is_host})


@login_required
def exit_room(request, code):
    room = get_object_or_404(Room, code=code)
    players = Player.objects.filter(room=room)
    
    try:
        player = players.get(user=request.user)
        player.delete()  
    except Player.DoesNotExist:
        pass
    
    return HttpResponseRedirect(reverse("home"))
