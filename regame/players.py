from django.contrib.auth import login
from django.contrib.auth.models import User
import secrets
import string
import uuid

def enforceuser(request):
    if request.user.is_authenticated:
        return request.user
    characterset = string.ascii_letters + string.digits
    name = str(uuid.uuid4())
    username = '_auto_' + name
    password = ''.join(secrets.choice(characterset) for i in range(26))
    user = User.objects.create_user(username, name + '@localhost', password)
    user.save()
    user.userprofile.temporary = True
    user.userprofile.save()
    login(request, user)
    request.session.set_expiry(0)
    return user
