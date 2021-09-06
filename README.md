# Spotify Playlist Creation using Running Cadence

## Overviw
This project aims to afasfasa

chagne this A script to create a new playlist of recommended songs that also matches the users running cadence

## Setting up Spotify API

## Downloading your Garmin Data

## Usage
1) Set up your Spotify API.
2) Change credentials.py to work with your credentials.
3) Adjust the username of the cache file on music_data.py, without indicating cache location spotipy often timed out for me (the normal token limit is 1hr unless it refreshes).
4) Run music_data.py which will create two pickle files of the two playlists needed.
5) Download your data from garmin connect and place within the source folder.
6) Work through garmin_data_analysis.ipynb and extract your values for Upper and Lower Cadence (SPM).
7) Work through model_comparison.ipynb to decide which model works best with your data.
8) Input cadence values into playlist_creation.py, as well as adjusting the code for a different model if required, playlist name, etc.
9) Run playlist_creation.py and enjoy the results! Ideally it should help you achieve faster running times, or at least better running form!!!

## Requirements to run:
* Spotify account
* Garmin Connect account
* Install the required libraries below

## Libraries:
* spotipy

## Next Steps:
* Improve ratings system of tracks 
* Create my own recommendation system rather than relying on Spotipys 
* Run more so I can get some more data, aswell as track if the playlist helps improve times
