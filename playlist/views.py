from django.shortcuts import render, redirect
from .forms import PlaylistForm
from django.http import JsonResponse
from django.conf import settings
from urllib.parse import urlencode
import requests
import logging
from .spotify_utils import playlist_generate
from django.views.decorators.http import require_POST
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def generate_playlist(request):

    spotify_token = request.session.get('spotify_access_token')

    if not spotify_token:
        return redirect('index') 

    if request.method == 'POST':
        form = PlaylistForm(request.POST)
        if form.is_valid():
            artist = form.cleaned_data['artist']
            genre = form.cleaned_data['genre']
            mood = form.cleaned_data['mood']
            number_of_songs = form.cleaned_data['number_of_songs']

            playlist = playlist_generate(artist, genre, mood, number_of_songs, spotify_token)

            if playlist:
                logger.info(f"Згенерований плейлист: {playlist}")  # Логування плейлиста
                track_ids = get_track_ids_from_playlist(playlist, spotify_token)
                message = f"Плейлист успішно згенеровано для автора '{artist}' з кількістю пісень {number_of_songs}."
                return render(request, 'playlist_result.html', {'message': message, 'playlist': playlist, 'track_ids': track_ids})
            else:
                message = "Не вдалося згенерувати плейлист. Спробуйте ще раз."
                return render(request, 'playlist_result.html', {'message': message})
    form = PlaylistForm()
    return render(request, 'generate_playlist.html', {'form': form})


def get_track_ids_from_playlist(playlist, spotify_token):
    track_ids = []
    for track in playlist:

        track_name = track.get('track_name')  
        artist_name = track.get('artists')  

        if track_name and artist_name:  
            track_id = get_track_id(track_name, artist_name, spotify_token)

            if track_id:
                track_ids.append(track_id)
        else:
            logger.warning(f"Трек пропущено, оскільки відсутня назва або виконавець: {track}")

    logger.info(f"Знайдені ID треків: {track_ids}")
    return track_ids


def get_track_id(track_name, artist_name, spotify_token):
    search_url = "https://api.spotify.com/v1/search"
    headers = {
        'Authorization': f'Bearer {spotify_token}',
        'Content-Type': 'application/json',
    }
    params = {
        'q': f'track:{track_name} artist:{artist_name}',
        'type': 'track',
        'limit': 1,
    }

    response = requests.get(search_url, headers=headers, params=params)

    if response.status_code == 200:
        results = response.json()
        tracks = results.get('tracks', {}).get('items', [])
        if tracks:
            track_id = tracks[0]['id']
            logger.info(f"Знайдено ID треку: {track_name} - {track_id}")
            return track_id
        else:
            logger.warning(f"Трек '{track_name}' від '{artist_name}' не знайдено.")
    else:
        logger.error(f"Помилка при пошуку треку: {response.status_code}, {response.text}")

    return None


def spotify_author_autocomplete(request):
    if 'term' in request.GET:
        term = request.GET.get('term')
        access_token = request.session.get('spotify_access_token')

        logger.info(f"Searching for term: {term} with token: {access_token}")

        if not access_token:
            logger.warning("Access token not found.")
            return JsonResponse([], safe=False)

        # Виконання запиту до Spotify API
        url = f"https://api.spotify.com/v1/search?q={term}&type=artist&limit=20"
        headers = {
            'Authorization': f'Bearer {access_token}',
        }

        response = requests.get(url, headers=headers)
        logger.info(f"Response status code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            artists = [artist['name'] for artist in data['artists']['items']]
            logger.info(f"Found artists: {artists}")
            return JsonResponse(artists, safe=False)

        else:
            logger.error(f"Error fetching artists: {response.status_code} - {response.text}")

    return JsonResponse([], safe=False)


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
        'scope': 'user-read-email user-library-read playlist-modify-public playlist-modify-private',  # Додайте потрібні дозволи
    }

    logger.info("Redirecting to Spotify authorization URL: %s", f"{spotify_auth_url}?{urlencode(params)}")
    return redirect(f"{spotify_auth_url}?{urlencode(params)}")


