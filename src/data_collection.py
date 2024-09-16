import glob, os
import pandas as pd
from cyanite_api import CyaniteAPI
from spotify_api_intergration import SpotifyAPI

class DataCollection(object):

    def __init__(self):
        self.batch = "batch_2"
        self.spotify = SpotifyAPI()
        self.train_files = self.get_train_files()
        self.test_files = self.get_test_files()
    
    def process_training_data(self):
        features = []
        playlist_count = 0
        track_count = 0
        for playlist in self.train_files:
            print(playlist)
            playlist_count += 1
            track_list = []
            label = {'label': self.train_files[playlist]}
            playlist = playlist[34:]
            data = self.spotify.get_playlist_data(playlist)
            data_list = data['tracks']['items']
            for track_index in range(len(data_list)):
                try:
                    track_list.append(data_list[track_index]['track']['id'])
                except Exception as e:
                    print(e)
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
            track_count += len(track_list)
            for track in track_list:
                song_analyser = CyaniteAPI(track)
                try:
                    mood, genre, advanced_genre, movement, character = song_analyser.get_data()
                    feature = label | mood | genre | advanced_genre | movement | character
                    features.append(feature)
                    song_count += 1
                except Exception as e:
                    print(track)
                    print(f"Failed to get song. Error: {e}")
                print(f"Processing Playlist: {playlist_count}/{len(self.train_files)}, Processed Song: {song_count}/{len(track_list)}, Total Song Count: {track_count}")
        self.save_data(features, f'../processed_dataset/song_training_data_{self.batch}.csv')

    def process_test_data(self):
        features = []
        song_count = 0
        for track in self.test_files:
            label = {'label': self.test_files[track]}
            track = track[31:]
            track = self.spotify.get_track_data(track)['id']
            song_analyser = CyaniteAPI(track)
            try:
                mood, genre, advanced_genre, movement, character = song_analyser.get_data()
                feature = label | mood | genre | advanced_genre | movement | character
                features.append(feature)
                song_count += 1
            except Exception as e:
                print(track)
                print(f"Failed to get song. Error: {e}")
            print(f"Processed Song: {song_count}/{len(self.test_files)}")
        self.save_data(features, f'../processed_dataset/song_test_data_{self.batch}.csv')

    def save_data(self, features, file_name):
        with open(file_name, 'w') as f:
            # Write all the dictionary keys in a file with commas separated.
            f.write(','.join(features[0].keys()))
            f.write('\n') # Add a new line
            for row in features:
                # Write the values in a row.
                f.write(','.join(str(x) for x in row.values()))
                f.write('\n') # Add a new line
        print("Successfully written file.")

    def get_train_files(self):
        os.chdir(f"../{self.batch}")
        files = {}
        for file in glob.glob("*Train.xlsx"):
            label = file[10:11]
            xl_file = pd.ExcelFile(file)
            dfs = {sheet_name: xl_file.parse(sheet_name) 
                    for sheet_name in xl_file.sheet_names}
            for link in dfs['Sheet1']['Link']:
                files[link] = label
        return files
    
    def get_test_files(self):
        os.chdir(f"../{self.batch}")
        files = {}
        for file in glob.glob("*Test.xlsx"):
            label = file[10:11]
            xl_file = pd.ExcelFile(file)
            dfs = {sheet_name: xl_file.parse(sheet_name) 
                    for sheet_name in xl_file.sheet_names}
            for link in dfs['Sheet1']['Link']:
                files[link] = label
        return files

data_col = DataCollection()
data_col.process_training_data()