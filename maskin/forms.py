from django.forms import Form, ModelForm, TextInput, BooleanField, Select, NumberInput, RadioSelect
from django.contrib.auth.models import User
from models import Profile, NewsBlogLatestArticleByCategory, MemberPluginModel
from django.utils.translation import ugettext_lazy as _
from aldryn_newsblog.forms import AutoAppConfigFormMixin


class MemberForm(Form):
    becomeMember=BooleanField(
        label=_('Become member'),
        help_text=_('Want to become a member?'))

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'last_name': TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'email': TextInput(attrs={'class': 'form-control', 'required': 'true'})
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
        fields = ('phone', 'program', 'start_year', 'master', 'rfid')
        widgets = {
            'phone': TextInput(attrs={'class': 'form-control'}),
            'program': Select(attrs={'class': 'form-control'}),
            'start_year': NumberInput(attrs={'class': 'form-control', 'min': 1969}),
            'master': TextInput(attrs={'class': 'form-control'}),
            'rfid': NumberInput(attrs={'class': 'form-control'})
        }
        help_texts = {
            'rfid': 'You find your number on the back of your LiUID.',
        }


class NewsBlogLatestArticleByCategoryPluginForm(AutoAppConfigFormMixin, ModelForm):
    class Meta:
        model = NewsBlogLatestArticleByCategory
        fields = [
            'app_config', 'latest_articles', 'categories'
        ]

class MemberPluginForm(ModelForm):
    class Meta:
        model = MemberPluginModel
        fields = [
            'ShowForMembers'
        ]
        widgets = {
            'ShowForMembers': RadioSelect
        }
