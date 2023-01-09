import graphene

from graphene import ResolveInfo

from apps.schema.nodes.user import UserNode
from apps.api.user import UserAPI
from apps.models import User


class Query(graphene.ObjectType):
    whoami = graphene.Field(UserNode)
    users = graphene.List(UserNode)

    def resolve_whoami(self, info):
        user = info.context.user
        # Check to ensure user is signed in
        if user.is_anonymous:
            raise Exception('Authentication Failure: Your must be signed in')
        return user

    def resolve_users(self, info):
        return User.objects.all()


class CreateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String()
        password = graphene.String()
        email = graphene.String()

    success = graphene.Boolean()
    token = graphene.String()
    refresh_token = graphene.String()
    details = graphene.String()

    def mutate(self, info: ResolveInfo, **kwargs):
        create_user = UserAPI.create_user(
            mutation_input=kwargs,
            context=info.context
        )

        return CreateUser(
            success=create_user.success,
            token=create_user.token,
            refresh_token=create_user.refresh_token,
            details=create_user.details
        )


class LoginUser(graphene.Mutation):
    class Arguments:
        username = graphene.String()
        password = graphene.String()

    success = graphene.Boolean()
    token = graphene.String()
    refresh_token = graphene.String()
    details = graphene.String()

    def mutate(self, info: ResolveInfo, **kwargs):
        login_user = UserAPI.login_user(
            mutation_input=kwargs,
            context=info.context
        )

        return LoginUser(
            success=login_user.success,
            token=login_user.token,
            refresh_token=login_user.refresh_token,
            details=login_user.details
        )


class LogoutUser(graphene.Mutation):
    success = graphene.Boolean()
    details = graphene.String()

    def mutate(self, info: ResolveInfo):
        logout_user = UserAPI.logout_user(context=info.context)

        return LogoutUser(
            success=logout_user.get("success"),
            details=logout_user.get("details"),
        )


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    login_user = LoginUser.Field()
    logout_user = LogoutUser.Field()
