from django.shortcuts import redirect, render_to_response
from apiclient.discovery import build
from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpResponse
from oauth2client.django_orm import Storage
from oauth2client.client import OAuth2WebServerFlow, FlowExchangeError
import httplib2
from stormcell.models import CredentialsModel, FlowModel
import datetime

import six

if six.PY2:
    from urllib import quote
if six.PY3:
    from urllib.parse import quote


def home(request):
    request.session['forcesave'] = True
    return render_to_response("stormcell/home.html")


def add_google_calendar(request):
    request.session['runningflow'] = True
    storage = Storage(CredentialsModel,
                      'id',
                      request.session.session_key,
                      'credential')
    credential = storage.get()
    scope = ('https://www.googleapis.com/auth/plus.login '
             'https://www.googleapis.com/auth/userinfo.email',
             'https://www.googleapis.com/auth/calendar.readonly',)
    if credential is None or credential.invalid is True:
        flow = OAuth2WebServerFlow(client_id=settings.GOOGLE_OAUTH_KEY,
                                   client_secret=settings.GOOGLE_OAUTH_SECRET,
                                   scope=scope,
                                   user_agent='plus-django-sample/1.0',
                                   state=request.GET.get('next', ''),
                                   redirect_uri=settings.GOOGLE_RETURN_URL)

        authorize_url = flow.step1_get_authorize_url()

        f = FlowModel(id=request.session.session_key, flow=flow)
        f.save()

        return redirect(authorize_url)

    http = httplib2.Http()
    plus = build('plus', 'v1', http=http)
    credential.authorize(http)
    name_data = plus.people().get(userId='me').execute()

    name = name_data["name"]["givenName"]
    last_name = name_data["name"]["familyName"]

    plus = build('oauth2', 'v2', http=http)
    credential.authorize(http)
    email_data = plus.userinfo().get().execute()
    email = email_data["email"]

    print("Email: ", email)

    service = build('calendar', 'v3', http=http)

    # 'Z' indicates UTC time
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    print('Getting the upcoming 10 events')
    eventsResult = service.events().list(
        calendarId='primary', timeMin=now, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])

    return HttpResponse("OK")


def google_return(request):
    f = FlowModel.objects.get(id=request.session.session_key)

    try:
        credential = f.flow.step2_exchange(request.REQUEST)
    except FlowExchangeError as ex:
        if ex[0] == "access_denied":
            return render_to_response("oauth2/denied.html", {})
        raise

    flow = f.flow
    if type(flow) == 'str':
        flow = f.flow.to_python()

    storage = Storage(CredentialsModel,
                      'id',
                      request.session.session_key,
                      'credential')
    storage.put(credential)

    google_login_url = reverse('google_return')
    google_login_url = "%s?next=%s" % (google_login_url,
                                       quote(request.GET['state']))

    return redirect(google_login_url)
