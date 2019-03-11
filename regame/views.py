from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .forms import NewMatchForm
from .models import Match

def error(request, message, code=200):
    return render(request, 'regame/error.html', {'message': message}, status=code)

@login_required()
def newmatch(request):
    if request.method == 'POST':
        form = NewMatchForm(request.POST)
        if form.is_valid():
            # TODO: validate user
            competitor = get_user_model().objects.get(username=form.cleaned_data['other_player'])
            match = Match(player1=request.user, player2=competitor)
            match.save()
            return HttpResponseRedirect(reverse('match', kwargs={'no': match.id}))
    else:
        form = NewMatchForm()
    context = {
        'form': form,
    }
    return render(request, 'regame/new_match.html', context)

def match(request, no):
    return HttpResponse(str(no))

def main(request):
    return render(request, 'regame/main.html')
