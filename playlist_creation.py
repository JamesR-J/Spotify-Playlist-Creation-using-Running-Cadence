import spotipy
import spotify_credentials

import pandas as pd
import spotipy.util as util

from spotipy.oauth2 import SpotifyOAuth
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.metrics import classification_report
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE


client_id = spotify_credentials.client_id
client_secret = spotify_credentials.client_secret
username = spotify_credentials.username
scope = "user-library-read user-follow-read user-top-read \
    playlist-read-private playlist-modify-public"
redirect_uri = spotify_credentials.redirect_uri

                                                      
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
))

token = util.prompt_for_user_token(username, scope, 
                                   client_id, client_secret, redirect_uri, 
                                   cache_path='./.cache-1129915706')
if token:
    sp = spotipy.Spotify(auth=token)
else:
    print("Can't get token for", username)
    

playlist_tracks_df = pd.read_pickle("./playlist_tracks.pkl")
recommendation_tracks_df = pd.read_pickle("./recommendation_tracks.pkl")
playlist_fav = ["Runmanting", "Hardcore", "N e u r o", 
                "OLD  P O P", "RnB - Fast and Furious vviiibbeess"]
#List of similar running playlists used to set song ratings
#change these to your running playlists
GARMIN_DATA_DIR = \
    './garmin-connect-export-3.2.1/2021-09-01_garmin_connect_export/activities.csv'


def remove_duplicates(playlist_df, recommendation_df):    
    """
    
    Parameters
    ----------
    playlist_df : pandas dataframe
        dataframe of songs from 50 or less of current users playlists
    recommendation_df : pandas dataframe
        this is a datagrame made from 20 spotify recommendations of each song 
        in playlist_fav

    Returns
    -------
    playlist_df : pandas dataframe
        new dataframe with no same songs as recommendation_df to stop data
        leakage
    recommendation_df : pandas dataframe
        new dataframe with no same songs as playlist_df

    """
    playlist_df = playlist_df.drop_duplicates(subset='id', 
                                              keep="first").reset_index()
    recommendation_df = recommendation_df.drop_duplicates\
        (subset='id', keep="first").reset_index()
    recommendation_df = recommendation_df\
        [~recommendation_df['id'].isin(playlist_df['id'].tolist())]
    
    return playlist_df, recommendation_df


def get_fave_playlist_ids(username, playlist_fav):
    """
    
    Parameters
    ----------
    username : string
        string of current users spotify username
    playlist_fav : list
        list of favourite playlist names set by user

    Returns
    -------
    playlist_fav_ids : list
        list of playlist IDs from favourite playlist names

    """
    playlist_fav_ids = []
    playlists = sp.current_user_playlists()
    
    playlist_data = playlists['items']
    playlist_ids = []
    for playlist in playlist_data:
        for i in range(playlist['tracks']['total']):
            playlist_ids.append(playlist['id'])
    playlist_ids = list(dict.fromkeys(playlist_ids))
    
    playlists = sp.user_playlists(username)
    names = [playlist['name'] for playlist in playlists['items']]
    for i in range(len(names)):
        if names[i] in playlist_fav:
            playlist_fav_ids.append(playlist_ids[i])
    
    return playlist_fav_ids


def create_ratings(playlist_df, playlist_fav_ids):
    """
    
    Parameters
    ----------
    playlist_df : pandas dataframe
        dataframe of current users playlists
    playlist_fav_ids : list
        list of playlist IDs of favourite playlists set by user

    Returns
    -------
    playlist_df : pandas dataframe
        adds rating for 1 if song in playlist_fav_ids, otherwise is a 0

    """
    playlist_df['ratings'] = playlist_df['playlist_id'].apply\
        (lambda x: 1 if x in playlist_fav_ids else 0)
    
    return playlist_df


