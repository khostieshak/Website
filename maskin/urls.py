# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from cms.sitemaps import CMSSitemap
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve
from . import views
import django_cas_ng.views


admin.autodiscover()

urlpatterns = [
    url(r'^sitemap\.xml$', sitemap,
        {'sitemaps': {'cmspages': CMSSitemap}}),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    url(r'^admin/', include(admin.site.urls)),  # NOQA
    url(r'^', include('cms.urls')),
    url(r'^accounts/login$', django_cas_ng.views.login, name='cas_ng_login'),
    url(r'^accounts/logout$', django_cas_ng.views.logout, name='cas_ng_logout'),
    url(r'^profile',views.update_profile, name='profile'),
    url(r'^checkin', views.checkin, name='checkin'),
    url(r'^ajax/search', views.ajax_search, name='ajax_search'),
    url(r'^ajax/blip', views.ajax_blip, name='ajax_blip'),
    url(r'^ajax/become_member', views.ajax_become_member, name='ajax_become_member'),
    url(r'^ajax/add_member', views.ajax_add_member, name='ajax_add_member'),
    url(r'^ajax/no_member', views.ajax_no_member, name='ajax_no_member'),
    url(r'^ajax/signups', views.ajax_signups, name='ajax_signups'),
    url(r'^ajax/checkin', views.ajax_checkin, name='ajax_checkin'),
    url(r'^ajax/delete_signup', views.ajax_delete_signup, name='ajax_delete_signup'),
)

# This is only needed when using runserver.
if settings.DEBUG:
    urlpatterns = [
        url(r'^media/(?P<path>.*)$', serve,
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        ] + staticfiles_urlpatterns() + urlpatterns
