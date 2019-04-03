from asgiref.sync import async_to_sync
from channels import layers
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import Http404
from django.urls import reverse

from .bot import handle as bot_handle
from .forms import AttackForm, OntoTableForm
from .models import Card, Match, PossessedCard, CardLocation, slotscount, WinConditionType, MatchStatus, MatchParticipant
from .players import competitor, getparticipant, isbot, havemove
import random
import re
import sre_constants


def randomcard():
    count = Card.objects.count()
    index = random.randint(0, count-1)
    return Card.objects.all()[index]


def creatematch(player1, form):
    cleaned_data = {**form.cleaned_data}
    player2 = cleaned_data.pop('player2')
    if player1 == player2:
        return None
    match = Match(**cleaned_data, currentparticipant=1)
    match.save()
    for i, player in enumerate([player1, player2]):
        participant = MatchParticipant(match=match, player=player, index=i)
        participant.save()
        for location in CardLocation:
            if location == CardLocation.REMOVED:
                continue
            for i in range(slotscount(location)):
                card = randomcard()
                posessed = PossessedCard(participant=participant, location=location, index=i, card=card)
                posessed.save()
    if isbot(match.current):
        bot_handle(getparticipant(match, match.current))
    return match


def score(text, pattern):
    try:
        match = re.search(pattern, text)
    except sre_constants.error:
        match = None
    return len(match.group(0)) if match else 0


def ontotable(participant, index):
    if not havemove(participant):
        return
    gap = participant.cards.filter(location=CardLocation.TABLE, card=None).first()
    if not gap:
        return
    put_card = participant.cards.filter(location=CardLocation.HAND, index=index).first()
    if not put_card:
        return
    gap.card = put_card.card
    put_card.card = randomcard()
    gap.save()
    put_card.save()
    participant.match.status = MatchStatus.PENDING
    participant.match.save()
    notify_moved(participant)


def matchwon(match):
    if match.winconditiontype == WinConditionType.POINTS_GET and max(match.player1score, match.player2score) >= match.winconditionnumber:
        return True
    if match.winconditiontype == WinConditionType.POINTS_AHEAD and abs(match.player1score - match.player2score) >= match.winconditionnumber:
        return True
    if match.winconditiontype == WinConditionType.TURNS and match.turnspassed >= match.winconditionnumber:
        return True
    return False


def move(participant, order, target):
    if not havemove(participant):
        return None
    if not order:
        return None
    competitorparticipant = competitor(participant)
    targetcard = competitorparticipant.cards.filter(location=CardLocation.TABLE, index=target).first()
    if not targetcard:
        return
    targettext = targetcard.card.text
    pattern = ''
    for i in order:
        possessedcard = participant.cards.filter(location=CardLocation.TABLE, index=i).first()
        if not possessedcard:
            return
        pattern += possessedcard.card.patternbit
    score_increase = score(targettext, pattern)
    participant.score += score_increase
    participant.save()
    if score_increase > 0:
        PossessedCard.objects.update_or_create(
            participant=competitorparticipant, location=CardLocation.REMOVED, index=0,
            defaults={'card': targetcard.card})
        targetcard.card = None
        targetcard.save()
    participant.match.activatenextparticipant()
    participant.match.status = MatchStatus.ENDED if matchwon(participant.match) else MatchStatus.PENDING
    participant.match.save()
    if participant.match.active and isbot(competitorparticipant.player):
        bot_handle(competitorparticipant)
    notify_moved(participant)
    return "You attacked {} with {}". format(targettext, ''.join(pattern))


def formfor(participant):
    if not havemove(participant):
        return (None, '')
    elif participant.cards.filter(card=None).exists():
        return (OntoTableForm(), reverse('match', kwargs={'no': participant.match_id}))
    else:
        return (AttackForm(), reverse('match', kwargs={'no': participant.match_id}))


def removedcard(participant):
    possessed = participant.cards.filter(location=CardLocation.REMOVED).first()
    return possessed.card if possessed else None


def freshmatches(player):
    return [
        {'match': p.match, 'competitor': competitor(p).player}
        for p in player.matchparticipant_set.filter(index=1, match__status=MatchStatus.FRESH).order_by('-pk')
    ]


def pendingmatches(player):
    return [
        {'match': p.match, 'competitor': competitor(p).player}
        for p in player.matchparticipant_set.filter(
            Q(match__status=MatchStatus.PENDING) |
            Q(index=0, match__status=MatchStatus.FRESH) ).order_by('-pk')
    ]


def channelgroupname(match):
    if isinstance(match, Match):
        match = match.id
    return 'match_{}'.format(match)


def notify_moved(participant):
    channel_layer = layers.get_channel_layer()
    group = channelgroupname(participant.match_id)
    content = {
            'type': 'notify.move',
            'player': participant.player.username,
        }
    async_to_sync(channel_layer.group_send)(
        group,
        content
    )


def match_or_error(no, request):
    try:
        match = Match.objects.get(id=no)
    except Match.DoesNotExist:
        raise Http404('No such match.')
    if not match.participants.filter(player=request.user).exists():
        raise PermissionDenied('You do not play that match.')
    return match
