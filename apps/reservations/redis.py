from django.core.cache import cache
from enum import IntEnum
from .exceptions import CartAlreadyActiveError, SeatsLockedError


class _CartResult(IntEnum):
    OK = 1
    CART_EXISTS = 2
    SEAT_CONFLICT = 3


class CartRedis:
    def __init__(self, user_id: int, session_id: int):
        self.user_id = user_id
        self.session_id = session_id

    @property
    def cart_key(self) -> str:
        return f"cart:{self.user_id}:{self.session_id}"

    @property
    def cart_seats_key(self) -> str:
        return f"cart_seats:{self.user_id}:{self.session_id}"

    @staticmethod
    def get_seat_lock_key(session_id: int, seat_id: int) -> str:
        return f"seat:{session_id}:{seat_id}"

    def _get_seat_lock_key(self, seat_id: int) -> str:
        return CartRedis.get_seat_lock_key(self.session_id, seat_id)

    def exists(self) -> bool:
        return cache.client.get_client().exists(self.cart_key) == 1

    def get_remaining_time(self) -> int:
        ttl = cache.client.get_client().ttl(self.cart_key)
        return max(ttl, 0)

    def release_orphan_locks(self, seat_ids: list) -> None:
        client = cache.client.get_client()
        lock_keys = [self._get_seat_lock_key(seat_id) for seat_id in seat_ids]

        pipe = client.pipeline()
        for lock_key in lock_keys:
            pipe.get(lock_key)
        user_ids = pipe.execute()

        locks_with_owner = [
            (lock_key, int(user_id))
            for lock_key, user_id in zip(lock_keys, user_ids)
            if user_id is not None
        ]

        if not locks_with_owner:
            return

        pipe = client.pipeline()
        for _, user_id in locks_with_owner:
            pipe.exists(f"cart:{user_id}:{self.session_id}")
        results = pipe.execute()

        keys_to_delete = [
            lock_key
            for (lock_key, _), cart_exists in zip(locks_with_owner, results)
            if not cart_exists
        ]
        if keys_to_delete:
            client.delete(*keys_to_delete)

    def delete(self) -> None:
        cache.client.get_client().delete(self.cart_key)

    def create(self, seat_ids: list, ttl: int) -> None:
        lock_keys = [self._get_seat_lock_key(seat_id) for seat_id in seat_ids]
        client = cache.client.get_client()

        with open("apps/reservations/lua/create_cart.lua") as f:
            script = f.read()

        result = client.eval(
            script,
            2 + len(lock_keys),
            self.cart_key,
            self.cart_seats_key,
            *lock_keys,
            ttl,
            str(self.user_id),
            str(self.session_id),
            *[str(s) for s in seat_ids],
        )

        if result == _CartResult.CART_EXISTS:
            raise CartAlreadyActiveError()
        if result == _CartResult.SEAT_CONFLICT:
            raise SeatsLockedError()
