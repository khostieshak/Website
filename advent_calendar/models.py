from aldryn_apphooks_config.fields import AppHookConfigField
from aldryn_apphooks_config.models import AppHookConfig
from django.utils.translation import ugettext_lazy as _
from django.db import models
from cms.models.fields import PlaceholderField
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime
from cms_appconfig import AdventCalendarConfig
import random

def placeholder_name(self):
    return _('Advent calendar') + ' ' + unicode(self.day)


class AdventCalenderDay(models.Model):
    app_config = AppHookConfigField(AdventCalendarConfig, verbose_name=_('calendar'), default=None)
    day = models.DateField(verbose_name=_('date'))
    placeholder = PlaceholderField(placeholder_name)
    order = models.IntegerField(verbose_name=_('display order'), default=0)

    def __str__(self):
        return _('Advent calendar') + ' ' + self.day.strftime('%Y-%m-%d')

    class Meta:
        verbose_name = _('Advent calendar day')
        verbose_name_plural = _('Advent calendar days')

@receiver(post_save, sender=AdventCalendarConfig)
def create_advent_calender_days(sender, instance, created, **kwargs):
    if created:
        calendar_days = 24
        order = range(calendar_days)
        random.shuffle(order)
        for day in range(calendar_days):
            date = instance.start_date + datetime.timedelta(days=day)
            AdventCalenderDay.objects.create(
                app_config=instance,
                day=unicode(date),
                order=order[day]
            )
