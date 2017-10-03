from aldryn_apphooks_config.fields import AppHookConfigField
from aldryn_apphooks_config.models import AppHookConfig
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class BookingManager(models.Manager):
    def free(self, app_config, start, end):
        if self.filter(app_config=app_config, start__lt=end, end__gt=start).count() == 0:
            return True
        else:
            return False

    def add_booking(self, app_config, name, madeBy, start, end):
        booking = self.create(app_config=app_config, name=name, madeBy=madeBy, start=start, end=end)
        return booking


class BookingSpot(models.Model):
    start = models.TimeField(verbose_name=_('start'))
    end = models.TimeField(verbose_name=_('end'))

    def __unicode__(self):
        return self.start.isoformat() + '-' + self.end.isoformat()

    class Meta:
        verbose_name = _('Booking spot')
        verbose_name_plural = _('Booking spots')

class BookingConfig(AppHookConfig):
    booking_spots = models.ManyToManyField(BookingSpot, verbose_name=_('Booking spots'))


class Booking(models.Model):
    app_config = AppHookConfigField(BookingConfig, verbose_name=_('app config'), default=None)
    name = models.CharField(verbose_name=_('name'),max_length=30,  default='')
    id = models.AutoField(primary_key=True)
    madeBy = models.ForeignKey(User, verbose_name=_('made by'))
    start = models.DateTimeField(verbose_name=_('start'), unique=True)
    end = models.DateTimeField(verbose_name=_('end'), unique=True)

    objects = BookingManager()

    def __unicode__(self):
        return self.start.isoformat()

    class Meta:
        verbose_name = _('Booking')
        verbose_name_plural = _('Bookings')
