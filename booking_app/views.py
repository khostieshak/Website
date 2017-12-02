from aldryn_apphooks_config.mixins import AppConfigMixin
from django.http import HttpResponseRedirect
from datetime import date, datetime, timedelta
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView, TemplateView, View
from itertools import chain
import pytz
from models import Booking, BookingConfig
from django.conf import settings
from django.shortcuts import render
from forms import BookingForm, DeleteBooking
from maskin.forms import EmailForm, PhoneForm

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

class bookings(AppConfigMixin, TemplateView):
    template_name = None

    def get(self, request, *args, **kwargs):
        try:
            email_form = EmailForm(instance=request.user)
            phone_form = PhoneForm(instance=request.user.profile)
            booking_form = BookingForm({'name': request.user.first_name + ' ' + request.user.last_name})
            tz = pytz.timezone(settings.TIME_ZONE)
            my_bookings = Booking.objects.filter(
                madeBy=request.user,
                start__gt=datetime.now(tz),
                app_config=self.config)
            delete_booking = DeleteBooking()
        except AttributeError:
            return render(request, 'bookings.html')
        return render(request, 'bookings.html', {
            'email_form': email_form,
            'phone_form': phone_form,
            'booking_form': booking_form,
            'my_bookings': my_bookings,
            'delete_booking': delete_booking,
        })

    def post(self, request, *args, **kwargs):
        try:
            email_form = EmailForm(request.POST, instance=request.user)
            phone_form = PhoneForm(request.POST, instance=request.user.profile)
            booking_form = BookingForm(request.POST)
            tz = pytz.timezone(settings.TIME_ZONE)
            my_bookings = Booking.objects.filter(
                madeBy=request.user,
                start__gt=datetime.now(tz),
                app_config=self.config).order_by('start')
            delete_booking = DeleteBooking(request.POST)
        except AttributeError:
            return render(request, 'bookings.html')

        if email_form.is_valid() and phone_form.is_valid() and booking_form.is_valid():
            email_form.save()
            phone_form.save()
            new_booking=booking_form.save(commit=False)
            if new_booking.start and new_booking.end:
                new_booking.app_config = self.config

                free = Booking.objects.free(new_booking.app_config, new_booking.start, new_booking.end)
                a_booking_spot = BookingConfig.objects.filter(
                    booking_spots__start__exact=new_booking.start.time(),
                    booking_spots__end__exact=new_booking.end.time()).exists()

                if free and a_booking_spot:
                    new_booking.made_by = request.user
                    Booking.objects.add_booking(new_booking.app_config, new_booking.name, new_booking.made_by, new_booking.start, new_booking.end)
        if delete_booking.is_valid():
            Booking.objects.filter(id__exact=delete_booking.cleaned_data['id']).delete()

        return render(request, 'bookings.html', {
            'email_form': email_form,
            'phone_form': phone_form,
            'booking_form': booking_form,
            'my_bookings': my_bookings,
            'delete_booking': delete_booking
        })

def ajax_info( request):
    if request.method == 'POST':
        booking = Booking.objects.get(id__exact=request.POST['bookingid'])
        return render(request, 'info.html', {'booking': booking})
