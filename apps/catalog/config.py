# apps/reservations/config.py
from django.conf import settings

SEATS_PER_ROW = getattr(settings, "SEATS_PER_ROW", 10)
PRE_SESSION_MINUTES = getattr(settings, "PRE_SESSION_MINUTES", 15)
POST_SESSION_MINUTES = getattr(settings, "POST_SESSION_MINUTES", 15)
