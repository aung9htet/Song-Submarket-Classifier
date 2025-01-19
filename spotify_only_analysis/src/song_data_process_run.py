import os
import sys
import csv
import pandas as pd
import numpy as np
from cyanite_api import CyaniteAPI
sys.path.append('../../src')
from spotify_api_intergration import SpotifyAPI
from apple_api_integration import AppleAPI
import matplotlib.pyplot as plt

class RunDataProcess():
    
    def __init__(self):
        self.data_dir = "../data_to_process"
        self.files_to_analyse = os.listdir(self.data_dir)
        self.spotify_api = SpotifyAPI()
        self.apple_api = AppleAPI()
        self.playlist = {'all': []}
        
    def analyse_all_data(self):
        """
            The following code is used to process all data
        """
        all_files_to_analyse = np.empty(0)
        # collect all data from dataset
        for end_point in self.files_to_analyse:
            file_to_analyse = os.path.join(self.data_dir, end_point)
            data = self.get_data_to_process(file_to_analyse)
            all_files_to_analyse = np.append(all_files_to_analyse, np.array(data))

        # process all files to song dataset
        file_counter = 0
        for file in all_files_to_analyse:
            file_counter += 1
            print(f"{file_counter}/{len(all_files_to_analyse)} files completed!")
            self.get_songs_to_process(file)   
        
        # process spotify data
        playlist_counter = 0
        # reduced to one combined playlist only
        # print(self.playlist.keys())
        # self.playlist = {'0czR5cQKhYNwPjVRQGPW3l': self.playlist['0czR5cQKhYNwPjVRQGPW3l']}
        for playlist_id in self.playlist:
            if playlist_id != 'all':
                spotify_playlist_data = self.spotify_api.get_playlist(playlist_id)
                dir_name = spotify_playlist_data['name'].strip()
            else:
                dir_name = 'all'
            directory = f"../results/{dir_name}"
            if not os.path.exists(directory):
                os.makedirs(directory)
            csv_file = f"../results/{dir_name}/song_data.csv"
            with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                track_counter = 0
                playlist_counter += 1
                tracks = self.playlist[playlist_id]
                for track in tracks:
                    try:
                        track_counter += 1
                        print(f"Processing: Playlist = {playlist_counter}/{len(self.playlist)}, Track = {track_counter}/{len(tracks)}")
                        spotify_data = self.spotify_api.get_track_data(track)
                        track_playcount = self.spotify_api.get_playcount(spotify_data['album']['id'])[0][f'spotify:track:{track}']
                        isrc = self.spotify_api.get_isrc(track)
                        apple_song_id = self.apple_api.get_song_id(isrc)
                        composer_name = self.apple_api.get_song_writer(apple_song_id)
                        song_data = self.process_data_dict(spotify_data, composer_name, track_playcount)

                        if track_counter == 1:
                            writer = csv.DictWriter(file, fieldnames=song_data.keys())
                            writer.writeheader()
                        writer.writerow(song_data)

                        # tester = self.apple_api.get_song_id()
                    except Exception as e:
                        print(f"Error processing {track}: {e}")

    def process_data_dict(self, spotify_data, composer_name, track_playcount):
        """
            Sort data to dict based on rows for csv
        """
        song_data = {'Song_Name': spotify_data['name'], 'Song_Link': spotify_data['id'], 'Artist_Name': ', '.join([item['name'] for item in spotify_data['artists'] if 'name' in item]), 
                     'Stream_Count': track_playcount, 'Release Date': spotify_data['album']['release_date'], 'Composer Nmae': composer_name}
        return song_data
                    
    def get_songs_to_process(self, file):
        """
            Get data from CSV. This may either be track, artist or playlist.
        """
        # Process for track
        if "track" in file:
            track_id = self.get_resource_id_from_track(file)
            if track_id is None:
                print(f"{file} is broken")
            else:
                if track_id not in self.playlist['all']:
                    self.playlist['all'].append(track_id)
        # Process for artist
        elif "artist" in file:
            artist_id = self.get_spotify_artist_id(file)
            artist_tracks = self.get_song_from_artist(artist_id)
            for track_id in artist_tracks:
                if track_id not in self.playlist['all']:
                    self.playlist['all'].append(track_id)
        # Process for playlist
        elif "playlist" in file:
            playlist_id = self.get_spotify_playlist_id(file)
            playlist_tracks = self.get_song_from_playlist(playlist_id)
            for track_id in playlist_tracks:
                if not playlist_id in self.playlist.keys():
                    self.playlist[playlist_id] = [track_id]
                else:
                    self.playlist[playlist_id].append(track_id)
                if track_id not in self.playlist['all']:
                    self.playlist['all'].append(track_id)
    
    def get_song_from_playlist(self, playlist_id):
        """
            Get all the track id of playlist
        """
        playlist_data = self.spotify_api.get_playlist_data(playlist_id)
        track_list = []
        for track_data in playlist_data['items']:
            track_data = track_data['track']
            track_list.append(track_data['id'])
        while not playlist_data['next'] is None:
            playlist_data = self.spotify_api.get_playlist_data(playlist_data['next'], next = True)
            for track_data in playlist_data['items']:
                track_data = track_data['track']
                track_list.append(track_data['id'])
        return track_list
    
    def get_song_from_artist(self, artist_id):
        """
            Get all the track id of artist
        """
        artist_data = self.spotify_api.get_artist_album(artist_id)
        track_list = []
        for track_data in artist_data['items']:
            track_list.append(track_data['id'])
        while not artist_data['next'] is None:
            artist_data = self.spotify_api.get_artist_data(artist_data['next'], next = True)
            for track_data in artist_data['items']:
                track_list.append(track_data['id'])
        return track_list

    def get_spotify_playlist_id(self, file):
        """
            Get track id if file is related to playlist
        """
        if 'spotify:playlist' in file:  # For Spotify URI
            playlist_id = file.split(':')[-1]
        elif 'open.spotify.com/playlist' in file:  # For Spotify link
            playlist_id = file.split('/')[-1].split('?')[0]  # Remove query params if any
        else:
            playlist_id = None  # Not a valid Spotify URI or link
        return playlist_id

    def get_spotify_artist_id(self, file):
        """
            Get track id if file is related to artist
        """
        if 'spotify:artist' in file:  # For Spotify URI
            artist_id = file.split(':')[-1]
        elif 'open.spotify.com/artist' in file:  # For Spotify link
            artist_id = file.split('/')[-1].split('?')[0]  # Remove query params if any
        else:
            artist_id = None  # Not a valid Spotify URI or link
        return artist_id
    
    def get_resource_id_from_track(self, file):
        """
            Get track id if file is related to track
        """
        if 'spotify:' in file:  # For Spotify URI
            resource_id = file.split(':')[-1]
        elif 'open.spotify.com' in file:  # For Spotify link
            resource_id = file.split('/')[-1].split('?')[0]
        else:
            resource_id = None
        return resource_id
        
    def get_data_to_process(self, file_to_analyse):
        """
            The following code is used to define how to process data from csv and xlsx format.
        """
        # Xlsx format
        if file_to_analyse.endswith('.xlsx'):
            file = pd.ExcelFile(file_to_analyse)
            if len(file.sheet_names) > 1:
                print(f"Error: {file_to_analyse} has more than 1 column")
            file = file.parse(file.sheet_names[0])
            data = file.values.tolist()
            print(f"Processed {file_to_analyse} from xlsx to list")
        # Csv format process
        elif file_to_analyse.endswith('.csv'):
            file = pd.read_csv(file_to_analyse)
            if len(file.sheet_names) > 1:
                print(f"Error: {file_to_analyse} has more than 1 column")
            file = file.parse(file.sheet_names[0])
            data = file.values.tolist()
            print(f"Processed {file_to_analyse} from csv to list")
        # Unknown format
        else:
            data = []
            print("Incompatible File Format")
        return data

runData = RunDataProcess()
runData.analyse_all_data()