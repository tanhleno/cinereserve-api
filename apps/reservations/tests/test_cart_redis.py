import pytest
import time
from django.core.cache import cache
from django.contrib.auth import get_user_model
from apps.reservations.redis import CartRedis
from apps.reservations.config import SEAT_LOCK_TIMEOUT

User = get_user_model()


class TestCartRedis:

    @pytest.mark.slow
    def should_expire_cart_key_after_ttl(self, user, session, seat_ids):
        cart = CartRedis(user.id, session.id)
        cart.create(seat_ids, ttl=1)

        client = cache.client.get_client()
        assert client.exists(f"cart:{user.id}:{session.id}") == 1

        time.sleep(2)

        assert client.exists(f"cart:{user.id}:{session.id}") == 0

    @pytest.mark.slow
    def should_release_orphan_locks_after_cart_expires(self, user, session, seat_ids):
        cart = CartRedis(user.id, session.id)
        cart.create(seat_ids, ttl=1)

        client = cache.client.get_client()
        for seat_id in seat_ids:
            assert (
                client.get(CartRedis.get_seat_lock_key(session.id, seat_id)) is not None
            )

        time.sleep(2)

        cart.release_orphan_locks(seat_ids)

        for seat_id in seat_ids:
            assert client.get(CartRedis.get_seat_lock_key(session.id, seat_id)) is None
