import base64
import requests
from datetime import datetime, timedelta
import spotipy

from django.conf import settings
from django.http import HttpRequest, HttpResponseForbidden
from django.shortcuts import redirect
from graphene_django.views import GraphQLView

from apps.models import User

def spotify_callback_handle(
    request: HttpRequest,
):
    error = request.GET.get("error")
    if error is not None:
        raise RuntimeError(f"Error during apify callback: {error!r}")

    user_id = request.GET.get("state")
    try:
        user_in_db = User.objects.filter(pk=user_id)
    except User.DoesNotExist:
        raise RuntimeError(f"No user found for user_id: {user_id}")

    authorization_code = request.GET.get("code")
    if authorization_code is None:
        raise RuntimeError("No authorization code provided")

    encodedData = base64.b64encode(bytes(f"{settings.SPOTIFY_APP_CLIENT_ID}:{settings.SPOTIFY_APP_CLIENT_SECRET}", "ISO-8859-1")).decode("ascii")
    credentials = f"{encodedData}"

    res = requests.post(
            "https://accounts.spotify.com/api/token?",
            data= {
                "grant_type": "authorization_code",
                "code": authorization_code,
                "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
            },
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )

    res_status = res.raise_for_status()

    res_data = res.json()

    # Update User token infos in DB
    user = User.objects.get(pk=user_id)
    user.spotify_access_token = res_data["access_token"]
    user.spotify_refresh_token = res_data["refresh_token"]
    user.spotify_token_expires_at = datetime.now() + timedelta(seconds=res_data["expires_in"])
    user.save(update_fields=['spotify_access_token', 'spotify_refresh_token', 'spotify_token_expires_at'])

    return redirect(to=settings.FRONTEND_REDIRECT_URI, permanent=True)


class AdminOnlyGraphiQLView(GraphQLView):
    def render_graphiql(self, request: HttpRequest, **data):
        if (
            settings.DEBUG == False
            and (
                not request.user.is_authenticated
                or not request.user.is_staff
            )
        ):
            return HttpResponseForbidden(
                content="<h1>This view is restricted to admin user</h1>"
            )
        else:
            return super().render_graphiql(request, **data)
