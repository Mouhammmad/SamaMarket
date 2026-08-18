from django.urls import path

from .views import FavoriteListCreateView, FavoriteDestroyView

# À inclure dans les urls du projet :
# path("api/v1/favorites/", include("favorites.urls"))
urlpatterns = [
    path("", FavoriteListCreateView.as_view(), name="favorite-list-create"),
    path("<int:item_id>/", FavoriteDestroyView.as_view(), name="favorite-destroy"),
]
