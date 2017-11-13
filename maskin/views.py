from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from forms import UserForm, ProfileForm, MemberForm
from django.contrib import messages
from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User,  Group
import models
from django.db.models import Q
import urllib2
import json
import os
import datetime
import pytz
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

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
        'school_year': models.SchoolYear.objects.current()
    })


@login_required()
def checkin(request):
    if request.user.has_perm('maskin.add_signup'):
        events = models.Event.objects.all()
        return render(request, 'checkin.html', {'events': events})
    else:
        return render(request, 'permission_denied.html')


def ajax_search(request):
    if request.method == 'GET':
        query = request.GET['query']
        eventid=request.GET['eventid']
    qs = User.objects.all()
    for term in query.split():
        qs = qs.filter(Q(first_name__icontains=term) |
                       Q(last_name__icontains=term) |
                       Q(username__icontains=term))

    return render(request, 'checkin_search.html', {'users': qs[:5], 'eventid': eventid})


@login_required()
def ajax_blip(request):
    if request.user.has_perm('maskin.add_signup'):
        if request.method == 'GET':
            query = request.GET['query']
            try:
                req = urllib2.Request('https://kobra.karservice.se/api/v1/students/' + query + '/')
                req.add_header('Authorization', 'Token ' + os.environ.get('KOBRA_API_TOKEN'))
                resp = urllib2.urlopen(req)
                content = resp.read()
                student = json.loads(content)
                user, created = User.objects.get_or_create(username=student['liu_id'])
                if created:
                    names = student['name'].encode('utf-8').split()
                    last_name = ' '.join(map(str, names[1:]))  # in case of several last names
                    user.first_name = names[0]
                    user.last_name = last_name
                    user.email = student['email']
                    user.save()
                event = models.Event.objects.get(id=request.GET['eventid'])
                tz = pytz.timezone(settings.TIME_ZONE)
                now = tz.localize(datetime.datetime.now())
                obj = models.Signup(user=user, event=event, timestamp=now)
                obj.save()
            except urllib2.HTTPError:
                response = JsonResponse({"msg": (_("No student found with card number: ") + query).encode('utf-8')})
                response.status_code = 400  # Bad request
                return response
            except IntegrityError:
                response = JsonResponse({"msg": (_("Already checked in to this event.")).encode('utf-8')})
                response.status_code = 400  # Bad request
                return response

        return ajax_signups(request)
    else:
        return render(request, 'permission_denied.html')

@login_required
def ajax_add_member(request):
    if request.method == 'GET':
        liuid = request.GET['liuid']
        group_name = models.SchoolYear.objects.current().get_member_group()
        g = Group.objects.get(name=group_name)
        user=User.objects.get(username=liuid)
        g.user_set.add(user)
    return ajax_signups(request)


@login_required
def ajax_become_member(request):
    group_name = models.SchoolYear.objects.current().get_member_group()
    g = Group.objects.get(name=group_name)
    g.user_set.add(request.user)
    return HttpResponse('')


@login_required
def ajax_no_member(request):
    request.session['no_member'] = True
    return HttpResponse('')


def ajax_signups(request):
    if request.method == 'GET':
        id = request.GET['eventid']
        qs = models.Signup.objects.filter(event__id=id)
    members=0
    for signup in qs:
        if is_member(signup.user):
            members += 1

    return render(request, 'signups.html', {'signups': qs, 'members': members})


@login_required()
def ajax_checkin(request):
    if request.user.has_perm('maskin.add_signup'):
        if request.method == 'GET':
            user=User.objects.get(username=request.GET['liuid'])
            event = models.Event.objects.get(id=request.GET['eventid'])
            try:
                tz = pytz.timezone(settings.TIME_ZONE)
                now=tz.localize(datetime.datetime.now())
                obj = models.Signup(user=user, event=event, timestamp=now)
                obj.save()
            except IntegrityError:  # Already signed up
                pass
            return ajax_signups(request)
    else:
        return render(request, 'permission_denied.html')


@login_required()
def ajax_delete_signup(request):
    if request.user.has_perm('maskin.delete_signup'):
        if request.method == 'GET':
            user=User.objects.get(username=request.GET['liuid'])
            event = models.Event.objects.get(id=request.GET['eventid'])
            try:
                models.Signup.objects.get(user=user, event=event).delete()
            except:
                pass
            return ajax_signups(request)
    else:
        return render(request, 'permission_denied.html')