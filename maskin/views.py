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
        if request.is_ajax():
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

                request.GET = request.GET.copy() # Make a copy of the request
                request.GET['liuid']=student['liu_id'] # Modify the request
                return ajax_checkin(request) # Send a check in request
            except urllib2.HTTPError:
                response = JsonResponse({"msg": (_("No student found with card number:") + ' ' + query).encode('utf-8')})
                response.status_code = 400  # Bad request
                return response

        return ajax_signups(request)
    else:
        return render(request, 'permission_denied.html')

@login_required
def ajax_add_member(request):
    if request.is_ajax():
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
    if request.is_ajax():
        id = request.GET['eventid']
        qs = models.Signup.objects.filter(event__id=id)
    N_signups=0
    N_checkins=0
    N_checkedinmembers=0

    for signup in qs:
        if signup.signup:
            N_signups += 1
        if signup.checkin:
            N_checkins += 1
            if is_member(signup.user):
                N_checkedinmembers += 1

    return render(request, 'signups.html', {
        'signups': qs,
        'N_checkedinmembers': N_checkedinmembers,
        'N_signups': N_signups,
        'N_checkins': N_checkins,
        'eventid': id
    })


@login_required()
def ajax_checkin(request):
    if request.user.has_perm('maskin.add_signup'):
        if request.is_ajax():
            user=User.objects.get(username=request.GET['liuid'])
            event = models.Event.objects.get(id=request.GET['eventid'])
            try:
                signup, created = models.Signup.objects.get_or_create(user=user, event=event)
                if signup.checkin:
                    response = JsonResponse({"msg": (_("Already checked-in to this event.")).encode('utf-8')})
                    response.status_code = 400  # Bad request
                    return response
                else:
                    signup.checkin = True
                    tz = pytz.timezone(settings.TIME_ZONE)
                    now=tz.localize(datetime.datetime.now())
                    signup.timestamp_checkin = now
                    signup.save()
            except IntegrityError:
                pass
            return ajax_signups(request)
    else:
        return render(request, 'permission_denied.html')


@login_required()
def ajax_remove_checkin(request):
    if request.user.has_perm('maskin.delete_signup'):
        if request.is_ajax():
            user = User.objects.get(username=request.GET['liuid'])
            event = models.Event.objects.get(id=request.GET['eventid'])
            try:
                signup = models.Signup.objects.get(user=user, event=event)
                signup.checkin = False
                signup.save()
            except:
                pass
            return ajax_signups(request)
    else:
        return render(request, 'permission_denied.html')

def event(request, eventid):
    event = models.Event.objects.get(id__exact=eventid)
    signups = models.Signup.objects.filter(event=event, signup=True)

    return render(request, 'event.html', {'event': event, 'signups': signups})


@login_required()
def ajax_add_signup(request, eventid):
    if request.is_ajax():
        signup, created = models.Signup.objects.get_or_create(user=request.user, event_id=eventid)
        if created or not signup.signup:
            signup.signup = True
            tz = pytz.timezone(settings.TIME_ZONE)
            now = tz.localize(datetime.datetime.now())
            signup.timestamp_signup = now
            signup.save()
            response = JsonResponse({"msg": (_("Thanks for your register.")).encode('utf-8')})
            response.status_code = 202  # Accepted
            return response
        else:
            response = JsonResponse({"msg": (_("Already signed up for this event.")).encode('utf-8')})
            response.status_code = 406  # Not Acceptable
            return response


@login_required()
def ajax_remove_signup(request, eventid):
    if request.is_ajax():

        signup = models.Signup.objects.get(user=request.user, event_id=eventid)
        if signup: #if signup exist
            signup.signup = False
            tz = pytz.timezone(settings.TIME_ZONE)
            mintime = tz.localize(datetime.datetime(999,1,1,0,0))
            signup.timestamp_signup = mintime
            signup.save()
            response = JsonResponse({"msg": (_("Register removed.")).encode('utf-8')})
            response.status_code = 202  # Accepted
            return response
        else:
            response = JsonResponse({"msg": (_("Something went wrong.")).encode('utf-8')})
            response.status_code = 400  # Bad Request
            return response
