from django.db import models


class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    duration_minutes = models.PositiveIntegerField()
    genre = models.CharField(max_length=100)
    banner_url = models.URLField()

    def __str__(self):
        return self.title
