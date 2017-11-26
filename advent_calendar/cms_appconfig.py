from aldryn_apphooks_config.models import AppHookConfig
from aldryn_apphooks_config.utils import setup_config
from django.db import models
from django.utils.translation import ugettext_lazy as _

class AdventCalendarConfig(AppHookConfig):
    start_date = models.DateField(verbose_name=_('start date'))
    publish_time = models.TimeField(verbose_name=_('publish time'))
    background = models.ImageField(verbose_name=_('background image'), default=None)

    class Meta:
        verbose_name = _('Advent calendar')
        verbose_name_plural = _('Advent calendars')