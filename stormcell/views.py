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
def add_google_calendar(request):
    request.session['runningflow'] = True

    username = request.user.username
    credential_id = GoogleOauth.generate_id(username)
    request.session["current_google_id"] = credential_id
    storage = Storage(CredentialsModel,
                      'id',
                      credential_id,
                      'credential')
    credential = storage.get()
    scope = ('https://www.googleapis.com/auth/plus.login '
             'https://www.googleapis.com/auth/userinfo.email',
             'https://www.googleapis.com/auth/calendar.readonly',)

    if credential is None or credential.invalid is True:
        flow = OAuth2WebServerFlow(client_id=settings.GOOGLE_OAUTH_KEY,
                                   client_secret=settings.GOOGLE_OAUTH_SECRET,
                                   scope=scope,
                                   user_agent='stormcell/1.0',
                                   state=request.GET.get('next', ''),
                                   redirect_uri=settings.GOOGLE_RETURN_URL)

        authorize_url = flow.step1_get_authorize_url()

        f = FlowModel(id=credential_id, flow=flow)
        f.save()

        return redirect(authorize_url)

    return HttpResponse("OK")


@login_required
def google_return(request):
    credential_id = request.session["current_google_id"]
    f = FlowModel.objects.get(id=credential_id)

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
                      credential_id,
                      'credential')
    storage.put(credential)

    http = httplib2.Http()
    plus = build('oauth2', 'v2', http=http)
    credential.authorize(http)
    email_data = plus.userinfo().get().execute()
    email = email_data["email"]

    try:
        existing = GoogleOauth.objects.get(user=request.user, account_id=email)
        existing.credential_id = credential_id
        existing.save()
    except GoogleOauth.DoesNotExist:
        cid = credential_id
        new_google_auth = GoogleOauth.objects.create(user=request.user,
                                                     credential_id=cid,
                                                     account_id=email)


#    service = build('calendar', 'v3', http=http)
#
#    # 'Z' indicates UTC time
#    now = datetime.datetime.utcnow().isoformat() + 'Z'
#    print('Getting the upcoming 10 events')
#    eventsResult = service.events().list(
#        calendarId='primary', timeMin=now, maxResults=10, singleEvents=True,
#        orderBy='startTime').execute()
#    events = eventsResult.get('items', [])
#
#    if not events:
#        print('No upcoming events found.')
#    for event in events:
#        start = event['start'].get('dateTime', event['start'].get('date'))
#        print(start, event['summary'])



    return redirect(reverse('home'))


def add_o365_calendar(request):
    import uuid
    import six
    if six.PY2:
        from urllib import urlencode
    else:
        from urllib.parse import urlencode
    nonce = str(uuid.uuid4())
    params = { 'client_id': settings.O365_OAUTH_CLIENT_ID,
               'redirect_uri': settings.O365_RETURN_URL,
               'response_type': 'code',
               #'scope': 'openid',
               'nonce': nonce,
               # 'prompt': 'admin_consent',
               'response_mode': 'form_post',
               'resource': 'https://outlook.office365.com/',
             }

             # https://login.windows.net/common/oauth2/authorize?response_type=code&client_id=acb81092-056e-41d6-a553-36c5bd1d4a72&redirect_uri=https://mycoolwebapp.azurewebsites.net&resource=https:%2f%2foutlook.office365.com%2f&state=5fdfd60b-8457-4536-b20f-fcb658d19458

    authorize_url = "https://login.microsoftonline.com/common/oauth2/authorize?{0}"
    authorization_url = authorize_url.format(urlencode(params))

    print authorization_url

    return HttpResponse("OK")
#    request.session['runningflow'] = True
#    storage = Storage(CredentialsModel,
#                      'id',
#                      request.session.session_key,
#                      'credential')
#    credential = storage.get()
#    scope = ('http://outlook.office.com/Calendars.Read',)
#    if credential is None or credential.invalid is True:
#        flow = OAuth2WebServerFlow(client_id=settings.O365_OAUTH_CLIENT_ID,
#                                   client_secret=settings.O365_OAUTH_CLIENT_KEY,
#                                   scope=scope,
#                                   user_agent='stormcell/1.0',
#                                   state=request.GET.get('next', ''),
#                                   redirect_uri=settings.O365_RETURN_URL,
#                                   auth_uri='https://login.microsoftonline.com/common/oauth2/authorize',
#                                   )
#
#        authorize_url = flow.step1_get_authorize_url()
#
#        f = FlowModel(id=request.session.session_key, flow=flow)
#        f.save()
#
#        return redirect(authorize_url)
#
#    http = httplib2.Http()
#    plus = build('plus', 'v1', http=http)
#    credential.authorize(http)
#    name_data = plus.people().get(userId='me').execute()
#
#    name = name_data["name"]["givenName"]
#    last_name = name_data["name"]["familyName"]
#
#    plus = build('oauth2', 'v2', http=http)
#    credential.authorize(http)
#    email_data = plus.userinfo().get().execute()
#    email = email_data["email"]
#
#    print("Email: ", email)
#
#    service = build('calendar', 'v3', http=http)
#
#    # 'Z' indicates UTC time
#    now = datetime.datetime.utcnow().isoformat() + 'Z'
#    print('Getting the upcoming 10 events')
#    eventsResult = service.events().list(
#        calendarId='primary', timeMin=now, maxResults=10, singleEvents=True,
#        orderBy='startTime').execute()
#    events = eventsResult.get('items', [])
#
#    if not events:
#        print('No upcoming events found.')
#    for event in events:
#        start = event['start'].get('dateTime', event['start'].get('date'))
#        print(start, event['summary'])
#
#    return HttpResponse("OK")
#



@csrf_exempt
def o365_return(request):

    print request
    print request.POST

    return HttpResponse("OK 2")
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
