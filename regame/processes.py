from django.urls import reverse
from .forms import MoveForm, OntoTableForm
from .models import Card, Match, PossessedCard, CardLocation, slotscount
import random
import re
import sre_constants

def randomcard():
    count = Card.objects.count()
    index = random.randint(0, count-1)
    return Card.objects.all()[index]

def creatematch(player1, player2):
    match = Match(player1=player1, player2=player2, current=player2)
    match.save()
    for player in [player1, player2]:
        for location in CardLocation:
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

def ontotable(match, player, index):
    if player != match.current:
        return None
    gap = PossessedCard.objects.filter(match=match, player=player, location=CardLocation.TABLE, card=None)[0]
    put_card = PossessedCard.objects.filter(match=match, player=player, location=CardLocation.HAND, index=index)[0]
    gap.card = put_card.card
    put_card.card = randomcard()
    gap.save()
    put_card.save()

def move(match, player, order, target):
    if player != match.current:
        return None
    if not order:
        return None
    targetcard = PossessedCard.objects.filter(match=match, player=competitor(match, player), location=CardLocation.TABLE, index=target)[0]
    targettext = targetcard.card.text
    pattern = ''
    for i in order:
        card = PossessedCard.objects.filter(match=match, player=player, location=CardLocation.TABLE, index=i)[0].card
        pattern += card.patternbit
    score_increase = score(targettext, pattern)
    if player == match.player1:
        match.player1score += score_increase
    else:
        match.player2score += score_increase
    match.current = competitor(match, player)
    match.save()
    if score_increase > 0:
        targetcard.card = None
        targetcard.save()
    return "You attacked {} with {}". format(targettext, ''.join(pattern))

def formfor(match, player):
     if match.current != player:
         return (None, '')
     elif PossessedCard.objects.filter(match=match, player=player, card=None).count() > 0:
         return (OntoTableForm(), reverse('match_refill', kwargs={'no': match.id}))
     else:
         return (MoveForm(), reverse('match_attack', kwargs={'no': match.id}))
