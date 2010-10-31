from datetime import datetime
import urlparse
import urllib2

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.contrib.auth.models import User

from django.utils.translation import ugettext_lazy as _

from follow.models import FollowAuthor, Update
from notification.models import *

@login_required
def followers(request,  username): 
    users = []
    user = get_object_or_404(User, username=username)
    if request.user.is_authenticated():        
        followers = FollowAuthor.objects.filter( UserTo = user )    
        for  follow in followers:        
            users.append( follow.UserFrom ) 
            
    if request.user == user:
        is_me = True
    else:
        is_me = False
    
    return render_to_response("profiles/profiles.html", {
        "other_profiles": users,
        "title": "Seguidores", 
        "is_me": is_me,
        "other_user": user,
    }, context_instance=RequestContext(request))

@login_required
def following(request,  username): 
    users = []
    user = get_object_or_404(User, username=username)
    if request.user.is_authenticated():
        followings = FollowAuthor.objects.filter( UserFrom = user )
        for  follow in followings:
            users.append( follow.UserTo )
        
    if request.user == user:
        is_me = True
    else:
        is_me = False

    return render_to_response("profiles/profiles.html", {
        "other_profiles": users,
        "title": "Seguindo",
        "is_me": is_me,
        "other_user": user,         
    }, context_instance=RequestContext(request))   


