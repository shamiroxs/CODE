from django.contrib.auth import views as auth_views

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    
    path('create/', views.create_room, name='create_room'),
    path('join/<str:code>/', views.join_room, name='join_room'),
    path('game/<str:code>/', views.game_view, name='game'),
    
    path('api/room/<str:code>/start/', views.start_game_view, name='start_game'),
    path('api/room/<str:code>/status/', views.get_status, name='get_status'),
    path('api/room/<str:code>/swap/', views.swap_card_view, name='swap_card'),
    path('api/reset/<str:code>/', views.reset_game_view, name='reset_game'),
    
]
