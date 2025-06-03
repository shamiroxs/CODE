import random
import string
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse

from .models import Room, Player, GameLog
from .game_logic import start_game, swap_card, reset_game

import json

def generate_room_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

GUEST_NAMES = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
guest_counter = 0

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
'''
def game(request):
    global guest_counter
    if request.user.is_authenticated:
        player_name = request.user.username
    else:
        player_name = f"Player {GUEST_NAMES[guest_counter % len(GUEST_NAMES)]}"
        guest_counter += 1

    return render(request, "game.html", {
        "player_name": player_name
    })
'''
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
    room = get_object_or_404(Room, code=code)
    players = Player.objects.filter(room=room)
    current_player = players[room.current_turn % len(players)] if players else None
    return render(request, 'game.html', {
        'room': room,
        'players': players,
        'player': Player.objects.get(user=request.user, room=room),
        'current_player': current_player,
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
    data = {
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
        'your_turn': players.get(user=request.user).is_turn,
        'current_user': request.user.username
    }
    return JsonResponse(data)
   
@csrf_exempt
@login_required
def swap_card_view(request, code):
    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid method.")

    try:
        data = json.loads(request.body)
        hand_card = data.get('hand_card')
        table_card = data.get('table_card')

        if not hand_card or not table_card:
            return JsonResponse({'error': 'Missing card data.'}, status=400)

    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'error': 'Invalid JSON.'}, status=400)

    room = get_object_or_404(Room, code=code)
    player = get_object_or_404(Player, user=request.user, room=room)

    # Convert card names to indices
    try:
        hand_index = player.hand.index(hand_card)
    except ValueError:
        return JsonResponse({'error': 'Card not in player hand.'}, status=400)

    try:
        table_index = room.table_cards.index(table_card)
    except ValueError:
        return JsonResponse({'error': 'Card not on table.'}, status=400)

    result = swap_card(player, room, hand_index, table_index)
    
    return JsonResponse({'success': result})    
      
@login_required
def reset_game_view(request, code):
    room = get_object_or_404(Room, code=code)
    reset_game(room)
    return JsonResponse({'status': 'reset'})
