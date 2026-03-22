from django.db import models


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
