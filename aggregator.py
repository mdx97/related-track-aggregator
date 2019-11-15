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
    # The maximum distance from the seed artist that the algorithm will search.
    MAX_DEPTH = 3

    # The maximum number of related artists that will be included in the search
    # for each artist.
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

    for key in ['SPOTIFY_CLIENT_ID', 'SPOTIFY_CLIENT_SECRET']:
        if key not in config:
            print(f'{key} missing from config.json!')
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
            related_artists_data = client.artist_related_artists(artist.id)['artists']
            related = [
                Artist(artist_data['id'], artist_data['name']) 
                for artist_data 
                in related_artists_data]

            neighbors_visited = 0

            for related_artist in related:
                if neighbors_visited == (MAX_NEIGHBORS - 1):
                    break
                if related_artist.id not in visited:
                    artist_queue.put((related_artist, depth + 1))
                    visited.add(related_artist.id)
                    neighbors_visited += 1