def spotify_genre_autocomplete(request):
    if 'term' in request.GET:
        term = request.GET.get('term').lower()
        access_token = request.session.get('spotify_access_token')

        if not access_token:
            return JsonResponse([], safe=False)

        # Запит до Spotify API для пошуку виконавців
        url = f"https://api.spotify.com/v1/search?q={term}&type=artist&limit=10"
        headers = {
            'Authorization': f'Bearer {access_token}',
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            genres = set()  # Використовуємо множину для унікальних значень
            for artist in data['artists']['items']:
                genres.update(artist['genres'])  # Додаємо жанри до множини

            return JsonResponse(list(genres), safe=False)
    
    return JsonResponse([], safe=False)


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
    
    
@require_POST
def add_tracks_to_spotify(request):
    # Отримуємо токен з сесії
    spotify_token = request.session.get('spotify_access_token')

    if not spotify_token:
        logger.warning("Токен Spotify не знайдено. Перенаправлення на сторінку підключення.")
        return redirect('index')

    # Отримуємо ID треків з POST-запиту
    track_ids_raw = request.POST.get('track_ids', '')
    track_ids = track_ids_raw.split(',')  # Розділяємо по комі
    track_ids = [track_id.strip() for track_id in track_ids if track_id.strip()]  # Очищення пробілів


    if not track_ids:
        logger.warning("Список ID треків порожній.")
        return redirect('generate_playlist')

    user_info_url = "https://api.spotify.com/v1/me"
    response = requests.get(user_info_url, headers={'Authorization': f'Bearer {spotify_token}'})
    
    if response.status_code == 200:
        user_id = response.json()['id']  # Отримання User ID
        logger.info(f"Отримано ID користувача: {user_id}")
    else:
        logger.error(f"Не вдалося отримати інформацію про користувача: {response.status_code}, {response.text}")
        return redirect('index')  # Якщо не вдалося отримати User ID
    
    # Створюємо плейлист у Spotify
    create_playlist_url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    headers = {
        'Authorization': f'Bearer {spotify_token}',
        'Content-Type': 'application/json',
    }
    data = {
        'name': 'My New Playlist',  # Назва плейлиста
        'description': 'Playlist created from the app.',
        'public': False,
    }

    response = requests.post(create_playlist_url, headers=headers, json=data)

    if response.status_code == 201:
        playlist_id = response.json()['id']
        logger.info(f"Створено плейлист з ID: {playlist_id}")

        # Додаємо треки до плейлиста
        add_tracks_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        add_data = {
            'uris': [f'spotify:track:{track_id}' for track_id in track_ids]  # Формат для додавання треків
        }
        add_response = requests.post(add_tracks_url, headers=headers, json=add_data)

        if add_response.status_code == 201:
            logger.info("Треки успішно додані до плейлиста.")
            return redirect('generate_playlist')  # Перенаправлення після успішного додавання
        else:
            logger.error(f"Помилка при додаванні треків до плейлиста: {add_response.status_code}, {add_response.text}")
            return redirect('generate_playlist')
    else:
        logger.error(f"Помилка при створенні плейлиста: {response.status_code}, {response.text}")
        return redirect('generate_playlist')


#вивід плейлистів --сторінка: наші плейлисти---
def display_playlists(request):
    spotify_token = request.session.get('spotify_access_token')

    if not spotify_token:
        return redirect('index')

    playlist_urls = [
        "https://open.spotify.com/playlist/2U2RN4a0aaDLd36jiSFOL8?si=dbb3b0d5b3f04241",
        "https://open.spotify.com/playlist/00qOalVs4UPqN8oofW9rYg?si=7c3e789e56a249c6",
        "https://open.spotify.com/playlist/1kS0gM6RjLrx3MfAGbVJ43?si=c708a56b2efb40fa",
        "https://open.spotify.com/playlist/03dUQA1UEY2nudUudLrf5E?si=244bd0e3d9364438",
    ]

    playlist_covers = []

    for playlist_url in playlist_urls:
        path = urlparse(playlist_url).path
        playlist_id = path.split('/')[-1]

        url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
        headers = {'Authorization': f'Bearer {spotify_token}'}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            playlist_data = response.json()
            cover_url = playlist_data['images'][0]['url'] if playlist_data['images'] else None
            playlist_covers.append({'id': playlist_id, 'cover_url': cover_url, 'url': playlist_url})
        else:
            logger.error(f"Error retrieving playlist data: {response.status_code}, {response.text}")
    
    logger.info(f"Завантажені плейлисти: {playlist_covers}")

    return render(request, 'playlist.html', {'playlist_covers': playlist_covers})

# плеєр наших плейлистів 
def display_playlist(request, playlist_id):
    spotify_token = request.session.get('spotify_access_token')

    if not spotify_token:
        return redirect('index')
    embed_url = f"https://open.spotify.com/embed/playlist/{playlist_id}"

    return render(request, 'playlist.html', {'embed_url': embed_url})