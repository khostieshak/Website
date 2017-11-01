from django import template
import maskin.models

register = template.Library()

@register.filter(name='signedinto')
def is_member(user, eventid):
    event=maskin.models.Event.objects.get(id=eventid)
    return maskin.models.Signup.objects.filter(user=user, event=event).exists()
