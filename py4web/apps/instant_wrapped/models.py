"""
This file defines the database models

All spotify IDs are base-62 numbers supplied by Spotify URIs
that identify an artist, track, album, etc.
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_user():
    return db(
        db.auth_user.email == get_user_email()
    ).select().first().id if auth.current_user else None
    # return auth.current_user if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()

def store_top_genre():
    ## Check if genre already exists in database. If not, create it. Store it in db.
    ## Create user_top_genree entry
    return

def store_top_artist():
    return

def store_top_album():
    return

def store_top_song():
    return

def store_playlist(pid, uid):
    db.user_playlist.insert(
        user_id=uid,
        spotify_playlist_id=pid,
    )
    return

def store_review():
    return

db.auth_user.id.readable = db.auth_user.id.writable = False

db.define_table(
    'genre',
    Field('name', requires=IS_NOT_EMPTY()),
)

db.define_table(
    'artist',
    Field('genre_id', 'reference genre'),
    Field('name', requires=IS_NOT_EMPTY()),
    Field('spotify_artist_id', requires=IS_NOT_EMPTY()),
    Field('leaderboard_pos', 'integer'),
)

db.define_table(
    'album',
    Field('artist_id', 'reference artist'),
    Field('name', requires=IS_NOT_EMPTY()),
    Field('spotify_album_id', requires=IS_NOT_EMPTY()),
    Field('leaderboard_pos', 'integer'),
)

db.define_table(
    'song',
    Field('album_id', 'reference album'),
    Field('name', requires=IS_NOT_EMPTY()),
    Field('spotify_song_id', requires=IS_NOT_EMPTY()),
    Field('leaderboard_pos', 'integer'),
)

db.define_table(
    'user_top_genre',
    Field('genre_id', 'reference genre'),
    Field('user_id', 'reference auth_user'),
    Field('user_position', 'integer', requires=IS_NOT_EMPTY()),
    Field('user_timespan', requires=IS_NOT_EMPTY()),
)

db.define_table(
    'user_top_artist',
    Field('artist_id', 'reference artist'),
    Field('user_id', 'reference auth_user'),
    Field('user_position', 'integer', requires=IS_NOT_EMPTY()),
    Field('user_timespan', requires=IS_NOT_EMPTY()),
)

db.define_table(
    'user_top_album',
    Field('album_id', 'reference album'),
    Field('user_id', 'reference auth_user'),
    Field('user_position', 'integer', requires=IS_NOT_EMPTY()),
    Field('user_timespan', requires=IS_NOT_EMPTY()),
)

db.define_table(
    'user_top_song',
    Field('song_id', 'reference song'),
    Field('user_id', 'reference auth_user'),
    Field('user_position', 'integer', requires=IS_NOT_EMPTY()),
    Field('user_timespan', requires=IS_NOT_EMPTY()),
)

db.define_table(
    'user_playlist',
    Field('user_id', 'reference auth_user'),
    Field('spotify_playlist_id', requires=IS_NOT_EMPTY()),
)

# Not sure how best to have review DB entry work for any type
# of resource (track, album, artist, etc) so I just added a field
# for Spotify ID and we can look up what type of resource it is at
# runtime. Not very accessible for our DB but I couldn't think of
# another way with how references work.
db.define_table(
    'review',
    Field('user_id', 'reference auth_user'),
    Field('spotify_id', requires=IS_NOT_EMPTY()),
    Field('description', 'text', requires=IS_NOT_EMPTY()),
)

db.commit()
