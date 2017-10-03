from aldryn_apphooks_config.app_base import CMSConfigApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _
from models import BookingConfig


class BookingApp(CMSConfigApp):
    name = _("Booking App")
    urls = ["booking_app.urls"]
    app_name = "booking"
    app_config = BookingConfig

apphook_pool.register(BookingApp)