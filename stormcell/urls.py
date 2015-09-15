from django.conf.urls import url

from stormcell import views

urlpatterns = [
    url('^$', views.home, name="home"),
    url('^add_google', views.add_google_calendar, name="add_google_calendar"),
    url('^google_return', views.google_return, name="google_return"),
]

#    url('^add_o365', views.add_o365_calendar, name="add_o365_calendar"),
#    url('^o365_return', views.o365_return, name="o365_return"),
