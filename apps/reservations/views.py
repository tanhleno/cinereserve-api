from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.utils import timezone
from django.shortcuts import get_object_or_404
from apps.catalog.models import Session, Seat
from .serializers import SeatStatusSerializer
from .exceptions import (
    SeatsUnavailable,
    InvalidSeatsSelection,
    MaxSeatsExceeded,
    ActiveCartExists,
    SeatsLockedError,
    CartAlreadyActiveError,
    SessionAlreadyStarted,
)
from .services import (
    is_seat_limit_exceeded,
    all_seats_exist,
    all_seats_active,
    create_cart,
)


class SessionSeatView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, session_id):
        session = get_object_or_404(Session, pk=session_id)
        seats = Seat.objects.filter(room=session.room)

        serializer = SeatStatusSerializer(
            seats, many=True, context={"session": session}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReservationCreateView(APIView):

    def post(self, request, session_id):
        session = get_object_or_404(Session, pk=session_id)
        seat_ids = request.data.get("seat_ids", [])
        user_id = request.user.id

        if session.starts_at <= timezone.now():
            raise SessionAlreadyStarted()
        if is_seat_limit_exceeded(seat_ids):
            raise MaxSeatsExceeded()
        if not (
            all_seats_exist(seat_ids, session) and all_seats_active(seat_ids, session)
        ):
            raise InvalidSeatsSelection()

        try:
            expires_in = create_cart(user_id, session_id, seat_ids)
            return Response(
                {
                    "expires_in": expires_in,
                    "seat_ids": seat_ids,
                },
                status=status.HTTP_201_CREATED,
            )
        except CartAlreadyActiveError:
            raise ActiveCartExists()
        except SeatsLockedError:
            raise SeatsUnavailable()
