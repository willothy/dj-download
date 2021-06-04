import os
import datetime
import csv
import subprocess

from youtubesearchpython import VideosSearch
from pytube import YouTube


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
        self.input_file = './playlists/mother.csv'

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
        while len(self.download_queue) > 0:
            song_url, song_name, song_artist = self.download_queue.dequeue()
            youtube = YouTube('https://www.youtube.com/watch?v='+song_url)
            video = youtube.streams.first()

            download_song_name = self.string_cleaner(song_name)
            video.download(self.download_folder, filename=download_song_name)

            subprocess.call(['ffmpeg -i ' + self.download_folder + download_song_name + '.mp4 ' + self.download_folder + download_song_name + '.mp3' ], shell=True)

            os.remove(self.download_folder + download_song_name + '.mp4')
            print('Downloaded: ' + song_name)

if __name__ == '__main__':
    test = Downloader()
    test.queue_adder(test.find_songs(test.load_csv()))
    test.queue_downloader()