from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'follow.views.following', name="following"),
    url(r'^following/(?P<username>[\w\._-]+)/$', 'follow.views.following', name="following"),
    url(r'^followers/(?P<username>[\w\._-]+)/$', 'follow.views.followers', name="followers"),    
    url(r'^updates/(?P<username>[\w\._-]+)/$', 'follow.views.updates', name="updates"),    
)
