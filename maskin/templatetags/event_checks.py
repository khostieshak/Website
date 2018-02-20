from django import template
import maskin.models

register = template.Library()

@register.filter(name='checkedinto')
def checkedinto(user, eventid):
    return maskin.models.Signup.objects.filter(user=user, event_id=eventid, checkin=True).exists()

@register.filter(name='signedup')
def signedup(user, eventid):
    return maskin.models.Signup.objects.filter(user=user, event_id=eventid, signup=True).exists()