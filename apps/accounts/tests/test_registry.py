import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

User = get_user_model()


@pytest.mark.django_db
class TestRegisterView:

    def should_return_201_when_data_is_valid(self, client):
        response = client.post(
            reverse("register"),
            {"email": "test@test.com", "username": "test", "password": "Test1234!"},
            content_type="application/json",
        )
        assert response.status_code == 201

    def should_not_include_password_in_response(self, client):
        response = client.post(
            reverse("register"),
            {"email": "test@test.com", "username": "test", "password": "Test1234!"},
            content_type="application/json",
        )
        assert "password" not in response.json()

    def should_return_422_when_email_is_duplicate(self, client):
        User.objects.create_user(
            email="test@test.com", username="existing", password="Test1234!"
        )
        response = client.post(
            reverse("register"),
            {"email": "test@test.com", "username": "test", "password": "Test1234!"},
            content_type="application/json",
        )
        assert response.status_code == 422

    def should_return_422_when_required_field_is_missing(self, client):
        response = client.post(
            reverse("register"),
            {"email": "test@test.com"},
            content_type="application/json",
        )
        assert response.status_code == 422

    def should_store_password_as_hash(self, client):
        client.post(
            reverse("register"),
            {"email": "test@test.com", "username": "test", "password": "Test1234!"},
            content_type="application/json",
        )
        user = User.objects.get(email="test@test.com")
        assert user.password != "Test1234!"
        assert check_password("Test1234!", user.password)
