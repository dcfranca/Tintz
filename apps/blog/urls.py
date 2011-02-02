from django.conf.urls.defaults import *

from blog import views, models
from blog.forms import *

urlpatterns = patterns('',
    # blog post
    url(r'^post/(?P<username>[^/]+)/(?P<year>\d{4})/(?P<month>\d{2})/(?P<slug>[-\w]+)/$', 'blog.views.post', name='blog_post'),

    # all blog posts
    url(r'^$', 'blog.views.blogs', name="blog_list_all"),

    # blog post for user
    url(r'^posts/(?P<username>[^/]+)/$', 'blog.views.blogs', name='blog_list_user'),

    # new blog post
    url(r'^new/$', 'blog.views.new', name='blog_new'),

    # edit blog post
    url(r'^edit/(\d+)/$', 'blog.views.edit', name='blog_edit'),

    #destory blog post
    url(r'^destroy/(\d+)/$', 'blog.views.destroy', name='blog_destroy'),

)
