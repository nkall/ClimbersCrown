from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'ClimbersCrown.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^podium/', include('climber.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', include('climber.urls')),
]