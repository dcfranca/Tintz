import django.conf.urls.defaults

urlpatterns = django.conf.urls.defaults.patterns('',
    django.conf.urls.defaults.url(r'^$', 'follow.views.following', name="following"),
    django.conf.urls.defaults.url(r'^following/(?P<username>[\w\._-]+)/$', 'follow.views.following', name="following"),
    django.conf.urls.defaults.url(r'^followers/(?P<username>[\w\._-]+)/$', 'follow.views.followers', name="followers"),
    #django.conf.urls.defaults.url(r'^updates/(?P<username>[\w\._-]+)/$', 'follow.views.updates', name="updates"),
)
