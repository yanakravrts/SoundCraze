import requests
import base64
from django.conf import settings

# Функція для отримання токену
def get_access_token():
    auth_header = base64.b64encode(f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}".encode()).decode()

    headers = {
        'Authorization': f'Basic {auth_header}'
    }
    data = {
        'grant_type': 'client_credentials'
    }
    
    response = requests.post(settings.SPOTIFY_AUTH_URL, headers=headers, data=data)
    if response.status_code == 200:
        token_info = response.json()
        return token_info['access_token']
    else:
        raise Exception(f"Failed to get access token: {response.json()}")

# Отримуємо токен
access_token = get_access_token()
