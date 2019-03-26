from django.urls import reverse
from .forms import AttackForm, OntoTableForm
from .models import Card, Match, PossessedCard, CardLocation, slotscount, WinConditionType, MatchStatus
import random
import re
import sre_constants

def randomcard():
    count = Card.objects.count()
    index = random.randint(0, count-1)
    return Card.objects.all()[index]

def creatematch(player1, form):
    player2 = form.cleaned_data['player2']
    if player1 == player2:
        return None
    match = Match(**form.cleaned_data, player1=player1, current=player2)
    match.save()
    for player in [player1, player2]:
        for location in CardLocation:
            if location == CardLocation.REMOVED:
                continue
            for i in range(slotscount(location)):
                card = randomcard()
                posessed = PossessedCard(match=match, player=player, location=location, index=i, card=card)
                posessed.save()
    return match

def competitor(match, player):
    return match.player1 if player == match.player2 else match.player2

def score(text, pattern):
    try:
        match = re.search(pattern, text)
    except sre_constants.error:
        match = None
    return len(match.group(0)) if match else 0

def scoreof(match, player):
    if player == match.player1:
        return match.player1score
    else:
        return match.player2score

def ontotable(match, player, index):
    if not match.active:
        return
    if player != match.current:
        return
    gap = PossessedCard.objects.filter(match=match, player=player, location=CardLocation.TABLE, card=None).first()
    if not gap:
        return
    put_card = PossessedCard.objects.filter(match=match, player=player, location=CardLocation.HAND, index=index).first()
    if not put_card:
        return
    gap.card = put_card.card
    put_card.card = randomcard()
    gap.save()
    put_card.save()
    match.status = MatchStatus.PENDING
    match.save()

def matchwon(match):
    if match.winconditiontype == WinConditionType.POINTS_GET and max(match.player1score, match.player2score) >= match.winconditionnumber:
        return True
    if match.winconditiontype == WinConditionType.POINTS_AHEAD and abs(match.player1score - match.player2score) >= match.winconditionnumber:
        return True
    if match.winconditiontype == WinConditionType.TURNS and match.turnspassed >= match.winconditionnumber:
        return True
    return False

def move(match, player, order, target):
    if not match.active:
        return None
    if player != match.current:
        return None
    if not order:
        return None
    competitorplayer = competitor(match, player)
    targetcard = PossessedCard.objects.filter(match=match, player=competitorplayer, location=CardLocation.TABLE, index=target).first()
    if not targetcard:
        return
    targettext = targetcard.card.text
    pattern = ''
    for i in order:
        possessedcard = PossessedCard.objects.filter(match=match, player=player, location=CardLocation.TABLE, index=i).first()
        if not possessedcard:
            return
        pattern += possessedcard.card.patternbit
    score_increase = score(targettext, pattern)
    if player == match.player1:
        match.player1score += score_increase
        match.turnspassed += 1
    else:
        match.player2score += score_increase
    if matchwon(match):
        match.status = MatchStatus.ENDED
    else:
        match.status = MatchStatus.PENDING
    match.current = competitorplayer
    if score_increase > 0:
        PossessedCard.objects.update_or_create(
            match=match, player=competitorplayer, location=CardLocation.REMOVED, index=0,
            defaults={'card': targetcard.card})
        targetcard.card = None
        targetcard.save()
    match.save()
    return "You attacked {} with {}". format(targettext, ''.join(pattern))

def formfor(match, player):
    noneform = (None, '')
    if not match.active:
        return noneform
    if match.current != player:
        return noneform
    elif PossessedCard.objects.filter(match=match, player=player, card=None).exists():
        return (OntoTableForm(), reverse('match', kwargs={'no': match.id}))
    else:
        return (AttackForm(), reverse('match', kwargs={'no': match.id}))

def removedcard(match, player):
    possessed = PossessedCard.objects.filter(match=match, location=CardLocation.REMOVED, player=player).first()
    return possessed.card if possessed else None
