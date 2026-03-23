from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Room, Seat
from .config import SEATS_PER_ROW


@receiver(post_save, sender=Room)
def create_seats(sender, instance, created, **kwargs):
    if not created:
        return

    seats_per_row = SEATS_PER_ROW
    total_rows = instance.total_seats // seats_per_row

    seats = []
    for row_index in range(total_rows):
        row_letter = chr(ord("A") + row_index)
        for number in range(1, seats_per_row + 1):
            seats.append(Seat(room=instance, row=row_letter, number=number))

    Seat.objects.bulk_create(seats)
