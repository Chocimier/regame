import itertools
from collections import namedtuple

from . import processes
from .models import CardLocation, PossessedCard, slotscount

def handle(match, player):
    ontotable(match, player)
    move(match, player)

def ontotable(match, player):
    participant = match.participants.get(player=player)
    competitorparticipant = match.participants.exclude(player=player).get()
    ontablecards = [i.card for i in participant.cards.filter(location=CardLocation.TABLE).order_by('index')]
    inhandcards = [i.card for i in participant.cards.filter(location=CardLocation.HAND).order_by('index')]
    competitorcards = [i.card for i in competitorparticipant.cards.filter(location=CardLocation.TABLE).order_by('index')]
    bestscore = -1
    bestcard = 0
    for i, newcard in enumerate(inhandcards):
        newtable = [card if card else newcard for card in ontablecards]
        bestofhand = bestmove(newtable, competitorcards)
        if bestofhand.score > bestscore:
            bestscore = bestofhand.score
            bestcard = i
    processes.ontotable(match, player, bestcard)

BestMoveResult = namedtuple('BestMoveResult', ['order', 'target', 'score'])

def bestmove(owncards, competitorcards):
    order = range(slotscount(CardLocation.TABLE))
    max_score = -1
    target = 0
    for r in range(1, slotscount(CardLocation.TABLE)+1):
        for perm in itertools.permutations(range(slotscount(CardLocation.TABLE)), r=r):
            pattern = ''
            for i in perm:
                card = owncards[i]
                pattern += card.patternbit
            for t, targetcard in enumerate(competitorcards):
                score = processes.score(targetcard.text, pattern)
                if max_score < score:
                    max_score = score
                    order = perm[:]
                    target = t
    return BestMoveResult(order, target, max_score)

def move(match, player):
    participant = match.participants.get(player=player)
    competitorparticipant = match.participants.exclude(player=player).get()
    owncards = [i.card for i in participant.cards.filter(location=CardLocation.TABLE).order_by('index')]
    competitorcards = [i.card for i in competitorparticipant.cards.filter(location=CardLocation.TABLE).order_by('index')]
    best = bestmove(owncards, competitorcards)
    processes.move(match, player, best.order, best.target)
