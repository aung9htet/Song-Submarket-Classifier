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
from itertools import islice
import re

class RunDataProcess():
    
    def __init__(self):
        self.data_dir = "../data_to_process"
        self.files_to_analyse = os.listdir(self.data_dir)
        self.spotify_api = SpotifyAPI()
        self.apple_api = AppleAPI()
        self.playlist = {'all': []}

    def sanitize_filename(self, filename, replacement="_", max_length=255):
        """Sanitize a filename to be safe for use on Windows and other filesystems."""
        pattern = r'\/?%*:|"<>'
        result = re.sub(pattern, "", filename, flags=re.IGNORECASE)
        filtered_result = re.sub(r"[^\w\s]", replacement, result)
        print(filtered_result)
        return filtered_result.strip()
    
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
        # for playlist_id in islice(self.playlist, 2, None):
            if playlist_id != 'all':
                spotify_playlist_data = self.spotify_api.get_playlist(playlist_id)
                dir_name = spotify_playlist_data['name'].strip()
                print(type(dir_name))
                dir_name = self.sanitize_filename(filename=str(dir_name))
                link = spotify_playlist_data['href']
                description = spotify_playlist_data['description']
                follower_count = spotify_playlist_data['followers']['total']
            else:
                dir_name = 'all'
            directory = f"../results/{dir_name}"
            if not os.path.exists(directory):
                os.makedirs(directory)
            csv_file = f"../results/{dir_name}/song_data.csv"
            with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                track_counter = 0
                mood = None
                simple_mood = None
                character = None
                genre = None
                vocal_presence = {}
                instruments = {}
                energy_level = {}
                song_key = {}
                meter = {}
                sub_genre = {}
                free_genre = {}
                musical_era = {}
                artists = {}
                positive_emotional_percentage = 0
                bpm_average = []
                female_dominant_vocal_percentage = 0
                playlist_counter += 1
                tracks = self.playlist[playlist_id]
                for track in tracks:
                    try:
                        track_counter += 1
                        print(f"Processing: Playlist = {playlist_counter}/{len(self.playlist)}, Track = {track_counter}/{len(tracks)}")
                        cyanite_api = CyaniteAPI(track)
                        cyanite_data = cyanite_api.get_all_data()
                        spotify_data = self.spotify_api.get_track_data(track)
                        track_playcount = self.spotify_api.get_playcount(spotify_data['album']['id'])[0][f'spotify:track:{track}']
                        isrc = self.spotify_api.get_isrc(track)
                        apple_song_id = self.apple_api.get_song_id(isrc)
                        composer_name = self.apple_api.get_song_writer(apple_song_id)
                        
                        # for composer in composer_name.split(","):
                        #     composer = composer.strip()
                        similar_song_list = self.apple_api.get_song_recommendation(composer_name, spotify_data['name'])
                        chosen_song = None
                        chosen_song_max_stream = 0
                        for similar_song in similar_song_list:
                            for song in self.spotify_api.get_id_from_isrc(similar_song)['tracks']['items']:
                                song_id = song['id']
                                if not song_id is None:
                                    song_data_parent = self.spotify_api.get_track_data(song_id)
                                    try:
                                        song_playcount = self.spotify_api.get_playcount(song_data_parent['album']['id'])[0][f'spotify:track:{song_id}']
                                        if song_playcount > chosen_song_max_stream:
                                            chosen_song_max_stream = song_playcount
                                            chosen_song = song_data_parent['external_urls']
                                        chosen_song_release_date = song_data_parent['album']['release_date']                            
                                    except Exception as e:
                                        song_playcount = None
                                        chosen_song = None
                                        chonsen_song_max_stream = None
                                        chosen_song_release_date = None
                                else:
                                    chosen_song = None
                                    chonsen_song_max_stream = None
                                    chosen_song_release_date = None

                        song_data = self.process_data_dict(cyanite_data, spotify_data, track_playcount, composer_name, chosen_song, chosen_song_max_stream, chosen_song_release_date)

                        # calculate average mood over playlist
                        if not cyanite_data['Mood'] is None:
                            if mood is None:
                                mood = {key: [value] for key, value in cyanite_data['Mood'].items()}
                            else:
                                new_item = {key: [value] for key, value in cyanite_data['Mood'].items()}
                                for key in mood:
                                    mood[key].extend(new_item[key])
                        
                        # calculate average simple mood over playlist
                        if not cyanite_data['Simple_Mood'] is None:
                            if simple_mood is None:
                                simple_mood = {key: [value] for key, value in cyanite_data['Simple_Mood'].items()}
                            else:
                                new_item = {key: [value] for key, value in cyanite_data['Simple_Mood'].items()}
                                for key in simple_mood:
                                    simple_mood[key].extend(new_item[key])

                        # calculate average character over playlist
                        if not cyanite_data['Character'] is None:
                            if character is None:
                                character = {key: [value] for key, value in cyanite_data['Character'].items()}
                            else:
                                new_item = {key: [value] for key, value in cyanite_data['Character'].items()}
                                for key in character:
                                    character[key].extend(new_item[key])

                        # calculate genre over playlist
                        if not cyanite_data['Genre'] is None:
                            if genre is None:
                                genre = {key: [value] for key, value in cyanite_data['Genre'].items()}
                            else:
                                new_item = {key: [value] for key, value in cyanite_data['Genre'].items()}
                                for key in genre:
                                    genre[key].extend(new_item[key])

                        # record vocal presence
                        if not cyanite_data['Voice_Presence'] is None:
                            if not cyanite_data['Voice_Presence'] in vocal_presence.keys():
                                vocal_presence[cyanite_data['Voice_Presence']] = 1
                            else:
                                vocal_presence[cyanite_data['Voice_Presence']] = vocal_presence[cyanite_data['Voice_Presence']] + 1
                        
                        # record instrument presence
                        if not cyanite_data['Instrument'] is None:
                            for instrument in cyanite_data['Instrument']:
                                if cyanite_data['Instrument'][instrument] == "throughout":
                                    if not instrument in instruments.keys():
                                        instruments[instrument] = 1
                                    else:
                                        instruments[instrument] = instruments[instrument] + 1

                        # record energy level
                        if not cyanite_data['Energy'] is None:
                            if not cyanite_data['Energy'] in energy_level.keys():
                                energy_level[cyanite_data['Energy']] = 1
                            else:
                                energy_level[cyanite_data['Energy']] = energy_level[cyanite_data['Energy']] + 1

                        # record key
                        if not cyanite_data['Key'] is None:
                            if not cyanite_data['Key']['value'] in song_key.keys():
                                song_key[cyanite_data['Key']['value']] = 1
                            else:
                                song_key[cyanite_data['Key']['value']] = song_key[cyanite_data['Key']['value']] + 1

                        # record meter
                        if not cyanite_data['Meter'] is None:
                            if not cyanite_data['Meter'] in meter.keys():
                                meter[cyanite_data['Meter']] = 1
                            else:
                                meter[cyanite_data['Meter']] = meter[cyanite_data['Meter']] + 1

                        # record sub-genre
                        if not cyanite_data['Sub_Genre_Tags'] is None:
                            for sub_gen in cyanite_data['Sub_Genre_Tags']:
                                if not sub_gen in sub_genre.keys():
                                    sub_genre[sub_gen] = 1
                                else:
                                    sub_genre[sub_gen] = sub_genre[sub_gen] + 1

                        # record free-genre
                        if not cyanite_data['Free Genre'] is None:
                            for free_gen in cyanite_data['Free Genre'].split(','):
                                if not free_gen in free_genre.keys():
                                    free_genre[free_gen] = 1
                                else:
                                    free_genre[free_gen] = free_genre[free_gen] + 1

                        # record musical era
                        if not cyanite_data['Musical_Era'] is None:
                            if not cyanite_data['Musical_Era'] in musical_era.keys():
                                musical_era[cyanite_data['Musical_Era']] = 1
                            else:
                                musical_era[cyanite_data['Musical_Era']] = musical_era[cyanite_data['Musical_Era']] + 1
                        
                        # record artists
                        artist_data = spotify_data["artists"]
                        for artist in artist_data:
                            artist_name = artist["name"]
                            if not artist_name in artists.keys():
                                artists[artist_name] = 1
                            else:
                                artists[artist_name] = artists[artist_name] + 1

                        # process for playlist general data
                        if playlist_id != 'all':
                            if cyanite_data['Emotional_Profile'] == 'positive':
                                positive_emotional_percentage += 1
                            if not cyanite_data['BPM'] is None:
                                bpm_average.append(cyanite_data['BPM']['value'])
                            if cyanite_data['Emotional_Profile'] == 'female':
                                female_dominant_vocal_percentage += cyanite_data['Predominant_Voice_Gender']

                        # Process Song Data
                        if track_counter == 1:
                            writer = csv.DictWriter(file, fieldnames=song_data.keys())
                            writer.writeheader()
                        writer.writerow(song_data)
                    except Exception as e:
                        print(f"Error processing {track}: {e}")
                print(f"Data added to {csv_file}")   
                # process all the mood
                csv_file = f"../results/{dir_name}/mood_data.csv"
                if mood is None:
                    print("No Mood in Playlist")
                else:
                    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                        for key, value in mood.items():
                            mood[key] = sum(float(item) for item in value) / len(value)
                        writer = csv.DictWriter(file, fieldnames=mood.keys())
                        writer.writeheader()
                        writer.writerow(mood)
                
                # process all the simple mood
                csv_file = f"../results/{dir_name}/simple_mood_data.csv"
                if simple_mood is None:
                    print("No Simple Mood in Playlist")
                else:
                    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                        for key, value in simple_mood.items():
                            simple_mood[key] = sum(float(item) for item in value) / len(value)
                        writer = csv.DictWriter(file, fieldnames=simple_mood.keys())
                        writer.writeheader()
                        writer.writerow(simple_mood)
                print(f"Data added to {csv_file}")     

                # process all the character
                csv_file = f"../results/{dir_name}/character_data.csv"
                if character is None:
                    print("No Character in Playlist")
                else:
                    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                        for key, value in character.items():
                            character[key] = sum(float(item) for item in value) / len(value)
                        writer = csv.DictWriter(file, fieldnames=character.keys())
                        writer.writeheader()
                        writer.writerow(character)
                print(f"Data added to {csv_file}") 

                # process all the genre
                csv_file = f"../results/{dir_name}/genre_data.csv"
                if genre is None:
                    print("No Genre in Playlist")
                else:
                    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                        for key, value in genre.items():
                            genre[key] = sum(float(item) for item in value) / len(value)
                        writer = csv.DictWriter(file, fieldnames=genre.keys())
                        writer.writeheader()
                        writer.writerow(genre)
                print(f"Data added to {csv_file}")       

                # process all the vocal presence
                csv_file = f"../results/{dir_name}/vocal_presence_data.csv"
                if vocal_presence is None:
                    print("No Vocal Presence Data in Playlist's Songs")
                else:
                    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                        writer = csv.DictWriter(file, fieldnames=['Vocal Presence', 'Counter'])
                        writer.writeheader()
                        for key, value in vocal_presence.items():
                            writer.writerow({'Vocal Presence': key, 'Counter': value})
                print(f"Data added to {csv_file}")

                # process all the instruments
                csv_file = f"../results/{dir_name}/instruments_data.csv"
                if instruments is None:
                    print("No Instrument Data in Playlist's Songs")
                else:
                    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                        writer = csv.DictWriter(file, fieldnames=['Instrument', 'Counter'])
                        writer.writeheader()
                        for key, value in instruments.items():
                            writer.writerow({'Instrument': key, 'Counter': value})
                print(f"Data added to {csv_file}")

                # process all the energy level
                csv_file = f"../results/{dir_name}/energy_level_data.csv"
                if energy_level is None:
                    print("No Energy Level Data in Playlist's Songs")
                else:
                    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                        writer = csv.DictWriter(file, fieldnames=['Energy Level', 'Counter'])
                        writer.writeheader()
                        for key, value in energy_level.items():
                            writer.writerow({'Energy Level': key, 'Counter': value})
                print(f"Data added to {csv_file}")

                # process all the key
                csv_file = f"../results/{dir_name}/song_key_data.csv"
                if song_key is None:
                    print("No Key Data in Playlist's Songs")
                else:
                    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                        writer = csv.DictWriter(file, fieldnames=['Key', 'Counter'])
                        writer.writeheader()
                        for key, value in song_key.items():
                            writer.writerow({'Key': key, 'Counter': value})
                print(f"Data added to {csv_file}")

                # process all the meter
                csv_file = f"../results/{dir_name}/meter_data.csv"
                if meter is None:
                    print("No Meter Data in Playlist's Songs")
                else:
                    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                        writer = csv.DictWriter(file, fieldnames=['Meter', 'Counter'])
                        writer.writeheader()
                        for key, value in meter.items():
                            writer.writerow({'Meter': key, 'Counter': value})
                print(f"Data added to {csv_file}")

                # process all the sub-genre
                csv_file = f"../results/{dir_name}/sub_genre_data.csv"
                if sub_genre is None:
                    print("No Sub Genre Data in Playlist's Songs")
                else:
                    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                        writer = csv.DictWriter(file, fieldnames=['Sub Genre', 'Counter'])
                        writer.writeheader()
                        for key, value in sub_genre.items():
                            writer.writerow({'Sub Genre': key, 'Counter': value})
                print(f"Data added to {csv_file}")

                # process all the free-genre
                csv_file = f"../results/{dir_name}/free_genre_data.csv"
                if free_genre is None:
                    print("No Free Genre Data in Playlist's Songs")
                else:
                    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                        writer = csv.DictWriter(file, fieldnames=['Free Genre', 'Counter'])
                        writer.writeheader()
                        for key, value in free_genre.items():
                            writer.writerow({'Free Genre': key, 'Counter': value})
                print(f"Data added to {csv_file}")

                # process all the musical era
                csv_file = f"../results/{dir_name}/musical_era_data.csv"
                if musical_era is None:
                    print("No Musical Era Data in Playlist's Songs")
                else:
                    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                        writer = csv.DictWriter(file, fieldnames=['Musical Era', 'Counter'])
                        writer.writeheader()
                        for key, value in musical_era.items():
                            writer.writerow({'Musical Era': key, 'Counter': value})
                print(f"Data added to {csv_file}")

                # record artist
                csv_file = f"../results/{dir_name}/artists_data.csv"
                if artists is None:
                    print("No Artist Data in Playlist's Songs")
                else:
                    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                        writer = csv.DictWriter(file, fieldnames=['Artists', 'Counter'])
                        writer.writeheader()
                        for key, value in artists.items():
                            writer.writerow({'Artists': key, 'Counter': value})
                print(f"Data added to {csv_file}")

                # record data for playlist
                if playlist_id != 'all':
                    positive_emotional_percentage = positive_emotional_percentage/len(tracks)
                    if len(bpm_average) > 0:    
                        bpm_average = sum(bpm_average) / len(bpm_average)
                    else:
                        bpm_average = None
                    female_dominant_vocal_percentage = female_dominant_vocal_percentage/len(tracks)
                    csv_file = f"../results/{dir_name}/playlist_data.csv"
                    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                        writer = csv.DictWriter(file, fieldnames=['Playlist Name', 'Playlist Link', 'Playlist Description', 'Follower Count', 'Positive Emotional Profile', 'Average BPM', 'Female Dominant Vocal Percentage'])
                        writer.writeheader()
                        writer.writerow({'Playlist Name': dir_name, 'Playlist Link': link, 'Playlist Description': description, 'Follower Count': follower_count, 'Positive Emotional Profile': f'{positive_emotional_percentage * 100}%', 'Average BPM': bpm_average, 'Female Dominant Vocal Percentage': f'{female_dominant_vocal_percentage * 100}%'})
                    print(f"Data added to {csv_file}")

    def process_data_dict(self, cyanite_data, spotify_data, track_playcount, composer_name, org_song, chosen_song_max_stream, chosen_song_release_date):
        """
            Sort data to dict based on rows for csv
        """
        song_data = {'Song_Name': spotify_data['name'], 'Song_Link': spotify_data['id'], 'Artist_Name': ', '.join([item['name'] for item in spotify_data['artists'] if 'name' in item]), 
                     'Stream_Count': track_playcount, 'Release Date': spotify_data['album']['release_date'], 
                     'Musical_Era': cyanite_data['Musical_Era'], 'Voice_Presence': cyanite_data['Voice_Presence'], 'Predominant_Voice_Gender': cyanite_data['Predominant_Voice_Gender'], 
                  'Genre_Tags': None if cyanite_data['Genre_Tags'] is None else ','.join(cyanite_data['Genre_Tags']), 'Sub_Genre_Tags': None if cyanite_data['Sub_Genre_Tags'] is None else ','.join(cyanite_data['Sub_Genre_Tags']), 'Free Genre': cyanite_data['Free Genre'], 
                  'Description': cyanite_data['Description'], 'Instrument_Tags': None if cyanite_data['Instrument_Tags'] is None else ','.join(cyanite_data['Instrument_Tags']), 'Emotional_Profile': cyanite_data['Emotional_Profile'],
                  'Mood_Tags': None if cyanite_data['Mood_Tags'] is None else ','.join(cyanite_data['Mood_Tags']), 'Simple_Mood_Tags': None if cyanite_data['Simple_Mood_Tags'] is None else ','.join(cyanite_data['Simple_Mood_Tags']), 'Character_Tags': None if cyanite_data['Character_Tags'] is None else ','.join(cyanite_data['Character_Tags']),
                  'Movement_Tags': None if cyanite_data['Movement_Tags'] is None else ','.join(cyanite_data['Movement_Tags']), 'Energy': cyanite_data['Energy'], 'BPM': None if cyanite_data['BPM'] is None else cyanite_data['BPM']['value'], 'Key': None if cyanite_data['Key'] is None else cyanite_data['Key']['value'], 'Meter': cyanite_data['Meter'], 'Composer Nmae': composer_name, 'Original Song Estimate': org_song, 'Original Song Stream Count': chosen_song_max_stream, 'Original Song Release Date': chosen_song_release_date}
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
            df = pd.read_csv(file_to_analyse)
            data = df.values.tolist()
            print(f"Processed {file_to_analyse} from csv to list")
        # Unknown format
        else:
            data = []
            print("Incompatible File Format")
        return data

