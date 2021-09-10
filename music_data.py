import spotipy, spotify_credentials

import spotipy.util as util

from spotipy.oauth2 import SpotifyOAuth
from data_functions import get_tracks_df, get_track_audio_df,\
    get_all_playlist_tracks_df, get_recommendations


client_id = spotify_credentials.client_id
client_secret = spotify_credentials.client_secret
username = spotify_credentials.username
scope = "user-library-read user-follow-read user-top-read playlist-read-private"
redirect_uri = spotify_credentials.redirect_uri


sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
))

token = util.prompt_for_user_token(username, scope, client_id, client_secret, 
                                   redirect_uri, cache_path='./.cache-<YOUR_USERNAME>')
if token:
    sp = spotipy.Spotify(auth=token)
else:
    print("Can't get token for", username)


print("Getting, transforming, and saving playlist track data...")
playlist_tracks_df = get_all_playlist_tracks_df(sp, sp.current_user_playlists())  
#spotipy limits sp.user_playlists to 50 playlists
print("My Playlist Tracks First Stage Done")
playlist_tracks_df = get_track_audio_df(sp, playlist_tracks_df)
print("My Playlist Tracks Second Stage Done")
playlist_tracks_df.to_pickle("./playlist_tracks_new.pkl")


print("Getting, transforming, and saving tracks recommendations...")
recommendation_tracks = get_recommendations\
    (sp, playlist_tracks_df[playlist_tracks_df['playlist_name'].isin(
    ["Runmanting", "N e u r o"
      ])].drop_duplicates(subset='id', keep="first")['id'].tolist())
#define sample playlists to yield tracks to get recommendations for, 20 
#recommendations per track by default
#change these to your playlists, it takes a long time so I kept mine to a minimum   
print("Recommendation Tracks First Stage Done")
recommendation_tracks_df = get_tracks_df(recommendation_tracks)
print("Recommendation Tracks Second Stage Done")
recommendation_tracks_df = get_track_audio_df(sp, recommendation_tracks_df)
recommendation_tracks_df.to_pickle("./recommendation_tracks_new.pkl")
