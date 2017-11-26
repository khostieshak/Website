from django.forms import ModelForm, Form, CharField, TextInput, HiddenInput
from django.utils.translation import ugettext_lazy as _
from models import Booking


class BookingForm(ModelForm):
    class Meta:
        model = Booking
        fields =('name', 'start', 'end')
        labels = {
            'name': _('Committee or name (for private use)')
        }

        widgets ={
            'name': TextInput(attrs={'class': 'form-control'}),
            'start': HiddenInput(),
            'end': HiddenInput()
        }


class DeleteBooking(Form):
    id = CharField(widget=HiddenInput())
