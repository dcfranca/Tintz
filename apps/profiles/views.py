# -*- coding: iso-8859-1 -*-
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseForbidden,HttpResponseRedirect
from django.conf import settings
from django.contrib.auth.decorators import login_required

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from profiles.models import Profile
from profiles.forms import ProfileForm
from publications.models import Publication
from follow.models import FollowAuthor,Update
from notification.models import *

from datetime import *
from blog.models import Post

from avatar.templatetags.avatar_tags import avatar
from account.utils import login_complete

from blog.models import Post

import logging

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

def getPublications(request, other_user, is_me):
    publications = []
    try:
        if is_me == True:
            publications = Publication.objects.filter( author = other_user ).order_by('-date_added')
        else:
            publications = Publication.objects.filter( author = other_user, rated__lte=request.user.get_profile().age ).order_by('-date_added')
    except Publication.DoesNotExist:
        pass
    return publications

def getFollowers(request, other_user):
    followers = FollowAuthor.objects.filter( UserTo = other_user )
    followerUsers = []
    for follow in followers:
        followerUsers.append( follow.UserFrom )    
    return followerUsers

def getFollowings(request, other_user):
    #Finding followings            
    followings = FollowAuthor.objects.filter( UserFrom = other_user )
    followinUsers = []
    for  follow in followings:
        followinUsers.append( follow.UserTo )
    return followinUsers

@login_complete
def home(request, template_name="homepage.html"):
    
    updates = []
    publications   = []
    followingUsers = []
    followerUsers  = []
    
    logging.debug("Home - Enter")

    if request.user.is_authenticated():
        logging.debug("home - Usuario logado")    
        updates = Update.objects.filter(user = request.user).order_by('-date_post')[0:10]
        publications = getPublications(request, request.user, True)
        followerUsers = getFollowers(request, request.user)
        followingUsers = getFollowings(request, request.user)
    else:
        logging.debug("Home - Usario nao logado")
        return HttpResponseRedirect(reverse('acct_login'))
        
    logging.debug("Home - Leave")
    
    return render_to_response(template_name, {
        "other_user": request.user,
        "is_me": True,
        "updates": updates,
        "notices": None,
        "publications": publications,
        "followers":followerUsers,
        "followings":followingUsers,
    }, context_instance=RequestContext(request))    
    

def profiles(request, template_name="profiles/profiles.html"):    
    return render_to_response(template_name, {
        "other_profiles": User.objects.all().order_by("-date_joined"),
        "title": "Perfis",
    }, context_instance=RequestContext(request))

def button_follow(request, other_user):
    follow = FollowAuthor()
    follow.UserFrom = request.user
    follow.UserTo = other_user
    Update.objects.update_followers(0, other_user)
    #request.user.message_set.create(message=_(u"Você agora está seguindo %(from_user)s") % {'from_user': other_user.username})
    follow.save()


def button_unfollow(request, other_user):
    try:
        follow = FollowAuthor.objects.get(  UserFrom=request.user,  UserTo=other_user )
        #request.user.message_set.create(message=_(u"Você não está mais seguindo %(from_user)s") % {'from_user': other_user.username})
        follow.delete()
    except FollowAuthor.DoesNotExist:
        pass

def profile(request, username, to_follow = None, template_name="profiles/profile.html"):
    other_user = get_object_or_404(User, username=username)
    publications = []
    is_follow = False

    calc_age(other_user.get_profile())

    if request.user == other_user:
        is_me = True
    else:
        is_me = False

    if not is_me and to_follow == '1':
        button_follow(request, other_user)
    elif not is_me and to_follow == '0':
        button_unfollow(request, other_user)

    #Finding publications
    calc_age(request.user.get_profile())

    publications = getPublications(request, other_user, is_me)

    #Finding followings
    followinUsers = getFollowings(request,other_user)

    #Finding followers
    followerUsers = getFollowers(request,other_user)

    blogs = Post.objects.filter(status=2).select_related(depth=1).order_by("-publish")
    posts = blogs.filter(author=other_user)

    is_edit = False

    if is_me:
        if request.method == "POST":
            if request.POST["action"] == "update":
                profile_form = ProfileForm(request.POST, instance=other_user.get_profile())
                if profile_form.is_valid():
                    profile = profile_form.save()
                    profile.user = other_user
                    profile.save()
                else:
                    is_edit = True
            elif request.POST["action"] == "edit":
                template_name="profiles/profile_edit.html"
                profile_form = ProfileForm(instance=other_user.get_profile())
                is_edit = True
            else:
                profile_form = ProfileForm(instance=other_user.get_profile())
        else:
            profile_form = ProfileForm(instance=other_user.get_profile())
    else:
        profile_form = None

    if request.user.is_authenticated:
        try:
            follow = FollowAuthor.objects.get( UserFrom=request.user,  UserTo=other_user )
            if follow:
                is_follow = True
            else:
                is_follow = False

        except FollowAuthor.DoesNotExist:
            pass

    nr_publications = len(publications)
    nr_posts        = len(posts)
    nr_followings   = len(followinUsers)
    nr_followers    = len(followerUsers)

    publications  = publications[:6]
    posts         = posts[:8]
    followinUsers = followinUsers[:21]
    followerUsers = followerUsers[:21]

    return render_to_response(template_name, {
        "form": profile_form,
        "is_me": is_me,
        "is_follow": is_follow,
        "other_user": other_user,
        "publications": publications,
        "followings": followinUsers,
        "followers": followerUsers,
        "is_edit": is_edit,
        "posts": posts,
        "nr_publications": nr_publications,
        "nr_posts": nr_posts,
        "nr_followings": nr_followings,
        "nr_followers": nr_followers,
        }, context_instance=RequestContext(request))


def calc_age(profile):
    if profile.birth_date.month > date.today().month or ( profile.birth_date.month == date.today().month and profile.birth_date.day > date.today().day ):
        profile.age = date.today().year - profile.birth_date.year - 1
    else:
        profile.age = date.today().year - profile.birth_date.year
   
