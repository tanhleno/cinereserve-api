from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from .models import Movie
from .serializers import MovieSerializer


class MovieListView(ListAPIView):
    queryset = Movie.objects.all().order_by("id")
    serializer_class = MovieSerializer
    permission_classes = [AllowAny]
