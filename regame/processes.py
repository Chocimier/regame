from .models import Card, Match, PossessedCard, CardLocation, slotscount
import random
import re

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
    match = re.search(pattern, text)
    return len(match.group(0)) if match else 0

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
