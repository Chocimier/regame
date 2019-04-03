from collections import defaultdict, namedtuple

from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import AttackForm, NewMatchForm, OntoTableForm, HideForm
from .models import CardLocation
from .players import activeusers, competitor, enforceuser, markactive, toplayer, isbot, getparticipant
from .processes import creatematch, formfor, freshmatches, match_or_error, move, ontotable, pendingmatches, removedcard


MoveResult = namedtuple('MoveResult', ['form', 'response'])
MoveResult.__new__.__defaults__ = (None,) * len(MoveResult._fields)

def newmatch(request):
    context = {}
    if request.method == 'POST':
        form = NewMatchForm(request.user, request.POST)
        if form.is_valid():
            enforceuser(request)
            match = creatematch(request.user, form)
            if match:
                return redirect('match', no=match.id)
    else:
        initial = {k: request.GET[k] for k in request.GET}
        if 'player2' in initial:
            initial['player2'] = toplayer(initial['player2'])
        form = NewMatchForm(request.user, initial=initial)
    context['form'] = form
    return render(request, 'regame/new_match.html', context)

@login_required()
def refill(request, no):
    match = match_or_error(no, request)
    participant = getparticipant(match, request.user)
    if request.method == 'POST':
        form = OntoTableForm(request.POST)
        if form.is_valid():
            ontotable(participant, form.cleaned_data['put_card'])
    return MoveResult(response=redirect('match', no=match.id))

@login_required()
def attack(request, no):
    match = match_or_error(no, request)
    participant = getparticipant(match, request.user)
    if request.method == 'POST':
        moveformreceived = AttackForm(request.POST)
        if moveformreceived.is_valid():
            move(participant, moveformreceived.order(), moveformreceived.cleaned_data['target_card'])
        else:
            return MoveResult(form=moveformreceived)
    return MoveResult(response=redirect('match', no=match.id))


def match(request, no):
    match = match_or_error(no, request)
    form = None
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'attack':
            result = attack(request, no)
        elif action == 'refill':
            result = refill(request, no)
        else:
            return redirect('match', no=no)
        if result.response:
            return result.response
        elif result.form:
            form = result.form
    participant = getparticipant(match, request.user)
    cleanform, actionurl = formfor(participant)
    if not form:
        form = cleanform
    competitorparticipant = competitor(participant)
    ownhandcards = participant.cards.filter(location=CardLocation.HAND).order_by('index')
    owntablecards = participant.cards.filter(location=CardLocation.TABLE).order_by('index')
    competitortablecards = competitorparticipant.cards.filter(location=CardLocation.TABLE).order_by('index')
    ownhandwidgets = form.widgetsfor(CardLocation.HAND, competitor=False) if form else defaultdict(lambda: None)
    owntablewidgets = form.widgetsfor(CardLocation.TABLE, competitor=False) if form else defaultdict(lambda: None)
    competitortablewidgets = form.widgetsfor(CardLocation.TABLE, competitor=True) if form else defaultdict(lambda: None)
    fresh = freshmatches(participant.player) if isbot(competitorparticipant.player) else []
    context = {
        'actionurl': actionurl,
        'match': match,
        'player': participant.player,
        'competitor': competitorparticipant.player,
        'playerscore': participant.score,
        'competitorscore': competitorparticipant.score,
        'yourremovedcard': removedcard(participant),
        'competitorsremovedcard': removedcard(competitorparticipant),
        'ownhandcards': [{'card': card, 'widget': ownhandwidgets[i]} for i, card in enumerate(ownhandcards)],
        'owntablecards': [{'card': card, 'widget': owntablewidgets[i]} for i, card in enumerate(owntablecards)],
        'competitortablecards': [{'card': card, 'widget': competitortablewidgets[i]} for i, card in enumerate(competitortablecards)],
        'form': form,
        'reloading': (match.active and not actionurl),
        'freshmatches': fresh,
    }
    return render(request, 'regame/match.html', context)



def main(request):
    player = request.user
    if player.is_authenticated:
        markactive(player)
        fresh = freshmatches(player)
        pending = pendingmatches(player)
    else:
        fresh = []
        pending = []
    users = ({
        'displayname': user.userprofile.display_name(),
        'lastseen': user.userprofile.lastseen,
        'username': user.username,
    } for user in activeusers())
    context = {
        'freshmatches': fresh,
        'pendingmatches': pending,
        'activeusers': users,
    }
    if request.user.is_authenticated:
        context['hideform'] = HideForm(instance=request.user.userprofile, initial={'hidden': not request.user.userprofile.hidden})
    else:
        context['hideform'] = HideForm(initial={'hidden': False})
    return render(request, 'regame/main.html', context)


def playerhidden(request):
    if request.method == 'POST':
        enforceuser(request)
        form = HideForm(request.POST, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
    return redirect('main')

def forget(request):
    if not request.user.is_authenticated:
        return redirect('main')
    player = request.user
    logout(request)
    if player.userprofile.temporary:
        player.delete()
    return redirect('main')


def helppage(request):
    return render(request, 'regame/helppage.html')


def contactpage(request):
    return render(request, 'regame/contact.html')
