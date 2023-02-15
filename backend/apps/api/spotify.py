import base64
import re
import requests
import spotipy

from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from datetime import timedelta, datetime
from typing import Any, Dict, List

from django.conf import settings
from django.http import HttpRequest
from django.utils import timezone

from apps.models import User


class SpotifyAPI:

    @staticmethod
    def get_tracks_from_my_suggestions(
        playlist_id,
        offset,
        context: HttpRequest,
    ) -> Dict[str, Any]:

        tracks = []
        limit_step = 20
        auth_manager = SpotifyClientCredentials(
            client_id=settings.SPOTIFY_USER_CLIENT_ID,
            client_secret=settings.SPOTIFY_USER_CLIENT_SECRET
        )
        spotipy_auth = spotipy.Spotify(auth_manager=auth_manager)

        songs = spotipy_auth.user_playlist_tracks(
            user='',
            playlist_id=playlist_id,
            limit=limit_step,
            offset=offset
        )

        for song in songs['items']:
            # RegEx manipulation to clean title of track
            title = re.sub("[\(\[].*?[\)\]]", "", song['track']['name'])  # pylint: disable=W1401
            title = re.sub(r'\-.*', "", title)
            title = re.sub(r'\|.*', "", title)
            # Get track data
            song_id = song['track']['id']
            artist = song['track']['artists'][0]['name']
            link = song['track']['external_urls']['spotify']
            cover = song['track']['album']['images'][0]["url"]
            preview = song['track']['preview_url']
            tracks.append({
                "id": song_id,
                "artist": artist,
                "title": title,
                "link": link,
                "cover": cover,
                "preview": preview,
            })

        last_page = songs['next'] is None
        return {"success": True, "tracks": tracks, "last_page": last_page}

    @staticmethod
    def get_user_playlists(
        offset,
        context: HttpRequest,
    ) -> Dict[str, Any]:

        if context.user.accepted_account is False:
            return {"success": False, "details": "Account not accepted.", "owner": {}, "playlists": [], "last_page": True}

        access_token = context.user.spotify_access_token

        if not access_token:
            return {"success": False, "details": "No access token registered", "owner": {}, "playlists": [], "last_page": True}
        elif SpotifyAPI.is_access_token_expired(context.user.spotify_token_expires_at) is True:
            access_token = SpotifyAPI.refresh_token(context.user.spotify_refresh_token, context).get("access_token")

        spotipy_auth = spotipy.Spotify(access_token)

        playlists = []
        user_playlists = spotipy_auth.current_user_playlists(limit=50, offset=offset)

        owner_data = user_playlists['items'][0]['owner']
        owner = {
            "id": owner_data['id'],
            "name": owner_data['display_name'],
            "href": owner_data['external_urls']['spotify'],
        }

        for playlist in user_playlists['items']:
            # TODO : fix that for image should be displayed a default if none is provided
            # make sure every playlist has an image and a name, if one hasn't don't send it to front
            if len(playlist['images']) < 1 or len(playlist['name']) < 1:
                continue

            playlist_id = playlist['id']
            playlist_name = playlist['name']
            playlist_description = playlist['description']
            playlist_href = playlist['external_urls']['spotify']
            playlist_image = playlist['images'][0]['url']

            playlists.append({
                "id": playlist_id,
                "name": playlist_name,
                "description": playlist_description,
                "href": playlist_href,
                "image": playlist_image,
            })

        last_page = user_playlists['next'] is None

        return {"success": True, "details": "Playlists successfuly fetched.", "owner": owner, "playlists": playlists, "last_page": last_page}

    @staticmethod
    def get_playlist_data(
        playlist_id,
        offset,
        context: HttpRequest,
    ) -> Dict[str, Any]:

        tracks = []
        limit_step = 20
        auth_manager = SpotifyClientCredentials(
            client_id=settings.SPOTIFY_USER_CLIENT_ID,
            client_secret=settings.SPOTIFY_USER_CLIENT_SECRET
        )
        spotipy_auth = spotipy.Spotify(auth_manager=auth_manager)

        # Fetch playlist infos
        playlist = spotipy_auth.user_playlist(
            user='',
            playlist_id=playlist_id,
        )

        playlist_name = playlist['name']
        playlist_description = playlist['description']
        playlist_url = playlist['external_urls']['spotify']
        owner_name = playlist['owner']['display_name']
        owner_url = playlist['owner']['external_urls']['spotify']
        playlist_data = {
            "playlist_name": playlist_name,
            "playlist_description": playlist_description,
            "playlist_url": playlist_url,
            "owner_name": owner_name,
            "owner_url": owner_url,
        }
        # TODO : followers : 'followers': {'href': None, 'total': 0},
        # TODO : playlist_image : 'images': [{'height': 640, 'url': 'https://mosaic.scdn.co/640/ab67616d0000b2739e01d5ed521b00f41593c4a7ab67616d0000b273a5aef98a1762d0f64bb6ed9aab67616d0000b273bcee8e2aa4ded86f18661153ab67616d0000b273c7167ab79dd0e4e14d3b575a', 'width': 640}, {'height': 300, 'url': 'https://mosaic.scdn.co/300/ab67616d0000b2739e01d5ed521b00f41593c4a7ab67616d0000b273a5aef98a1762d0f64bb6ed9aab67616d0000b273bcee8e2aa4ded86f18661153ab67616d0000b273c7167ab79dd0e4e14d3b575a', 'width': 300}, {'height': 60, 'url': 'https://mosaic.scdn.co/60/ab67616d0000b2739e01d5ed521b00f41593c4a7ab67616d0000b273a5aef98a1762d0f64bb6ed9aab67616d0000b273bcee8e2aa4ded86f18661153ab67616d0000b273c7167ab79dd0e4e14d3b575a', 'width': 60}],

        # Fetch tracks of playlist infos
        songs = spotipy_auth.user_playlist_tracks(
            user='',
            playlist_id=playlist_id,
            limit=limit_step,
            offset=offset
        )

        for song in songs['items']:
            if song['track']['duration_ms'] != 0:
                # RegEx manipulation to clean title of track
                title = re.sub("[\(\[].*?[\)\]]", "", song['track']['name'])  # pylint: disable=W1401
                title = re.sub(r'\-.*', "", title)
                title = re.sub(r'\|.*', "", title)
                # Get track data
                song_id = song['track']['id']
                artist = song['track']['artists'][0]['name']
                link = song['track']['external_urls']['spotify']
                cover = song['track']['album']['images'][0]["url"]
                preview = song['track']['preview_url']
                tracks.append({
                    "id": song_id,
                    "artist": artist,
                    "title": title,
                    "link": link,
                    "cover": cover,
                    "preview": preview,
                })

        last_page = songs['next'] is None
        return {"success": True, "playlist": playlist_data, "tracks": tracks, "last_page": last_page}

    @staticmethod
    def get_spotify_oauth_link(
        context: HttpRequest,
    ) -> Dict[str, Any]:

        scope = "user-library-read user-read-private playlist-read-private user-read-email"

        res = requests.get(
            "https://accounts.spotify.com/authorize?",
            params={
                "response_type": 'code',
                "scope": scope,
                "client_id": settings.SPOTIFY_APP_CLIENT_ID,
                "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
                "state": context.user.id,
            }
        )

        res_status = res.raise_for_status()

        href = res.url

        return {"success": True, "href": href}

    @staticmethod
    def refresh_token(
        refresh_token: str,
        context: HttpRequest,
    ) -> Dict[str, Any]:

        encodedData = base64.b64encode(
            bytes(f"{settings.SPOTIFY_APP_CLIENT_ID}:{settings.SPOTIFY_APP_CLIENT_SECRET}", "ISO-8859-1")).decode("ascii")
        credentials = f"{encodedData}"

        res = requests.post(
            "https://accounts.spotify.com/api/token?",
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )

        res_status = res.raise_for_status()

        res_data = res.json()

        # Update User token infos in DB
        user = User.objects.get(pk=context.user.id)
        user.spotify_access_token = res_data["access_token"]
        user.spotify_token_expires_at = timezone.now() + timedelta(seconds=res_data["expires_in"])
        user.save(update_fields=['spotify_access_token', 'spotify_token_expires_at'])

        return {"access_token": res_data["access_token"]}

    @staticmethod
    def is_access_token_expired(
        token_expiration_date: datetime,
    ) -> bool:

        is_expired = token_expiration_date - timezone.now()
        return is_expired.total_seconds() <= 0
