from django import forms

class PlaylistForm(forms.Form):
    artist = forms.CharField(label='Artist', max_length=100, required=False)
    genre = forms.CharField(label='Genre', max_length=100, required=False)  # Поле для жанру, необов'язкове
    mood = forms.CharField(label='Mood', max_length=100, required=False) 
    number_of_songs = forms.IntegerField(label='Number of songs', min_value=1, max_value=50)