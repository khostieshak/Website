from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.bookings.as_view()),
    url(r'^bookings.xml', views.XMLView.as_view()),
    url(r'^ajax/info', views.ajax_info),
]
