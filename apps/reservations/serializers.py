from rest_framework import serializers
from apps.catalog.models import Seat
from .services import get_seat_status


class SeatStatusSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = Seat
        fields = ["id", "row", "number", "status"]

    def get_status(self, seat):
        session = self.context["session"]
        return get_seat_status(session, seat)
