from django import template
from django.contrib.humanize.templatetags import humanize
from datetime import datetime, timedelta, timezone
from regame import players

register = template.Library()

@register.filter(is_safe=True)
def naturaltime(value):
    if datetime.now(timezone.utc) - value <= timedelta(minutes=5):
        return "just now"
    return humanize.naturaltime(value)

@register.filter(is_safe=True)
def displayname(value):
    return players.displayname(value)

@register.filter(is_safe=True)
def usernameispublic(value):
    return players.usernameispublic(value)
