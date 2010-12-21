# -*- coding: iso-8859-1 -*-
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',    
    #upload publication
    url(r'^upload$', 'publications.views.uploadpublication', name='publication_upload'),
    #a publication details
    url(r'^details/(?P<username>[^/]+)/(?P<id>\d+)/$', 'publications.views.detailspublication', name="publication_details"),
    #publication viewer
    url(r'^viewer/(?P<username>[^/]+)/(?P<id>\d+)/$', 'publications.views.viewerpublication', name="publication_viewer"),
    #search prepare
    url(r'^searchprepare$', 'publications.views.searchprepare', name="search_prepare"),
    #search publications
    url(r'^search/(?P<search_text>[^/]+)/$', 'publications.views.searchresults', name="search_results"),
    #delete publications
    url(r'^destroy/(\d+)/$', 'publications.views.destroypublication', name="destroy_publication"),
    #edit publications
    url(r'^edit/(\d+)/$', 'publications.views.editpublication', name="edit_publication"),
    #view my publications
    url(r'^(?P<username>[^/]+)/$', 'publications.views.publications', name='publications'),
    #report abuse
    url(r'^report_abuse/(?P<id>\d+)/$', 'publications.views.reportabuse', name='report_abuse'),

)
