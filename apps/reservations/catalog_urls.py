from django.urls import path
from .views import SessionSeatView

urlpatterns = [
    path(
        "sessions/<int:session_id>/seats/",
        SessionSeatView.as_view(),
        name="session-seats",
    ),
]
