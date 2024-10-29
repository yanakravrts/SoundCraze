from django.urls import path
from . import views

urlpatterns = [
    path('generate-playlist/', views.generate_playlist, name='generate_playlist'),
    path('about/', views.about, name='about'),
    path('', views.index, name='index'),
    path('playlist/', views.display_playlists, name='playlist'),
    path('callback/', views.spotify_callback, name='spotify_callback'),
    path('author-autocomplete/', views.spotify_author_autocomplete, name='author_autocomplete'),
    path('genre-autocomplete/', views.spotify_genre_autocomplete, name='genre_autocomplete'),
    path('add-tracks-to-spotify/', views.add_tracks_to_spotify, name='add_tracks_to_spotify'),
    path('connect_spotify/', views.connect_spotify, name='connect_spotify')
]