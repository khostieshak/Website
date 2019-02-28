from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from datetime import date

from aldryn_newsblog.models import Article, NewsBlogCMSPlugin
from aldryn_newsblog.utils.utilities import get_valid_languages_from_request
from aldryn_categories.fields import CategoryManyToManyField

from cms.models.pluginmodel import CMSPlugin
from django import forms

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
        ("M", _("Mechanical engineering")),
        ("DPU", _("Design and Product Development")),
        ("EMM", _("Energy-Environment-Management")),
        ("MASTER", _("Masterprogram")),
        ("EX", _("Exchange student")),
        ("OTHER", _("Other"))
    )
    program = models.CharField(_("Program"), max_length=10, blank=True, choices=PROGRAM_CHOICES)
    start_year = models.IntegerField(_("Start year"), default=0)
    master = models.CharField(_("Master profile"), max_length=30, blank=True)
    rfid = models.BigIntegerField(_("LiU-ID Card number"), default=0)

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

    def __str__(self):
        return self.name.encode('utf-8')

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")

class Signup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(verbose_name=_('timestamp'))

    class Meta:
        verbose_name = _("Sign up")
        verbose_name_plural = _("Sign ups")
        ordering = ['-timestamp']
        unique_together = (('user', 'event'),)


class NewsBlogLatestArticleByCategory(NewsBlogCMSPlugin):
    latest_articles = models.IntegerField(
        default=5,
        help_text=_('The maximum number of latest articles to display.')
    )
    categories = CategoryManyToManyField('aldryn_categories.Category',
                                         verbose_name=_('categories'),
                                         blank=True)

    # copy manytomany and foreignkey relationship from edited plugin to published plugin
    def copy_relations(self, oldinstance):
        self.categories = oldinstance.categories.all()

    def get_articles(self, request):
        """
        Returns a queryset of the latest N articles in one or more of the M categories.
        N is the plugin setting: latest_articles.
        M is the plugin setting: categories
        """
        queryset = Article.objects.published()
        queryset = queryset.all().filter(categories__in=self.categories.all())

        if not self.latest_articles:
            return Article.objects.none()
        languages = get_valid_languages_from_request(
            self.app_config.namespace, request)
        if self.language not in languages:
            return queryset.none()
        queryset = queryset.translated(*languages).filter(
            app_config=self.app_config)

        return queryset[:self.latest_articles]

    def __str__(self):
        return ugettext('%(app_title)s latest articles by category: %(latest_articles)s') % {
            'app_title': self.app_config.get_app_title(),
            'latest_articles': self.latest_articles,
        }

class MemberPluginModel(CMSPlugin):
    MEMBER_CHOICES = ((True, _('Show for members only.')), (False, _('Show for none members only.')))
    ShowForMembers = models.BooleanField(
        default=True,
        choices=MEMBER_CHOICES
    )
