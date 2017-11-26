from aldryn_apphooks_config.app_base import CMSConfigApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _
from models import AdventCalendarConfig


class AdventCalendar(CMSConfigApp):
    name = _("Advent calendar")
    urls = ["advent_calendar.urls"]
    app_name = "Advent calendar"
    app_config = AdventCalendarConfig

apphook_pool.register(AdventCalendar)