from django.conf.urls import url

from stormcell.views import page
from stormcell.views import providers

urlpatterns = [
    url('^$', page.home, name="home"),
    url('^new$', page.show_availability, name="show_availability"),
    url('^add_google',
        providers.add_google_calendar,
        name="add_google_calendar"),
    url('^google_return', providers.google_return, name="google_return"),
]

#    url('^add_o365', views.add_o365_calendar, name="add_o365_calendar"),
#    url('^o365_return', views.o365_return, name="o365_return"),
