from django.conf.urls.defaults import *

urlpatterns = patterns('',

    # all tintzsettings
    url(r'^$', 'tintzsettings.views.tintzsettings', name="tintz_settings"),
)
