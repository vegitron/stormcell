from django.conf.urls import url

from stormcell import views

urlpatterns = [
    url('^$', views.home, name="home"),
    url('^add_google', views.add_google_calendar, name="add_google_calendar"),
    url('^google_return', views.google_return, name="google_return"),
]
