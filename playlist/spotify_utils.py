import requests
from .token_get import access_token
from .artist_find import search_artist

def get_recommendations(artist_id, genre,mood, limit, access_token):
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
    if mood == 'happy':
        params["target_valence"] = 0.9  
        params["target_energy"] = 0.8   
    elif mood == 'sad':
        params["target_valence"] = 0.2  
        params["target_energy"] = 0.3   
    elif mood == 'chill':
        params["target_valence"] = 0.6  
        params["target_energy"] = 0.4   
    else:
        params["target_valence"] = 0.5
        params["target_energy"] = 0.5   


    response = requests.get(rec_url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        tracks = data['tracks']
        tracks.sort(key=lambda track: track['name'].lower())
        playlist = [
            {
                "track_name": track['name'],
                "artists": ', '.join([artist['name'] for artist in track['artists']]),
                "spotify_url": track['external_urls']['spotify'],
                "track_id": track['id'],
                "embed_url": f'https://open.spotify.com/embed/track/{track["id"]}?theme=0'
                
            }
            for track in tracks
        ]
        return playlist
    else:
        print(f"Error: {response.status_code}")
        return None


def playlist_generate(artist_name, genre, mood, limit, access_token):

    artist_id = None

    if artist_name:
        artist_id = search_artist(artist_name, access_token)

    if artist_id or genre:
        playlist = get_recommendations(artist_id, genre,mood, limit, access_token)
        if playlist:
            return playlist
        else:
            return None
    else:
        return None
