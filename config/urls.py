from django.urls import path, include

urlpatterns = [
    path("auth/", include("apps.accounts.urls")),
    path("", include("apps.catalog.urls")),
    path("", include("apps.reservations.catalog_urls")),
    path("reservations/", include("apps.reservations.urls")),
]
