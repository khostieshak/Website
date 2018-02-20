from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from datetime import date, datetime
import pytz
from django.conf import settings
from cms.models.fields import PlaceholderField

class SchoolYearManager(models.Manager):
    def current(self):
        try:
            return self.get(start__lte=date.today(), end__gte=date.today())
        except SchoolYear.DoesNotExist:
            return None


class SchoolYear(models.Model):
    name = models.CharField(verbose_name=_('name'), max_length=30, unique=True)
    member_group = models.OneToOneField(Group, verbose_name=_('Member group'), on_delete=models.CASCADE, null=True)
    start = models.DateField(verbose_name=_('start'), unique=True)
    end = models.DateField(verbose_name=_('end'), unique=True)

    objects=SchoolYearManager()

    def get_member_group(self):
        return self.member_group

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("School year")
        verbose_name_plural = _("School years")


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    member = models.ManyToManyField(SchoolYear, blank=True,  verbose_name=_("Member years"))
    phone = models.CharField(_("Phone number"), max_length=30, blank=True)
    PROGRAM_CHOICES=(
        ("M", _("Mechanical engingering")),
        ("DPU", _("Design and Product Development")),
        ("EMM", _("Energy-Environment-Management")),
        ("MASTER", _("Masterprogram")),
        ("EX", _("Exchange student")),
        ("OTHER", _("Other"))
    )
    program = models.CharField(_("Program"), max_length=10, blank=True, choices=PROGRAM_CHOICES)
    start_year = models.IntegerField(_("Start year"), default=0)
    master = models.CharField(_("Master profile"), max_length=30, blank=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Event(models.Model):
    name = models.CharField(verbose_name=_('name'), max_length=30, unique=True)
    location = models.CharField(verbose_name=_('location'), max_length=30)
    start = models.DateTimeField(verbose_name=_('start'))
    end = models.DateTimeField(verbose_name=_('end'))
    types = (
        (0, _('No signup')),
        (1, _('Max limit')),
        (2, _('Selection'))
    )
    type = models.IntegerField(verbose_name=_('Type'), choices=types, default=0)
    placeholder = PlaceholderField('Info')
    maxsignups = models.IntegerField(verbose_name=_('Max signups'), default=9999)

    def __str__(self):
        return self.name.encode('utf-8')

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")

class Signup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    signup = models.BooleanField(verbose_name=_('signup'), default=False)

    tz = pytz.timezone(settings.TIME_ZONE)
    default_time = tz.localize(datetime(999,1,1,0,0,0))

    timestamp_signup = models.DateTimeField(verbose_name=_('timestamp signup'), default=default_time)
    accepted = models.BooleanField(verbose_name=_('accepted'), default=False)
    checkin = models.BooleanField(verbose_name=_('check-in'), default=False)
    timestamp_checkin = models.DateTimeField(verbose_name=_('timestamp check-in'), default=default_time)

    class Meta:
        verbose_name = _("Sign up")
        verbose_name_plural = _("Sign ups")
        unique_together = (('user', 'event'),)
