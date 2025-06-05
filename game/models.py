from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Player(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey('Room', on_delete=models.CASCADE)
    hand = models.JSONField(default=list)
    is_turn = models.BooleanField(default=False)
    has_won = models.BooleanField(default=False)
    last_seen = models.DateTimeField(default=timezone.now)

class Room(models.Model):
    code = models.CharField(max_length=6, unique=True)
    players = models.ManyToManyField(User, through=Player)
    table_cards = models.JSONField(default=list)
    current_turn = models.IntegerField(default=0)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_rooms', null=True)
    status = models.CharField(max_length=20, default='waiting')
