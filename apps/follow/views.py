from datetime import datetime
import urlparse
import urllib2

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.contrib.auth.models import User

from django.utils.translation import ugettext_lazy as _

from follow.models import FollowAuthor, Update
#from notification.models import *

from account.utils import login_complete

@login_complete
def followers(request,  username): 
    users = []
    user = get_object_or_404(User, username=username)
    if request.user.is_authenticated():        
        followers = FollowAuthor.objects.filter( UserTo = user )    
        for  follow in followers:        
            users.append( follow.UserFrom ) 
            
    users = users[0:10]

    is_follow = False
    try:
        follow = FollowAuthor.objects.get( UserFrom=request.user,  UserTo=user )
        if follow:
            is_follow = True
        else:
            is_follow = False
    except FollowAuthor.DoesNotExist:
        pass

    if request.user == user:
        is_me = True
    else:
        is_me = False
    
    return render_to_response("profiles/profiles.html", {
        "other_profiles": users,
        "title": "Seguidores", 
        "is_me": is_me,
        "other_user": user,
        "is_follow": is_follow,
    }, context_instance=RequestContext(request))

@login_complete
def following(request,  username): 
    users = []
    user = get_object_or_404(User, username=username)
    if request.user.is_authenticated():
        followings = FollowAuthor.objects.filter( UserFrom = user )
        for  follow in followings:
            users.append( follow.UserTo )

    users = users[0:10]

    is_follow = False
    try:
        follow = FollowAuthor.objects.get( UserFrom=request.user,  UserTo=user )
        if follow:
            is_follow = True
        else:
            is_follow = False
    except FollowAuthor.DoesNotExist:
        pass
        
    if request.user == user:
        is_me = True
    else:
        is_me = False

    return render_to_response("profiles/profiles.html", {
        "other_profiles": users,
        "title": "Seguindo",
        "is_me": is_me,
        "other_user": user,
        "is_follow": is_follow,
    }, context_instance=RequestContext(request))   


