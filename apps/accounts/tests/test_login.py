import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestLoginView:

    def should_return_200_with_tokens_when_credentials_are_valid(self, client):
        User.objects.create_user(
            email="test@test.com", username="test", password="Test1234!"
        )
        response = client.post(
            reverse("login"),
            {"email": "test@test.com", "password": "Test1234!"},
            content_type="application/json",
        )
        assert response.status_code == 200
        assert "access" in response.json()
        assert "refresh" in response.json()

    def should_return_401_when_password_is_incorrect(self, client):
        User.objects.create_user(
            email="test@test.com", username="test", password="Test1234!"
        )
        response = client.post(
            reverse("login"),
            {"email": "test@test.com", "password": "wrongpassword"},
            content_type="application/json",
        )
        assert response.status_code == 401

    def should_return_401_when_user_does_not_exist(self, client):
        response = client.post(
            reverse("login"),
            {"email": "noone@test.com", "password": "Test1234!"},
            content_type="application/json",
        )
        assert response.status_code == 401
