from django.contrib.auth import login, get_user_model
from django.contrib.auth.models import User
import uuid
from datetime import datetime, timedelta, timezone

def enforceuser(request):
    if request.user.is_authenticated:
        return request.user
    name = str(uuid.uuid4())
    username = '_auto_' + name
    user = User.objects.create_user(username)
    user.save()
    user.userprofile.temporary = True
    user.userprofile.save()
    login(request, user)
    request.session.set_expiry(0)
    return user

def activeusers():
    return (User.objects
                .filter(userprofile__lastseen__gte=datetime.now() - timedelta(hours=8))
                .filter(userprofile__hidden=False)
                .order_by('-userprofile__lastseen')
                [:40])

def markactive(user):
    if not user.userprofile.hidden:
        sinceupdate = datetime.now(timezone.utc) - user.userprofile.lastseen
        if sinceupdate >= timedelta(minutes=5):
            user.userprofile.lastseen = datetime.now(timezone.utc)
            user.userprofile.save()

def toplayer(player):
    if isinstance(player, str):
        return get_user_model().objects.filter(username=player).first()
    return player

def displayname(player):
    return toplayer(player).userprofile.display_name()

def usernameispublic(player):
    if not player:
        return True
    player = toplayer(player)
    if player.username == 'bot':
        return False
    return not player.userprofile.temporary

def isbot(player):
    return player.username == 'bot'
