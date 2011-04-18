# -*- coding: iso-8859-1 -*-
from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

from dajaxice.core import dajaxice_autodiscover
dajaxice_autodiscover()

admin.autodiscover()

urlpatterns = patterns('',

    url(r'^$', 'profiles.views.home', name='home'),
    url(r'^home2$', 'profiles.views.home2', name='home2'),

    (r'^about/', include('about.urls')),
    (r'^account/', include('account.urls')),

    #(r'^bbauth/', include('bbauth.urls')),
    #(r'^authsub/', include('authsub.urls')),
    (r'^profiles/', include('profiles.urls')),
    (r'^blog/', include('blog.urls')),
    #(r'^tags/', include('tag_app.urls')),
    #(r'^notices/', include('notification.urls')),
    (r'^comments/', include('threadedcomments.urls')),
    #(r'^robots.txt$', include('robots.urls')),
    #(r'^i18n/', include('django.conf.urls.i18n')),
    (r'^follow/', include('follow.urls')),
    (r'^adm_tintz/(.*)', admin.site.root),
    (r'^publications/', include('publications.urls')),
    (r'^avatar/', include('avatar.urls')),
    #(r'^flag/', include('flag.urls')),
    (r'^tintzsettings/', include('tintzsettings.urls')),
    (r'^search/', include('haystack.urls')),

    #Dajax
    (r'^%s/' % settings.DAJAXICE_MEDIA_PREFIX, include('dajaxice.urls')),
)


if settings.SERVE_MEDIA:
    urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'misc.views.serve')
    )
