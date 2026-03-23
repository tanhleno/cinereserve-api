from django.urls import path
from .views import SessionSeatView, ReservationCreateView

urlpatterns = [
    path(
        "sessions/<int:session_id>/seats/",
        SessionSeatView.as_view(),
        name="session-seats",
    ),
    path(
        "sessions/<int:session_id>/reservations/",
        ReservationCreateView.as_view(),
        name="session-reservation-create",
    ),
]
