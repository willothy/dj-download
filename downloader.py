import os
import datetime
import csv
import subprocess

import unicodedata
import re
from requests import auth

from youtubesearchpython import VideosSearch
from pytube import YouTube

import eyed3

import spotipy
import sys
from spotipy.oauth2 import SpotifyClientCredentials

# dotenv
import os
from os.path import join, dirname
from dotenv import load_dotenv
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

my_client_id = os.getenv("CLIENT_ID")
my_client_secret = os.getenv("CLIENT_SECRET")
my_redurect_uri = "http://127.0.0.1:5000/"
my_scope = 'user-read-recently-played, user-read-playback-state, user-read-currently-playing'

def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value)
    return re.sub(r'[-\s]+', '-', value).strip('-_')

class Queue:
    def __init__(self):
        self.queue = []

    def enqueue(self, item):
        self.queue.insert(0, item)

    def dequeue(self):
        return self.queue.pop()

    def __len__(self):
        return len(self.queue)

class Downloader:
    def __init__(self):
        self.download_queue = Queue()
        self.download_folder = './downloads/'+str(int(datetime.datetime.now().timestamp()))+'/'
        self.input_file = './playlists/2021.csv'
        self.sp = None

    def spotify_auth(self):
        cache_handler = spotipy.cache_handler.CacheFileHandler()
        auth_manager = spotipy.oauth2.SpotifyOAuth(client_id=my_client_id, client_secret=my_client_secret, redirect_uri=my_redurect_uri, scope=my_scope, cache_handler=cache_handler, show_dialog=True)
        
        sp = spotipy.Spotify(auth_manager=auth_manager)
        self.sp = sp
        return sp.me()

    def spotify_song_list_playlist(self, playlist_id):
        song_list = []

        if self.sp != None:
            playlist_info = self.sp.playlist(playlist_id)
            # print(playlist_info['tracks'])
            
            if playlist_info != None:
                for item in playlist_info['tracks']['items']:
                    track_name = item['track']['name']
                    
                    artist_list = []
                    for artist in item['track']['artists']:
                        artist_list.append(artist['name'])

                    track_artist = artist_list[0]

                    song_list.append((track_name, track_name))

        return song_list

    def string_cleaner(self, string):
        new_string = string
        for char in ["'", '.', '/', '-', ':', ';', '"']:
            new_string = new_string.replace(char, "")

        return new_string

    def load_csv(self):
        song_list = []

        with open(self.input_file, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)

            for index, row in enumerate(csv_reader):
                song_list.append((row['Track name'],row[' Artist name']))

        return song_list

    def find_songs(self, song_list):
        ready_to_download = []

        for song in song_list:
            song_name, song_artist = song
            search_results = VideosSearch(song_name + ' ' + song_artist + ' lyrics', limit = 1)
            
            song_url = search_results.result()['result'][0]['id']

            ready_to_download.append((song_url, song_name, song_artist))
            print('Found: ' + song_name)

        return ready_to_download

    def queue_adder(self, song_list):
        for song in song_list:
            self.download_queue.enqueue(song)

    def queue_downloader(self):
        counter = 0
        while len(self.download_queue) > 0:
            counter += 1
            song_url, song_name, song_artist = self.download_queue.dequeue()
            try:
                youtube = YouTube('https://www.youtube.com/watch?v='+song_url)
                video = youtube.streams.get_audio_only()

                download_song_name = slugify(song_name)
                video.download(self.download_folder, filename=download_song_name+'.mp4')

                subprocess.call(['ffmpeg -i ' + self.download_folder + download_song_name + '.mp4 ' + self.download_folder + download_song_name + '.mp3' ], shell=True)

                os.remove(self.download_folder + download_song_name + '.mp4')

                audiofile = eyed3.load(self.download_folder + download_song_name + '.mp3')
                audiofile.tag.artist = song_artist
                audiofile.tag.title = song_name

                audiofile.tag.save()

                print('Downloaded: ' + song_name)
            except:
                print('Failed to download: ' + song_name)

if __name__ == '__main__':
    test = Downloader()
    test.spotify_auth()
    test.queue_adder(test.find_songs(test.spotify_song_list_playlist('7AtK8K2MbPBzlosZKg76J5')))
    test.queue_downloader()