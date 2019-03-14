from django.db import models
from django.conf import settings
from enumfields import EnumField
from enum import Enum

class Card(models.Model):
    text = models.CharField(max_length=10)
    patternbit = models.CharField(max_length=10)


class Match(models.Model):
    player1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='match_as_player1_set')
    player2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='match_as_player2_set')
    current = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='match_as_current_set')
    player1score = models.IntegerField(default=0)
    player2score = models.IntegerField(default=0)
    active = models.BooleanField(default=True)

    def result(self, player):
        if player == self.player1:
            return self.player1score
        else:
            return self.player2score


class CardLocation(Enum):
    TABLE = 't'
    HAND = 'h'

def slotscount(location):
    count = {
        CardLocation.TABLE: 3,
        CardLocation.HAND: 4,
    }
    return count[location]

class PossessedCard(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    location = EnumField(CardLocation, max_length=1)
    index = models.PositiveSmallIntegerField()
    card = models.ForeignKey(Card, on_delete=models.PROTECT)
