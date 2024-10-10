from django import forms

class PlaylistForm(forms.Form):
    artist = forms.CharField(label='Автор', max_length=100)
    genre = forms.CharField(label='Жанр', max_length=100, required=False)  # Поле для жанру, необов'язкове
    number_of_songs = forms.IntegerField(label='Кількість пісень у плейлисті', min_value=1, max_value=50)