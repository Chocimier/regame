from collections import defaultdict, namedtuple

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .forms import AttackForm, NewMatchForm, OntoTableForm, HideForm
from .models import Match, PossessedCard, CardLocation
from .players import activeusers, enforceuser, markactive, toplayer
from .processes import creatematch, competitor, formfor, move, ontotable, removedcard

def error(request, message, code=200):
    return render(request, 'regame/error.html', {'message': message}, status=code)

MoveResult = namedtuple('MoveResult', ['form', 'response'])
MoveResult.__new__.__defaults__ = (None,) * len(MoveResult._fields)

def newmatch(request):
    context = {}
    if request.method == 'POST':
        form = NewMatchForm(request.POST)
        if form.is_valid():
            enforceuser(request)
            match = creatematch(request.user, form)
            return redirect('match', no=match.id)
    else:
        initial = {k: request.GET[k] for k in request.GET}
        if 'player2' in initial:
            initial['player2'] = toplayer(initial['player2'])
        form = NewMatchForm(initial=initial)
    context['form'] = form
    return render(request, 'regame/new_match.html', context)

@login_required()
def refill(request, no):
    try:
        match = Match.objects.get(id=no)
    except Match.DoesNotExist:
        return error(request, 'No such match.', 404)
    if request.user != match.player1 and request.user != match.player2:
        return error(request, 'You do not play that match.', 403)
    player = request.user
    if request.method == 'POST':
        form = OntoTableForm(request.POST)
        if form.is_valid():
            ontotable(match, player, form.cleaned_data['put_card'])
    return MoveResult(response=redirect('match', no=match.id))

@login_required()
def attack(request, no):
    try:
        match = Match.objects.get(id=no)
    except Match.DoesNotExist:
        return error(request, 'No such match.', 404)
    if request.user != match.player1 and request.user != match.player2:
        return error(request, 'You do not play that match.', 403)
    player = request.user
    if request.method == 'POST':
        moveformreceived = AttackForm(request.POST)
        if moveformreceived.is_valid():
            move(match, player, moveformreceived.order(), moveformreceived.cleaned_data['target_card'])
        else:
            return MoveResult(form=moveformreceived)
    return MoveResult(response=redirect('match', no=match.id))

@login_required()
def match(request, no):
    try:
        match = Match.objects.get(id=no)
    except Match.DoesNotExist:
        return error(request, 'No such match.', 404)
    player = request.user
    form = None
    if player != match.player1 and player != match.player2:
        return error(request, 'You do not play that match.', 403)
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
    other = competitor(match, player)
    cleanform, actionurl = formfor(match, player)
    if not form:
        form = cleanform
    ownhandcards = PossessedCard.objects.filter(match=match, player=player, location=CardLocation.HAND).order_by('index')
    owntablecards = PossessedCard.objects.filter(match=match, player=player, location=CardLocation.TABLE).order_by('index')
    competitortablecards = PossessedCard.objects.filter(match=match, player=other, location=CardLocation.TABLE).order_by('index')
    ownhandwidgets = form.widgetsfor(CardLocation.HAND, competitor=False) if form else defaultdict(lambda: None)
    owntablewidgets = form.widgetsfor(CardLocation.TABLE, competitor=False) if form else defaultdict(lambda: None)
    competitortablewidgets = form.widgetsfor(CardLocation.TABLE, competitor=True) if form else defaultdict(lambda: None)
    context = {
        'actionurl': actionurl,
        'match': match,
        'player': player,
        'competitor': other,
        'playerscore': match.result(player),
        'competitorscore': match.result(other),
        'yourremovedcard': removedcard(match, player),
        'competitorsremovedcard': removedcard(match, other),
        'ownhandcards': [{'card': card, 'widget': ownhandwidgets[i]} for i, card in enumerate(ownhandcards)],
        'owntablecards': [{'card': card, 'widget': owntablewidgets[i]} for i, card in enumerate(owntablecards)],
        'competitortablecards': [{'card': card, 'widget': competitortablewidgets[i]} for i, card in enumerate(competitortablecards)],
        'form': form,
        'reloading': (match.active and not actionurl),
    }
    return render(request, 'regame/match.html', context)



def main(request):
    player = request.user
    if player.is_authenticated:
        markactive(player)
        matchlinks = [ {'match': i, 'competitor': competitor(i, player)}
            for i in Match.objects.filter(Q(player1=player) | Q(player2=player), active=True).order_by('-pk')]
    else:
        matchlinks = []
    users = ({
        'displayname': user.userprofile.display_name(),
        'lastseen': user.userprofile.lastseen,
        'username': user.username,
    } for user in activeusers())
    context = {
        'matchlinks': matchlinks,
        'activeusers': users,
    }
    if request.user.is_authenticated:
        context['hideform'] = HideForm(instance=request.user.userprofile, initial={'hidden': not request.user.userprofile.hidden})
    return render(request, 'regame/main.html', context)


@login_required()
def playerhidden(request):
    if request.method == 'POST':
        form = HideForm(request.POST, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
    return redirect('main')
