import pytest
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.catalog.models import Movie, Room, Session, Seat

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="user1", email="user1@test.com", password="testpass123"
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        username="user2", email="user2@test.com", password="testpass123"
    )


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def movie(db):
    return Movie.objects.create(
        title="Inception",
        description="A mind-bending thriller.",
        duration_minutes=148,
        genre="Sci-Fi",
        banner_url="https://example.com/inception.jpg",
    )


@pytest.fixture
def room(db):
    return Room.objects.create(name="Sala Teste", total_seats=10)


@pytest.fixture
def session(movie, room):
    return Session.objects.create(
        movie=movie,
        room=room,
        starts_at=timezone.now() + timedelta(days=1),
    )


@pytest.fixture
def seat_ids(room):
    return list(Seat.objects.filter(room=room).values_list("id", flat=True)[:3])
