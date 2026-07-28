from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import SimpleTestCase


class AuthUserModelTests(SimpleTestCase):
    def test_auth_user_model_points_to_the_custom_user_model(self):
        self.assertEqual(settings.AUTH_USER_MODEL, 'comptes.User')
        self.assertEqual(get_user_model().__name__, 'User')
