from spotipy.client import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from typing import List
import json
import os
import queue
import sys

class Artist:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name

    def __str__(self):
        return f'{self.name} ({self.id})'

class Track:
    def __init__(self, id: str, name: str, artist: Artist):
        self.id = id
        self.name = name
        self.artist = artist
    
    def __str__(self):
        return f'{self.name} - {self.artist.name} ({self.id})'

def deserialize_artist(json_data: dict) -> Artist:
    '''Creates an Artist object from json.'''
    return Artist(json_data['id'], json_data['name']) 

def deserialize_track(json_data: dict, artist: Artist) -> Track:
    '''Creates an Track object from json.'''
    return Track(json_data['id'], json_data['name'], artist)

def get_related_artists(spotify_client: Spotify, seed_artist: Artist,
                        max_depth: int, max_neighbors: int) -> List[Artist]:
    '''Starting at a "seed" artist, performs a breadth first search to find related artists.'''
    artist_queue = queue.Queue()
    artist_queue.put((seed_artist, 0))
    visited = set([seed_artist.id])
    artists = []

    while not artist_queue.empty():
        artist, depth = artist_queue.get()
        artists.append(artist)

        if depth < max_depth:
            related_artists_data = spotify_client.artist_related_artists(artist.id)['artists']
            related = [
                deserialize_artist(artist_data)
                for artist_data 
                in related_artists_data]

            neighbors_visited = 0

            for related_artist in related:
                if neighbors_visited == max_neighbors:
                    break
                if related_artist.id not in visited:
                    artist_queue.put((related_artist, depth + 1))
                    visited.add(related_artist.id)
                    neighbors_visited += 1

    return artists

def get_artist_tracks(spotify_client: Spotify, artist: Artist, count: int) -> List[Track]:
    '''Gets a list of an artist's top tracks.'''
    artist_tracks_data = spotify_client.artist_top_tracks(artist.id)['tracks']
    artist_tracks = [
        deserialize_track(track_data, artist)
        for track_data
        in artist_tracks_data[:count]]

    return artist_tracks

if __name__ == '__main__':
    # The maximum distance from the seed artist that the algorithm will search.
    MAX_DEPTH = 3

    # The maximum number of related artists that will be included in the search
    # for each artist.
    MAX_NEIGHBORS = 3

    # The number of tracks that are pulled from each artist's top tracks.
    TRACKS_PER_ARTIST = 5

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

    credentials = SpotifyClientCredentials(
        config['SPOTIFY_CLIENT_ID'],
        config['SPOTIFY_CLIENT_SECRET'])
        
    client = Spotify(client_credentials_manager=credentials)

    seed_artist_data = client.artist(seed_artist_id)
    seed_artist = deserialize_artist(seed_artist_data)

    artists = get_related_artists(client, seed_artist, MAX_DEPTH, MAX_NEIGHBORS)
    tracks = []

    for artist in artists:
        artist_tracks = get_artist_tracks(client, artist, TRACKS_PER_ARTIST)
        tracks.extend(artist_tracks)
    
    for track in tracks:
        print(track)
    