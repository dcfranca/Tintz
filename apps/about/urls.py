from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
    url(r'^$', direct_to_template, {"template": "about/about.html"}, name="about"),

    url(r'^terms/$', direct_to_template, {"template": "about/terms.html"}, name="terms"),
    url(r'^privacy/$', direct_to_template, {"template": "about/privacy.html"}, name="privacy"),
    url(r'^dmca/$', direct_to_template, {"template": "about/dmca.html"}, name="dmca"),

    url(r'^whats_tintz/$', direct_to_template, {"template": "about/whats_tintz.html"}, name="whats_tintz"),
    url(r'^confirm_email/$', direct_to_template, {"template": "about/confirm_email.html"}, name="confirm_email"),
    url(r'^old_browser/$', direct_to_template, {"template": "about/old_browser.html"}, name="old_browser"),
)
