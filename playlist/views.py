from django.shortcuts import render, redirect
from .forms import PlaylistForm
from django.conf import settings
from urllib.parse import urlencode
import requests
import logging
from .spotify_utils import playlist_generate

logger = logging.getLogger(__name__)

def generate_playlist(request):
    # Отримуємо токен з сесії
    spotify_token = request.session.get('spotify_access_token')

    # Перевіряємо, чи є токен
    if not spotify_token:
        return redirect('index')  # Якщо токена немає, перенаправляємо на сторінку підключення

    # Якщо токен є, продовжуємо виконання логіки генерації плейлиста
    if request.method == 'POST':
        form = PlaylistForm(request.POST)
        if form.is_valid():
            artist = form.cleaned_data['artist']
            genre = form.cleaned_data['genre']  # Отримуємо жанр з форми
            number_of_songs = form.cleaned_data['number_of_songs']

            # Генеруємо плейлист за допомогою функції з spotify_utils
            playlist = playlist_generate(artist, genre, number_of_songs, spotify_token)

            if playlist:
                # Формуємо повідомлення про успіх
                message = f"Плейлист успішно згенеровано для автора '{artist}' з кількістю пісень {number_of_songs}."
                # Передаємо плейлист на шаблон
                return render(request, 'playlist_result.html', {'message': message, 'playlist': playlist})
            else:
                message = "Не вдалося згенерувати плейлист. Спробуйте ще раз."
                return render(request, 'playlist_result.html', {'message': message})

    # Якщо метод не POST, повертаємо порожній формуляр
    form = PlaylistForm()
    return render(request, 'generate_playlist.html', {'form': form})

def about(request):
    return render(request, 'about.html')

def index(request):
    return render(request, 'index.html')

def playlist(request):
    # Ти можеш додати логіку для завантаження плейлистів із бази даних або API
    return render(request, 'playlist.html')


def connect_spotify(request):
    logger.info("Connecting to Spotify...")
    
    if request.user.is_authenticated:
        logger.info("User is authenticated, redirecting to generate_playlist.")
        return redirect('generate_playlist')
    
    spotify_auth_url = 'https://accounts.spotify.com/authorize'
    redirect_uri = settings.SPOTIFY_REDIRECT_URI  
    params = {
        'client_id': settings.SPOTIFY_CLIENT_ID, 
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'scope': 'user-read-email user-library-read playlist-modify-public',
    }
    logger.info("Redirecting to Spotify authorization URL: %s", f"{spotify_auth_url}?{urlencode(params)}")
    return redirect(f"{spotify_auth_url}?{urlencode(params)}")


def spotify_callback(request):
    code = request.GET.get('code')
    if not code:
        return redirect('index')

    token_url = 'https://accounts.spotify.com/api/token'
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': settings.SPOTIFY_REDIRECT_URI,  # Відповідно до налаштувань
        'client_id': settings.SPOTIFY_CLIENT_ID,  # Відповідно до налаштувань
        'client_secret': settings.SPOTIFY_CLIENT_SECRET,  # Відповідно до налаштувань
    }
    response = requests.post(token_url, data=token_data)
    token_info = response.json()

    if 'access_token' in token_info:
        access_token = token_info['access_token']
        request.session['spotify_access_token'] = access_token
        return redirect('generate_playlist')
    else:
        return redirect('index')  # Якщо помилка — перенаправляємо назад
    
