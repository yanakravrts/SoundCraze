import requests
from .token_get import access_token
from .artist_find import search_artist

def get_recommendations(artist_id, genre, limit, access_token):
    rec_url = "https://api.spotify.com/v1/recommendations"
    headers = {'Authorization': f'Bearer {access_token}'}

    params = {
        "market": 'UA',
        "limit": limit
    }

    if artist_id:
        params["seed_artists"] = artist_id
    if genre:
        params["seed_genres"] = genre

    response = requests.get(rec_url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        tracks = data['tracks']
        playlist = [
            {
                #"track_name": track['name'],
                #"artists": ', '.join([artist['name'] for artist in track['artists']]),
                #"spotify_url": track['external_urls']['spotify'],
                "track_id": track['id'],
                "embed_url": f'https://open.spotify.com/embed/track/{track["id"]}'
                
            }
            for track in tracks
        ]
        return playlist
    else:
        print(f"Error: {response.status_code}")
        return None

def playlist_generate(artist_name, genre, limit, access_token):
    artist_id = None

    if artist_name:
        artist_id = search_artist(artist_name, access_token)

    if artist_id or genre:
        playlist = get_recommendations(artist_id, genre, limit, access_token)
        if playlist:
            return playlist
        else:
            return None
    else:
        return None
