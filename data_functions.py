import pandas as pd


def get_tracks_df(tracks):
    """
    
    Parameters
    ----------
    tracks : pandas dataframe
        dataframe of a selection of songs from user playlist

    Returns
    -------
    pandas dataframe
        returns same dataframe with new columns and removes unnecessary ones

    """
    tracks_df = pd.DataFrame(tracks)
    if 'track' in tracks_df.columns.tolist():
        tracks_df = tracks_df.drop('track', 1).assign(**tracks_df['track'].apply(pd.Series))
    #Spread track values if not yet spread to columns
    tracks_df['album_id'] = tracks_df['album'].apply(lambda x: x['id'])
    tracks_df['album_artist_id'] = tracks_df['album'].apply(lambda x: x['artists'][0]['id'])
    tracks_df['artist_id'] = tracks_df['artists'].apply(lambda x: x[0]['id'])
    tracks_df['artist_name'] = tracks_df['artists'].apply(lambda x: x[0]['name'])
    select_columns = ['id', 'name', 'popularity', 'type', 'is_local', 
                      'explicit', 'duration_ms', 'artist_id', 'artist_name', 
                      'album_artist_id', 'album_id'
                      ]
    #selects columns of required data
    if 'added_at' in tracks_df.columns.tolist():
        select_columns.append('added_at')
        
    return tracks_df[select_columns]


def get_track_audio_df(sp, df):
    """
    
    Parameters
    ----------
    sp : Spotify OAuth
        used to recieve a token from spotify
    df : pandas dataframe
        dataframe of spotify track data

    Returns
    -------
    df : pandas dataframe
        adds song audio features and artist genres to the dataframe

    """
    df['genres'] = df['artist_id'].apply(lambda x: sp.artist(x)['genres'])
    df['album_genres'] = df['album_artist_id'].apply(lambda x: sp.artist(x)['genres'])
    #genres based on artist
    df['audio_features'] = df['id'].apply(lambda x: sp.audio_features(x))
    df['audio_features'] = df['audio_features'].apply(pd.Series)
    df = df.drop('audio_features', 1).assign(**df['audio_features'].apply(pd.Series))
    #audio features from song eg liveliness, danceability
    return df


def get_all_playlist_tracks_df(sp, sp_call):
    """
    
    Parameters
    ----------
    sp : Spotify OAuth
        used to recieve a token from spotify
    sp_call : list
        recieves from spotify all tracks from users current playlists

    Returns
    -------
    pandas dataframe
        returns same dataframe with new columns and removes unnecessary ones

    """
    playlists = sp_call
    playlist_data, data = playlists['items'], []
    playlist_ids, playlist_names, playlist_tracks = [], [], []
    for playlist in playlist_data:
        for i in range(playlist['tracks']['total']):
            playlist_ids.append(playlist['id'])
            playlist_names.append(playlist['name'])
            playlist_tracks.append(playlist['tracks']['total'])
        saved_tracks = sp.playlist(playlist['id'], fields="tracks, next")
        results = saved_tracks['tracks']
        data.extend(results['items'])
        while results['next']:
            results = sp.next(results)
            data.extend(results['items'])
    #gets playlist ids and tracks from all current user playlists
    tracks_df = pd.DataFrame(data)
    
    tracks_df['playlist_id'] = playlist_ids
    tracks_df['playlist_name'] = playlist_names
    tracks_df['playlist_tracks'] = playlist_tracks
    tracks_df = tracks_df[tracks_df['is_local'] == False]  
    #removes local tracks since they have no audio data
    tracks_df = tracks_df.drop('track', 1).assign(**tracks_df['track'].apply(pd.Series))
    tracks_df['album_id'] = tracks_df['album'].apply(lambda x: x['id'])
    tracks_df['album_artist_id'] = tracks_df['album'].apply(lambda x: x['artists'][0]['id'])
    tracks_df['artist_id'] = tracks_df['artists'].apply(lambda x: x[0]['id'])
    tracks_df['artist_name'] = tracks_df['artists'].apply(lambda x: x[0]['name'])
    select_columns = ['id', 'name', 'popularity', 'type', 'is_local', 
                      'explicit', 'duration_ms', 'artist_id', 'artist_name', 
                      'album_artist_id', 'album_id', 'playlist_id', 
                      'playlist_name', 'playlist_tracks',
                      ]
    return tracks_df[select_columns]


def get_recommendations(sp, tracks):
    """
    
    Parameters
    ----------
    sp : Spotify OAuth
        used to recieve a token from spotify
    tracks : list
        list of 20 spotify song ids per song in selected playlists

    Returns
    -------
    data : pandas dataframe
        list of recommended songs

    """
    data = []
    for x in tracks:
        results = sp.recommendations(seed_tracks=[x]) 
    #default limit of 20 recommendations per song, this can be changed if needed
    #this takes a long time so beneficial to keep amount of songs to minimum
        data.extend(results['tracks'])
    return data
