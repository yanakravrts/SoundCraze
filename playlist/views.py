from django.shortcuts import render
from .forms import PlaylistForm

def generate_playlist(request):
    if request.method == 'POST':
        form = PlaylistForm(request.POST)
        if form.is_valid():
            genre = form.cleaned_data['genre']
            song = form.cleaned_data['song']
            artist = form.cleaned_data['artist']
            message = f"Плейлист успішно згенеровано для жанру '{genre}', пісні '{song}' та автора '{artist}'."
            
            # Поверніть результат або оброблену інформацію
            return render(request, 'playlist_result.html', {'message': message})
    else:
        form = PlaylistForm()
    
    return render(request, 'generate_playlist.html', {'form': form})


def about(request):
    return render(request, 'about.html')