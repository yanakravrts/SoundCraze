from django import forms

class PlaylistForm(forms.Form):
    genre = forms.CharField(label='Жанр', max_length=100)
    song = forms.CharField(label='Пісня', max_length=100)
    artist = forms.CharField(label='Автор', max_length=100)