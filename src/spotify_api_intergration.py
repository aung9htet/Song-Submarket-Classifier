import os
import json
import time
import requests

class SpotifyAPI():

    def __init__(self, end_point="", url=None, **params):
        """
            The following object is supposed to create a class for integration of spotify API
            into python. These includes web api, ad api and usage of playcount.
        """
        # general
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_url = "https://api.spotify.com/v1"
        self.session = requests.Session()

        # url to process
        self.end_point = end_point
        self.url = url if not url is None else os.path.join(self.base_url, self.end_point)
        self.params = params

        # authentication to process
        self.access_token_url = "https://open.spotify.com/get_access_token"
        self.token_location_ref = "../authentication/spotify-authentication.json"
        self.token_location = os.path.join(self.current_dir, self.token_location_ref)
    
    def update_url(self, end_point="", url=None):
        """
            The following method updates the url based on whether an endpoint is given or
            a url is given.
        """
        self.end_point = end_point
        self.url = url if not url is None else (self.base_url + "/" + self.end_point)

    def get_token(self):
        """
            Reads a local access token.
        """
        with open(self.token_location) as f:
            token = json.load(f)
        return token
    
    def get_access_token(self):
        """
            Gets a valid access token for usage.
        """
        if not os.path.exists(self.token_location):
            self.create_new_token()

        token = self.get_token()
        curr_time = time.time()
        if int(curr_time * 1000) > token['accessTokenExpirationTimestampMs']:
            self.create_new_token()
            token = self.get_token()
        access_token = token['accessToken']
        return access_token

        
    def create_new_token(self):
        """
            Gets a new access token and save it locally.
        """
        try:
            # get from spotify
            token = requests.get(self.access_token_url, timeout=5).json()

            # save
            with open(self.token_location, 'w') as f:
                json.dump(token, f, indent=4)
            
            print("Successfully saved")
        except Exception as e:
            print(e)

    def get_data(self):
        """
            The following method gets json data from spotify for specific url
        """
        self.session.headers.update({'Authorization': f'Bearer {self.get_access_token()}'})
        try:
            response = self.session.get(self.url, params=self.params, timeout=5)
            data = response.json()
        except Exception as e:
            print(e)
        return data
    
    def get_artist_data(self, artist_id, next = False):
        """
            The following method uses the artist id to get data of the artist.
        """
        if next == False:
            end_point= f"artists/{artist_id}"
            self.update_url(end_point=end_point)
        else:
            self.url = artist_id
        data = self.get_data()
        return data
    
    def get_artist_album(self, artist_id):
        """
            The following method uses the artist id to get data of the artist.
        """
        end_point= f"artists/{artist_id}/albums"
        self.update_url(end_point=end_point)
        data = self.get_data()
        return data
    
    def get_playlist_data(self, playlist, next = False):
        """
            The following method uses the playlist id to get data of the playlist.
        """
        if next == False:
            end_point= f"playlists/{playlist}/tracks"
            self.update_url(end_point=end_point)
        else:
            self.url = playlist
        print(self.url)
        data = self.get_data()
        return data

    def get_playlist(self, playlist, next = False):
        """
            The following method uses the playlist id to get data of the playlist.
        """
        if next == False:
            end_point= f"playlists/{playlist}"
            self.update_url(end_point=end_point)
        else:
            self.url = playlist
        data = self.get_data()
        return data
    
    def get_track_data(self, track_id):
        """
            The following method uses the track id to get data of the playlist.
        """
        end_point= f"tracks/{track_id}"
        self.update_url(end_point=end_point)
        data = self.get_data()
        return data
    
    def get_track_audio_feature(self, track_id):
        """
            The following method uses the track id to get spotify's analysis of audio features.
        """
        end_point = f"audio-features/{track_id}"
        self.update_url(end_point=end_point)
        data = self.get_data()
        return data
    
    def get_track_audio_analysis(self, track_id):
        """
            The following method uses the track id to get spotify's analysis audio.
        """
        end_point = f"audio-analysis/{track_id}"
        self.update_url(end_point=end_point)
        data = self.get_data()
        return data
    
    def get_id_from_isrc(self, isrc):
        """
            The following method uses the isrc to get track id.
        """
        end_point = f"search?type=track&q=isrc:{isrc}"
        self.update_url(end_point=end_point)
        data = self.get_data()
        return data

    def get_isrc(self, track_id):
        """
            The following method returns the songwriter
        """
        end_point = f"tracks/{track_id}"
        self.update_url(end_point=end_point)
        data = self.get_data()
        isrc = data["external_ids"]["isrc"]
        return isrc
    
    def get_playcount(self, album_id):
        """
            The following method returns the total playcount for the album and for all the tracks
            in the album.
        """
        self.url = "https://api-partner.spotify.com/pathfinder/v1/query"
        self.params = {
            'operationName': 'queryAlbumTracks',
            'variables': json.dumps({
                'uri': f'spotify:album:{album_id}',
                'offset': 0,
                'limit': 999
            }),
            'extensions': json.dumps({
                'persistedQuery': {
                    'version': 1,
                    'sha256Hash': '3ea563e1d68f486d8df30f69de9dcedae74c77e684b889ba7408c589d30f7f2e'
                }
            })
        }
        data = self.get_data()

        album_playcount = {}

        for item in data['data']['album']['tracks']['items']:
            track = item['track']

            track_uri, playcount = track['uri'], track['playcount']
            album_playcount[track_uri] = int(playcount)

        total_playcount = sum(album_playcount.values())

        return album_playcount, total_playcount