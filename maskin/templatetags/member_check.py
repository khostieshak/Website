from django import template
import maskin.models

register = template.Library()

@register.filter(name='is_member')
def is_member(user):
    school_year = maskin.models.SchoolYear.objects.current()
    if school_year is None:
        return False
    else:
        group_name = school_year.get_member_group()
        if group_name is None:
            return False
        else:
            return user.groups.filter(name=group_name).exists()
