from spotipy.client import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
import json
import os
import queue
import sys

class Artist:
    def __init__(self, id, name):
        self.id = id
        self.name = name

if __name__ == '__main__':
    MAX_DEPTH = 3
    MAX_NEIGHBORS = 3

    if len(sys.argv) < 2:
        print('Usage: python3 aggregator.py <artist id>')
        sys.exit(1)

    seed_artist_id = sys.argv[1]

    if not os.path.exists('config.json'):
        print('config.json file not present!')
        sys.exit(1)

    config_file = open('config.json', 'r')
    config = json.load(config_file)

    if 'SPOTIFY_CLIENT_ID' not in config:
        print('SPOTIFY_CLIENT_ID missing from config.json')
        sys.exit(1)

    if 'SPOTIFY_CLIENT_SECRET' not in config:
        print('SPOTIFY_CLIENT_SECRET missing from config.json')
        sys.exit(1)

    creds = SpotifyClientCredentials(
        config['SPOTIFY_CLIENT_ID'],
        config['SPOTIFY_CLIENT_SECRET'])
        
    client = Spotify(client_credentials_manager=creds)

    artist_data = client.artist(seed_artist_id)
    seed_artist = Artist(seed_artist_id, artist_data['name'])
    artist_queue = queue.Queue()
    artist_queue.put((seed_artist, 0))
    visited = set([seed_artist.id])

    while not artist_queue.empty():
        artist, depth = artist_queue.get()
        print(artist.name)
        
        if depth < MAX_DEPTH:
            related_artist_data = client.artist_related_artists(artist.id)['artists']
            related = [Artist(artist_data['id'], artist_data['name']) for artist_data in related_artist_data]

            for i, related_artist in enumerate(related):
                if i == (MAX_NEIGHBORS - 1):
                    break
                if related_artist.id not in visited:
                    artist_queue.put((related_artist, depth + 1))
                    visited.add(related_artist.id)
