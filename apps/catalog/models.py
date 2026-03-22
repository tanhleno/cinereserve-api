from django.db import models
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.conf import settings


class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    duration_minutes = models.PositiveIntegerField()
    genre = models.CharField(max_length=100)
    banner_url = models.URLField()

    def __str__(self):
        return self.title


class Room(models.Model):
    name = models.CharField(max_length=255)
    total_seats = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Seat(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="seats")
    row = models.CharField(max_length=10)
    number = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.room} - {self.row}{self.number}"


class Session(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="sessions")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="sessions")
    starts_at = models.DateTimeField()

    def clean(self):
        pre = timedelta(minutes=settings.PRE_SESSION_MINUTES)
        post = timedelta(minutes=settings.POST_SESSION_MINUTES)
        duration = timedelta(minutes=self.movie.duration_minutes)

        new_start = self.starts_at - pre
        new_end = self.starts_at + duration + post

        conflicting = Session.objects.filter(
            room=self.room,
            starts_at__lt=new_end,
            starts_at__gt=new_start - timedelta(minutes=self.movie.duration_minutes),
        ).exclude(pk=self.pk)

        if conflicting.exists():
            raise ValidationError("Room already occupied at this time.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.movie} - {self.room} - {self.starts_at}"
