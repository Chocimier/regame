from .models import Card, Match, PossessedCard, CardLocation, slotscount
import random

def randomcard():
    count = Card.objects.count()
    index = random.randint(0, count-1)
    return Card.objects.all()[index]

def creatematch(player1, player2):
    match = Match(player1=player1, player2=player2)
    match.save()
    for player in [player1, player2]:
        for location in CardLocation:
            for i in range(slotscount(location)):
                card = randomcard()
                posessed = PossessedCard(match=match, player=player, location=location, index=i, card=card)
                posessed.save()
    return match