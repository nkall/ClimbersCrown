from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<cityName>[a-zA-Z_]+)/$', views.leaderboard, name='leaderboard'),
]