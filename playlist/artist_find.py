import requests
from .token_get import access_token  # Імпорт токена доступу

# Пошук ідентифікатора артиста за назвою
def search_artist(artist_name, access_token):
    search_url = f"https://api.spotify.com/v1/search?q={artist_name}&type=artist"
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    response = requests.get(search_url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        artists = data['artists']['items']
        if artists:
            selected_artist = artists[0]  # За замовчуванням обираємо першого артиста
            return selected_artist['id']
        else:
            print("No artist found")
            return None
    else:
        print(f"Error: {response.status_code}")
        return None

# artist_id = search_artist('KRUTЬ', access_token)
