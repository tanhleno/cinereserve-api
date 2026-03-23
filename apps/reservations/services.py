from django.core.cache import cache
from apps.catalog.models import Seat
from .redis import CartRedis
from .config import SEAT_LOCK_TIMEOUT, MAX_SEATS_PER_RESERVATION


def get_seat_status(session, seat):
    if not seat.is_active:
        return "unavailable"

    client = cache.client.get_client()
    user_id = client.get(CartRedis.get_seat_lock_key(session.id, seat.id))

    if user_id is None:
        return "available"

    cart = CartRedis(int(user_id), session.id)
    if not cart.exists():
        return "available"  # órfão

    return "reserved"


def all_seats_exist(seat_ids: list, session) -> bool:
    found_count = Seat.objects.filter(id__in=seat_ids, room=session.room).count()
    return found_count == len(seat_ids)


def is_seat_limit_exceeded(seat_ids: list) -> bool:
    return len(seat_ids) > MAX_SEATS_PER_RESERVATION


def all_seats_active(seat_ids: list, session) -> bool:
    return not Seat.objects.filter(
        id__in=seat_ids, room=session.room, is_active=False
    ).exists()


def create_cart(user_id: int, session_id: int, seat_ids: list) -> int:
    cart = CartRedis(user_id, session_id)
    cart.release_orphan_locks(seat_ids)
    cart.create(seat_ids, SEAT_LOCK_TIMEOUT)
    return SEAT_LOCK_TIMEOUT
