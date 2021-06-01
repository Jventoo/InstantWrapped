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
    ## Create user_top_genre entry
    return

def store_top_artist():
    # Check if album is in db.
        # If it is, continue.
        # If not, insert it.    
            # Check if genres are inserted. If not, insert them
    # Insert into user's top songs
    return

def store_top_album():
    # Check if album is in db.
        # If it is, continue.
        # If not, insert it.    
            # Check if album artist is inserted. If not, insert them
    # Insert into user's top songs
    return

def store_top_song(sid, uid):
    # Check if song is in db.
        # If it is, continue.
        # If not, insert it.    
            # Check if song album is inserted. If not, insert them
    # Insert into user's top songs
    return

def store_playlist(pid, uid):
    db.user_playlist.insert(
        user_id=uid,
        spotify_playlist_id=pid,
    )
    return

def store_review():
    return

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
    Field('rate_score', 'integer', default=0),
    Field('leaderboard_display', default=False),
)

db.define_table(
    'playlist_upvote',
    Field('playlist_id', 'reference user_playlist', ondelete ="CASCADE"), # Playlist that is starred
    Field('rater', 'reference auth_user', default=get_user), # User doing the rating.
    Field('upvote', 'integer', default=0), # +1 = upvote
)

db.define_table(
    'comments',
    Field('playlist_id', 'reference user_playlist', ondelete ="CASCADE"),
    Field('comment_author', 'reference auth_user', default=get_user),
    Field('user_email', default=get_user_email),
    Field('comment_txt', 'text', requires=IS_NOT_EMPTY()),
)

#redundant, but I didn't want to deal with parent child references
db.define_table(
    'replies',
    Field('comment_id', 'reference comments', ondelete ="CASCADE"),
    Field('reply_author', 'reference auth_user', default=get_user),
    Field('user_email', default=get_user_email),
    Field('reply_txt', 'text', requires=IS_NOT_EMPTY()),
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
