import graphene
from graphene_django import DjangoObjectType

from apps.models import User
from apps.api.spotify import SpotifyAPI


class UserNode(DjangoObjectType):
    """ Node for User model """
    class Meta:
        model = User
        name = 'User'
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "spotify_token_expires_at"
            ]

    has_spotify_token = graphene.NonNull(graphene.Boolean)
    has_spotify_refresh_token = graphene.NonNull(graphene.Boolean)
    is_access_token_expired = graphene.NonNull(graphene.Boolean)

    def resolve_has_spotify_token(self: User, context: graphene.ResolveInfo) -> bool:
        return self.spotify_access_token is not None

    def resolve_has_spotify_refresh_token(self: User, context: graphene.ResolveInfo) -> bool:
        return self.spotify_refresh_token is not None

    def resolve_is_access_token_expired(self: User, context: graphene.ResolveInfo) -> bool:
        return SpotifyAPI.is_access_token_expired(self.spotify_token_expires_at)
