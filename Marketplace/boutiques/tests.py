from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Boutique
from .serializers import BoutiqueSerializer


class BoutiqueSerializerTests(TestCase):
    def test_serializer_exposes_approved_field(self):
        user = get_user_model().objects.create_user(
            username='vendor',
            email='vendor@example.com',
            password='secret123'
        )
        boutique = Boutique.objects.create(
            responsable=user,
            nom='Ma boutique',
            description='Description',
            ville='Dakar'
        )

        serializer = BoutiqueSerializer(boutique)

        self.assertIn('apprové', serializer.data)
        self.assertFalse(serializer.data['apprové'])
