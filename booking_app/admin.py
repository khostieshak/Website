from django.contrib import admin
from models import Booking, BookingSpot, BookingConfig
from aldryn_apphooks_config.admin import ModelAppHookConfig, BaseAppHookConfig


class BookingAdmin(ModelAppHookConfig, admin.ModelAdmin):
    list_display = (
        'app_config',
        'name',
        'madeBy',
        'start',
        'end',

    )
    list_filter = (
        'madeBy',
    )

admin.site.register(Booking, BookingAdmin)
admin.site.register(BookingSpot)


class BookingConfigAdmin(BaseAppHookConfig, admin.ModelAdmin):
    def get_config_fields(self):
        return (
            'booking_spots',
        )
admin.site.register(BookingConfig, BookingConfigAdmin)
