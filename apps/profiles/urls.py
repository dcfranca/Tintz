# -*- coding: iso-8859-1 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'profiles.views.profiles', name='profile_list'),    
    url(r'^(?P<username>[\w\._-]+)/$', 'profiles.views.profile', name='profile_detail'),
    url(r'^(?P<username>[\w\._-]+)/(?P<to_follow>[\d])$', 'profiles.views.profile', name='profile_detail'),
    url(r'^search/(?P<search_text>[^/]+)/$', 'profiles.views.searchresults', name="search_results_prof"),
    url(r'^get_updates/(\d+)/$', 'profiles.views.get_updates', name='get_updates'),
)
