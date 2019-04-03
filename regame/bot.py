import itertools
from collections import namedtuple

from . import processes
from .models import CardLocation, slotscount
from .players import competitor


def handle(participant):
    ontotable(participant)
    move(participant)


def ontotable(participant):
    ontablecards = [i.card for i in participant.cards.filter(location=CardLocation.TABLE).order_by('index')]
    if None not in ontablecards:
        return
    competitorparticipant = competitor(participant)
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
    processes.ontotable(participant, bestcard)


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


def move(participant):
    competitorparticipant = competitor(participant)
    owncards = [i.card for i in participant.cards.filter(location=CardLocation.TABLE).order_by('index')]
    competitorcards = [i.card for i in competitorparticipant.cards.filter(location=CardLocation.TABLE).order_by('index')]
    best = bestmove(owncards, competitorcards)
    processes.move(participant, best.order, best.target)
