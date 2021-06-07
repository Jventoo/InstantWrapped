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

from re import M
from requests.api import get, post
from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
from urllib.error import HTTPError
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash, spotify_ranges
from py4web.utils.url_signer import URLSigner
from . import settings, models
import ast
import json
import datetime

url_signer = URLSigner(session)

# #######################################################
# Helpers
# #######################################################

def get_sp():
    # Use refresh token for new sp if expiring (access tokens last one hour)
    if (models.get_time() - db.auth_user[auth.current_user.get('id')]['access_token_creation'] > datetime.timedelta(minutes=50)):
        res = post("https://accounts.spotify.com/api/token", 
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': db.auth_user[auth.current_user.get('id')]['refresh_token'],
            },
            auth=(settings.OAUTH2SPOTIFY_CLIENT_ID, settings.OAUTH2SPOTIFY_CLIENT_SECRET)
        )
        data = res.json()
        db(db.auth_user.id == auth.current_user.get('id')).update(
            access_token=data['access_token'], access_token_creation=models.get_time()
        )
    
    return spotipy.Spotify(auth=db.auth_user[auth.current_user.get('id')]['access_token'])

def get_artist(name):
    sp = get_sp()
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

@action('privacy-policy')
@action.uses(db, auth, 'privacy_policy.html')
def privacyPolicy():
    return dict()

