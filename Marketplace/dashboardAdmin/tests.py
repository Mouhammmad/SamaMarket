from django.contrib.auth import get_user_model
from django.test import TestCase


class AdminStatsEndpointTests(TestCase):
    def setUp(self):
        self.User = get_user_model()

    def test_admin_stats_are_returned_for_admin_role_user(self):
        user = self.User.objects.create_user(
            username='adminrole',
            email='adminrole@example.com',
            password='admin123',
            role='ADMIN',
            is_staff=False,
            is_superuser=False,
        )

        self.client.force_login(user)
        response = self.client.get('/api/dashboard/admin/stats/')

        self.assertEqual(response.status_code, 200)
        self.assertIn('utilisateurs_total', response.json())
        self.assertIn('commandes_total', response.json())

    def test_non_admin_user_cannot_access_admin_stats(self):
        user = self.User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='customer123',
            role='CUSTOMER',
        )

        self.client.force_login(user)
        response = self.client.get('/api/dashboard/admin/stats/')

        self.assertEqual(response.status_code, 403)
