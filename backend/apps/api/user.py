from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest
from django.core.mail import send_mail

from typing import Any, Dict, NamedTuple
from graphql_jwt.shortcuts import create_refresh_token, get_token
from collections import namedtuple

from apps.models import User


class UserAPI:

    @staticmethod
    def create_user(
        mutation_input: Dict[str, Any],
        context: HttpRequest,
    ) -> NamedTuple:
        # Namedtuple to return
        Create_User = namedtuple("Create_User", ["success", "token", "refresh_token", "details"])

        # Get mutations data
        username = mutation_input.get("username")
        password = mutation_input.get("password")
        email = mutation_input.get("email")

        # Initial data
        success = False
        token = None
        refresh_token = None
        details = ""
        accepted_users = [
            'ulysselejovial@gmail.com',
            'archenior@gmail.com',
            'naomi.prost@gmail.com',
            'paulcasanova@outlook.fr',
            'louise.gerbelle@gmail.com',
            'raphael.rousselot95@gmail.com',
            'quentin.baudis@hotmail.fr',
            'vladimir.broez@gmail.com',
            'hellomathlac@gmail.com',
            'simon.buty@gmail.com',
            'hugo.schmittperez@gmail.com',
            "test@user.com",
        ]

        # Check for empty fields
        # TODO : should check for strong password and valid email
        if username is None or password is None:
            details = "Input malformed !"
        else:
            # Check for preexisting user with same username
            # TODO : should check for email too
            user_already_exists = User.objects.filter(username=username).exists()

            if user_already_exists:
                details = "User already exist !"
            else:
                # Check if user is on our list
                accepted = email in accepted_users

                # Create user
                user = User(username=username, email=email, accepted_account=accepted)
                user.set_password(password)
                user.save()
                token = get_token(user)
                refresh_token = create_refresh_token(user)
                success = True
                details = f"User {username} created successfully !"

                # Email admin to ask for approval
                try:
                    send_mail(
                        'New subscription to Müsik app',
                        f"""
                        Username : {username}
                        User email : {email}

                        To add the user to Müsik go to :
                        https://developer.spotify.com/dashboard/applications/fffe2eacff224b6d8e37291b4433a444/users

                        Once the user informations are added to Spotify dev space, activate his account at :
                        https://musik.ulysselacour.com/admin/apps/user/

                        """,
                        'contact@ulysselacour.com',
                        ['me@ulysselacour.com'],
                        fail_silently=False,
                    )
                except Exception as e:
                    print(e)

        return Create_User(success, token, refresh_token, details)

    @staticmethod
    def login_user(
        mutation_input: Dict[str, Any],
        context: HttpRequest,
    ) -> NamedTuple:
        # Namedtuple to return
        Login_User = namedtuple("Login_User", ["success", "token", "refresh_token", "details"])

        # Get mutation data
        username = mutation_input.get("username")
        password = mutation_input.get("password")

        # Try to authenticate user
        user = authenticate(context, username=username, password=password)

        # Login user
        if user is not None:
            login(context, user)
            token = get_token(user)
            refresh_token = create_refresh_token(user)
            success = True
            details = f"User {username} logged in !"

        # Handle errors
        # TODO : improve error handling (forgot your password, user doesn't exist ?)
        else:
            token = None
            refresh_token = None
            success = False
            details = "Error in either password or username !"

        return Login_User(success, token, refresh_token, details)

    @staticmethod
    def logout_user(
        context: HttpRequest,
    ) -> Dict[str, Any]:
        logout(context)

        return {"success": True, "details": "User logged out!"}