def define_train_test_data(playlist_df, recommendation_df):
    """
    
    Parameters
    ----------
    playlist_df : pands dataframe
        dataframe of current users tracks with added ratings
    recommendation_df : pandas dataframe
        dataframe of 20 tracks recommended by spotify for some input tracks

    Returns
    -------
    X_recommend : pandas dataframe
        songs from recommendation dataframe which will be fed into ML model
        for it to predict songs for new playlist
    X_train_os : pandas dataframe
        Oversampled X training subset for model
    X_test : pandas dataframe
        X testing subset for model
    y_train_os : pandas dataframe
        Oversampled y training subset for model
    y_test : pandas dataframe
        y testing subset for model
    recommendation_df : pandas dataframe
        new dataframe with rows dropped with no value

    """
    X = playlist_df[['popularity', 'explicit', 'duration_ms', 'danceability', 
                     'energy', 'key', 'loudness', 'mode', 'speechiness', 
                     'acousticness', 'instrumentalness', 'liveness', 'valence',
                     'tempo', 'time_signature', 'genres']] 
    #chosen features to help predict new songs
    y = playlist_df['ratings']
    #training data

    X = X.dropna()
    recommendation_df = recommendation_df.dropna()
    #drops empty rows
    
    X = X.drop('genres', 1).join(X['genres'].str.join('|').str.get_dummies())
    X_recommend = recommendation_df.copy()
    X_recommend = X_recommend.drop('genres', 1).\
        join(X_recommend['genres'].str.join('|').str.get_dummies())
    #create genre columns (one-hot encoding)
    
    
    X = X[X.columns.intersection(X_recommend.columns)]
    X_recommend = X_recommend[X_recommend.columns.intersection(X.columns)]
    #ensures features are consistent across training, test, and evaluation
    
    X_train, X_test, y_train, y_test = train_test_split(X, 
                                                        y, 
                                                        test_size=0.2, 
                                                        random_state=42)
    
    oversample = SMOTE(random_state=42)
    X_train_os, y_train_os = oversample.fit_resample(X_train, y_train)
    #oversampling since big disparity in training labels
    #no oversampling on training data, oversampling can lead to false generalisation
    
    return X_recommend, X_train_os, X_test, y_train_os, y_test, recommendation_df


def RandomForest_classification(X_train, y_train, X_test, y_test):
    """
    
    Parameters
    ----------
    X_train : pandas dataframe
        X training subset for model
    y_train : pandas dataframe
        y training subset for model
    X_test : pandas dataframe
        X testing subset for model
    y_test : pandas dataframe
        y testing subset for model

    Returns
    -------
    rfc_gcv : ML model
        grid searched random forest classifier used to predict song rating

    """
    rfc = RandomForestClassifier(n_estimators = 1000, random_state=42)
    rfc_gcv_parameters = {'min_samples_leaf': [1, 3, 5, 8], 
                          'max_depth': [3, 4, 5, 8, 12, 16, 20], 
                         }
    rfc_gcv = GridSearchCV(rfc, 
                           rfc_gcv_parameters, 
                           n_jobs=-1, 
                           cv=StratifiedKFold(2), 
                           verbose=1, 
                           scoring='roc_auc')
    rfc_gcv.fit(X_train, y_train)
    rfc_gcv.best_estimator_, rfc_gcv.best_score_
    print(classification_report(y_test, rfc_gcv.predict(X_test)))
    
    return rfc_gcv


def import_garmin_data(garmin_dir, running_speed, max_offseter = 5):
    """
    
    Parameters
    ----------
    garmin_dir : string
        directory pointing towards location of garmin data .CSV file
    running_speed : int
        user input running seed to find optimal cadence
    max_offseter : int, optional
        value to achieve a higher cadence to inspire the user
        to run faster. The default is 5.

    Returns
    -------
    lower_spm : int
        lower threshold for running cadence
    upper_spm : int
        higher threshold for running cadence

    """
    df_activities = pd.read_csv(garmin_dir)
    df_running = df_activities[df_activities['Activity Type'] == 'Running']
    #filters out just running acitivities, since there are others ie cycling
    df_running_speed = df_running.sort_values('Average Moving Speed (km/h or min/km)')
    df_running_speed_optimal = df_running_speed\
        [(df_running_speed['Average Moving Speed (km/h or min/km)'] \
          <= running_speed) & (df_running_speed['Avg. Run Cadence'] >= 165)]
    #finds cadence of runs that are faster than set time
    #also due to innacurate cadence measurement the greater than 165 helps
    #prevent outliers
    lower_spm = int(df_running_speed_optimal['Avg. Run Cadence'].min())
    upper_spm = int(df_running_speed_optimal['Avg. Run Cadence'].max()) + max_offseter
    #offset added so that user can aim for a faster cadence
    
    print('{}: Lower Cadence Limit (SPM)'.format(lower_spm))
    print('{}: Upper Cadence Limit (SPM)'.format(upper_spm))
    return lower_spm, upper_spm