@action('get_statistics/<range>/<artist_lim:int>/<track_lim:int>/<recent_lim:int>/<genre_lim:int>/<album_lim:int>')
@action.uses(db, auth.user)
def get_statistics(
    range, artist_lim=20, track_lim=20, recent_lim=20,
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
    sp = get_sp()

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
            genre = genre.title()
            if genre in genre_frequency:
                genre_frequency[genre] += 1
            else:
                genre_frequency[genre] = 1

    # Get genres and albums (non-singles) for top tracks
    for track_item in top_tracks['items']:
        # Only grab main artist off song, all artists takes too long
        genres = sp.artist(track_item['artists'][0]['id'])['genres']
        for genre in genres:
            genre = genre.title()
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

    # Insert top items into db
    for x, item in enumerate(top_artists['items']):
        models.store_top_artist(
            item['name'], item['id'], x, range
        )
    
    for x, item in enumerate(top_tracks['items']):
        artist_name = item['artists'][0]['name']
        album_name = item['album']['name']

        artist_row = db(db.artist.name == artist_name).select().first()
        if artist_row is None:
            artist_id = db.artist.insert(
                name=artist_name,
                spotify_artist_id=item['artists'][0]['id']
            )
        else:
            artist_id = artist_row.id

        album_row = db(db.album.name == album_name).select().first()
        if album_row is None:
            album_id = db.album.insert(
                artist_id=artist_id,
                name=album_name,
                spotify_album_id=item['album']['id']
            )
        else:
            album_id = album_row.id
        
        models.store_top_song(
            album_id,
            item['name'],
            item['id'],
            x, range
        )

    for x, item in enumerate(top_genres):
        models.store_top_genre(
            item, x, range
        )
    
    for x, item in enumerate(top_albums):
        top_album = sp.album(item)
        artist_name = top_album['artists'][0]['name']

        artist_row = db(db.artist.name == artist_name).select().first()
        if artist_row is None:
            artist_id = db.artist.insert(
                name=artist_name,
                spotify_artist_id=top_album['artists'][0]['id']
            )
        else:
            artist_id = artist_row.id

        models.store_top_album(
            artist_id,
            top_album['name'],
            item,
            x, range
        )

    # Fill stats dictionary with results
    statistics = {
        "artists": top_artists,
        "tracks": top_tracks,
        "recent_tracks": recent_tracks,
        "genres": top_genres,
        "albums": top_albums
    }
    return dict(statistics=statistics)

@action('create_playlist', method = "POST")
@action.uses(db, auth.user)
def create_playlist():
    tids = []
    tracks = request.json.get('top_tracks')
    name = request.json.get('name')
    assert tracks is not None
    for t in tracks:
        tids.append(t['id'])
    if name is None or not name:
        name = "Instant Wrapped Top Tracks"
    sp = get_sp()

    user_id = sp.me()['id']
    pid = sp.user_playlist_create(user_id, name)['id']
    sp.playlist_add_items(pid, tids)
    user_id = models.get_user()
    models.store_playlist(pid, user_id)
    return dict(pid=pid)

@action('post_playlist', method="POST")
@action.uses(db, auth.user)
def post_playlist():
    pid = request.json.get('pid')
    post_status = request.json.get('post_status')
    db((db.user_playlist.user_id == models.get_user()) & (db.user_playlist.spotify_playlist_id == pid)).update(
        leaderboard_display=post_status,
    )
    return "ok"

@action('save_playlist', method='POST')
@action.uses(db, auth.user)
def save_playlist():
    sp = get_sp()
    pid = request.json.get('pid')
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
        track_artist_data = track_data[a]["artists"]
        name = ""
        for j in range(len(track_artist_data)):
            name += track_artist_data[j]["name"] + ", "
        name = name[:-2:]
        rows["top_tracks"].append((track_data[a]["name"], name))
        rows["track_rankings"].append(a)
    for b in range(len(artist_data)):
        rows["top_artists"].append(artist_data[b]["name"])
        rows["artist_rankings"].append(b)
    return dict(rows = rows, top_tracks = track_data)

@action('dashboard')
@action.uses(db, auth.user, 'dashboard.html')
def dashboard():
    return dict(
        load_stats_url=URL('load_stats', signer=url_signer),
        create_playlist_url=URL('create_playlist', signer=url_signer),
        post_playlist_url=URL('post_playlist', signer=url_signer),
    )

@action('update_profile', method='POST')
@action.uses(db, auth.user)
def update_profile():
    return dict()

@action('load_profile/<user_id:int>', method='GET')
@action.uses(db, auth.user)
def get_profile(user_id):
    # CONSTANTS
    num_songs = 5
    num_artists = 5
    num_genres = 5

    uid = user_id
    assert uid is not None

    name = db.auth_user[uid]['username']
    picture = db.auth_user[uid]['profile_picture']
    bio = db.auth_user[uid]['biography']

    songs = db(
        (db.user_top_song.user_id == uid) & (db.user_top_song.user_timespan == spotify_ranges[2])
    ).select(orderby=db.user_top_song.user_position).as_list()
    songs = songs[0:num_songs]
    for song in songs:
        temp = db(db.song.id == song["song_id"]).select().first()
        if temp is None:
            song["song_name"] = "None Type"
        else:
            song["song_name"] = temp.name


    artists = db(
        (db.user_top_artist.user_id == uid) & (db.user_top_artist.user_timespan == spotify_ranges[2])
    ).select(orderby=db.user_top_artist.user_position).as_list()
    artists = artists[0:num_artists]
    for artist in artists:
        temp = db(db.artist.id == artist["artist_id"]).select().first()
        if temp is None:
            artist["artist_name"] = "None Type"
        else:
            artist["artist_name"] = temp.name


    genres = db(
        (db.user_top_genre.user_id == uid) & (db.user_top_genre.user_timespan == spotify_ranges[2])
    ).select(orderby=db.user_top_genre.user_position).as_list()
    genres = genres[0:num_genres]
    for genre in genres:
        temp = db(db.genre.id == genre["genre_id"]).select().first()
        if temp is None:
            genre["genre_name"] = "None Type"
        else:
            genre["genre_name"] = temp.name

    pls = db(db.user_playlist.user_id == uid).select(orderby=db.user_playlist.rate_score).as_list()
    sp = get_sp()
    for pl in pls:
        try:
            playlist = sp.playlist(pl["spotify_playlist_id"])
            pName = playlist["name"]
            pl["playlist_name"] = pName
            playlist_id = db(db.user_playlist.spotify_playlist_id == pl["spotify_playlist_id"]).select().first()
            pl["playlist_url"] = URL('view_playlist', playlist_id["id"])
        except:
            continue

    follow_row = db(
        (db.followers.followee == uid) & (db.followers.follower == models.get_user())
    ).select().first()
    is_following = (follow_row is not None)

    followers_count = len(db(db.followers.followee == uid).select().as_list())
    following_count = len(db(db.followers.follower == uid).select().as_list())

    followers_url = URL ('view_followers', uid)
    return dict(
        user_id=uid, current_user=models.get_user(), followers_url = followers_url, user_name=name,
        user_picture=picture, biography=bio, top_songs=songs,
        top_artists=artists, top_genres=genres, playlists=pls,
        following=is_following,num_followers=followers_count,
        num_following=following_count
    )

@action('find_matches', method='GET')
@action.uses(db, auth.user)
def get_matches():
    return dict()

@action('view_user_profile/<user_id:int>')
@action.uses(db, auth.user, 'view_user_profile.html')
def dashboard(user_id):
    return dict(
        load_profile_url=URL('load_profile', user_id),
        load_stats_url=URL('load_stats', signer=url_signer),
        add_comment_url=URL('add_profile_comment', user_id, signer=url_signer),
        load_comments_url=URL('load_profile_comments', user_id),
        delete_comment_url = URL('delete_profile_comment', signer=url_signer),
        start_follow_url = URL('start_following', signer=url_signer),
        stop_follow_url = URL('stop_following', signer=url_signer),
    )

@action('load_leaderboard')
@action.uses(db, auth.user)
def load_leaderboard():
    sp = get_sp()
    rows = db(db.user_playlist.leaderboard_display == 1).select().as_list()
    for row in rows:
        r = db(db.auth_user.id == row["user_id"]).select().first()
        row["playlist_author"] = r.username
        row["author_id"] = r.id
        playlist = sp.playlist(row["spotify_playlist_id"])
        pName = playlist["name"]
        row["playlist_name"] = pName
        playlist_id = db(db.user_playlist.spotify_playlist_id == row["spotify_playlist_id"] ).select().first()
        row["playlist_url"] = URL('view_playlist', playlist_id["id"])
        row["author_url"] = URL('view_user_profile', r.id)
    rows2 = sorted(rows, key=lambda i: i['rate_score'],reverse=True)
    return dict(rows = rows2, current_user=models.get_user())

@action('load_matches')
@action.uses(db, auth.user, url_signer.verify())
def load_matches():
    user_lim = 5               # CONSTANT
    uid = models.get_user()
    assert uid is not None
    
    user_frequency = {}        # {user id, freq}
    top_genres = db(db.user_top_genre.user_id == uid).select().as_list()

    # Find similar users based on top genres
    for top_entry in top_genres:
        genre_id = top_entry['genre_id']
        rows = db(
            (db.user_top_genre.genre_id == genre_id) & (db.user_top_genre.user_id != uid)
        ).select().as_list()
        for row in rows:
            user = row['user_id']
            if user in user_frequency:
                user_frequency[user] += 1
            else:
                user_frequency[user] = 1

    # Take top users from frequency list and insert into top list by descending matching
    top_user_ids = sorted(user_frequency, key=user_frequency.get, reverse=True)

    top_users = []
    for i in range(user_lim):
        if i >= len(top_user_ids):
            break
        id = top_user_ids[i]
        username = db.auth_user[top_user_ids[i]].username
        picture = db.auth_user[top_user_ids[i]].profile_picture
        profile_url = URL('view_user_profile', id)
        top_users.append((id, username, picture, profile_url))

    return dict(top_users=top_users)

@action('upvote', method='POST')
@action.uses(url_signer.verify(), db)
def upvote():
    playlist_id = request.json.get('playlist_id')
    upvote_status = request.json.get('upvote_status')
    new_score = request.json.get('new_score')
    assert playlist_id is not None and upvote_status is not None
    
    db.playlist_upvote.update_or_insert(
        ((db.playlist_upvote.playlist_id == playlist_id) & (db.playlist_upvote.rater == models.get_user())),
        playlist_id=playlist_id,
        rater=models.get_user(),
        upvote=upvote_status,
    )

    db(db.user_playlist.id == playlist_id).update(
        rate_score = new_score,
    )
    return "ok"

@action('get_rating')
@action.uses(url_signer.verify(), db)
def get_rating():
    playlist_id = request.params.get('playlist_id')
    row = db((db.playlist_upvote.playlist_id == playlist_id) &
             (db.playlist_upvote.rater == models.get_user())).select().first()
    upvote_status = row.upvote if row is not None else 0
    temp = db(db.user_playlist.id == playlist_id).select().first()
    current_score = temp.rate_score
    return dict(upvote_status=upvote_status, current_score = current_score)


@action('leaderboard')
@action.uses(db, auth.user, 'leaderboard.html')
def leaderboard():
    return dict(
        load_leaderboard_url=URL('load_leaderboard'),
        upvote_url=URL('upvote', signer=url_signer),
        get_rating_url=URL('get_rating', signer=url_signer),
        save_playlist_url=URL('save_playlist', signer=url_signer),
        load_matches_url=URL('load_matches', signer=url_signer),
    )

@action('load_playlist/<playlist_id:int>')
@action.uses(db, auth.user)
def load_playlist(playlist_id):
    sp = get_sp()
    
    current_user = models.get_user()
    temp = db(db.user_playlist.id == playlist_id).select().first()
    playlist_owner = temp["user_id"]
    playlist_author_url = URL('view_user_profile', playlist_owner)
    playlist_owner_name = db(db.auth_user.id == playlist_owner).select().first().username
    currently_displayed = temp["leaderboard_display"]
    pid = temp["spotify_playlist_id"]
    rows = {
        "tracks": [],
        "authors": [],
    }

    temp2 = sp.playlist(temp["spotify_playlist_id"])
    playlist_name = temp2["name"]
    pl_pic = temp2["images"][1]["url"]
    pl_link = temp2["external_urls"]["spotify"]
    track_data = temp2["tracks"]["items"]
    for i in range(len(track_data)):
        rows["tracks"].append(track_data[i]["track"]["name"])
        artist_data = track_data[i]["track"]["artists"]
        name = ""
        for j in range(len(artist_data)):
            name += artist_data[j]["name"] + ", "
        name = name[:-2:]
        rows["authors"].append(name)
    return dict(
        rows = rows, playlist_author_url = playlist_author_url, current_user = current_user, playlist_picture = pl_pic, playlist_link = pl_link,
        playlist_owner = playlist_owner, playlist_owner_name = playlist_owner_name, 
        currently_displayed = currently_displayed, pid = pid, playlist_name=playlist_name
        )

@action('view_playlist/<playlist_id:int>')
@action.uses(db, auth.user, 'view_playlist.html')
def view_playlist(playlist_id):
    return dict(
        load_playlist_url=URL('load_playlist', playlist_id),
        post_playlist_url=URL('post_playlist', signer=url_signer),
        add_comment_url=URL('add_comment', playlist_id, signer=url_signer),
        load_comments_url=URL('load_comments', playlist_id),
        delete_comment_url = URL('delete_comment', signer=url_signer),
        add_reply_url=URL('add_reply', signer=url_signer),
        load_replies_url=URL('load_replies'),
        delete_reply_url=URL('delete_reply', signer=url_signer),
    )

@action('add_comment/<playlist_id:int>', method="POST")
@action.uses(db, auth.user, url_signer.verify())
def add_comment(playlist_id):
    r = db(db.auth_user.id == models.get_user()).select().first()
    id = db.comments.insert(
        playlist_id = playlist_id, 
        comment_author = models.get_user(),
        comment_txt = request.json.get('comment_txt'),
    )
    name = r.username
    author_url = URL('view_user_profile', r.id)
    return dict(id=id, author=name, current_user_name = name, author_url=author_url)

@action('load_comments/<playlist_id:int>')
@action.uses(db, auth.user)
def load_comments(playlist_id):
    comments = db(db.comments.playlist_id == playlist_id).select().as_list()
    temp = db(db.auth_user.id == models.get_user()).select().first()
    current_user_name = temp.username
    for comment in comments:
        r = db(db.auth_user.id == comment["comment_author"]).select().first()
        comment["author_name"] = r.username
        comment["author_url"] = URL('view_user_profile', r.id)
    return dict(comments=comments, current_user_name = current_user_name)

@action('delete_comment')
@action.uses(url_signer.verify(), db)
def delete_post():
    id = request.params.get('id')
    assert id is not None
    db(db.comments.id == id).delete()
    return "ok"

@action('add_reply', method="POST")
@action.uses(db, auth.user, url_signer.verify())
def add_reply():
    r = db(db.auth_user.id == models.get_user()).select().first()
    id = db.replies.insert(
        comment_id = request.json.get('comment_id'),
        reply_author = models.get_user(),
        reply_txt=request.json.get('reply_txt'), 
    )
    name = r.username
    return dict(id=id, author=name, current_user_name = name)


@action('load_replies')
@action.uses(db, auth.user)
def load_replies():
    comment_id = request.params.get('comment_id')
    replies = db(db.replies.comment_id == comment_id).select().as_list()
    temp = db(db.auth_user.id == models.get_user()).select().first()
    current_user_name = temp.username
    for reply in replies:
        r = db(db.auth_user.id == reply["reply_author"]).select().first()
        reply["author_name"] = r.username
        reply["author_url"] = URL('view_user_profile', r.id)
    return dict(replies=replies, current_user_name = current_user_name)

@action('delete_reply')
@action.uses(url_signer.verify(), db)
def delete_post():
    id = request.params.get('id')
    assert id is not None
    db(db.replies.id == id).delete()
    return "ok"

@action('add_profile_comment/<uid:int>', method="POST")
@action.uses(db, auth.user, url_signer.verify())
def add_comment(uid):
    r = db(db.auth_user.id == models.get_user()).select().first()
    id = db.profile_comments.insert(
        comment_author = models.get_user(),
        profile_id = uid, 
        comment_txt = request.json.get('comment_txt'),
    )
    name = r.username
    author_url = URL('view_user_profile', r.id)
    return dict(id=id, author=name, current_user_name = name, author_url=author_url)

@action('load_profile_comments/<uid:int>')
@action.uses(db, auth.user)
def load_comments(uid):
    assert uid is not None
    comments = db(db.profile_comments.profile_id == uid).select().as_list()
    temp = db(db.auth_user.id == models.get_user()).select().first()
    current_user_name = temp.username
    for comment in comments:
        r = db(db.auth_user.id == comment["comment_author"]).select().first()
        comment["author_name"] = r.username
        comment["author_url"] = URL('view_user_profile', r.id)
    return dict(comments=comments, current_user_name = current_user_name)

@action('delete_profile_comment')
@action.uses(url_signer.verify(), db)
def delete_post():
    id = request.params.get('id')
    assert id is not None
    db(db.profile_comments.id == id).delete()
    return "ok"

@action('view_followers/<user_id:int>')
@action.uses(db, auth.user, 'view_followers.html')
def view_followers(user_id):
    return dict(
        load_followers_url=URL('load_followers', user_id),
    )

@action('load_followers/<user_id:int>', method="GET")
@action.uses(db, auth.user)
def load_followers(user_id):
    assert user_id is not None

    follower_rows = db(db.followers.followee == user_id).select().as_list()
    follower_names = []
    for entry in follower_rows:
        temp_follower = db(db.auth_user.id == entry['follower']).select().first()
        follower_url = URL('view_user_profile', temp_follower.id)
        follower_names.append((temp_follower.id, temp_follower.username, temp_follower.profile_picture, follower_url))

    following_rows = db(db.followers.follower == user_id).select().as_list()
    following_names = []
    for entry in following_rows:
        temp_following = db(db.auth_user.id == entry['followee']).select().first()
        following_url = URL('view_user_profile', temp_following.id)
        following_names.append((temp_following.id, temp_following.username, temp_following.profile_picture, following_url))

    profile_url = URL('view_user_profile', user_id)
    temp = db(db.auth_user.id == user_id).select().first()
    username = temp.username
    return dict(followers=follower_names, following=following_names,
        user_id=user_id, username=username, profile_url = profile_url)

@action('start_following', method="POST")
@action.uses(db, auth.user, url_signer.verify())
def start_following():
    user_id = request.params.get('user_id')
    assert user_id is not None
    db.followers.update_or_insert(follower=models.get_user(),followee=user_id)
    return dict()

@action('stop_following', method="POST")
@action.uses(db, auth.user, url_signer.verify())
def stop_following():
    user_id = request.params.get('user_id')
    assert user_id is not None
    db(
        (db.followers.follower == models.get_user()) & (db.followers.followee == user_id)
    ).delete()
    return "ok"