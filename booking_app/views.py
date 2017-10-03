from aldryn_apphooks_config.mixins import AppConfigMixin
from django.http import HttpResponse, HttpResponseBadRequest
from datetime import date, datetime, timedelta
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView, CreateView, TemplateView
from itertools import chain
from django import forms
import pytz
from models import Booking, BookingConfig
from django.conf import settings


class FreeSpot(object):
    def __init__(self, id, name, start, end):
        self.id = id
        self.name = name
        self.start = start
        self.end = end

class XMLView(AppConfigMixin, ListView):
    model = Booking
    template_name = 'bookings.xml'

    def get_queryset(self):
        made_bookings = Booking.objects.filter(app_config=self.config)
        free_spots=[]
        daterange = date.today().day + 182  # half a year
        tz = pytz.timezone(settings.TIME_ZONE)

        for day in (date.today() + timedelta(n) for n in range(daterange)):
            for booking_spot in self.config.booking_spots.all():
                start=tz.localize(datetime.combine(day, booking_spot.start))
                end=tz.localize(datetime.combine(day, booking_spot.end))
                if Booking.objects.free(self.config, start, end):
                    name = _("Free") + \
                           ' (' + booking_spot.start.strftime('%H') + \
                           '-' + booking_spot.end.strftime('%H') + ')'
                    free_spots.append(FreeSpot( -1, name, start, end))

        result_list = sorted(chain(free_spots, made_bookings),
                            key=lambda instance: instance.start)
        return result_list


class bookings(AppConfigMixin, CreateView):
    model = Booking
    template_name = 'bookings.html'
    fields = ['start', 'end']
    widgets = {
        'start': forms.HiddenInput(),
        'end': forms.HiddenInput()}

    def form_valid(self, form):
        form.instance.app_config = self.config
        form.instance.madeBy = self.request.user
        form.instance.name = self.request.user.first_name + ' ' + self.request.user.last_name
        if form.instance.name.isspace():
            form.instance.name = form.instance.madeBy
        self.object = form.save()
        return self.render_to_response(self.get_context_data(form=form))


class book(AppConfigMixin, TemplateView):
    template_name = None

    def post(self, request, *args, **kwargs):
        if request.is_ajax:
            if request.POST.has_key('start') and request.POST.has_key('end'):
                tz = pytz.timezone(settings.TIME_ZONE)
                start = datetime.strptime(request.POST['start'], '%Y-%m-%d %H:%M')
                start = tz.localize(start)
                end = datetime.strptime(request.POST['end'], '%Y-%m-%d %H:%M')
                end = tz.localize(end)
                app_config = self.config

                free = Booking.objects.free(app_config, start, end)
                a_booking_spot = BookingConfig.objects.filter(
                    booking_spots__start__exact=start.time(),
                    booking_spots__end__exact=end.time()).exists()

                if free and a_booking_spot:
                    made_by = self.request.user
                    name = self.request.user.first_name + ' ' + self.request.user.last_name
                    if name.isspace():
                        name = made_by
                    Booking.objects.add_booking(app_config, name, made_by, start, end)

                    status = "Good"
                    return HttpResponse(status)
                else:
                    status = "Error"
                    return HttpResponseBadRequest(status)

            else:
                status = "Error"
                return HttpResponseBadRequest(status)