def predict(recommendation_df,xgb_gcv,X_recommend,prob_rating,lower_spm,upper_spm):
    """
    
    Parameters
    ----------
    recommendation_df : pandas dataframe
        dataframe of 20 recommended songs per song in user playlist
    xgb_gcv : ML model
        optimal model used to predict what rating a song in recommendation 
        playlist achieves
    X_recommend : pandas dataframe
        songs from recommendation dataframe which will be fed into ML model
        for it to recommend songs for new playlist
    prob_rating : int
        lower threshold that dictates a rating above that value makes the cut 
        and is added to the new playlist
    lower_spm : int
        lowest running cadence that then becomes lower threshold for bpm for
        songs to be added to the new playlist
    upper_spm : int
        highest running cadence that then becomes higher threshold for bpm for
        songs to be added to the new playlist

    Returns
    -------
    bpm_tracks_to_add : list
        list of track IDs that the model predicts the user will like, aswell 
        as being in the acceptable bpm range, to then be added to new playlist

    """
    recommendation_df.loc[:, 'ratings'] = xgb_gcv.predict(X_recommend)
    recommendation_df.loc[:,'prob_ratings'] = xgb_gcv.predict_proba(X_recommend)[:,1]  
    tracks_to_add_df = recommendation_df[recommendation_df['prob_ratings'] >= prob_rating]
    bpm_tracks_to_add_df = tracks_to_add_df\
        [((tracks_to_add_df['tempo'] <= upper_spm) & \
          (tracks_to_add_df['tempo'] >= lower_spm)) | \
         ((tracks_to_add_df['tempo'] <= upper_spm/2) & \
          (tracks_to_add_df['tempo'] >= lower_spm/2))]
    #chooses tracks to add within cadence bpm allowance, also allows songs of 
    #"half time" tempo
    bpm_tracks_to_add = bpm_tracks_to_add_df['id']

    print('{} Tracks to Add'.format(len(bpm_tracks_to_add)))
    return bpm_tracks_to_add


def add_tracks_to_playlist(sp, username, tracks_to_add, playlist_name): 
    """

    Parameters
    ----------
    sp : Spotify Oauth
        is required to achieve a token from spotify
    username : string
        string of current users spotify username
    tracks_to_add : list
        list of track IDs that the model predicts the user will like, aswell 
        as being in the acceptable bpm range, to then be added to new playlist
    playlist_name : string
        chosen name of the new playlist

    Returns
    -------
    None.

    """
    playlists = sp.user_playlists(username)
    names = [playlist['name'] for playlist in playlists['items']]
    if playlist_name not in names:
        new_playlist = sp.user_playlist_create(user=username, 
                                               name=playlist_name,
                                               public=True, 
                                               collaborative=False, 
                                               description="Created using \
                                                   Python and Scikit mmm mmmm",
                                               )
        print('Created {} Playlist'.format(playlist_name))
    elif playlist_name in names:
        new_playlist = playlists['items'][names.index(playlist_name)]
        print('{} already exists'.format(playlist_name))    
    #creates playlist if a playlist of that name does not already exist
    
    for id in tracks_to_add:
        sp.user_playlist_add_tracks(user=username, 
                                    playlist_id=new_playlist['id'], 
                                    tracks=[id],
                                   )
        

def main():
    df1, df2 = remove_duplicates(playlist_tracks_df, recommendation_tracks_df)
    playlist_fav_ids = get_fave_playlist_ids(username, playlist_fav)
    df3 = create_ratings(df1, playlist_fav_ids)
    X_recommend, X_train, X_test, y_train, y_test, df4 = define_train_test_data(df3, df2)
    rfc_gcv = RandomForest_classification(X_train, y_train, X_test, y_test)
    lower_spm, upper_spm = import_garmin_data(GARMIN_DATA_DIR, '04:10')
    tracks_to_add = predict(df4, rfc_gcv, X_recommend, 0.8, lower_spm, upper_spm)
    add_tracks_to_playlist\
        (sp, username, tracks_to_add, 'ML Running Playlist BPM Adjusted')
    

if __name__ == "__main__":
    main()