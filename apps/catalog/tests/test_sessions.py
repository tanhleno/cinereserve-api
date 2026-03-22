import pytest
from django.urls import reverse
from apps.catalog.models import Movie, Room, Session
from django.utils import timezone
from datetime import timedelta


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
    return Room.objects.create(name="Sala Teste", total_seats=50)


@pytest.mark.django_db
class TestSessionListView:

    def should_return_200_with_pagination_when_movie_exists(self, client, movie):
        response = client.get(reverse("session-list", kwargs={"movie_id": movie.pk}))
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "next" in data
        assert "previous" in data
        assert "results" in data

    def should_return_404_when_movie_does_not_exist(self, client):
        response = client.get(reverse("session-list", kwargs={"movie_id": 9999}))
        assert response.status_code == 404

    def should_return_empty_list_when_movie_has_no_sessions(self, client, movie):
        response = client.get(reverse("session-list", kwargs={"movie_id": movie.pk}))
        assert response.status_code == 200
        assert response.json()["results"] == []

    def should_raise_validation_error_when_room_is_occupied(self, movie, room):
        starts_at = timezone.now() + timedelta(hours=1)
        Session.objects.create(movie=movie, room=room, starts_at=starts_at)
        with pytest.raises(Exception):
            session = Session(movie=movie, room=room, starts_at=starts_at)
            session.full_clean()
