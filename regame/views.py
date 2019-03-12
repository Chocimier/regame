from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .forms import NewMatchForm
from .models import Match, PossessedCard, CardLocation
from .processes import creatematch, competitor

def error(request, message, code=200):
    return render(request, 'regame/error.html', {'message': message}, status=code)

@login_required()
def newmatch(request):
    context = {}
    if request.method == 'POST':
        form = NewMatchForm(request.POST)
        if not form.is_valid():
            return error(request, 'Something went wrong.')
        try:
            competitor = get_user_model().objects.get(username=form.cleaned_data['other_player'])
        except get_user_model().DoesNotExist:
            competitor = None
            context['error'] = 'I do not know who {} is.'.format(form.cleaned_data['other_player'])
        if competitor:
            match = creatematch(request.user, competitor)
            return HttpResponseRedirect(reverse('match', kwargs={'no': match.id}))
    else:
        form = NewMatchForm()
    context['form'] = form
    return render(request, 'regame/new_match.html', context)

@login_required()
def match(request, no):
    try:
        match = Match.objects.get(id=no)
    except Match.DoesNotExist:
        return error(request, 'No such match.', 404)
    if request.user != match.player1 and request.user != match.player2:
        return error(request, 'You do not play that match.', 403)
    player = request.user
    other = competitor(match, player)
    context = {
        'player': player,
        'competitor': other,
        'ownhandcards': PossessedCard.objects.filter(match=match, player=player, location=CardLocation.HAND),
        'owntablecards': PossessedCard.objects.filter(match=match, player=player, location=CardLocation.TABLE),
        'competitortablecards': PossessedCard.objects.filter(match=match, player=other, location=CardLocation.TABLE),
    }
    return render(request, 'regame/match.html', context)

def main(request):
    player = request.user
    if player.is_authenticated:
        matchlinks = [ {'match': i, 'competitor': competitor(i, player)}
            for i in Match.objects.filter(Q(player1=player) | Q(player2=player))]
    else:
        matchlinks = []
    context = {
        'matchlinks': matchlinks
    }
    return render(request, 'regame/main.html', context)
