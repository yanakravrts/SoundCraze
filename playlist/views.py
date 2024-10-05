from django.shortcuts import render, redirect
from .forms import PlaylistForm

def generate_playlist(request):
    if request.method == 'POST':
        form = PlaylistForm(request.POST)
        if form.is_valid():
            # Отримуємо дані з форми
            song = form.cleaned_data['song']
            artist = form.cleaned_data['artist']
            number_of_songs = form.cleaned_data['number_of_songs']

            # Формуємо повідомлення
            message = f"Плейлист успішно згенеровано для пісні '{song}', автора '{artist}' з кількістю пісень {number_of_songs}."

            # Поки що без реального Spotify URL
            spotify_url = None
            
            # Повертаємо повідомлення та spotify_url
            return render(request, 'playlist_result.html', {'message': message, 'spotify_url': spotify_url})
    else:
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
    # Поки без логіки, просто перенаправляємо на сторінку генерації плейлиста
    return redirect('generate_playlist')

