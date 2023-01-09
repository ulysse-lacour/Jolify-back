import json

from graphene_django.utils.testing import GraphQLTestCase

from apps.models.user import User

class TestUser(GraphQLTestCase):

    def setUp(self) -> None:
        super().setUp()

        self.user = User.objects.create(
            username="foo",
            email="foo@bar.com",
        )
        self.user_password = "my_foo_password"
        self.user.set_password(self.user_password)
        self.user.save()

    def test_create_user_success(self):
        username = "fooUsername"
        email = "foo@bar.com"
        password = "myPassword"

        response = self.query(
            """
            mutation createUser(
                $email: String,
                $username: String,
                $password: String,
            ){
                createUser(
                    email: $email,
                    username: $username,
                    password: $password,
                ) {
                    success
                    token
                    refreshToken
                    details
                }
            }
            """,
            operation_name="createUser",
            variables={
                "email": email,
                "username": username,
                "password": password,
            }
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["createUser"]

        self.assertTrue(content["success"])
        self.assertIsNotNone(content["token"])
        self.assertIsNotNone(content["refreshToken"])
        self.assertEqual(
            f"User {username} created successfully !",
            content["details"]
        )

        db_user = User.objects.get(username=username)

        self.assertEqual(
            email,
            db_user.email
        )

        self.assertTrue(
            db_user.check_password(password)
        )

        self.assertFalse(
            db_user.accepted_account,
        )

    def test_create_user_success_accepted_user(self):
        username = "fooUsername"
        email = "test@user.com"
        password = "myPassword"

        response = self.query(
            """
            mutation createUser(
                $email: String,
                $username: String,
                $password: String,
            ){
                createUser(
                    email: $email,
                    username: $username,
                    password: $password,
                ) {
                    success
                    token
                    refreshToken
                    details
                }
            }
            """,
            operation_name="createUser",
            variables={
                "email": email,
                "username": username,
                "password": password,
            }
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["createUser"]

        self.assertTrue(content["success"])
        self.assertIsNotNone(content["token"])
        self.assertIsNotNone(content["refreshToken"])
        self.assertEqual(
            f"User {username} created successfully !",
            content["details"]
        )

        db_user = User.objects.get(username=username)

        self.assertEqual(
            email,
            db_user.email
        )

        self.assertTrue(
            db_user.check_password(password)
        )

        self.assertTrue(
            db_user.accepted_account,
        )

    def test_create_user_error_no_username(self):
        username = None
        email = "test@user.com"
        password = "myPassword"

        response = self.query(
            """
            mutation createUser(
                $email: String,
                $username: String,
                $password: String,
            ){
                createUser(
                    email: $email,
                    username: $username,
                    password: $password,
                ) {
                    success
                    token
                    refreshToken
                    details
                }
            }
            """,
            operation_name="createUser",
            variables={
                "email": email,
                "username": username,
                "password": password,
            }
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["createUser"]

        self.assertFalse(content["success"])
        self.assertIsNone(content["token"])
        self.assertIsNone(content["refreshToken"])
        self.assertEqual(
            "Input malformed !",
            content["details"]
        )

        db_user = User.objects.filter(username=username)

        self.assertEqual(
            0,
            len(db_user)
        )

    def test_create_user_error_no_password(self):
        username = "fooUsername"
        email = "test@user.com"
        password = None

        response = self.query(
            """
            mutation createUser(
                $email: String,
                $username: String,
                $password: String,
            ){
                createUser(
                    email: $email,
                    username: $username,
                    password: $password,
                ) {
                    success
                    token
                    refreshToken
                    details
                }
            }
            """,
            operation_name="createUser",
            variables={
                "email": email,
                "username": username,
                "password": password,
            }
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["createUser"]

        self.assertFalse(content["success"])
        self.assertIsNone(content["token"])
        self.assertIsNone(content["refreshToken"])
        self.assertEqual(
            "Input malformed !",
            content["details"]
        )

        db_user = User.objects.filter(username=username)

        self.assertEqual(
            0,
            len(db_user)
        )

    def test_create_user_error_existing_user(self):
        username = "fooUsername"
        email = "test@user.com"
        password = "myPassword"

        User.objects.create(
            username=username,
            email="another@email.com",
            password="anotherPassword"
        )

        response = self.query(
            """
            mutation createUser(
                $email: String,
                $username: String,
                $password: String,
            ){
                createUser(
                    email: $email,
                    username: $username,
                    password: $password,
                ) {
                    success
                    token
                    refreshToken
                    details
                }
            }
            """,
            operation_name="createUser",
            variables={
                "email": email,
                "username": username,
                "password": password,
            }
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)["data"]["createUser"]

        self.assertFalse(content["success"])
        self.assertIsNone(content["token"])
        self.assertIsNone(content["refreshToken"])
        self.assertEqual(
            "User already exist !",
            content["details"]
        )

        db_users = User.objects.filter(username=username)

        self.assertEqual(
            1,  # Should not be 2
            len(db_users)
        )

        [db_user] = db_users

        self.assertNotEqual(
            db_user.email,
            email,
        )

        self.assertFalse(
            db_user.check_password(password)
        )

    def test_login_success(self):
        response = self.query(
            """
            mutation loginUser(
                $username: String,
                $password: String,
            ){
                loginUser(
                    username: $username,
                    password: $password,
                ) {
                    success
                    token
                    refreshToken
                    details
                }
            }
            """,
            operation_name="loginUser",
            variables={
                "username": self.user.username,
                "password": self.user_password,
            }
        )

        content = json.loads(response.content)["data"]["loginUser"]

        self.assertTrue(
            content["success"]
        )
        self.assertIsNotNone(content["token"])
        self.assertIsNotNone(content["refreshToken"])
        self.assertEqual(
            f"User {self.user.username} logged in !",
            content["details"]
        )

        db_user = self.user

        self.assertTrue(
            db_user.is_authenticated
        )

    def test_login_error_invalid_password(self):
        response = self.query(
            """
            mutation loginUser(
                $username: String,
                $password: String,
            ){
                loginUser(
                    username: $username,
                    password: $password,
                ) {
                    success
                    token
                    refreshToken
                    details
                }
            }
            """,
            operation_name="loginUser",
            variables={
                "username": self.user.username,
                "password": "invalid_password",
            }
        )

        content = json.loads(response.content)["data"]["loginUser"]

        self.assertFalse(
            content["success"]
        )
        self.assertIsNone(content["token"])
        self.assertIsNone(content["refreshToken"])
        self.assertEqual(
            "Error in either password or username !",
            content["details"]
        )
