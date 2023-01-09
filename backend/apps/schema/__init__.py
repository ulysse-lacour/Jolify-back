from apps.schema.nodes.user import UserNode
from apps.schema.operations import user
from apps.schema.operations import spotify

TYPES = [
    UserNode
]

class Mutation(
    user.Mutation,
    spotify.Mutation,
):
    pass

class Query(
    user.Query,
    spotify.Query,
):

    pass
