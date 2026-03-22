from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from apps.catalog.models import Movie, Room, Session


class Command(BaseCommand):
    help = "Seed sessions between a date range"

    def add_arguments(self, parser):
        parser.add_argument("--days-ahead", type=int, default=7)
        parser.add_argument("--count", type=int, default=10)

    def handle(self, *args, **options):
        movies = list(Movie.objects.all())
        rooms = list(Room.objects.all())

        if not movies or not rooms:
            self.stdout.write("No movies or rooms found.")
            return

        days_ahead = options["days_ahead"]
        count = options["count"]
        created = 0
        now = timezone.now()

        for _ in range(count):
            movie = random.choice(movies)
            room = random.choice(rooms)
            random_minutes = random.randint(0, days_ahead * 24 * 60)
            starts_at = now + timedelta(minutes=random_minutes)

            session = Session(movie=movie, room=room, starts_at=starts_at)
            try:
                session.full_clean()
                session.save()
                created += 1
            except Exception:
                pass

        self.stdout.write(f"{created}/{count} sessions created.")
