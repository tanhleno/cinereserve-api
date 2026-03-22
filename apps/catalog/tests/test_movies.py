# apps/catalog/tests/test_movies.py
import pytest
from django.urls import reverse
from apps.catalog.models import Movie


@pytest.mark.django_db
class TestMovieListView:

    def should_return_200_with_pagination_structure(self, client):
        response = client.get(reverse("movie-list"))
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "next" in data
        assert "previous" in data
        assert "results" in data

    def should_return_empty_list_when_no_movies_exist(self, client):
        response = client.get(reverse("movie-list"))
        assert response.status_code == 200
        assert response.json()["results"] == []
        assert response.json()["count"] == 0
