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

def get_time():
    return datetime.datetime.utcnow()

def store_top_genre(top_genre, pos, range):
    row = db(db.genre.name == top_genre).select().first()
    if row is None:
        id = db.genre.insert(name=top_genre)
    else:
        id = row.id

    db.user_top_genre.update_or_insert(
        (db.user_top_genre.user_position == pos) & (db.user_top_genre.user_timespan == range),
        genre_id=id,
        user_id=get_user(),
        user_position=pos,
        user_timespan=range
    )
    return

def store_top_artist(artist_name, artist_id, pos, range):
    row = db(db.artist.name == artist_name).select().first()
    if row is None:
        id = db.artist.insert(
            name=artist_name, spotify_artist_id=artist_id
        )
    else:
        id = row.id

    db.user_top_artist.update_or_insert(
        (db.user_top_artist.user_position == pos) & (db.user_top_artist.user_timespan == range),
        artist_id=id,
        user_id=get_user(),
        user_position=pos,
        user_timespan=range
    )
    return

def store_top_album(artist_id, album_name, album_id, pos, range):
    row = db(db.album.name == album_name).select().first()
    if row is None:
        id = db.album.insert(
            artist_id=artist_id,
            name=album_name,
            spotify_album_id=album_id
        )
    else:
        id = row.id

    db.user_top_album.update_or_insert(
        (db.user_top_album.user_position == pos) & (db.user_top_album.user_timespan == range),
        album_id=id,
        user_id=get_user(),
        user_position=pos,
        user_timespan=range
    )
    return

def store_top_song(album_id, song_name, song_id, pos, range):
    row = db(db.song.name == song_name).select().first()
    if row is None:
        id = db.song.insert(
            album_id=album_id,
            name=song_name,
            spotify_song_id=song_id
        )
    else:
        id = row.id
    
    db.user_top_song.update_or_insert(
        (db.user_top_song.user_position == pos) & (db.user_top_song.user_timespan == range),
        song_id=id,
        user_id=get_user(),
        user_position=pos,
        user_timespan=range
    )
    return

def store_playlist(pid, uid):
    db.user_playlist.insert(
        user_id=uid,
        spotify_playlist_id=pid,
    )
    return

# def store_review():
#     return

db.define_table(
    'genre',
    Field('name', requires=IS_NOT_EMPTY()),
)

db.define_table(
    'artist',
    Field('name', requires=IS_NOT_EMPTY()),
    Field('spotify_artist_id', requires=IS_NOT_EMPTY()),
)

db.define_table(
    'album',
    Field('artist_id', 'reference artist'),
    Field('name', requires=IS_NOT_EMPTY()),
    Field('spotify_album_id', requires=IS_NOT_EMPTY()),
)

db.define_table(
    'song',
    Field('album_id', 'reference album'),
    Field('name', requires=IS_NOT_EMPTY()),
    Field('spotify_song_id', requires=IS_NOT_EMPTY()),
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
    Field('user_id', default=get_user),
    Field('comment_txt', 'text', requires=IS_NOT_EMPTY()),
)

#redundant, but I didn't want to deal with parent child references
db.define_table(
    'replies',
    Field('comment_id', 'reference comments', ondelete ="CASCADE"),
    Field('reply_author', 'reference auth_user', default=get_user),
    Field('user_id', default=get_user),
    Field('reply_txt', 'text', requires=IS_NOT_EMPTY()),
)



# Not sure how best to have review DB entry work for any type
# of resource (track, album, artist, etc) so I just added a field
# for Spotify ID and we can look up what type of resource it is at
# runtime. Not very accessible for our DB but I couldn't think of
# another way with how references work.
# db.define_table(
#     'review',
#     Field('user_id', 'reference auth_user'),
#     Field('spotify_id', requires=IS_NOT_EMPTY()),
#     Field('description', 'text', requires=IS_NOT_EMPTY()),
# )

db.commit()
