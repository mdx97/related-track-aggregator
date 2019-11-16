from aggregator import *
from spotipy.client import Spotify
from unittest import TestCase
from unittest.mock import MagicMock

class TestDeSerializationMethods(TestCase):
    def test_deserialize_artist_valid_json_data_returns_object(self):
        json_data = {
            'id': '1',
            'name': 'Van Halen'
            }
        artist = deserialize_artist(json_data)
        self.assertEqual(artist.id, '1')
        self.assertEqual(artist.name, 'Van Halen')
    
    def test_deserialize_artist_invalid_json_data_raises_key_error(self):
        json_data = {
            'id': '1'
            }
        self.assertRaises(KeyError, deserialize_artist, json_data)
    
    def test_deserialize_track_valid_json_data_returns_object(self):
        json_data = {
            'id': '2',
            'name': 'Ain\'t Talkin Bout Love'
            }
        artist = Artist('1', 'Van Halen')
        track = deserialize_track(json_data, artist)
        self.assertEqual(track.id, '2')
        self.assertEqual(track.name, 'Ain\'t Talkin Bout Love')
        self.assertEqual(track.artist.id, '1')
        self.assertEqual(track.artist.name, 'Van Halen')

    def test_deserialize_track_invalid_json_data_raises_key_error(self):
        json_data = {
            'id': '2'
            }
        artist = Artist('1', 'Van Halen')
        self.assertRaises(KeyError, deserialize_track, json_data, artist)

class TestRelatedArtists(TestCase):
    def test_get_related_artists_returns_the_seed_artist_when_there_are_no_related_artists(self):
        json_data = {'artists': []}
        client = Spotify()
        client.artist_related_artists = MagicMock(return_value=json_data)

        related = get_related_artists(client, Artist('1', 'Van Halen'), 10, 10)

        self.assertEqual(len(related), 1)
        self.assertEqual(related[0].id, '1')
    
    def test_get_related_artists_returns_seed_artist_plus_neighbors(self):
        json_data = {
            'artists': [
                {
                    'id': '5',
                    'name': 'AC/DC'
                },
                {
                    'id': '8',
                    'name': 'Ozzy Osbourne'
                }
            ]}
        neighbor_json_data = {'artists': []}
        client = Spotify()

        def mock_artist_related_artists(artist_id):
            return json_data if artist_id == '1' else neighbor_json_data
        
        client.artist_related_artists = MagicMock(side_effect=mock_artist_related_artists)

        related = get_related_artists(client, Artist('1', 'Van Halen'), 10, 10)

        self.assertEqual(len(related), 3)
        self.assertEqual(related[0].id, '1')
        self.assertEqual(related[1].id, '5')
        self.assertEqual(related[2].id, '8')
    
    def test_get_related_artists_returns_seed_artist_plus_limited_neighbors_when_max_neighbors_passed(self):
        json_data = {
            'artists': [
                {
                    'id': '5',
                    'name': 'AC/DC'
                },
                {
                    'id': '8',
                    'name': 'Ozzy Osbourne'
                }
            ]}
        neighbor_json_data = {'artists': []}
        client = Spotify()

        def mock_artist_related_artists(artist_id):
            return json_data if artist_id == '1' else neighbor_json_data
        
        client.artist_related_artists = MagicMock(side_effect=mock_artist_related_artists)

        related = get_related_artists(client, Artist('1', 'Van Halen'), 10, 1)

        self.assertEqual(len(related), 2)
        self.assertEqual(related[0].id, '1')
        self.assertEqual(related[1].id, '5')
    
    def test_get_related_artists_returns_limited_neighbors_when_max_depth_passed(self):
        json_data = {
            'artists': [
                {
                    'id': '5',
                    'name': 'AC/DC'
                },
                {
                    'id': '8',
                    'name': 'Ozzy Osbourne'
                }
            ]}
        neighbor_json_data = {
            'artists': [
                {
                    'id': '11',
                    'name': 'Cinderella'
                },
                {
                    'id': '15',
                    'name': 'Guns N Roses'
                }
            ]}
        client = Spotify()

        def mock_artist_related_artists(artist_id):
            return json_data if artist_id == '1' else neighbor_json_data
        
        client.artist_related_artists = MagicMock(side_effect=mock_artist_related_artists)

        related = get_related_artists(client, Artist('1', 'Van Halen'), 1, 10)

        self.assertEqual(len(related), 3)
        self.assertEqual(related[0].id, '1')
        self.assertEqual(related[1].id, '5')
        self.assertEqual(related[2].id, '8')

class TestArtistTracks(TestCase):
    def setUp(self):
        json_data = {
            'tracks': [
                {
                    'id': '1',
                    'name': 'Ain\'t Talkin Bout Love'
                },
                {
                    'id': '12',
                    'name': 'Panama'
                },
                {
                    'id': '31',
                    'name': 'I\'ll Wait'
                }
            ]}
        self.client = Spotify()
        self.client.artist_top_tracks = MagicMock(return_value=json_data)
        self.artist = Artist('1', 'Van Halen')

    def test_get_artist_tracks_with_count_less_than_tracks_returns_a_subset_of_tracks(self):
        tracks = get_artist_tracks(self.client, self.artist, 2)
        self.assertEqual(len(tracks), 2)
        self.assertEqual(tracks[0].id, '1')
        self.assertEqual(tracks[1].id, '12')

    def test_get_artist_tracks_with_count_equal_to_tracks_returns_all_tracks(self):
        tracks = get_artist_tracks(self.client, self.artist, 3)
        self.assertEqual(len(tracks), 3)
        self.assertEqual(tracks[0].id, '1')
        self.assertEqual(tracks[1].id, '12')
        self.assertEqual(tracks[2].id, '31')

    def test_get_artist_tracks_with_count_greater_than_tracks_returns_all_tracks(self):
        tracks = get_artist_tracks(self.client, self.artist, 4)
        self.assertEqual(len(tracks), 3)
        self.assertEqual(tracks[0].id, '1')
        self.assertEqual(tracks[1].id, '12')
        self.assertEqual(tracks[2].id, '31')

    def test_get_artist_tracks_sets_artist_on_tracks(self):
        tracks = get_artist_tracks(self.client, self.artist, 2)
        self.assertEqual(tracks[0].artist.id, '1')
        self.assertEqual(tracks[1].artist.id, '1')
