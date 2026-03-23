import pytest
import threading
from django.core.cache import cache
from django.urls import reverse
from freezegun import freeze_time
from django.contrib.auth import get_user_model
from datetime import timedelta
from rest_framework.test import APIClient
from apps.catalog.models import Room, Seat
from apps.reservations.config import SEAT_LOCK_TIMEOUT, MAX_SEATS_PER_RESERVATION

User = get_user_model()


class TestReservationCreate:

    def should_return_201_with_valid_payload(self, auth_client, session, seat_ids):
        response = auth_client.post(
            reverse("session-reservation-create", kwargs={"session_id": session.id}),
            {"seat_ids": seat_ids},
            format="json",
        )
        assert response.status_code == 201

    def should_return_expires_in_and_seat_ids(self, auth_client, session, seat_ids):
        response = auth_client.post(
            reverse("session-reservation-create", kwargs={"session_id": session.id}),
            {"seat_ids": seat_ids},
            format="json",
        )
        assert "expires_in" in response.data
        assert sorted(response.data["seat_ids"]) == sorted(seat_ids)

    def should_create_cart_key_with_ttl(self, auth_client, user, session, seat_ids):
        auth_client.post(
            reverse("session-reservation-create", kwargs={"session_id": session.id}),
            {"seat_ids": seat_ids},
            format="json",
        )
        ttl = cache.client.get_client().ttl(f"cart:{user.id}:{session.id}")
        assert 0 < ttl <= SEAT_LOCK_TIMEOUT

    def should_create_cart_seats_with_all_seat_ids(
        self, auth_client, user, session, seat_ids
    ):
        auth_client.post(
            reverse("session-reservation-create", kwargs={"session_id": session.id}),
            {"seat_ids": seat_ids},
            format="json",
        )
        members = cache.client.get_client().smembers(
            f"cart_seats:{user.id}:{session.id}"
        )
        assert {int(m) for m in members} == set(seat_ids)

    def should_create_seat_locks_for_all_seats(
        self, auth_client, user, session, seat_ids
    ):
        auth_client.post(
            reverse("session-reservation-create", kwargs={"session_id": session.id}),
            {"seat_ids": seat_ids},
            format="json",
        )
        client = cache.client.get_client()
        for seat_id in seat_ids:
            assert client.get(f"seat:{session.id}:{seat_id}") is not None

    @pytest.mark.slow
    def should_allow_reservation_after_cart_expires(
        self, auth_client, other_user, session, seat_ids
    ):
        import time
        from apps.reservations.redis import CartRedis

        cart = CartRedis(other_user.id, session.id)
        cart.create(seat_ids, ttl=1)

        time.sleep(2)

        response = auth_client.post(
            reverse("session-reservation-create", kwargs={"session_id": session.id}),
            {"seat_ids": seat_ids},
            format="json",
        )
        assert response.status_code == 201

    def should_return_409_when_cart_already_active(
        self, auth_client, session, seat_ids
    ):
        auth_client.post(
            reverse("session-reservation-create", kwargs={"session_id": session.id}),
            {"seat_ids": seat_ids},
            format="json",
        )
        response = auth_client.post(
            reverse("session-reservation-create", kwargs={"session_id": session.id}),
            {"seat_ids": seat_ids},
            format="json",
        )
        assert response.status_code == 409

    def should_return_409_when_seat_locked_by_other_user(
        self, auth_client, other_user, session, seat_ids
    ):
        other_client = APIClient()
        other_client.force_authenticate(user=other_user)
        other_client.post(
            reverse("session-reservation-create", kwargs={"session_id": session.id}),
            {"seat_ids": seat_ids},
            format="json",
        )
        response = auth_client.post(
            reverse("session-reservation-create", kwargs={"session_id": session.id}),
            {"seat_ids": seat_ids},
            format="json",
        )
        assert response.status_code == 409

    @pytest.mark.django_db(transaction=True)
    def should_allow_only_one_winner_under_concurrent_requests(self, session, seat_ids):
        from django.db import connection

        user1 = User.objects.create_user(
            username="concurrent1", email="concurrent1@test.com", password="x"
        )
        user2 = User.objects.create_user(
            username="concurrent2", email="concurrent2@test.com", password="x"
        )
        results = []

        def make_request(user):
            client = APIClient()
            client.force_authenticate(user=user)
            response = client.post(
                reverse(
                    "session-reservation-create", kwargs={"session_id": session.id}
                ),
                {"seat_ids": seat_ids},
                format="json",
            )
            results.append(response.status_code)
            connection.close()

        t1 = threading.Thread(target=make_request, args=(user1,))
        t2 = threading.Thread(target=make_request, args=(user2,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        assert results.count(201) == 1
        assert results.count(409) == 1

    def should_return_404_when_session_not_found(self, auth_client):
        response = auth_client.post(
            reverse("session-reservation-create", kwargs={"session_id": 99999}),
            {"seat_ids": [1]},
            format="json",
        )
        assert response.status_code == 404

    def should_return_400_when_seat_limit_exceeded(self, auth_client, session, room):
        seat_ids = list(
            Seat.objects.filter(room=room).values_list("id", flat=True)[
                : MAX_SEATS_PER_RESERVATION + 1
            ]
        )
        assert len(seat_ids) == MAX_SEATS_PER_RESERVATION + 1
        response = auth_client.post(
            reverse("session-reservation-create", kwargs={"session_id": session.id}),
            {"seat_ids": seat_ids},
            format="json",
        )
        assert response.status_code == 400

    def should_return_422_when_session_already_started(
        self, auth_client, session, seat_ids
    ):
        future_time = session.starts_at + timedelta(minutes=1)
        with freeze_time(future_time):
            response = auth_client.post(
                reverse(
                    "session-reservation-create", kwargs={"session_id": session.id}
                ),
                {"seat_ids": seat_ids},
                format="json",
            )
        assert response.status_code == 422

    def should_return_422_when_seat_does_not_belong_to_session(
        self, auth_client, session
    ):
        other_room = Room.objects.create(name="Outra Sala", total_seats=5)
        foreign_seat = Seat.objects.create(
            room=other_room, row="Z", number=1, is_active=True
        )
        response = auth_client.post(
            reverse("session-reservation-create", kwargs={"session_id": session.id}),
            {"seat_ids": [foreign_seat.id]},
            format="json",
        )
        assert response.status_code == 422

    def should_return_422_when_seat_is_inactive(self, auth_client, session, room):
        seat = Seat.objects.filter(room=room).first()
        seat.is_active = False
        seat.save()
        response = auth_client.post(
            reverse("session-reservation-create", kwargs={"session_id": session.id}),
            {"seat_ids": [seat.id]},
            format="json",
        )
        assert response.status_code == 422

    def should_return_401_when_not_authenticated(self, client, session, seat_ids):
        response = client.post(
            reverse("session-reservation-create", kwargs={"session_id": session.id}),
            {"seat_ids": seat_ids},
            format="json",
        )
        assert response.status_code == 401
