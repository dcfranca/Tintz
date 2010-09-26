# -*- coding: iso-8859-1 -*-
from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template
from django.contrib import admin

from dajaxice.core import dajaxice_autodiscover
dajaxice_autodiscover()

#from bookmarks.feeds import BookmarkFeed
#bookmarks_feed_dict = {"feed_dict": { '': BookmarkFeed }}

admin.autodiscover()

urlpatterns = patterns('',

    url(r'^$', 'profiles.views.home', name='home'),

    (r'^about/', include('about.urls')),
    (r'^account/', include('account.urls')),

    #(r'^registration/', include('registration.urls')),
    (r'^bbauth/', include('bbauth.urls')),
    (r'^authsub/', include('authsub.urls')),
    (r'^profiles/', include('profiles.urls')),
    (r'^blog/', include('blog.urls')),
    (r'^tags/', include('tag_app.urls')),
    (r'^notices/', include('notification.urls')),
    #(r'^announcements/', include('announcements.urls')),
    (r'^comments/', include('threadedcomments.urls')),
    (r'^robots.txt$', include('robots.urls')),
    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'^follow/', include('follow.urls')),
    (r'^admin/(.*)', admin.site.root),
    (r'^publications/', include('publications.urls')),
    (r'^avatar/', include('avatar.urls')),
    (r'^flag/', include('flag.urls')),

    #Dajax
    (r'^%s/' % settings.DAJAXICE_MEDIA_PREFIX, include('dajaxice.urls')),

    #(r'^feeds/bookmarks/(.*)/?$', 'django.contrib.syndication.views.feed', bookmarks_feed_dict),
)


if settings.SERVE_MEDIA:
    urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'misc.views.serve')
    )
