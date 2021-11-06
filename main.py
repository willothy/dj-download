import downloader as DJ
import getopt, sys

# Remove 1st argument from the
# list of command line arguments
argumentList = sys.argv[1:]
 
# Options
options = "hc:s:m:"
 
# Long options
long_options = [""]
 
try:
    # Parsing argument
    arguments, values = getopt.getopt(argumentList, options, long_options)
     
    # checking each argument
    for currentArgument, currentValue in arguments:
             
        # help
        if currentArgument in ("-h"):
            print("Help: use -c <filename.csv> to download csv; use -s <spotify playlist id> to download playlist; use -m '<song name>,<artist name>' to download one song manually (artist name param optional);")

        # csv
        elif currentArgument in ("-c"):
            runner = DJ.Downloader()
            print("Downloading from " + currentValue)
            runner.queue_adder(runner.find_songs(runner.load_csv(currentValue)))
            runner.queue_downloader()
        
        # spotify
        elif currentArgument in ("-s"):
            print("Authenticating Spotify user")
            runner = DJ.Downloader()
            runner.spotify_auth()
            print("Downloading playlist ID " + currentValue)
            runner.queue_adder(runner.find_songs(runner.spotify_song_list_playlist(currentValue)))
            runner.queue_downloader()

        elif currentArgument in ("-m"):
            song_list = []

            if ',' in currentValue:
                song_name, song_artist = currentValue.split(',')
                song_list.append((song_name, song_artist))
            else:
                song_name = currentArgument
                song_list.append((song_name, ''))

            runner = DJ.Downloader()
            runner.spotify_auth()
            print("Downloading " + song_name)
            runner.queue_adder(runner.find_songs(song_list))
            runner.queue_downloader()
             
except getopt.error as err:
    # output error, and return with an error code
    print (str(err))