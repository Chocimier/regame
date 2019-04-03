from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from enumfields import EnumField, Enum as LabeledEnum
from enum import Enum
from django.db.models.signals import post_save

class Card(models.Model):
    text = models.CharField(max_length=12)
    patternbit = models.CharField(max_length=12)


class WinConditionType(LabeledEnum):
    POINTS_GET = 'g'
    POINTS_AHEAD = 'a'
    TURNS = 't'

    class Labels:
        POINTS_GET = 'get that many points'
        POINTS_AHEAD = 'get that many more points'
        TURNS = 'have more points after that many turns'


class MatchStatus(Enum):
    FRESH = 'f'
    PENDING = 'p'
    ENDED = 'e'
    REJECTED = 'r'


class MoveKind(Enum):
    ATTACK = 'a'
    THROWOUT = 't'


def nextmovekind(kind):
    nextmap = {
        MoveKind.ATTACK: MoveKind.THROWOUT,
        MoveKind.THROWOUT: MoveKind.ATTACK,
    }
    return nextmap.get(kind, MoveKind.ATTACK)


DEFAULT_WIN_CONDITION_NUMBER = 21
PLAYER_INDEX_CHOICES = [(i, i) for i in (0, 1)]


class Match(models.Model):
    currentparticipant = models.PositiveSmallIntegerField(choices=PLAYER_INDEX_CHOICES, null=True)
    status = EnumField(MatchStatus, default='f', max_length=1)
    winconditiontype = EnumField(WinConditionType, max_length=1, default=WinConditionType.POINTS_GET)
    winconditionnumber = models.PositiveSmallIntegerField(default=DEFAULT_WIN_CONDITION_NUMBER)
    turnspassed = models.PositiveIntegerField(default=0)


    @property
    def player1(self):
        return self.participants.get(index=0).player


    @property
    def player2(self):
        return self.participants.get(index=1).player


    @property
    def current(self):
        return self.participants.get(index=self.currentparticipant).player


    @property
    def player1score(self):
        return self.participants.get(index=0).score


    @property
    def player2score(self):
        return self.participants.get(index=1).score


    def result(self, player):
        if player == self.player1:
            return self.player1score
        else:
            return self.player2score


    @staticmethod
    def activestates():
        return (MatchStatus.FRESH, MatchStatus.PENDING)

    @property
    def active(self):
        return self.status in self.activestates()


    def activatenextparticipant(self):
        if self.currentparticipant == 0:
            self.turnspassed += 1
        self.currentparticipant = (self.currentparticipant + 1) % 2


class MatchParticipant(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='participants')
    player = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    index = models.PositiveSmallIntegerField()
    score = models.IntegerField(default=0)
    activity = models.TextField()
    chat = models.CharField(max_length=200)
    drawoffer = models.BooleanField(default=False)
    movekind = EnumField(MoveKind, max_length=1, default=MoveKind.ATTACK)


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
    participant = models.ForeignKey(MatchParticipant, on_delete=models.CASCADE, null=True, related_name='cards')
    location = EnumField(CardLocation, max_length=1)
    index = models.PositiveSmallIntegerField()
    card = models.ForeignKey(Card, on_delete=models.PROTECT, null=True)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    temporary = models.BooleanField(default=False)
    sound = models.BooleanField(default=False)
    hidden = models.BooleanField(default=False)
    lastseen = models.DateTimeField(auto_now_add=True, null=True)

    def display_name(self):
        if self.user.first_name:
            return self.user.first_name
        elif self.temporary:
            return "a stranger"
        else:
            return self.user.username


def create_profile(sender, *, created=False, instance=None, **kwargs):
    if created:
        user_profile = UserProfile(user=instance)
        user_profile.save()

post_save.connect(create_profile, sender=User)
