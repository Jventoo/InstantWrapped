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

def get_time():
    return datetime.datetime.utcnow()

db.define_table(
    'user',
    Field('username', requires=IS_NOT_EMPTY()),
    Field('spotify_id', requires=[IS_NOT_EMPTY()]),
    Field('user_email', default=get_user_email),
)

db.user.id.readable = db.user.id.writable = False
db.user.user_email.readable = db.user.user_email.writable = False

db.define_table(
    'genre',
    Field('name', requires=IS_NOT_EMPTY()),
    Field('spotify_genre_id', requires=IS_NOT_EMPTY()),
    Field('leaderboard_pos', 'integer'),
)

db.define_table(
    'artist',
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
    Field('genre_id', 'reference genre'),
    Field('name', requires=IS_NOT_EMPTY()),
    Field('spotify_song_id', requires=IS_NOT_EMPTY()),
    Field('leaderboard_pos', 'integer'),
)

db.define_table(
    'user_top_genre',
    Field('spotify_genre_id', requires=IS_NOT_EMPTY()),
    Field('user_position', 'integer', requires=IS_NOT_EMPTY()),
    Field('user_timespan', requires=IS_NOT_EMPTY()),
)

db.define_table(
    'user_top_artist',
    Field('artist_id', 'reference artist'),
    Field('user_id', 'reference user'),
    Field('user_position', 'integer', requires=IS_NOT_EMPTY()),
    Field('user_timespan', requires=IS_NOT_EMPTY()),
)

db.define_table(
    'user_top_album',
    Field('album_id', 'reference album'),
    Field('user_id', 'reference user'),
    Field('user_position', 'integer', requires=IS_NOT_EMPTY()),
    Field('user_timespan', requires=IS_NOT_EMPTY()),
)

db.define_table(
    'user_top_song',
    Field('song_id', 'reference song'),
    Field('user_id', 'reference user'),
    Field('user_position', 'integer', requires=IS_NOT_EMPTY()),
    Field('user_timespan', requires=IS_NOT_EMPTY()),
)

db.define_table(
    'user_playlist',
    Field('user_id', 'reference user'),
    Field('name', requires=IS_NOT_EMPTY()),
    Field('spotify_playlist_id', requires=IS_NOT_EMPTY()),
)

# Not sure how best to have review DB entry work for any type
# of resource (track, album, artist, etc) so I just added a field
# for Spotify ID and we can look up what type of resource it is at
# runtime. Not very accessible for our DB but I couldn't think of
# another way with how references work.
db.define_table(
    'review',
    Field('user_id', 'reference user'),
    Field('spotify_id', requires=IS_NOT_EMPTY()),
    Field('description', 'text', requires=IS_NOT_EMPTY()),
)

db.commit()
