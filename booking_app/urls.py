from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.bookings.as_view()),
    url(r'^bookings.xml', views.XMLView.as_view()),
    url(r'^book', views.book.as_view())
]