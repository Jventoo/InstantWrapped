from . import OAuth2


class OAuth2Spotify(OAuth2):
    name = "oauth2spotify"
    label = "Spotify"

    login_url = "http://accounts.spotify.com/authorize"
    token_url = "https://accounts.spotify.com/api/token"
    userinfo_url = "https://api.spotify.com/v1/me"
    revoke_url = ""
    default_scope = "user-read-email user-read-recently-played user-top-read playlist-modify-public user-modify-playback-state playlist-modify-private user-follow-modify user-library-modify streaming"
    maps = {
        "email": "email",
        "sso_id": "id",
        "username": "display_name",
        "profile_picture": "images.0.url",
        "profile_url": "external_urls.spotify"
    }
