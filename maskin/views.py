from django.contrib.auth.decorators import login_required
from django.db import transaction
from forms import UserForm, ProfileForm, MemberForm
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.models import User,  Group
import models
from django.db.models import Q
import urllib2
import json
import os

def is_member(user):
    school_year = models.SchoolYear.objects.current()
    if school_year is None:
        return False
    else:
        group_name = school_year.get_member_group()
        if group_name is None:
            return False
        else:
            return user.groups.filter(name=group_name).exists()


@login_required
@transaction.atomic
def update_profile(request):
    if request.method == 'POST':
        if not is_member(request.user):
            member_form = MemberForm(request.POST)
            if member_form.is_valid() and member_form.cleaned_data['becomeMember']:
                group_name = models.SchoolYear.objects.current().get_member_group()
                g = Group.objects.get(name=group_name)
                g.user_set.add(request.user)
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('/profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        member_form = MemberForm()
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'profile.html', {
        'member_form': member_form,
        'user_form': user_form,
        'profile_form': profile_form,
        'member': is_member(request.user),
        'school_year': models.SchoolYear.objects.current()
    })


def checkin(request):
    return render(request, 'checkin.html')

def ajax_search(request):
    if request.method == 'GET':
        query = request.GET['query']
    qs = User.objects.all()
    for term in query.split():
        qs = qs.filter(Q(first_name__icontains=term) |
                       Q(last_name__icontains=term) |
                       Q(username__icontains=term))

    if not qs:
        req = urllib2.Request('https://kobra.karservice.se/api/v1/students/' + query +'/')
        req.add_header('Authorization', 'Token '+ os.environ.get('KOBRA_API_TOKEN'))
        try:
            resp = urllib2.urlopen(req)
            content = resp.read()
            liu_id = json.loads(content)['liu_id']
            qs = User.objects.filter(username__iexact=liu_id)
        except urllib2.HTTPError:
            pass

    return render(request, 'checkin_search.html', {'users': qs})
