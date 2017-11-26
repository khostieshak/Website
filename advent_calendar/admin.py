from django.contrib import admin
from models import AdventCalenderDay, AdventCalendarConfig
from aldryn_apphooks_config.admin import BaseAppHookConfig

admin.site.register(AdventCalenderDay)
class CalendarConfigAdmin(BaseAppHookConfig, admin.ModelAdmin):
    def get_config_fields(self):
        return (
            'background',
            'start_date',
            'publish_time',
        )

admin.site.register(AdventCalendarConfig, CalendarConfigAdmin)