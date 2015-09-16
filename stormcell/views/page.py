from django.shortcuts import redirect, render_to_response
from django.contrib.auth.decorators import login_required
from apiclient.discovery import build
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.context_processors import csrf
from django.conf import settings
from django.http import HttpResponse
from oauth2client.django_orm import Storage
from oauth2client.client import OAuth2WebServerFlow, FlowExchangeError
import httplib2
from stormcell.models import CredentialsModel, FlowModel, GoogleOauth
from stormcell.dao.schedule import get_availability_for_users
import datetime

import six

if six.PY2:
    from urllib import quote
if six.PY3:
    from urllib.parse import quote


@login_required
def home(request):
    request.session['forcesave'] = True

    context = {
        "google": []
    }

    existing_google_access = GoogleOauth.objects.filter(user=request.user)

    for access in existing_google_access:
        context["google"].append({
            "email": access.account_id,
        })

    context.update(csrf(request))
    return render_to_response("stormcell/home.html", context)


@login_required
def show_availability(request):
    duration = int(request.GET.get('duration', '30'))

    days_to_search = []
    availability = get_availability_for_users([request.user], days_to_search)

    return render_to_response("stormcell/availability.html", {
        "availability": availability,
    })
    pass
