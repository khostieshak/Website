from django import template
import maskin.models

register = template.Library()


@register.assignment_tag(name='school_year_exists')
def school_year_exists():
    school_year = maskin.models.SchoolYear.objects.current()
    if school_year is None:
        return False
    else:
        group_name = school_year.get_member_group()
        if group_name is None:
            return False
        else:
            return True
