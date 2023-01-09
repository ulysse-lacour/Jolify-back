import graphene

from apps.api.spotify import SpotifyAPI


# DEFINE DATA TYPE AND STRUCTURE
class PlaylistInfo(graphene.ObjectType):
    playlist_name = graphene.String()
    playlist_description = graphene.String()
    playlist_url = graphene.String()
    owner_name = graphene.String()
    owner_url = graphene.String()

    def resolve_playlist_info(self, parent, info):
        return f"{parent.playlist_name} made by {parent.owner_name}"

class TrackData(graphene.ObjectType):
    id = graphene.String()
    artist = graphene.String()
    title = graphene.String()
    link = graphene.String()
    cover = graphene.String()
    preview = graphene.String()

    def resolve_track(self, parent, info):
        return f"{parent.artist} - {parent.title}"

class PlaylistsData(graphene.ObjectType):
    id = graphene.String()
    name = graphene.String()
    description = graphene.String()
    href = graphene.String()
    image = graphene.String()

    def resolve_playlist(self, parent, info):
        return f"{parent.name} : {parent.id}"

class UserData(graphene.ObjectType):
    id = graphene.String()
    name = graphene.String()
    href = graphene.String()

    def resolve_playlist(self, parent, info):
        return f"{parent.name} : {parent.href}"

class PlaylistData(graphene.ObjectType):
    success = graphene.Boolean()
    tracks = graphene.List(TrackData)
    last_page = graphene.Boolean()

class SpecificPlaylistData(graphene.ObjectType):
    success = graphene.Boolean()
    playlist =  graphene.Field(PlaylistInfo)
    tracks = graphene.List(TrackData)
    last_page = graphene.Boolean()

class UserPlaylistsData(graphene.ObjectType):
    success = graphene.Boolean()
    details = graphene.String()
    owner = graphene.Field(UserData)
    playlists = graphene.List(PlaylistsData)
    last_page = graphene.Boolean()

class AuthLink(graphene.ObjectType):
    success = graphene.Boolean()
    href = graphene.String()



class Query(graphene.ObjectType):
    my_suggestions = graphene.Field(
        PlaylistData,
        args={
            'playlist_id': graphene.String(),
            'offset': graphene.Int(),
        })

    specific_playlist_data = graphene.Field(
        SpecificPlaylistData,
        args={
            'playlist_id': graphene.String(),
            'offset': graphene.Int(),
        })

    user_playlists_data = graphene.Field(
        UserPlaylistsData,
        args={
            'offset': graphene.Int(),
        })

    auth_link = graphene.Field(AuthLink)

    def resolve_my_suggestions(self, info, playlist_id, offset):
        playlist = SpotifyAPI.get_tracks_from_my_suggestions(
            playlist_id=playlist_id,
            offset=offset,
            context=info.context
        )
        return PlaylistData(
            success=playlist.get("success"),
            tracks=playlist.get("tracks"),
            last_page=playlist.get("last_page"),
        )

    def resolve_specific_playlist_data(self, info, playlist_id, offset):
        playlist = SpotifyAPI.get_playlist_data(
            playlist_id=playlist_id,
            offset=offset,
            context=info.context
        )
        return SpecificPlaylistData(
            success=playlist.get("success"),
            playlist=playlist.get("playlist"),
            tracks=playlist.get("tracks"),
            last_page=playlist.get("last_page"),
        )

    def resolve_user_playlists_data(self, info, offset):
        playlists = SpotifyAPI.get_user_playlists(
            offset=offset,
            context=info.context
        )

        return UserPlaylistsData(
            success=playlists.get("success"),
            details=playlists.get("details"),
            owner=playlists.get("owner"),
            playlists=playlists.get("playlists"),
            last_page=playlists.get("last_page"),
        )

    def resolve_auth_link(self, info):
        auth_link = SpotifyAPI.get_spotify_oauth_link(context=info.context)

        return AuthLink(
            success=auth_link.get("success"),
            href=auth_link.get("href"),
        )


class Mutation(graphene.ObjectType):
    pass
