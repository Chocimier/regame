from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from enumfields import EnumField
from enum import Enum
from django.db.models.signals import post_save

class Card(models.Model):
    text = models.CharField(max_length=12)
    patternbit = models.CharField(max_length=12)


class Match(models.Model):
    player1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='match_as_player1_set')
    player2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='match_as_player2_set')
    current = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='match_as_current_set')
    player1score = models.IntegerField(default=0)
    player2score = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    score_to_win = models.PositiveSmallIntegerField(default=40)

    def result(self, player):
        if player == self.player1:
            return self.player1score
        else:
            return self.player2score


class CardLocation(Enum):
    TABLE = 't'
    HAND = 'h'
    REMOVED = 'r'

def slotscount(location):
    count = {
        CardLocation.TABLE: 3,
        CardLocation.HAND: 4,
        CardLocation.REMOVED: 1,
    }
    return count[location]

class PossessedCard(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    location = EnumField(CardLocation, max_length=1)
    index = models.PositiveSmallIntegerField()
    card = models.ForeignKey(Card, on_delete=models.PROTECT, null=True)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    temporary = models.BooleanField(default=False)
    sound = models.BooleanField(default=False)
    lastseen = models.DateTimeField(auto_now_add=True, null=True)

    def display_name(self):
        if self.user.first_name:
            return self.user.first_name
        elif self.user.userprofile.temporary:
            return "a stranger"
        else:
            return self.user.username


def create_profile(sender, *, created=False, instance=None, **kwargs):
    if created:
        user_profile = UserProfile(user=instance)
        user_profile.save()

post_save.connect(create_profile, sender=User)
