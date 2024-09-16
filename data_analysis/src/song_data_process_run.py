import os
import sys
import csv
import pandas as pd
import numpy as np
from cyanite_api import CyaniteAPI
sys.path.append('../../src')
from spotify_api_intergration import SpotifyAPI

class RunDataProcess():
    
    def __init__(self):
        self.data_dir = "../data_to_process"
        self.files_to_analyse = os.listdir(self.data_dir)
        self.spotify_api = SpotifyAPI()
        self.tracks = []
        
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
        file_name_counter = 1
        csv_file = f"../results/song_data_{file_name_counter}.csv"
        while os.path.isfile(csv_file) is True:
            file_name_counter += 1
            csv_file = f"../results/song_data_{file_name_counter}.csv"
        with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
            track_counter = 0
            mood = None
            for track in self.tracks[:3]:
                track_counter += 1
                print(f"Processing {track_counter}/{len(self.tracks)}")
                cyanite_api = CyaniteAPI(track)
                cyanite_data = cyanite_api.get_all_data()
                spotify_data = self.spotify_api.get_track_data(track)
                track_playcount = self.spotify_api.get_playcount(spotify_data['album']['id'])[0][f'spotify:track:{track}']
                song_data = self.process_data_dict(cyanite_data, spotify_data,track_playcount)
                if mood is None:
                    mood = {key: [value] for key, value in cyanite_data['Mood'].items()}
                else:
                    mood_new = {key: [value] for key, value in cyanite_data['Mood'].items()}
                    for key in mood:
                        mood[key].extend(mood_new[key])
                # Process Song Data
                if track_counter == 1:
                    writer = csv.DictWriter(file, fieldnames=song_data.keys())
                    writer.writeheader()
                writer.writerow(song_data)
        print(f"Data added to {csv_file}")
        # process all the mood
        file_name_counter = 1
        csv_file = f"../results/mood_data_{file_name_counter}.csv"
        while os.path.isfile(csv_file) is True:
            file_name_counter += 1
            csv_file = f"../results/mood_data_{file_name_counter}.csv"
        with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
            for key, value in mood.items():
                mood[key] = sum(float(item) for item in value) / len(value)
            writer = csv.DictWriter(file, fieldnames=mood.keys())
            writer.writeheader()
            writer.writerow(mood)
        print(f"Data added to {csv_file}")                

    def process_data_dict(self, cyanite_data, spotify_data, track_playcount):
        """
            Sort data to dict based on rows for csv
        """
        song_data = {'Song_Name': spotify_data['name'], 'Song_Link': spotify_data['id'], 'Artist_Name': ', '.join([item['name'] for item in spotify_data['artists'] if 'name' in item]), 
                     'Stream_Count': track_playcount, 'Release Date': spotify_data['album']['release_date'], 
                     'Musical_Era': cyanite_data['Musical_Era'], 'Voice_Presence': cyanite_data['Voice_Presence'], 'Predominant_Voice_Gender': cyanite_data['Predominant_Voice_Gender'], 
                  'Genre_Tags': ','.join(cyanite_data['Genre_Tags']), 'Sub_Genre_Tags': ','.join(cyanite_data['Sub_Genre_Tags']), 'Free Genre': cyanite_data['Free Genre'], 
                  'Description': cyanite_data['Description'], 'Instrument_Tags': ','.join(cyanite_data['Instrument_Tags']), 'Emotional_Profile': cyanite_data['Emotional_Profile'],
                  'Mood_Tags': ','.join(cyanite_data['Mood_Tags']), 'Simple_Mood_Tags': ','.join(cyanite_data['Simple_Mood_Tags']), 'Character_Tags': ','.join(cyanite_data['Character_Tags']),
                  'Movement_Tags': ','.join(cyanite_data['Movement_Tags']), 'Energy': cyanite_data['Energy'], 'BPM': cyanite_data['BPM']['value'], 'Key': cyanite_data['Key']['value'], 'Meter': cyanite_data['Meter']}
        return song_data
                    
    def get_songs_to_process(self, file):
        """
            Get data of song
        """
        # Process for track
        if "track" in file:
            track_id = self.get_resource_id_from_track(file)
            if track_id is None:
                print(f"{file} is broken")
            else:
                if track_id not in self.tracks:
                    self.tracks.append(track_id)
        # Process for artist
        elif "artist" in file:
            artist_id = self.get_spotify_artist_id(file)
            artist_tracks = self.get_song_from_artist(artist_id)
            for track_id in artist_tracks:
                if track_id not in self.tracks:
                    self.tracks.append(track_id)
        # Process for playlist
        elif "playlist" in file:
            playlist_id = self.get_spotify_playlist_id(file)
            playlist_tracks = self.get_song_from_playlist(playlist_id)
            for track_id in playlist_tracks:
                if track_id not in self.tracks:
                    self.tracks.append(track_id)
    
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
    
# if m.endswith('.mp3'):
runData = RunDataProcess()
runData.analyse_all_data()