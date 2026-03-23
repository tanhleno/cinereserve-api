# apps/reservations/config.py
from django.conf import settings

SEAT_LOCK_TIMEOUT = getattr(settings, "SEAT_LOCK_TIMEOUT", 600)
MAX_SEATS_PER_RESERVATION = getattr(settings, "MAX_SEATS_PER_RESERVATION", 8)
