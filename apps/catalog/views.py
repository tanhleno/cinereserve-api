from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from .models import Movie, Session
from .serializers import MovieSerializer, SessionSerializer
from django.shortcuts import get_object_or_404


class MovieListView(ListAPIView):
    queryset = Movie.objects.all().order_by("id")
    serializer_class = MovieSerializer
    permission_classes = [AllowAny]


class SessionListView(ListAPIView):
    serializer_class = SessionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        movie = get_object_or_404(Movie, pk=self.kwargs["movie_id"])
        return Session.objects.filter(movie=movie).order_by("starts_at")
