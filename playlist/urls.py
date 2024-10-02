from django.urls import path
from . import views

urlpatterns = [
    path('generate-playlist/', views.generate_playlist, name='generate_playlist'),  # Додаємо шлях до функції generate_playlist
]