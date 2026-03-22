import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from freezegun import freeze_time
from datetime import timedelta
from django.utils import timezone

User = get_user_model()


@pytest.mark.django_db
class TestRefreshView:

    def should_return_200_with_new_access_token_when_refresh_is_valid(self, client):
        User.objects.create_user(
            email="test@test.com", username="test", password="Test1234!"
        )
        login = client.post(
            reverse("login"),
            {"email": "test@test.com", "password": "Test1234!"},
            content_type="application/json",
        )
        refresh = login.json()["refresh"]
        response = client.post(
            reverse("refresh"),
            {"refresh": refresh},
            content_type="application/json",
        )
        assert response.status_code == 200
        assert "access" in response.json()

    def should_return_401_when_refresh_token_is_invalid(self, client):
        response = client.post(
            reverse("refresh"),
            {"refresh": "invalidtoken"},
            content_type="application/json",
        )
        assert response.status_code == 401

    def should_return_401_when_refresh_token_is_expired(self, client):
        User.objects.create_user(
            email="test@test.com", username="test", password="Test1234!"
        )
        login = client.post(
            reverse("login"),
            {"email": "test@test.com", "password": "Test1234!"},
            content_type="application/json",
        )
        refresh = login.json()["refresh"]

        future = (
            timezone.now()
            + settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]
            + timedelta(seconds=1)
        )
        with freeze_time(future):
            response = client.post(
                reverse("refresh"),
                {"refresh": refresh},
                content_type="application/json",
            )
            assert response.status_code == 401
