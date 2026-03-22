from rest_framework import serializers
from .models import Movie, Session


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = [
            "id",
            "title",
            "description",
            "duration_minutes",
            "genre",
            "banner_url",
        ]


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ["id", "movie", "room", "starts_at"]
