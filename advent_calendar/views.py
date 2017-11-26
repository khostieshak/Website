from aldryn_apphooks_config.mixins import AppConfigMixin
from django.views.generic import ListView
from models import AdventCalenderDay
import pytz
from django.conf import settings
from datetime import datetime

class IndexView(AppConfigMixin, ListView):
    model = AdventCalenderDay
    template_name = 'advent_calendar.html'


    def get_queryset(self):
        tz = pytz.timezone(settings.TIME_ZONE)
        calendardays = AdventCalenderDay.objects.filter(app_config=self.config).order_by('order')

        for calendarday in calendardays:
            publishtime= tz.localize(datetime.combine(calendarday.day, self.config.publish_time))
            if publishtime < datetime.now(tz) or self.request.user.has_perm('maskin.add_AdventCalendarConfig'):
                calendarday.publish = True
            else:
                calendarday.publish = False
        return calendardays