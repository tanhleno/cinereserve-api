import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from apps.catalog.models import Movie, Room, Session, Seat


@pytest.fixture
def movie():
    return Movie.objects.create(
        title="Inception",
        description="A mind-bending thriller.",
        duration_minutes=148,
        genre="Sci-Fi",
        banner_url="https://example.com/inception.jpg",
    )


@pytest.fixture
def room():
    return Room.objects.create(name="Sala Teste", total_seats=10)


@pytest.fixture
def session(movie, room):
    return Session.objects.create(
        movie=movie,
        room=room,
        starts_at=timezone.now() + timedelta(days=1),
    )


@pytest.mark.django_db
class TestSessionSeatView:

    def should_return_200_when_session_exists(self, client, session):
        response = client.get(
            reverse("session-seats", kwargs={"session_id": session.pk})
        )
        assert response.status_code == 200

    def should_return_404_when_session_does_not_exist(self, client):
        response = client.get(reverse("session-seats", kwargs={"session_id": 9999}))
        assert response.status_code == 404

    def should_return_seats_with_row_number_and_status(self, client, session):
        response = client.get(
            reverse("session-seats", kwargs={"session_id": session.pk})
        )
        seat = response.json()[0]
        assert "row" in seat
        assert "number" in seat
        assert "status" in seat

    def should_return_available_when_no_lock(self, client, session):
        response = client.get(
            reverse("session-seats", kwargs={"session_id": session.pk})
        )
        statuses = [s["status"] for s in response.json()]
        assert all(s == "available" for s in statuses)

    def should_return_reserved_when_lock_and_cart_exist(self, client, session):
        seat = Seat.objects.filter(room=session.room).first()
        from django.core.cache import cache

        cart_id = "test-cart-uuid"
        cache.set(f"seat:{session.id}:{seat.id}", cart_id)
        cache.set(f"cart:{cart_id}", {"seat_ids": [seat.id]})
        response = client.get(
            reverse("session-seats", kwargs={"session_id": session.pk})
        )
        seat_data = next(s for s in response.json() if s["id"] == seat.id)
        assert seat_data["status"] == "reserved"

    def should_return_available_when_lock_exists_but_cart_is_orphan(
        self, client, session
    ):
        seat = Seat.objects.filter(room=session.room).first()
        from django.core.cache import cache

        cache.set(f"seat:{session.id}:{seat.id}", "orphan-cart-uuid")
        response = client.get(
            reverse("session-seats", kwargs={"session_id": session.pk})
        )
        seat_data = next(s for s in response.json() if s["id"] == seat.id)
        assert seat_data["status"] == "available"

    def should_return_unavailable_when_seat_is_inactive(self, client, session):
        seat = Seat.objects.filter(room=session.room).first()
        seat.is_active = False
        seat.save()
        response = client.get(
            reverse("session-seats", kwargs={"session_id": session.pk})
        )
        seat_data = next(s for s in response.json() if s["id"] == seat.id)
        assert seat_data["status"] == "unavailable"
