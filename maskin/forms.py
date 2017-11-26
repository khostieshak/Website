from django.forms import Form, ModelForm, TextInput, BooleanField, Select, NumberInput, CheckboxInput
from django.contrib.auth.models import User
from models import Profile
from django.utils.translation import ugettext_lazy as _


class MemberForm(Form):
    becomeMember=BooleanField(
        label=_('Become member'),
        help_text=_('Want to become a member?'))

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        widgets={
            'first_name': TextInput(attrs={'class': 'form-control'}),
            'last_name': TextInput(attrs={'class': 'form-control'}),
            'email': TextInput(attrs={'class': 'form-control'})
        }

class EmailForm(ModelForm):
    class Meta:
        model = User
        fields = ('email',)
        widgets = {
            'email': TextInput(attrs={'class': 'form-control'})
        }

class PhoneForm(ModelForm):
    class Meta:
        model = Profile
        fields = ('phone',)
        widgets = {
            'phone': TextInput(attrs={'class': 'form-control'})
        }

class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ('phone', 'program', 'start_year', 'master')
        widgets = {
            'phone': TextInput(attrs={'class': 'form-control'}),
            'program': Select(attrs={'class': 'form-control'}),
            'start_year': NumberInput(attrs={'class': 'form-control'}),
            'master': TextInput(attrs={'class': 'form-control'})
        }
