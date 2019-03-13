from .models import Card, Match, PossessedCard, CardLocation, slotscount
import random

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

def move(match, player, order, target):
    if not order:
        return None
    targettext = PossessedCard.objects.filter(match=match, player=competitor(match, player), location=CardLocation.TABLE, index=target)[0].card.text
    pattern = ''
    for i in order:
        card = PossessedCard.objects.filter(match=match, player=player, location=CardLocation.TABLE, index=i)[0].card
        pattern += card.patternbit
    return "You attacked {} with {}". format(targettext, ''.join(pattern))
