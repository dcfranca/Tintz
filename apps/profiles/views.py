# -*- coding: iso-8859-1 -*-
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseForbidden,HttpResponseRedirect
from django.conf import settings

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from profiles.models import Profile
from profiles.forms import ProfileForm
from publications.models import Publication
from follow.models import FollowAuthor
from notification.models import *

from datetime import *

from avatar.templatetags.avatar_tags import avatar

import logging

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

def getNotices(request):
    notices = []
    notice_types = NoticeType.objects.filter( to_follow=True )
    for notice_type in notice_types:
        notices += Notice.objects.notices_for(request.user, notice_type=notice_type,  on_site=True)
    for medium_id, medium_display in NOTICE_MEDIA:
        form_label = "%s_%s" % (notice_type.label, medium_id)

    return notices;

def getPublications(request, other_user, is_me):
    publications = []
    try:
        if is_me == True:
            publications = Publication.objects.filter( author = other_user )
        else:
            publications = Publication.objects.filter( author = other_user, rated__lte=request.user.get_profile().age )        
    except Publication.DoesNotExist:
        pass
    return publications[:4]

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

def home(request, template_name="homepage.html"):
    
    notices = []
    publications   = []
    followingUsers = []
    followerUsers  = []
    
    logging.debug("Home - Enter")

    if request.user.is_authenticated():
        logging.debug("home - Usuario logado")    
        notices = getNotices(request)
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
        "notices": notices,
        "publications": publications,
        "followers":followerUsers,
        "followings":followingUsers,
    }, context_instance=RequestContext(request))    
    

def profiles(request, template_name="profiles/profiles.html"):    
    return render_to_response(template_name, {
        "other_profiles": User.objects.all().order_by("-date_joined"),
        "title": "Perfis",
    }, context_instance=RequestContext(request))

def profile(request, username, template_name="profiles/profile.html"):
    other_user = get_object_or_404(User, username=username)    
    publications = []
    is_follow = False
    
    calc_age(other_user.get_profile())
    
    if request.user == other_user:
        is_me = True
    else:
        is_me = False

    if  request.user.is_authenticated() and request.method == "POST":
        if request.POST["action"] == "follow":
            #invite_form = InviteFriendForm(request.user, {
            #    'to_user': username,
            #    'message': ugettext("Vamos ser Amigos!"),
            #})
            
            follow = FollowAuthor()
            follow.UserFrom = request.user
            follow.UserTo = other_user                
            request.user.message_set.create(message=_(u"Você agora está seguindo %(from_user)s") % {'from_user': other_user.username})
            follow.save()
        elif request.POST["action"] == "unfollow":
            #invite_form = InviteFriendForm(request.user, {
            #    'to_user': username,
            #    'message': ugettext("Vamos ser Amigos!"),
            #})
            try:
                follow = FollowAuthor.objects.get(  UserFrom=request.user,  UserTo=other_user )
                request.user.message_set.create(message=_(u"Você não está mais seguindo %(from_user)s") % {'from_user': other_user.username})
                follow.delete()                
            except FollowAuthor.DoesNotExist:
                pass                
    
    #Finding publications
    calc_age(request.user.get_profile())

    publications = getPublications(request, other_user, is_me)
    
    #Finding followings
    followinUsers = getFollowings(request,other_user)
            
    #Finding followers            
    followerUsers = getFollowers(request,other_user)    
    
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

#    other_friends = other_friends[:10]
    publications  = publications[:3]
    followinUsers = followinUsers[:10]
    followerUsers = followerUsers[:10]
    
    return render_to_response(template_name, {
        "profile_form": profile_form,
        "is_me": is_me,
        #"is_friend": is_friend,
        "is_follow": is_follow, 
        "other_user": other_user,
        #"other_friends": other_friends,
        #"invite_form": invite_form,
        #"previous_invitations_to": previous_invitations_to,
        #"previous_invitations_from": previous_invitations_from,
        "publications": publications, 
        "followings": followinUsers,
        "followers": followerUsers,
        "is_edit": is_edit,        
    }, context_instance=RequestContext(request))


def calc_age(profile):    
    if profile.birth_date.month > date.today().month or ( profile.birth_date.month == date.today().month and profile.birth_date.day > date.today().day ):
        profile.age = date.today().year - profile.birth_date.year - 1
    else:
        profile.age = date.today().year - profile.birth_date.year
   
