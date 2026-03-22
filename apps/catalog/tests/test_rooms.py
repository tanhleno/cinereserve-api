import pytest
from apps.catalog.models import Room, Seat


@pytest.mark.django_db
class TestRoomSignal:

    def should_create_seats_when_room_is_created(self):
        room = Room.objects.create(name="Sala 1", total_seats=50)
        assert Seat.objects.filter(room=room).count() == 50

    def should_create_correct_number_of_rows(self):
        room = Room.objects.create(name="Sala 1", total_seats=50)
        rows = Seat.objects.filter(room=room).values_list("row", flat=True).distinct()
        assert len(rows) == 5

    def should_create_seats_with_is_active_true_by_default(self):
        room = Room.objects.create(name="Sala 1", total_seats=50)
        assert Seat.objects.filter(room=room, is_active=False).count() == 0
