"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

from requests.api import get
from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash, spotify_ranges, sp
from py4web.utils.url_signer import URLSigner
from . import settings, models
import json

url_signer = URLSigner(session)

# #######################################################
# Helpers
# #######################################################

def get_artist(name):
    results = sp.search(q='artist:' + name, type='artist')
    items = results['artists']['items']
    if len(items) > 0:
        return items[0]
    else:
        return None

# #######################################################
# Actions
# #######################################################

@action('index')
@action.uses(db, auth, 'index.html')
def index():
    return dict()

@action('get_statistics/<range>/<artist_lim:int>/<track_lim:int>/<recent_lim:int>/<genre_lim:int>/<album_lim:int>')
@action.uses(db, auth.user)
def get_statistics(
    range, artist_lim=20, track_lim=50, recent_lim=20,
    genre_lim=20, album_lim=20
):
    """ Generate listening statistics for the given time period and current user.
        See Spotify Web API endpoints for further type information.

        Returns a dictionary containing lists of top_artists (artists items),
        top tracks (tracks items), recent tracks (tracks items),
        top genres (name strings), and top albums (album ids).

        Parameters:
            - range: time period to generate statistics for (see common.py.spotify_ranges for available ranges)
            - limits: amount of each statistic to generate
    """
    statistics = dict()
    assert range in spotify_ranges

    top_artists = sp.current_user_top_artists(time_range=range, limit=artist_lim)
    top_tracks = sp.current_user_top_tracks(time_range=range, limit=track_lim)
    recent_tracks = sp.current_user_recently_played(limit=recent_lim)
    top_genres = []             # genre names
    top_albums = []             # album ids

    genre_frequency = {}        # {genre name, freq}
    album_frequency = {}        # {album id, freq}

    # Get genres of top artists
    for artist_item in top_artists['items']:
        genres = artist_item['genres']
        for genre in genres:
            if genre in genre_frequency:
                genre_frequency[genre] += 1
            else:
                genre_frequency[genre] = 1

    # Get genres and albums (non-singles) for top tracks
    for track_item in top_tracks['items']:
        # Only grab main artist off song, all artists takes too long
        genres = sp.artist(track_item['artists'][0]['id'])['genres']
        for genre in genres:
            if genre in genre_frequency:
                genre_frequency[genre] += 1
            else:
                genre_frequency[genre] = 1
        album = track_item['album']
        if (album['album_type'] == "ALBUM"):  # Not adding singles
            album_id = album['id']
            if album_id in album_frequency:
                album_frequency[album_id] += 1
            else:
                album_frequency[album_id] = 1

    # Take top items from frequency lists and insert into top lists by descending popularity
    top_genres = sorted(genre_frequency, key=genre_frequency.get, reverse=True)
    top_genres = top_genres[0:genre_lim]

    top_albums = sorted(album_frequency, key=album_frequency.get, reverse=True)
    top_albums = top_albums[0:album_lim]

    # Fill stats dictionary with results
    statistics = {
        "artists": top_artists,
        "tracks": top_tracks,
        "recent_tracks": recent_tracks,
        "genres": top_genres,
        "albums": top_albums
    }
    return dict(statistics=statistics)

@action('create_playlist')
@action.uses(db, auth.user)
def create_playlist():
    tids = []
    tracks = sp.current_user_top_tracks(time_range="short_term", limit=20)#request.params.get('top_tracks')
    name = request.params.get('name')
    assert tracks is not None
    for t in tracks['items']:
        tids.append(t['id'])

    if name is None or not name:
        name = "Instant Wrapped Top Tracks"
    user_id = sp.me()['id']
    pid = sp.user_playlist_create(user_id, name)['id']
    sp.playlist_add_items(pid, tids)
    return dict(pid=pid)

@action('post_playlist/<pid>')
@action.uses(db, auth.user)
def post_playlist(pid):
    user_id = models.get_user()
    assert pid is not None and user_id is not None
    models.store_playlist(pid, user_id)
    return dict()

@action('save_playlist/<pid>')
@action.uses(db, auth.user)
def save_playlist(pid):
    sp.current_user_follow_playlist(pid)
    return dict()

@action('load_stats')
@action.uses(db, auth.user)
def load_stats():
    time_range = int(request.params.get('time_range'))
    data = get_statistics(spotify_ranges[time_range])
    json_data = json.loads(data)
    track_data = json_data["statistics"]["tracks"]["items"]
    artist_data = json_data["statistics"]["artists"]["items"]
    rows = {
        "top_tracks": [],
        "top_artists": [],
        "track_rankings":[],
        "artist_rankings": [],
    }
    for a in range(len(track_data)):
        # print(track_data[a]["name"])
        rows["top_tracks"].append(track_data[a]["name"])
        rows["track_rankings"].append(a)
    for b in range(len(artist_data)):
        # print(artist_data[b]["name"])
        rows["top_artists"].append(artist_data[b]["name"])
        rows["artist_rankings"].append(b)
    # for row in rows['track_rankings']:
    #     print(row)
    #     print(rows["top_tracks"][row])
    # print(rows)
    return dict(rows = rows)

@action('dashboard')
@action.uses(db, auth.user, 'dashboard.html')
def dashboard():
    print("User:", models.get_user_email())
    return dict(
        load_stats_url=URL('load_stats', signer=url_signer),
    )

@action('account_mng')
@action.uses(db, auth, 'account_mng.html')
def account_mng():
    print("User:", models.get_user_email())
    return dict()
