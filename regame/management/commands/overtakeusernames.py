from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError


class Command(BaseCommand):
    help = 'Overtakes usernames that should be not available for players'

    def handle(self, *args, **options):
        reserved = [
            'a stranger',
            'admin',
            'bot',
            'stranger',
            'you',
            'your',
        ]
        for username in reserved:
            try:
                player = get_user_model().objects.create_user(username=username)
            except IntegrityError:
                player = get_user_model().objects.get(username=username)
            player.userprofile.hidden = True
            player.userprofile.save()
