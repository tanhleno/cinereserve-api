from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.shortcuts import get_object_or_404
from apps.catalog.models import Session, Seat
from .serializers import SeatStatusSerializer


class SessionSeatView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, session_id):
        session = get_object_or_404(Session, pk=session_id)
        seats = Seat.objects.filter(room=session.room)

        serializer = SeatStatusSerializer(
            seats, many=True, context={"session": session}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
