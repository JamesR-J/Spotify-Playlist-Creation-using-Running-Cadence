# Spotify Playlist Creation using Running Cadence

## Overview
As a runner I always aim for a new PB. Recently I have felt I have reached a plateaux so want to create some tools to help me train. Using ML in my own project is v cool.
Combined with the fact I am delving into the world of bare foot shoes it is important that I improve my running cadence and form. This Spotify playlist creation script hopes to help that!

It will create a new music playlist based from your current playlists, with your favourite playlists (I used my current runningesque playlist) to influence the decision of the new songs. 4 common ML models are compared to find the best one to predict the most likeable music. 

Using the Garmin Data to gather average cadence 
This project aims to afasfasa

chagne this A script to create a new playlist of recommended songs that also matches the users running cadence

## Setting up Spotify API
To get Spotify data you firstly need to go to this link and create an app:

[https://developer.spotify.com/dashboard/](https://developer.spotify.com/dashboard/)

I named mine Test but what you call it shouldn't matter so long as the word Spotify is not included.

You then have to set a Redirect URL. From the developer apps panel click on 'Edit Settings' and add the required link under Redirect URLS. I used:

    "http://localhost:8889/callback/"
    
 Jupyter was using localhost:8888 but if :8889 is busy just set it to another number that is free. On your app page also note down the client ID and client Secret. To get your Spotify username, open up Spotify and navigate to your Account webpage via clicking on your profile name on the top right drop down menu, and your username should be listed there.
 
 Input all these details into the spotify_credentials.py and you should be ready to go !!

## Downloading your Garmin Data
To get Garmin Data I found this script to work the best for my data requirements:

[garmin-connect-export script](https://github.com/pe-st/garmin-connect-export/)

Either clone the repo from git or download the zip file on the downloads page.

Using the command line, set your current directory to where the file is and then run this prompt:

    python gcexport.py --count all

`--count all` downloads all your activities for you, if you don't require all the data check the link for alternatives

## Usage
1) Set up your Spotify API.
2) Change spotify_credentials.py to work with your credentials.
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
