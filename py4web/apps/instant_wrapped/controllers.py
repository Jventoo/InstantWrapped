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

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash, spotify_ranges, sp
from py4web.utils.url_signer import URLSigner
from .models import get_user_email
from . import settings

url_signer = URLSigner(session)

@action('index')
@action.uses(db, auth, 'index.html')
def index():
    for sp_range in spotify_ranges:
        print("range:", sp_range)

        results = sp.current_user_top_artists(time_range=sp_range, limit=50)

        for i, item in enumerate(results['items']):
            print(i, item['name'])
        print()
    return dict()

@action('dashboard')
@action.uses(db, auth, 'dashboard.html')
def index():
    print("User:", get_user_email())
    return dict()

@action('account_mng')
@action.uses(db, auth, 'account_mng.html')
def index():
    print("User:", get_user_email())
    return dict()

@action('login')
@action.uses(db, auth, 'login.html')
def index():
    print("User:", get_user_email())
    return dict()
