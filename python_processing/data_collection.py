import glob, os
import pandas as pd
from cyanite_api import CyaniteAPI
from spotify_api_intergration import SpotifyAPI

class DataCollection(object):

    def __init__(self):
        self.spotify = SpotifyAPI()
        self.files = self.get_files()
    
    def process_training_data(self):
        features = []
        playlist_count = 0
        for playlist in self.files:
            playlist_count += 1
            track_list = []
            label = {'label': self.files[playlist]}
            playlist = playlist[34:]
            data = self.spotify.get_playlist_data(playlist)
            for track_data in data['tracks']['items']:
                track_list.append(track_data['track']['id'])
            next_playlist = data['tracks']['next']
            if next_playlist is None:
                find_next = False
            else:
                find_next = True
            while find_next is True:
                data = self.spotify.get_playlist_data(next_playlist, next=True)
                for track_data in data['items']:
                    track_list.append(track_data['track']['id'])
                if data['next'] is None:
                    find_next = False
                else:
                    next_playlist = data['next']
            song_count = 0
            for track in track_list:
                song_analyser = CyaniteAPI(track)
                try:
                    mood, genre, advanced_genre, movement, character = song_analyser.get_data()
                    feature = label | mood | genre | advanced_genre | movement | character
                    features.append(feature)
                    song_count += 1
                except:
                    print("Failed to get song.")
                print(f"Processing Playlist: {playlist_count}/{len(self.files)} Processed Song: {song_count}/{len(track_list)}")
        self.save_data(features)

    def save_data(self, features):
        with open('test.csv', 'w') as f:
            # Write all the dictionary keys in a file with commas separated.
            f.write(','.join(features[0].keys()))
            f.write('\n') # Add a new line
            for row in features:
                # Write the values in a row.
                f.write(','.join(str(x) for x in row.values()))
                f.write('\n') # Add a new line

    def get_files(self):
        os.chdir("../batch_1")
        files = {}
        for file in glob.glob("*Train.xlsx"):
            label = file[10:11]
            xl_file = pd.ExcelFile(file)
            dfs = {sheet_name: xl_file.parse(sheet_name) 
                    for sheet_name in xl_file.sheet_names}
            for link in dfs['Sheet1']['Link']:
                files[link] = label
        return files
    
data_col = DataCollection()
data_col.process_training_data()