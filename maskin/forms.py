from django import forms
from django.contrib.auth.models import User
from models import Profile
from django.utils.translation import ugettext_lazy as _


class MemberForm(forms.Form):
    becomeMember=forms.BooleanField(label=_('Become member'), help_text=_('Want to become a member?'))


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('phone', 'program', 'start_year', 'master')