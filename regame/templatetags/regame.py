from django import template
from django.contrib.humanize.templatetags import humanize
from datetime import datetime, timedelta, timezone

register = template.Library()

@register.filter(is_safe=True)
def naturaltime(value):
    if datetime.now(timezone.utc) - value <= timedelta(minutes=5):
        return "just now"
    return humanize.naturaltime(value)