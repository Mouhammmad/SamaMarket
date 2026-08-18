from unittest import mock

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from samamarket.models import Product
from .models import Favorite

User = get_user_model()


class FavoriteAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="issaga", password="motdepasse123"
        )
        self.product = Product.objects.create(
            name="Écharpe Bazin Riche", slug="echarpe-bazin-riche", price=12500
        )
        self.list_create_url = reverse("favorite-list-create")

    def destroy_url(self, item_id):
        return reverse("favorite-destroy", kwargs={"item_id": item_id})

    # --- Accès anonyme ---
    def test_anonymous_user_gets_401_on_list(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_user_gets_401_on_post(self):
        response = self.client.post(self.list_create_url, {"item": self.product.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_user_gets_401_on_delete(self):
        response = self.client.delete(self.destroy_url(self.product.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Isolation par utilisateur ---
    def test_list_only_returns_current_user_favorites(self):
        other_user = User.objects.create_user(
            username="autre", password="motdepasse123"
        )
        Favorite.objects.create(user=other_user, item=self.product)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_create_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    # --- POST (ajout) ---
    def test_post_creates_favorite(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.list_create_url, {"item": self.product.id})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Favorite.objects.filter(user=self.user, item=self.product).exists()
        )

    def test_post_duplicate_favorite_returns_400(self):
        Favorite.objects.create(user=self.user, item=self.product)
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.list_create_url, {"item": self.product.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_unknown_item_returns_400(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.list_create_url, {"item": 999999})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- DELETE (suppression) ---
    def test_delete_removes_favorite_and_frees_uniqueness(self):
        Favorite.objects.create(user=self.user, item=self.product)
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(self.destroy_url(self.product.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Favorite.objects.filter(user=self.user, item=self.product).exists()
        )

        # La contrainte unique_together est bien libérée : on peut re-créer
        response = self.client.post(self.list_create_url, {"item": self.product.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_not_favorited_returns_404(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.destroy_url(self.product.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_race_condition_returns_400_not_500(self):
        """
        Si deux requêtes passent la validation en même temps (le SELECT de
        validate_item ne voit pas encore la ligne de l'autre requête), la
        contrainte unique_together lève une IntegrityError au .save().
        On simule ce cas en contournant volontairement validate_item pour
        vérifier que la vue renvoie bien 400 et pas une 500 non gérée.
        """
        self.client.force_authenticate(user=self.user)
        Favorite.objects.create(user=self.user, item=self.product)

        with mock.patch(
            "favorites.serializers.FavoriteCreateSerializer.validate_item",
            side_effect=lambda value: value,
        ):
            response = self.client.post(
                self.list_create_url, {"item": self.product.id}
            )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
