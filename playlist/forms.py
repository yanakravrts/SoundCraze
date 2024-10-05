from django import forms

class PlaylistForm(forms.Form):
    song = forms.CharField(label='Пісня', max_length=100)
    artist = forms.CharField(label='Автор', max_length=100)
    number_of_songs = forms.IntegerField(label='Кількість пісень у плейлисті', min_value=1, max_value=50)