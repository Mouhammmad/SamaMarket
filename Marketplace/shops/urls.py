from django.urls import path
from .views import BoutiqueView
from .views import BoutiqueProduitsView
from .views import BoutiqueAvisView
from .views import BoutiqueDetailView

urlpatterns = [
    path('<int:pk>/', BoutiqueView.as_view()),
    path('<int:pk>/produits/', BoutiqueProduitsView.as_view()),
    path('<int:pk>/avis/', BoutiqueAvisView.as_view()),
    path('<int:pk>/details/', BoutiqueDetailView.as_view()),
]