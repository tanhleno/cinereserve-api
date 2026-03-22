from django.core.cache import cache


def get_seat_status(session, seat):
    if not seat.is_active:
        return "unavailable"

    lock_key = f"seat:{session.id}:{seat.id}"
    lock = cache.get(lock_key)

    if lock is None:
        return "available"

    cart_key = f"cart:{lock}"
    cart = cache.get(cart_key)

    if cart is None:
        return "available"  # órfão

    return "reserved"
