from django.urls import path
from . import views

urlpatterns = [
    path('generate-playlist/', views.generate_playlist, name='generate_playlist'),
    path('about/', views.about, name='about'),
    path('', views.index, name='index'),
    path('playlist/', views.playlist, name='playlist'),
    path('callback/', views.spotify_callback, name='spotify_callback'),
    path('connect_spotify/', views.connect_spotify, name='connect_spotify')
]