class ResultsPlotter():
    def __init__(self):
        base_dir = '../results/'
        self.data_dirs = [base_dir + name for name in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, name))]
    
    def process_plots(self):
        for process_dir in self.data_dirs:
            try:
                artists_data, artists_counter = zip(*self.get_csv_bar(process_dir, 'artists_data'))
                self.plot_bar(artists_data, artists_counter, 'Artist', 'Recurrence Count', 'Artist Count', process_dir + '/artists_data.png')
            except Exception:
                pass

            try:
                character = self.get_csv_pie(process_dir, 'character_data')
                self.plot_pie(character[1], character[0], 'Character Distribution', process_dir + '/character_data.png')
            except Exception:
                pass

            try:
                energy_level_data, energy_level_counter = zip(*self.get_csv_bar(process_dir, 'energy_level_data'))
                self.plot_bar(energy_level_data, energy_level_counter, 'Energy Level', 'Recurrence Count', 'Energy Level Count', process_dir + '/energy_level_data.png')
            except Exception:
                pass

            try:
                free_genre_data, free_genre_counter = zip(*self.get_csv_bar(process_dir, 'free_genre_data'))
                self.plot_bar(free_genre_data, free_genre_counter, 'Free Genre', 'Recurrence Count', 'Free Genre Count', process_dir + '/free_genre_data.png')
            except Exception:
                pass

            try:
                genre = self.get_csv_pie(process_dir, 'genre_data')
                threshold = float(sorted(sorted(genre[1],reverse=True)[:8])[0])
                self.plot_pie(genre[1], genre[0], 'Genre Distribution', process_dir + '/genre_data.png', threshold)
            except Exception:
                pass

            try:
                instruments_data, instruments_counter = zip(*self.get_csv_bar(process_dir, 'instruments_data'))
                self.plot_bar(instruments_data, instruments_counter, 'Instruments', 'Recurrence Count', 'Instruments Count', process_dir + '/instruments_data.png')
            except Exception:
                pass

            try:
                meter_data, meter_counter = zip(*self.get_csv_bar(process_dir, 'meter_data'))
                self.plot_bar(meter_data, meter_counter, 'Meter', 'Recurrence Count', 'Meter Count', process_dir + '/meter_data.png')
            except Exception:
                pass
            
            try:
                mood = self.get_csv_pie(process_dir, 'mood_data')
                threshold = float(sorted(sorted(mood[1],reverse=True)[:10])[0])
                self.plot_pie(mood[1], mood[0], 'Mood Distribution', process_dir + '/mood_data.png', threshold)
            except Exception:
                pass
   
            try:
                musical_era_data, musical_era_counter = zip(*self.get_csv_bar(process_dir, 'musical_era_data'))
                self.plot_bar(musical_era_data[0], musical_era_counter, 'Musical Era', 'Recurrence Count', 'Musical Era Count', process_dir + '/musical_era_data.png')
            except Exception:
                pass

            try:
                simple_mood = self.get_csv_pie(process_dir, 'simple_mood_data')
                self.plot_pie(simple_mood[1], simple_mood[0], 'Simple Mood Distribution', process_dir + '/simple_mood_data.png')
            except Exception:
                pass
            
            try:    
                song_key_data, song_key_counter = zip(*self.get_csv_bar(process_dir, 'song_key_data'))
                self.plot_bar(song_key_data, song_key_counter, 'Song Key', 'Recurrence Count', 'Song Key Count', process_dir + '/song_key_data.png')
            except Exception:
                pass
           
            try:
                sub_genre_data, sub_genre_counter = zip(*self.get_csv_bar(process_dir, 'sub_genre_data'))
                self.plot_bar(sub_genre_data, sub_genre_counter, 'Sub Genre', 'Recurrence Count', 'Sub Genre Count', process_dir + '/sub_genre_data.png')
            except Exception:
                pass

            try:
                vocal_presence_data, vocal_presence_counter = zip(*self.get_csv_bar(process_dir, 'vocal_presence_data'))
                self.plot_bar(vocal_presence_data, vocal_presence_counter, 'Vocal Presence', 'Recurrence Count', 'Vocal Presence Count', process_dir + '/vocal_presence_data.png')
            except Exception:
                pass

    def get_csv_bar(self, base_dir, file_name):
        # data = []
        
        # Open and read the CSV file
        with open(base_dir + '/' + file_name + '.csv', mode='r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            rows = list(csv_reader)
            
            # Transpose rows to get columns
            columns = list(zip(*rows))
            
            # Extract data, skip the headers
            data_name = list(columns[0][1:])
            data_count = counts = [float(item) for item in columns[1][1:]]

            combined_data = list(zip(data_name, counts))
        
            # Sort by counts in descending order
            sorted_data = sorted(combined_data, key=lambda x: x[1], reverse=True)

            top_data = sorted_data[:20] if len(sorted_data) > 20 else sorted_data

            # # Convert the second list to float
            # data[1] = [float(item) for item in data[1]]  # Converting the second column (after the header) to floats

        return top_data

    
    def get_csv_pie(self, base_dir, file_name):
        data = []
        with open(base_dir + '/' + file_name + '.csv', mode='r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                data.append(row)
        return data

    def plot_bar(self, x, y, x_label, y_label, title, loc):
        plt.figure(figsize=(40, 20))
        plt.bar(x, y)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title)
        plt.savefig(loc)
        plt.close()

    def plot_pie(self, x, y, title, loc, threshold=0):
        # Convert the x list to integers
        try:
            x = list(map(float, x))
        except ValueError:
            print("Error: All elements in x must be convertible to integers.")
            return
        
        # Group values smaller than the threshold into "Others"
        large_values = []
        large_labels = []
        small_values_sum = 0

        for value, label in zip(x, y):
            if value >= threshold:
                large_values.append(value)
                large_labels.append(label)
            else:
                small_values_sum += value

        if small_values_sum > 0:
            large_values.append(small_values_sum)
            large_labels.append('Others')

        # Create the pie chart
        plt.figure()
        plt.pie(large_values, labels=large_labels, autopct='%1.1f%%', startangle=90)
        plt.title(title)
        plt.axis('equal')  # Ensure pie chart is drawn as a circle
        
        # Save the chart
        plt.savefig(loc)
        plt.close()  # Close the plot after saving

runData = RunDataProcess()
runData.analyse_all_data()
plotter = ResultsPlotter()
plotter.process_plots()